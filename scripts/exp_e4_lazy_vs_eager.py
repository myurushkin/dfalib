"""
Experiment E4: Lazy vs eager intersection, scaling by k.

Uses a contrast pair: p1 = (a|c|g|t)^k (exact-length-k strings, k+1 states)
and p2 = X*g^k X* (contains k consecutive 'g', k+1 states). Their intersection
has exactly one minimal string g^k.

Performs raw intersection WITHOUT minimize so that state_count reflects the
intermediate automaton size: eager builds the full Cartesian product ~(k+1)^2
states; lazy only follows reachable transitions, staying O(k).

Output CSV columns: k, mode (eager/lazy), time_s, peak_rss_kb, states_raw
"""

import sys
import pathlib
import argparse
import csv

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from _bench_subprocess import run_bench

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e4.csv"


def main():
    parser = argparse.ArgumentParser(description="Experiment E4: lazy vs eager intersection")
    parser.add_argument("--ks", type=str, default="20,40,60,80,120",
                        help="Comma-separated k values (default 20,40,60,80,120)")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: only smallest two k values")
    args = parser.parse_args()

    k_values = [int(x) for x in args.ks.split(",")]
    if args.quick:
        k_values = k_values[:2]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for k in k_values:
        for mode_name in ["eager", "lazy"]:
            print(f"  k={k}  mode={mode_name} ...", end=" ", flush=True)
            try:
                data = run_bench("--exp", "e4", "--k", str(k), "--mode", mode_name)
                time_s = data["time_s"]
                rss = data["peak_rss_kb"]
                states = data["states_raw"]
                print(f"time={time_s:.4f}s  peak_rss={rss}KB  states={states}")
            except RuntimeError as exc:
                print(f"ERROR: {exc}")
                time_s, rss, states = -1, -1, -1
            rows.append({
                "k": k,
                "mode": mode_name,
                "time_s": round(time_s, 6),
                "peak_rss_kb": rss,
                "states_raw": states,
            })

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["k", "mode", "time_s", "peak_rss_kb", "states_raw"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
