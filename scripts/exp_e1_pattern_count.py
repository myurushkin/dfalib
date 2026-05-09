"""
Experiment E1: Scaling by number of patterns (k).

Measures time and memory for pintersect of k patterns (eager, minimized).
Does NOT call min_strings — construction cost only.

Output CSV columns: k, time_s, peak_rss_kb_delta, states_final
"""

import sys
import pathlib
import argparse
import csv
import time
import gc
import resource
import itertools

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context, pintersect, createGQD, createIMT, createHRP

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e1.csv"

# 16 unique pattern configurations across three families to avoid saturation.
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


def measure_k(k):
    """Run one measurement for k patterns. Returns (time_s, rss_delta_kb, states)."""
    gc.collect()
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    patterns = build_patterns(k, ctx)

    rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    t0 = time.perf_counter()

    result = pintersect(patterns, lazy=False)

    t1 = time.perf_counter()
    rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    states = result.state_count()
    elapsed = t1 - t0
    rss_delta = rss_after - rss_before

    del result, patterns, ctx
    gc.collect()

    return elapsed, rss_delta, states


def main():
    parser = argparse.ArgumentParser(description="Experiment E1: scaling by pattern count")
    parser.add_argument("--max-k", type=int, default=16,
                        help="Maximum k value (default 16)")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: forces --max-k=4")
    args = parser.parse_args()

    if args.quick:
        args.max_k = 4

    k_values = [k for k in [1, 2, 4, 8, 16] if k <= args.max_k]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for k in k_values:
        print(f"  k={k} ...", end=" ", flush=True)
        time_s, rss_delta, states = measure_k(k)
        print(f"time={time_s:.3f}s  rss_delta={rss_delta}KB  states={states}")
        rows.append({"k": k, "time_s": round(time_s, 6),
                     "peak_rss_kb_delta": rss_delta, "states_final": states})

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["k", "time_s", "peak_rss_kb_delta", "states_final"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
