"""Do the old (dfalib C++ product automata) and new (minstr lazy search)
engines return the *same set* of minimal strings?

Each query is a list of groups; a group is a list of dfalib patterns
(unioned with psum), groups are intersected with pintersect.  The same
pattern strings are translated for minstr (X -> ., Y -> [act]) so both
sides are built from one source.  Compared: minimal length, number of
minimal strings, and the sets themselves.

Run from the repository root:  venv/bin/python prototype/crosscheck_dfalib.py
"""

from __future__ import annotations

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from minstr import formula as F
from minstr.search import Problem, find_minimal, all_minimal
from minstr.trackers import RegexTracker
from dafna.shared import Context, psum, pintersect

from blowup_bench import trp_pattern_dfalib, trp_triples, imt_pattern_dfalib, gqd_pattern_dfalib

ALPHA = "acgt"


def to_minstr(pat):
    return pat.replace("X", ".").replace("Y", "[act]")


def tandem_dfalib(k):
    return "X*" + "gY" * (4 * k - 1) + "gX*"


def hrp_dfalib(counts):
    comp = {"a": "t", "t": "a", "c": "g", "g": "c"}
    values = [v * counts[v] for v in "atgc"]
    comp_values = [comp[v] * counts[v] for v in "atgc"]
    return "X*" + "X*".join(values) + "XXXX*" + "X*".join(reversed(comp_values)) + "X*"


def run_dfalib(groups):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    ctx.create_pattern("a|c|t", simple=True, name="Y")
    t0 = time.perf_counter()
    parts = [psum([ctx.create_pattern(p) for p in g]) for g in groups]
    result = pintersect(parts)
    words = set(result.min_strings())
    return words, time.perf_counter() - t0


def run_minstr(groups, max_len=64):
    trackers, ors = [], []
    for g in groups:
        leaves = []
        for p in g:
            leaves.append(F.leaf(len(trackers)))
            trackers.append(RegexTracker(to_minstr(p), ALPHA))
        ors.append(F.OR(*leaves))
    formula = F.AND(*ors)
    t0 = time.perf_counter()
    prob = Problem(trackers, formula, ALPHA, max_len=max_len)
    word, _ = find_minimal(prob)
    if word is None:
        return set(), time.perf_counter() - t0
    graph, _ = all_minimal(prob, length=len(word))
    words = set(graph.enumerate(limit=graph.count()))
    return words, time.perf_counter() - t0


QUERIES = [
    ("GQD2", [[gqd_pattern_dfalib(2)]]),
    ("GQD3", [[gqd_pattern_dfalib(3)]]),
    ("TAND2", [[tandem_dfalib(2)]]),
    ("IMT(2,2,1,1,1)", [[imt_pattern_dfalib(2, 2, 1, 1, 1)]]),
    ("IMT(3,2,2,3,3)", [[imt_pattern_dfalib(3, 2, 2, 3, 3)]]),
    ("HRP{a1,t1,g1,c1}", [[hrp_dfalib({"a": 1, "t": 1, "g": 1, "c": 1})]]),
    ("GQD2 and IMT", [[gqd_pattern_dfalib(2)], [imt_pattern_dfalib(2, 2, 1, 1, 1)]]),
    ("GQD2 and not-GQD3-free: GQD2 and TAND2",
     [[gqd_pattern_dfalib(2)], [tandem_dfalib(2)]]),
    ("(GQD3 or TAND2) and IMT",
     [[gqd_pattern_dfalib(3), tandem_dfalib(2)], [imt_pattern_dfalib(2, 2, 1, 1, 1)]]),
    ("union of 9 IMTs", [[imt_pattern_dfalib(n, m, a, 1, 1)
                          for n in (2, 3) for m in (2, 3) for a in (1, 2)][:9]]),
    ("union of 9 IMTs and GQD2",
     [[imt_pattern_dfalib(n, m, a, 1, 1) for n in (2, 3) for m in (2, 3) for a in (1, 2)][:9],
      [gqd_pattern_dfalib(2)]]),
    ("TRP(2) union (40)", [[trp_pattern_dfalib(*t) for t in trp_triples(2)]]),
    ("TRP(2) union and GQD2", [[trp_pattern_dfalib(*t) for t in trp_triples(2)],
                               [gqd_pattern_dfalib(2)]]),
    ("GQD2 and HRP and IMT", [[gqd_pattern_dfalib(2)],
                              [hrp_dfalib({"a": 1, "t": 1, "g": 1, "c": 1})],
                              [imt_pattern_dfalib(2, 2, 1, 1, 1)]]),
]


def main():
    all_ok = True
    print(f"{'query':<36} {'len':>4} {'#dfalib':>9} {'#minstr':>9}  same   t_dfalib  t_minstr")
    for name, groups in QUERIES:
        a, ta = run_dfalib(groups)
        b, tb = run_minstr(groups)
        la = len(next(iter(a))) if a else None
        lb = len(next(iter(b))) if b else None
        same = a == b
        all_ok &= same
        print(f"{name:<36} {str(la)+'/'+str(lb):>4} {len(a):>9,} {len(b):>9,}  "
              f"{'yes' if same else 'NO ':<5} {ta:8.2f}s {tb:8.2f}s")
        if not same:
            only_a = sorted(a - b)[:3]
            only_b = sorted(b - a)[:3]
            print(f"    only dfalib: {only_a}\n    only minstr: {only_b}")
    print("\nALL SETS IDENTICAL" if all_ok else "\nMISMATCHES FOUND")


if __name__ == "__main__":
    main()
