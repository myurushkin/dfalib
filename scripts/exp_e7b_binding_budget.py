"""
Experiment E7b: LB pseudo-polynomial scaling — binding-budget regime.

Complements E7 (early-termination regime) by constructing a DFA where the
minimum-cost accepting string has cost EQUAL to budget B for each data point.

Construction:
  - Base DFA: intersection of k=4 patterns (GQD+IMT+HRP, 981 states after minimize).
  - Exact-length constraint: intersect with (a|c|g|t)^B DFA so the only accepted
    strings have length exactly B.
  - Cost: unit cost=(1,1,1,1). Every symbol costs 1, so minimum accepting cost = B.
  - Budget = B: budget is exactly the minimum accepting cost — always binding.

As B increases, the product DFA state space grows as O(|Q_base| * B) and the
augmented BFS state space grows as O(|Q_product| * B) = O(|Q_base| * B^2).
The BFS cannot terminate early since the shortest accepted string has length exactly B.
This gives a clean pseudo-polynomial regime for manuscript §5.

Output CSV columns: budget, n_states, time_lb_ms
Output plot: manuscript/figures/exp_e7b_binding_budget.pdf
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
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e7b.csv"

UNIT_COST = (1, 1, 1, 1)

PATTERN_CONFIGS_K4 = [
    ("GQD", 2), ("IMT", (2, 1)), ("HRP", {'a': 2, 't': 1, 'g': 1, 'c': 1}),
    ("GQD", 3),
]

# Budget values: start from B=25 (first B where k=4 GQD accepts length-B strings)
DEFAULT_BUDGETS = [25, 30, 35, 40, 50, 60, 70, 80, 100, 120, 150]
REPEATS = 5


def build_binding_dfa(budget):
    """Build product DFA: k=4 GQD/IMT/HRP patterns intersected with exact-length-B DFA."""
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    patterns = []
    for kind, arg in PATTERN_CONFIGS_K4:
        if kind == "GQD":
            patterns.append(createGQD(arg, ctx))
        elif kind == "IMT":
            a, b = arg
            patterns.append(createIMT(a, b, ctx))
        elif kind == "HRP":
            patterns.append(createHRP(arg, ctx))

    # Exact-length-B constraint: forces minimum accepting string length == B
    exact_len = ctx.create_pattern("(a|c|g|t)" * budget)
    patterns.append(exact_len)

    big = pintersect(patterns, lazy=False)
    big.minimize()
    return big


def measure_lb(big, budget):
    gc.collect()
    t0 = time.perf_counter()
    find_min_string_under_budget(big, UNIT_COST, budget, budget + 1)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000


def compute_r2(xs, ys):
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    if ss_tot == 0:
        return 1.0
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / \
            sum((x - mean_x) ** 2 for x in xs)
    intercept = mean_y - slope * mean_x
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    return 1.0 - ss_res / ss_tot


def main():
    parser = argparse.ArgumentParser(
        description="E7b: LB pseudo-polynomial scaling in binding-budget regime")
    parser.add_argument("--budgets", type=str,
                        default=",".join(str(b) for b in DEFAULT_BUDGETS),
                        help="Comma-separated budget values")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: budgets 25,30,40,50,70,100")
    args = parser.parse_args()

    budgets = [int(x) for x in args.budgets.split(",")]
    if args.quick:
        budgets = [b for b in budgets if b <= 100]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    valid_bs = []
    valid_ts = []

    for budget in budgets:
        print(f"  B={budget} ...", end=" ", flush=True)
        try:
            big = build_binding_dfa(budget)
            n_states = big.state_count()

            if n_states <= 1:
                # DFA is empty (no accepting strings of length B for this k=4 DFA)
                print(f"EMPTY DFA (no strings of length {budget} accepted) — skip")
                rows.append({"budget": budget, "n_states": n_states, "time_lb_ms": -1})
                continue

            times = [measure_lb(big, budget) for _ in range(REPEATS)]
            t_ms = min(times)
            print(f"states={n_states}  time={t_ms:.3f}ms")

            valid_bs.append(budget)
            valid_ts.append(t_ms)

        except Exception as exc:
            print(f"ERROR: {exc}")
            n_states, t_ms = -1, -1

        rows.append({"budget": budget, "n_states": n_states, "time_lb_ms": round(t_ms, 4)})

    # Linearity check
    if len(valid_bs) >= 3:
        r2 = compute_r2(valid_bs, valid_ts)
        print(f"\nLinearity check (linear fit on valid points): R2={r2:.4f}")
        if r2 >= 0.7:
            print(f"  PASS: R2={r2:.4f} >= 0.7 — pseudo-polynomial scaling confirmed.")
        else:
            print(f"  WARN: R2={r2:.4f} < 0.7 — linear fit weak; inspect data.")
    else:
        r2 = None
        print("\nInsufficient data points for linearity check.")

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["budget", "n_states", "time_lb_ms"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output}")
    return r2


if __name__ == "__main__":
    main()
