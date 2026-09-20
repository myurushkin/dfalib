"""Command line: solve a query file.

    python3 -m minstr.cli query.txt --all --count --sample 5
"""

from __future__ import annotations

import argparse
import sys

from .query import parse_problem
from .search import find_minimal, all_minimal
from .baseline import find_minimal_eager
from . import formula as F


def main(argv=None):
    ap = argparse.ArgumentParser(prog="minstr", description=__doc__)
    ap.add_argument("file", help="query file ('-' for stdin)")
    ap.add_argument("--all", action="store_true", help="build the graph of all minimal solutions")
    ap.add_argument("--count", action="store_true", help="print how many minimal solutions exist")
    ap.add_argument("--list", type=int, metavar="N", help="print N minimal solutions")
    ap.add_argument("--sample", type=int, metavar="N", help="print N uniformly random minimal solutions")
    ap.add_argument("--eager", action="store_true", help="also run the eager product baseline")
    ap.add_argument("--stats", action="store_true", help="print search statistics")
    args = ap.parse_args(argv)

    text = sys.stdin.read() if args.file == "-" else open(args.file).read()
    problem, names = parse_problem(text)
    print("query:", F.pretty(problem.formula, names))

    word, stats = find_minimal(problem)
    if word is None:
        print("no solution within the length window")
        return 1
    print(f"minimal: {word!r} (length {len(word)})")
    if args.stats:
        print("lazy   :", stats.as_dict())

    if args.all or args.count or args.list or args.sample:
        graph, gstats = all_minimal(problem, length=len(word))
        if args.count:
            print("count  :", graph.count())
        if args.list:
            for w in graph.enumerate(limit=args.list):
                print("  ", w)
        if args.sample:
            for _ in range(args.sample):
                print("  ~", graph.sample())
        if args.stats:
            print("graph  :", gstats.as_dict(), "nodes", graph.nodes())

    if args.eager:
        w, est = find_minimal_eager(problem.trackers, problem.formula, problem.alphabet,
                                    problem.min_len,
                                    None if problem.max_len == float("inf") else problem.max_len)
        print("eager  :", repr(w), est.as_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
