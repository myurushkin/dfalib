"""Walkthrough: what goes in, how the constraints relate, what comes out."""

from __future__ import annotations

import sys

sys.path.insert(0, ".")

from minstr import formula as F
from minstr.search import Problem, find_minimal, all_minimal
from minstr.trackers import RegexTracker, CountTracker, RunsTracker, BalancedTracker
from minstr.optimize import FeasibleGraph, uniform_search, cross_entropy, window_mcmc
from minstr.baseline import find_minimal_eager

A4 = "acgt"


def run(word, trackers):
    """Which constraints does this word satisfy?"""
    out = []
    for t in trackers:
        s = t.start
        for ch in word:
            s = t.step(s, ch)
        out.append(t.accepts(s))
    return out


def show(title, trackers, formula, max_len=40, list_n=4, eager=True):
    names = [t.name for t in trackers]
    print("=" * 78)
    print(title)
    print("-" * 78)
    print("constraints:")
    for i, t in enumerate(trackers):
        kind = type(t).__name__.replace("Tracker", "")
        print(f"   L{i}  {kind:<9} {t.name}")
        if not isinstance(t, RegexTracker):
            print(f"        {'':<9} as a regex this would be: {t.to_regex()}")
    print("relation:  " + F.pretty(formula, [f"L{i}" for i in range(len(trackers))]))
    print("           " + F.pretty(formula, names))

    p = Problem(trackers, formula, A4, max_len=max_len)
    word, st = find_minimal(p)
    if word is None:
        print("result:    no string satisfies this within the length window")
        return None
    print(f"\nminimal:   {word!r}   length {len(word)}   "
          f"(visited {st.distinct:,} states in {st.seconds:.3f}s)")
    marks = run(word, trackers)
    print("           satisfies: " + ", ".join(
        f"L{i}={'yes' if m else 'no'}" for i, m in enumerate(marks)))
    graph, _ = all_minimal(p, length=len(word))
    total = graph.count()
    print(f"all minimal solutions: {total:,}")
    shown = list(graph.enumerate(limit=list_n))
    print("           " + ", ".join(repr(w) for w in shown) + (" ..." if total > len(shown) else ""))
    if eager:
        ew, est = find_minimal_eager(trackers, formula, A4, max_len=max_len, limit=300_000)
        d = est.as_dict()
        print(f"eager pipeline: {ew!r}  peak DFA {d['peak_states']:,} states, "
              f"{d['seconds_build'] + d['seconds_search']:.3f}s"
              + (f"  [{d['failed']}]" if d["failed"] else ""))
    return p


# ---------------------------------------------------------------- 1 --------
t1 = [RegexTracker(".*gg.*", A4, name="contains gg"),
      RegexTracker(".*ct.*", A4, name="contains ct"),
      RegexTracker(".*aca.*", A4, name="contains aca")]
show("EXAMPLE 1  plain intersection of three regular expressions",
     t1, F.AND(F.leaf(0), F.leaf(1), F.leaf(2)))

# ---------------------------------------------------------------- 2 --------
t2 = [RegexTracker(".*gg.*", A4, name="contains gg"),
      RegexTracker(".*ct.*", A4, name="contains ct"),
      RegexTracker(".*aca.*", A4, name="contains aca"),
      RegexTracker("g.*", A4, name="starts with g")]
show("EXAMPLE 2  the same, but one branch is a union and one is negated",
     t2, F.AND(F.OR(F.leaf(0), F.leaf(1)), F.leaf(2), F.NOT(F.leaf(3))))

# ---------------------------------------------------------------- 3 --------
t3 = [BalancedTracker("g", ".*", "c", 2, 4, A4),
      RegexTracker(".*at.*", A4, name="contains at"),
      CountTracker("ta", 2, A4)]
show("EXAMPLE 3  the x{n} M z{n} construct: equal numbers of g before and c after",
     t3, F.AND(F.leaf(0), F.leaf(1), F.leaf(2)))

