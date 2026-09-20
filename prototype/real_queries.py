"""Real dfalib query families driven through the minstr prototype.

The constraint families reproduce ``src/dafna/lib/generation``:

* GQD canonical, strength k:   X* g^k X+ g^k X+ g^k X+ g^k X*
* GQD tandem repeats, k:       X* (gY)^{4k-1} g X*          (Y = a|c|t)
* i-motif(n, m, a, b, c):      X* c^n X^a c^m X^b c^n X^c c^m X*

Minimal strings are found exactly by the lazy search, compared against the
eager product pipeline, and every answer is cross-checked with the *real*
strength functions from ``src/dafna/lib/strength``.  The optimisation part
maximises the real (non-additive) strengths over feasible strings of a fixed
length under the same evaluation budget for every method.

Run from the repository root:  venv/bin/python prototype/real_queries.py
"""

from __future__ import annotations

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from minstr import formula as F
from minstr.search import Problem, Stats, find_minimal, all_minimal
from minstr.trackers import RegexTracker
from minstr.baseline import find_minimal_eager, TooLarge
from minstr.optimize import FeasibleGraph, uniform_search, cross_entropy, window_mcmc

from dafna.lib.strength.strength import (
    gqd_max_strength,
    i_motif_max_strength,
    hairpin_max_strength,
    triplex_max_strength,
)

ALPHA = "acgt"


def gqd_canonical(k, name=None):
    g = "g" * k
    return RegexTracker(f".*{g}.+{g}.+{g}.+{g}.*", ALPHA, name=name or f"GQD{k}")


def gqd_tandem(k, name=None):
    body = "(g[act])" + "{" + str(4 * k - 1) + "}g"
    return RegexTracker(f".*{body}.*", ALPHA, name=name or f"TAND{k}")


def i_motif(n, m, a, b, c, name=None):
    cn, cm = "c" * n, "c" * m
    pat = f".*{cn}.{{{a}}}{cm}.{{{b}}}{cn}.{{{c}}}{cm}.*"
    return RegexTracker(pat, ALPHA, name=name or f"IMT({n},{m},{a},{b},{c})")


def imt_strength(w):
    return max(i_motif_max_strength(w, False), i_motif_max_strength(w, True))


def check(word, checks):
    """Cross-check a found word against the real dfalib strength functions.

    Deliberately non-fatal: the dfalib checkers are position-sensitive (their
    ``findall`` scan is non-overlapping and can lock onto an earlier, weaker
    occurrence), so a word matching the generator pattern may still be scored
    below the nominal strength.  Mismatches are reported, not raised.
    """
    out, ok_all = [], True
    for label, fn, expect in checks:
        got = fn(word)
        ok = expect(got)
        ok_all &= ok
        out.append(f"{label}={got}{'' if ok else '  << below nominal'}")
    return "  ".join(out), ok_all


def run_case(title, trackers, formula, checks, max_len=64, eager_limit=300_000):
    print("=" * 78)
    print(title)
    p = Problem(trackers, formula, ALPHA, max_len=max_len)
    st = Stats()
    t0 = time.time()
    word, st = find_minimal(p)
    lazy_t = time.time() - t0
    if word is None:
        print(f"  no string up to length {max_len}")
        return
    graph, _ = all_minimal(p, length=len(word))
    total = graph.count()
    print(f"  lazy : {word!r}  len={len(word)}  states={st.distinct:,}  "
          f"time={lazy_t:.3f}s  optima={total:,}")
    try:
        t0 = time.time()
        ew, est = find_minimal_eager(trackers, formula, ALPHA,
                                     max_len=max_len, limit=eager_limit)
        d = est.as_dict()
        print(f"  eager: {ew!r}  len={len(ew) if ew else '-'}  "
              f"peak={d.get('peak_states', '?'):,}  time={time.time()-t0:.3f}s")
        assert ew is not None and len(ew) == len(word), "eager/lazy length mismatch"
    except TooLarge:
        print(f"  eager: product exceeded {eager_limit:,} states, abandoned")
    text, ok_all = check(word, checks)
    print("  real strengths of the lazy answer: " + text)
    if not ok_all:
        # The pattern is satisfied but the real checker rates the word below
        # the nominal strength.  Count how many of the equally-minimal words
        # actually pass, and show one that does.
        passing, first, seen = 0, None, 0
        for w in graph.enumerate(limit=4096):
            seen += 1
            if all(expect(fn(w)) for _, fn, expect in checks):
                passing += 1
                if first is None:
                    first = w
        print(f"  checker-approved optima: {passing:,}/{seen:,} inspected"
              + (f", e.g. {first!r}" if first else ""))


