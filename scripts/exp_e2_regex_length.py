"""
Experiment E2: Scaling by regex length (L).

Builds a single pattern of form X* (a|c|g|t)^L X*, minimizes it, and records
time, peak RSS delta, and state count.

Output CSV columns: regex_length, time_s, peak_rss_kb_delta, states_final
"""

import sys
import pathlib
import argparse
import csv
import time
import gc
import resource

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e2.csv"


def measure_length(L):
    """Build and minimize pattern of length L. Returns (time_s, rss_delta_kb, states)."""
    gc.collect()
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    # Build: X* followed by (a|c|g|t) repeated L times, then X*
    repeated = "(a|c|g|t)" * L
    regex = "X*" + repeated + "X*"

    rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    t0 = time.perf_counter()

    automaton = ctx.create_pattern(regex)
    automaton.minimize()

    t1 = time.perf_counter()
    rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    states = automaton.state_count()
    elapsed = t1 - t0
    rss_delta = rss_after - rss_before

    del automaton, ctx
    gc.collect()

    return elapsed, rss_delta, states


def main():
    parser = argparse.ArgumentParser(description="Experiment E2: scaling by regex length")
    parser.add_argument("--max-len", type=int, default=80,
                        help="Maximum regex length (default 80)")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: forces --max-len=20")
    args = parser.parse_args()

    if args.quick:
        args.max_len = 20

    all_lengths = [10, 20, 40, 80]
    lengths = [L for L in all_lengths if L <= args.max_len]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for L in lengths:
        print(f"  L={L} ...", end=" ", flush=True)
        time_s, rss_delta, states = measure_length(L)
        print(f"time={time_s:.3f}s  rss_delta={rss_delta}KB  states={states}")
        rows.append({"regex_length": L, "time_s": round(time_s, 6),
                     "peak_rss_kb_delta": rss_delta, "states_final": states})

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["regex_length", "time_s", "peak_rss_kb_delta", "states_final"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