# ---------------------------------------------------------------- 4 --------
n = 10
t4 = [RegexTracker(f".*a.{{{n}}}", A4, name=f"an 'a' exactly {n} symbols before the end"),
      RegexTracker(f".*c.{{{n-1}}}", A4, name=f"a 'c' exactly {n-1} symbols before the end"),
      RegexTracker(".*gt.*", A4, name="contains gt")]
show(f"EXAMPLE 4  the hard family: two 'lookback' constraints (n={n})",
     t4, F.AND(F.leaf(0), F.leaf(1), F.leaf(2)))

# ---------------------------------------------------------------- 5 --------
print("=" * 78)
print("EXAMPLE 5  optimising a black-box score over the feasible strings")
print("-" * 78)
t5 = [RegexTracker(".*gg.*", A4, name="contains gg"),
      CountTracker("ca", 2, A4),
      BalancedTracker("a", ".*", "t", 1, 3, A4),
      RegexTracker(".*cccc.*", A4, name="contains cccc")]
f5 = F.AND(F.leaf(0), F.leaf(1), F.leaf(2), F.NOT(F.leaf(3)))
for i, t in enumerate(t5):
    print(f"   L{i}  {t.name}")
print("relation:  " + F.pretty(f5, [f"L{i}" for i in range(4)]))

p5 = Problem(t5, f5, A4, max_len=20)
shortest, _ = find_minimal(p5)
print(f"\nshortest feasible string: {shortest!r} ({len(shortest)})")

LENGTH = 18
BUDGET = 2000


def score_grams(w):
    """Distinct 4-grams minus a penalty for the longest repeated block.
    A smooth landscape: nearly every feasible string is close to the ceiling."""
    grams = len({w[i:i + 4] for i in range(len(w) - 3)})
    longest = 0
    for i in range(len(w)):
        for j in range(i + 1, len(w)):
            k = 0
            while j + k < len(w) and w[i + k] == w[j + k]:
                k += 1
            longest = max(longest, k)
    return grams - 1.5 * longest


def score_rugged(w):
    """Every 3-gram carries a fixed pseudo-random weight, so the landscape has
    many local optima and no additive structure to exploit."""
    import hashlib
    total = 0.0
    for i in range(len(w) - 2):
        h = hashlib.md5(w[i:i + 3].encode()).digest()[0]
        total += (h / 255.0) ** 3
    return round(total, 3)


graph = FeasibleGraph(p5, LENGTH)
print(f"\nfeasible strings of length {LENGTH}: {graph.count():,}  "
      f"(graph: {len(graph.alive):,} nodes)")

for label, sc in (("smooth score (distinct 4-grams minus longest repeat)", score_grams),
                  ("rugged score (pseudo-random weight per 3-gram)", score_rugged)):
    print(f"\n{label}, budget {BUDGET} evaluations, mean over 3 seeds:")
    print(f"   {'method':<16}{'mean best':>11}{'best':>9}   best string found")
    for name, fn in (("uniform", uniform_search), ("cross-entropy", cross_entropy),
                     ("window-mcmc", window_mcmc)):
        vals, best = [], None
        for seed in range(3):
            tr = fn(graph, sc, BUDGET, seed=seed)
            vals.append(tr.best)
            if best is None or tr.best > best.best:
                best = tr
        print(f"   {name:<16}{sum(vals) / len(vals):>11.3f}{best.best:>9.3f}   {best.best_word}")
        marks = run(best.best_word, t5)
        assert marks[0] and marks[1] and marks[2] and not marks[3]

print("\nOn the smooth score every method ties: sampling uniformly from the")
print("language already lands near the ceiling, so nothing is left to learn.")
print("On the rugged score the learners separate from uniform sampling.")
print("\nEvery candidate ever proposed satisfies the constraints by construction:")
tr = window_mcmc(graph, score_rugged, 500, seed=0)
good = sum(1 for w in tr.cache if all(run(w, t5)[:3]) and not run(w, t5)[3])
print(f"   {len(tr.cache):,} distinct strings evaluated, {good:,} of them feasible")
