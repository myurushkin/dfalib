"""Disjunctive decomposition of a query into small lazy searches.

Monolithic lazy search carries one tracker state per live leaf, so a query
that is a union of hundreds of patterns drags a huge tuple through every
step.  This module splits the formula into DNF conjuncts (tiny AND-only
queries over a handful of leaves), solves each with the ordinary lazy A*,
and combines the answers:

* conjuncts are ordered by their admissible lower bound, cheapest first;
* a global incumbent prunes: once a word of length ``B`` is known, conjuncts
  whose bound is ``>= B`` cannot improve it, and since the list is sorted the
  whole remaining tail is dropped;
* every solved conjunct tightens ``max_len`` for the following ones;
* ``stop_at_first`` turns the search into pure feasibility checking (any
  satisfying word ends the sweep) — the natural mode for fixed-length queries.

The decomposition is exact: the minimum over conjuncts is the minimum over
the original formula.  ``to_dnf`` can blow up on adversarial formulas, so the
number of conjuncts is capped and a ``DecompositionTooLarge`` is raised above
the cap — the caller should fall back to the monolithic search.
"""

from __future__ import annotations

import time

from . import formula as F
from .search import Problem, find_minimal

INF = float("inf")


class DecompositionTooLarge(ValueError):
    pass


class DecomposeStats:
    def __init__(self):
        self.conjuncts = 0
        self.solved = 0
        self.pruned = 0
        self.feasible = 0
        self.distinct = 0
        self.seconds = 0.0
        self.best_conjunct = None
        self.exhausted = False   # state budget ran out before the sweep ended

    def as_dict(self):
        return dict(conjuncts=self.conjuncts, solved=self.solved,
                    pruned=self.pruned, feasible=self.feasible,
                    distinct=self.distinct, seconds=round(self.seconds, 4),
                    best_conjunct=self.best_conjunct, exhausted=self.exhausted)


def solve_dnf(trackers, formula, alphabet, min_len=0, max_len=None,
              stop_at_first=False, max_conjuncts=100_000, state_budget=None,
              stats=None):
    """Minimal word satisfying ``formula`` via per-conjunct lazy searches.

    Returns ``(word, stats)``; ``word`` is None when no conjunct is feasible
    within the length window.  With ``stop_at_first`` the first satisfying
    word (from the cheapest-bound conjunct on) is returned instead of the
    guaranteed minimum — with ``min_len == max_len`` the two coincide.

    ``state_budget`` caps the total distinct states across the sweep; when it
    runs out the sweep stops and ``stats.exhausted`` is set, so ``word is
    None`` then means *undecided*, not proven infeasible.
    """
    st = stats or DecomposeStats()
    t0 = time.perf_counter()

    conjuncts = F.to_dnf(formula)
    if len(conjuncts) > max_conjuncts:
        raise DecompositionTooLarge(
            f"{len(conjuncts)} conjuncts exceed the cap {max_conjuncts}")
    # Dedupe (to_dnf of overlapping unions can repeat literal sets).
    seen, uniq = set(), []
    for lits in conjuncts:
        key = frozenset(lits)
        if key not in seen:
            seen.add(key)
            uniq.append(F.AND(*lits) if lits else F.TRUE)
    st.conjuncts = len(uniq)

    # Order by the admissible bound of the initial state, cheapest first.
    ordered = []
    for cf in uniq:
        p = Problem(trackers, cf, alphabet, min_len=min_len, max_len=max_len)
        ordered.append((p.bound(p.initial()), cf))
    ordered.sort(key=lambda bc: bc[0])

    best, best_len = None, INF
    limit = max_len if max_len is not None else INF
    for bound, cf in ordered:
        if bound >= best_len or bound > limit:
            # Sorted by bound: nothing later can improve the incumbent.
            st.pruned += st.conjuncts - st.solved
            break
        cap = min(limit, best_len - 1) if best is not None else limit
        p = Problem(trackers, cf, alphabet, min_len=min_len,
                    max_len=None if cap is INF else cap)
        word, sub = find_minimal(p)
        st.solved += 1
        st.distinct += sub.distinct
        if word is not None:
            st.feasible += 1
            if len(word) < best_len:
                best, best_len = word, len(word)
                st.best_conjunct = F.pretty(cf, [getattr(t, "name", str(i))
                                                 for i, t in enumerate(trackers)])
            if stop_at_first or best_len <= bound:
                # bound is admissible, so best_len == bound is unbeatable.
                st.pruned += st.conjuncts - st.solved
                break
        if state_budget is not None and st.distinct >= state_budget:
            st.exhausted = True
            break

    st.seconds = time.perf_counter() - t0
    return best, st
