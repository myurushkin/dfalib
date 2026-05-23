"""
Experiment E8: LW scaling by window width (cost_hi - cost_lo).

Fixed DFA: intersection of 4 patterns (same as E7).
Fixed cost_hi = 20 (upper GC count bound).
Vary cost_lo from cost_hi down to 0 (window width = cost_hi - cost_lo).

For each window width: time find_min_string_in_window runtime.

Output CSV columns: window_width, cost_lo, cost_hi, time_lw_ms
"""

import sys
import pathlib
import argparse
import csv
import time
import gc

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context, pintersect, createGQD, createIMT, createHRP
from dafna.window import find_min_string_in_window

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e8.csv"

# GC cost vector: a=0, g=1, c=1, t=0
GC_COST = (0, 1, 1, 0)

PATTERN_CONFIGS_K4 = [
    ("GQD", 2), ("IMT", (2, 1)), ("HRP", {'a': 2, 't': 1, 'g': 1, 'c': 1}),
    ("GQD", 3),
]

LENGTH_CAP = 60
COST_HI = 20
REPEATS = 3


def build_fixed_dfa(ctx):
    patterns = []
    for kind, arg in PATTERN_CONFIGS_K4:
        if kind == "GQD":
            patterns.append(createGQD(arg, ctx))
        elif kind == "IMT":
            a, b = arg
            patterns.append(createIMT(a, b, ctx))
        elif kind == "HRP":
            patterns.append(createHRP(arg, ctx))
    big = pintersect(patterns, lazy=False)
    big.minimize()
    return big


def measure_lw(big, cost_lo, cost_hi):
    gc.collect()
    t0 = time.perf_counter()
    find_min_string_in_window(big, GC_COST, cost_lo, cost_hi, LENGTH_CAP)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000


def main():
    parser = argparse.ArgumentParser(description="Experiment E8: LW scaling by window width")
    parser.add_argument("--cost-hi", type=int, default=COST_HI,
                        help=f"Fixed upper cost bound (default {COST_HI})")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: only 4 window widths")
    args = parser.parse_args()

    cost_hi = args.cost_hi

    # Window widths: 0, cost_hi//4, cost_hi//2, 3*cost_hi//4, cost_hi
    # Corresponding cost_lo values: cost_hi, 3*cost_hi//4, cost_hi//2, cost_hi//4, 0
    if args.quick:
        width_values = [0, cost_hi // 2, cost_hi]
    else:
        # 6 evenly-spaced widths
        step = max(1, cost_hi // 5)
        width_values = sorted(set([0, step, step * 2, step * 3, step * 4, cost_hi]))

    args.output.parent.mkdir(parents=True, exist_ok=True)

    print("Building fixed DFA (k=4)...", flush=True)
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    big = build_fixed_dfa(ctx)
    n_states = big.state_count()
    print(f"  DFA states: {n_states}  cost_hi={cost_hi}  length_cap={LENGTH_CAP}")

    rows = []
    for width in width_values:
        cost_lo = max(0, cost_hi - width)
        print(f"  width={width} (cost_lo={cost_lo}, cost_hi={cost_hi}) ...", end=" ", flush=True)
        try:
            times = [measure_lw(big, cost_lo, cost_hi) for _ in range(REPEATS)]
            t_ms = min(times)
            print(f"time={t_ms:.3f}ms")
        except Exception as exc:
            print(f"ERROR: {exc}")
            t_ms = -1
        rows.append({
            "window_width": width,
            "cost_lo": cost_lo,
            "cost_hi": cost_hi,
            "time_lw_ms": round(t_ms, 4),
        })

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["window_width", "cost_lo", "cost_hi", "time_lw_ms"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
