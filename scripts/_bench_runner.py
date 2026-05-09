"""
Internal CLI: run ONE benchmark measurement and print a JSON result to stdout.

Usage:
  _bench_runner.py --exp e1 --k K
  _bench_runner.py --exp e2 --L L
  _bench_runner.py --exp e4 --k K --mode {eager,lazy}

Prints exactly one JSON dict to stdout. No other prints. Exit 0 on success, 1 on error.

Time is measured with time.perf_counter around the operation only — Python startup
and dafna import are excluded from time_s.
"""

import sys
import pathlib
import argparse
import json
import time
import resource

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(REPO_ROOT / "src"))

from dafna.shared import Context, pintersect, createGQD, createIMT, createHRP

# 16 unique pattern configurations across three families (same as E1 sweep).
PATTERN_CONFIGS = [
    ("GQD", 2), ("IMT", (2, 1)), ("HRP", {'a': 2, 't': 1, 'g': 1, 'c': 1}),
    ("GQD", 3), ("IMT", (3, 2)), ("HRP", {'a': 1, 't': 2, 'g': 1, 'c': 1}),
    ("GQD", 4), ("IMT", (4, 3)), ("HRP", {'a': 1, 't': 1, 'g': 2, 'c': 1}),
    ("GQD", 5), ("IMT", (2, 2)), ("HRP", {'a': 1, 't': 1, 'g': 1, 'c': 2}),
    ("GQD", 6), ("IMT", (3, 3)), ("IMT", (4, 4)), ("IMT", (5, 5)),
]


def build_patterns(k, ctx):
    """Build k unique patterns from PATTERN_CONFIGS."""
    patterns = []
    for kind, arg in PATTERN_CONFIGS[:k]:
        if kind == "GQD":
            patterns.append(createGQD(arg, ctx))
        elif kind == "IMT":
            a, b = arg
            patterns.append(createIMT(a, b, ctx))
        elif kind == "HRP":
            patterns.append(createHRP(arg, ctx))
    return patterns


def _self_peak_rss_kb():
    """Return this process's peak RSS in KB by reading /proc/self/status VmHWM.

    VmHWM (High Water Mark) is the peak resident set size for this process —
    identical to what getrusage(RUSAGE_SELF).ru_maxrss reports on Linux, but
    readable at any time (not just at process exit).
    """
    try:
        for line in pathlib.Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])  # already in kB
    except Exception:
        pass
    # Fallback: getrusage reports in KB on Linux
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def run_e1(k):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    patterns = build_patterns(k, ctx)

    t0 = time.perf_counter()
    result = pintersect(patterns, lazy=False)
    result.minimize()
    t1 = time.perf_counter()

    states = result.state_count()
    peak_rss_kb = _self_peak_rss_kb()
    return {"time_s": t1 - t0, "states_final": states, "peak_rss_kb": peak_rss_kb}


def run_e2(L):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    repeated = "(a|c|g|t)" * L
    regex = "X*" + repeated + "X*"

    t0 = time.perf_counter()
    automaton = ctx.create_pattern(regex)
    automaton.minimize()
    t1 = time.perf_counter()

    states = automaton.state_count()
    peak_rss_kb = _self_peak_rss_kb()
    return {"time_s": t1 - t0, "states_final": states, "peak_rss_kb": peak_rss_kb}


def run_e4(k, mode):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    p1 = ctx.create_pattern("(a|c|g|t)" * k)
    p2 = ctx.create_pattern("X*" + "g" * k + "X*")

    t0 = time.perf_counter()
    if mode == "lazy":
        result = p1.intersect_lazy(p2)
    else:
        result = p1.intersect(p2)
    t1 = time.perf_counter()

    states_raw = result.state_count()
    peak_rss_kb = _self_peak_rss_kb()
    return {"time_s": t1 - t0, "states_raw": states_raw, "peak_rss_kb": peak_rss_kb}


def main():
    parser = argparse.ArgumentParser(description="Internal bench runner — prints one JSON line")
    parser.add_argument("--exp", required=True, choices=["e1", "e2", "e4"])
    parser.add_argument("--k", type=int)
    parser.add_argument("--L", type=int)
    parser.add_argument("--mode", choices=["eager", "lazy"])
    args = parser.parse_args()

    try:
        if args.exp == "e1":
            if args.k is None:
                raise ValueError("--k required for e1")
            result = run_e1(args.k)
        elif args.exp == "e2":
            if args.L is None:
                raise ValueError("--L required for e2")
            result = run_e2(args.L)
        elif args.exp == "e4":
            if args.k is None:
                raise ValueError("--k required for e4")
            if args.mode is None:
                raise ValueError("--mode required for e4")
            result = run_e4(args.k, args.mode)
        else:
            raise ValueError(f"Unknown exp: {args.exp}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
