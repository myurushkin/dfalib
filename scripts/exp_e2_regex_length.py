"""
Experiment E2: Scaling by regex length (L).

Builds a single pattern of form X* (a|c|g|t)^L X*, minimizes it, and records
time, peak RSS, and state count.

Output CSV columns: regex_length, time_s, peak_rss_kb, states_final
"""

import sys
import pathlib
import argparse
import csv

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from _bench_subprocess import run_bench

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e2.csv"


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
        try:
            data = run_bench("--exp", "e2", "--L", str(L))
            time_s = data["time_s"]
            rss = data["peak_rss_kb"]
            states = data["states_final"]
            print(f"time={time_s:.3f}s  peak_rss={rss}KB  states={states}")
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            time_s, rss, states = -1, -1, -1
        rows.append({"regex_length": L, "time_s": round(time_s, 6),
                     "peak_rss_kb": rss, "states_final": states})

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["regex_length", "time_s", "peak_rss_kb", "states_final"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
