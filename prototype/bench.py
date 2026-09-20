"""Eager product construction versus lazy tracker search.

Every row cross-checks the two methods: they must return solutions of the same
length, otherwise the row is marked BAD.  The point of the table is the cost
paid *before* the search starts.
"""

from __future__ import annotations

import argparse
import sys
import time

sys.path.insert(0, ".")

from minstr import formula as F
from minstr.search import Problem, find_minimal
from minstr.baseline import find_minimal_eager
from minstr.trackers import RegexTracker, CountTracker, RunsTracker, BalancedTracker

ALPHA = "acgt"
LIMIT = 300_000


def family_substrings(k):
    """k substring constraints, all conjoined."""
    subs = ["gg", "ct", "aca", "tgt", "cca", "agg", "tta", "gac"][:k]
    tr = [RegexTracker(f".*{s}.*", ALPHA, name=f"has({s})") for s in subs]
    return tr, F.AND(*[F.leaf(i) for i in range(k)]), f"{k} substrings"


def family_counters(hi):
    """One balanced {n} constraint with range [1..hi] plus two regexes."""
    tr = [BalancedTracker("a", ".*", "c", 1, hi, ALPHA),
          RegexTracker(".*gg.*", ALPHA, name="has(gg)"),
          RegexTracker(".*tt.*", ALPHA, name="has(tt)")]
    return tr, F.AND(F.leaf(0), F.leaf(1), F.leaf(2)), f"balanced n=[1..{hi}]"


def family_thresholds(k):
    """Counting thresholds: at least k occurrences of two substrings."""
    tr = [CountTracker("ca", k, ALPHA), CountTracker("gt", k, ALPHA),
          RunsTracker("g", 2, k, ALPHA)]
    return tr, F.AND(F.leaf(0), F.leaf(1), F.leaf(2)), f"thresholds k={k}"


def family_union(k):
    """Disjunction of k conjunctions: the case where folding pays."""
    tr, parts = [], []
    for i in range(k):
        a, b = ["gg", "ct", "aca", "tgt", "cca", "agg"][i % 6], ["tt", "ga", "cgc", "aag"][i % 4]
        tr.append(RegexTracker(f".*{a}.*", ALPHA, name=f"A{i}"))
        tr.append(RegexTracker(f".*{b}.*", ALPHA, name=f"B{i}"))
        parts.append(F.AND(F.leaf(2 * i), F.leaf(2 * i + 1)))
    return tr, F.OR(*parts), f"union of {k} pairs"


def family_lookback(n):
    """Classic determinisation blow-up: ".*a.{n}" needs 2^n DFA states.
    Two of them with different offsets, conjoined with a substring."""
    tr = [RegexTracker(f".*a.{{{n}}}", ALPHA, name=f"a.{{{n}}}$"),
          RegexTracker(f".*c.{{{max(n - 1, 1)}}}", ALPHA, name=f"c.{{{n-1}}}$"),
          RegexTracker(".*gt.*", ALPHA, name="has(gt)")]
    return tr, F.AND(F.leaf(0), F.leaf(1), F.leaf(2)), f"lookback n={n}"


def family_multi_balanced(k):
    """k balanced {n} constraints at once, ranges [1..3]; the eager pipeline
    unrolls each into a union and multiplies them."""
    pairs = [("a", "c"), ("g", "t"), ("c", "g"), ("t", "a"), ("a", "g")][:k]
    tr = [BalancedTracker(l, ".+", r, 1, 3, ALPHA) for l, r in pairs]
    tr.append(RegexTracker(".*tt.*", ALPHA, name="has(tt)"))
    return tr, F.AND(*[F.leaf(i) for i in range(k + 1)]), f"{k} balanced"


FAMILIES = [
    ("lookback", family_lookback, [4, 6, 8, 10, 12, 14]),
    ("multibalanced", family_multi_balanced, [1, 2, 3, 4, 5]),
    ("substrings", family_substrings, [2, 3, 4, 5, 6, 7, 8]),
    ("balanced", family_counters, [1, 2, 3, 4, 5, 6]),
    ("thresholds", family_thresholds, [1, 2, 3, 4, 5]),
    ("union", family_union, [1, 2, 3, 4]),
]


def bench_one(trackers, formula, label, max_len, do_eager=True):
    problem = Problem(trackers, formula, ALPHA, max_len=max_len)
    lazy_word, lstats = find_minimal(problem)

    nofold = Problem(trackers, formula, ALPHA, max_len=max_len, fold=False)
    nf_word, nfstats = find_minimal(nofold)

    if do_eager:
        eager_word, estats = find_minimal_eager(trackers, formula, ALPHA, max_len=max_len,
                                                limit=LIMIT)
    else:
        eager_word, estats = None, None

    ok = "ok"
    if lazy_word is None or nf_word is None or len(lazy_word) != len(nf_word):
        ok = "BAD"
    if estats is not None and estats.failed is None:
        if (eager_word is None) != (lazy_word is None) or (
                lazy_word and len(eager_word) != len(lazy_word)):
            ok = "BAD"
    return dict(label=label, ok=ok, word=lazy_word,
                lazy_states=lstats.distinct, lazy_time=lstats.seconds,
                nofold_states=nfstats.distinct, nofold_time=nfstats.seconds,
                eager_peak=(estats.peak_states if estats else None),
                eager_time=((estats.seconds_build + estats.seconds_search) if estats else None),
                eager_failed=(estats.failed if estats else None))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-len", type=int, default=40)
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    hdr = f"{'family / size':<26}{'answer':>8}{'lazy states':>13}{'lazy s':>9}" \
          f"{'nofold states':>15}{'eager peak':>12}{'eager s':>10}  status"
    print(hdr)
    print("-" * len(hdr))
    for name, fn, sizes in FAMILIES:
        if args.only and args.only != name:
            continue
        eager_alive = True
        for size in sizes:
            trackers, formula, label = fn(size)
            row = bench_one(trackers, formula, label, args.max_len, do_eager=eager_alive)
            peak = row["eager_peak"]
            if row["eager_failed"]:
                peak_s, etime, eager_alive = "over limit", "-", False
            elif peak is None:
                peak_s, etime = "skipped", "-"
            else:
                peak_s, etime = f"{peak:,}", f"{row['eager_time']:.3f}"
            print(f"{label:<26}{len(row['word']) if row['word'] else '-':>8}"
                  f"{row['lazy_states']:>13,}{row['lazy_time']:>9.3f}"
                  f"{row['nofold_states']:>15,}{peak_s:>12}{etime:>10}  {row['ok']}")
        print()


if __name__ == "__main__":
    main()
