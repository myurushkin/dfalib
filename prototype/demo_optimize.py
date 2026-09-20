"""Optimise a black-box score over the feasible strings of a query.

The score below is deliberately non-additive (it looks at global structure),
so no exact dynamic programme applies and the three optimisers compete on
equal footing under the same evaluation budget.
"""

from __future__ import annotations

import argparse
import sys

sys.path.insert(0, ".")

from minstr import formula as F
from minstr.search import Problem, find_minimal
from minstr.trackers import RegexTracker, CountTracker, BalancedTracker
from minstr.optimize import FeasibleGraph, uniform_search, cross_entropy, window_mcmc

ALPHA = "abcd"


def score(w):
    """Longest palindromic substring, plus distinct 3-grams, minus the longest run."""
    n = len(w)
    best = 1
    for c in range(n):
        for lo, hi in ((c, c), (c, c + 1)):
            while lo >= 0 and hi < n and w[lo] == w[hi]:
                lo -= 1
                hi += 1
            best = max(best, hi - lo - 1)
    grams = len({w[i:i + 3] for i in range(n - 2)})
    run = max(len(r) for r in __import__("re").findall(r"(.)\1*", w)) if n else 0
    run = max((len(m.group(0)) for m in __import__("re").finditer(r"(.)\1*", w)), default=0)
    return best + 0.5 * grams - 2.0 * run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=16)
    ap.add_argument("--budget", type=int, default=3000)
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()

    trackers = [RegexTracker(".*ab.*", ALPHA, name="has(ab)"),
                CountTracker("cd", 2, ALPHA),
                BalancedTracker("a", ".", "c", 1, 3, ALPHA),
                RegexTracker(".*dd.*", ALPHA, name="has(dd)")]
    formula = F.AND(F.leaf(0), F.leaf(1), F.leaf(2), F.NOT(F.leaf(3)))
    problem = Problem(trackers, formula, ALPHA, max_len=args.length)

    shortest, _ = find_minimal(problem)
    print(f"shortest feasible string: {shortest!r} ({len(shortest)})")
    graph = FeasibleGraph(problem, args.length)
    print(f"feasible strings of length {args.length}: {graph.count():,} "
          f"(graph nodes {len(graph.alive):,})")

    methods = [("uniform", uniform_search), ("cross-entropy", cross_entropy), ("window-mcmc", window_mcmc)]
    checkpoints = [c for c in (100, 300, 1000, 3000, 10000) if c <= args.budget]
    print(f"\n{'method':<16}" + "".join(f"{'@' + str(c):>10}" for c in checkpoints) + f"{'best word':>22}")
    for name, fn in methods:
        rows = []
        best_word = None
        for seed in range(args.seeds):
            tr = fn(graph, score, args.budget, seed=seed)
            at = []
            for c in checkpoints:
                v = max((b for e, b in tr.curve if e <= c), default=float("nan"))
                at.append(v)
            rows.append(at)
            if best_word is None or tr.best > score(best_word):
                best_word = tr.best_word
        mean = [sum(r[i] for r in rows) / len(rows) for i in range(len(checkpoints))]
        print(f"{name:<16}" + "".join(f"{m:>10.2f}" for m in mean) + f"{best_word:>22}")
    print("\n(values are the mean over seeds of the best score found within the budget)")


if __name__ == "__main__":
    main()