def main():
    # 1. Pure GQD canonical, strength 2.
    run_case("GQD canonical, strength 2",
             [gqd_canonical(2)], F.leaf(0),
             [("GQD", gqd_max_strength, lambda v: v >= 2)])

    # 2. GQD strength exactly 2: GQD(2) and not GQD(3).
    run_case("GQD strength exactly 2  (GQD2 and not GQD3)",
             [gqd_canonical(2), gqd_canonical(3)],
             F.AND(F.leaf(0), F.NOT(F.leaf(1))),
             [("GQD", gqd_max_strength, lambda v: v == 2)])

    # 3. Intersection of two structures: GQD(2) and i-motif(2,2,1,1,1).
    run_case("GQD2 and IMT(2,2,1,1,1)",
             [gqd_canonical(2), i_motif(2, 2, 1, 1, 1)],
             F.AND(F.leaf(0), F.leaf(1)),
             [("GQD", gqd_max_strength, lambda v: v >= 2),
              ("IMT", imt_strength, lambda v: v >= 2)])

    # 4. Union plus intersection with nesting: (GQD3 or TAND2) and IMT.
    run_case("(GQD3 or TAND2) and IMT(2,2,1,1,1)",
             [gqd_canonical(3), gqd_tandem(2), i_motif(2, 2, 1, 1, 1)],
             F.AND(F.OR(F.leaf(0), F.leaf(1)), F.leaf(2)),
             [("GQD", gqd_max_strength, lambda v: v >= 2),
              ("IMT", imt_strength, lambda v: v >= 2)])

    # 5. Larger intersection: three motifs at once.
    run_case("GQD2 and TAND2 and IMT(2,2,1,1,1)",
             [gqd_canonical(2), gqd_tandem(2), i_motif(2, 2, 1, 1, 1)],
             F.AND(F.leaf(0), F.leaf(1), F.leaf(2)),
             [("GQD", gqd_max_strength, lambda v: v >= 2),
              ("IMT", imt_strength, lambda v: v >= 2)])

    # ------------------------------------------------------------------
    # Optimisation of the real, non-additive force over feasible strings.
    # Constraint: GQD canonical >= 2.  Score: i-motif + hairpin strengths.
    # ------------------------------------------------------------------
    length = 24
    print("=" * 78)
    print(f"Optimise real force over GQD2-feasible strings of length {length}")

    def force(w):
        return imt_strength(w) + hairpin_max_strength(w)

    p = Problem([gqd_canonical(2)], F.leaf(0), ALPHA, max_len=length)
    graph = FeasibleGraph(p, length)
    print(f"  feasible strings of this length: {graph.count():,}")

    t0 = time.time()
    force("g" * length)
    per_call = max(time.time() - t0, 1e-4)
    budget = int(min(600, max(120, 25.0 / per_call / 3)))
    print(f"  one force call ~{per_call*1000:.1f}ms, budget per method: {budget}")

    rows = []
    for label, fn in (("uniform", uniform_search),
                      ("cross-entropy", cross_entropy),
                      ("window-mcmc", window_mcmc)):
        best_w, best_v = None, None
        t0 = time.time()
        for seed in range(3):
            tr = fn(graph, force, budget // 3, seed=seed)
            if best_v is None or tr.best > best_v:
                best_w, best_v = tr.best_word, tr.best
        rows.append((label, best_v, best_w, time.time() - t0))
    for label, v, w, dt in rows:
        parts = (f"IMT={imt_strength(w)}", f"HRP={hairpin_max_strength(w)}",
                 f"GQD={gqd_max_strength(w)}")
        print(f"  {label:<14} best={v:.1f}  {w!r}  ({', '.join(parts)})  {dt:.1f}s")


if __name__ == "__main__":
    main()
