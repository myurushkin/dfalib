"""
Experiment E7: LB scaling by budget B (pseudo-polynomial).

Fixed DFA: intersection of 4 patterns (same as E1/E6 k=4 point).
Vary B in {10, 50, 100, 500, 1000}.
For each B: time find_min_string_under_budget runtime.

Expected behavior: roughly linear in B (pseudo-polynomial complexity
O(|Q| * (B+1) * l_value * length_cap)).

If quadratic or worse growth is observed → escalation trigger (bug in BFS).

Output CSV columns: budget, time_lb_ms
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
from dafna.window import find_min_string_under_budget

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e7.csv"

# GC cost vector: a=0, g=1, c=1, t=0
GC_COST = (0, 1, 1, 0)

# Fixed DFA: k=4 patterns (same configuration as E6)
PATTERN_CONFIGS_K4 = [
    ("GQD", 2), ("IMT", (2, 1)), ("HRP", {'a': 2, 't': 1, 'g': 1, 'c': 1}),
    ("GQD", 3),
]

DEFAULT_BUDGETS = [10, 50, 100, 500, 1000]
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


def measure_lb(big, budget, length_cap):
    gc.collect()
    t0 = time.perf_counter()
    find_min_string_under_budget(big, GC_COST, budget, length_cap)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000


def main():
    parser = argparse.ArgumentParser(description="Experiment E7: LB scaling by budget B")
    parser.add_argument("--budgets", type=str, default="10,50,100,500,1000",
                        help="Comma-separated budget values (default: 10,50,100,500,1000)")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: only budgets 10,50,100")
    args = parser.parse_args()

    budgets = [int(x) for x in args.budgets.split(",")]
    if args.quick:
        budgets = [b for b in budgets if b <= 100]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    print("Building fixed DFA (k=4)...", flush=True)
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    big = build_fixed_dfa(ctx)
    n_states = big.state_count()
    print(f"  DFA states: {n_states}")

    rows = []
    prev_time = None
    for budget in budgets:
        # length_cap: enough to accommodate the budget (GC cost <= 1 per symbol)
        length_cap = max(budget * 2, 60)
        print(f"  B={budget} (length_cap={length_cap}) ...", end=" ", flush=True)
        try:
            times = [measure_lb(big, budget, length_cap) for _ in range(REPEATS)]
            t_ms = min(times)
            if prev_time is not None and prev_time > 0:
                ratio = t_ms / prev_time
                print(f"time={t_ms:.3f}ms  ratio_prev={ratio:.2f}x")
                # Escalation: quadratic or worse growth would show ratio >> budget_ratio
                budget_ratio = budget / budgets[budgets.index(budget) - 1]
                if ratio > budget_ratio ** 2:
                    print(f"  WARNING: super-quadratic growth detected at B={budget}. Escalation trigger!")
            else:
                print(f"time={t_ms:.3f}ms")
            prev_time = t_ms
        except Exception as exc:
            print(f"ERROR: {exc}")
            t_ms = -1
        rows.append({"budget": budget, "time_lb_ms": round(t_ms, 4)})

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["budget", "time_lb_ms"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
