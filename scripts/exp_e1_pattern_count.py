"""
Experiment E1: Scaling by number of patterns (k).

Measures time and memory for pintersect of k patterns (eager, minimized).
Does NOT call min_strings — construction cost only.

Output CSV columns: k, time_s, peak_rss_kb, states_final
"""

import sys
import pathlib
import argparse
import csv

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from _bench_subprocess import run_bench

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e1.csv"


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
        try:
            data = run_bench("--exp", "e1", "--k", str(k))
            time_s = data["time_s"]
            rss = data["peak_rss_kb"]
            states = data["states_final"]
            print(f"time={time_s:.3f}s  peak_rss={rss}KB  states={states}")
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            time_s, rss, states = -1, -1, -1
        rows.append({"k": k, "time_s": round(time_s, 6),
                     "peak_rss_kb": rss, "states_final": states})

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["k", "time_s", "peak_rss_kb", "states_final"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
