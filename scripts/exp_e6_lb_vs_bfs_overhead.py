"""
Experiment E6: LB augmented BFS vs round-2 BFS overhead at unit cost (cost=1).

Compares:
  (a) round-2 BFS: find_all_min_strings on non-augmented product DFA
  (b) LB augmented BFS: find_min_string_under_budget on (q,b)-augmented space

At unit cost (cost=(1,1,1,1)) with budget=length_cap, both methods return the
same shortest string. The overhead measures the cost of augmenting the state
space with a budget dimension — not algorithmic complexity difference.

Legend terminology per Week 5 plan §5:
  "LB augmented BFS (cost=1)" vs "round-2 BFS (no cost dim)"

Output CSV columns: n_patterns, time_round2_ms, time_lb_unit_ms, ratio, n_states
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
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e6.csv"

# Unit cost: all symbols cost 1 (a=1, g=1, c=1, t=1)
UNIT_COST = (1, 1, 1, 1)
LENGTH_CAP = 40

# Same pattern configs as _bench_runner.py E1 sweep
PATTERN_CONFIGS = [
    ("GQD", 2), ("IMT", (2, 1)), ("HRP", {'a': 2, 't': 1, 'g': 1, 'c': 1}),
    ("GQD", 3), ("IMT", (3, 2)), ("HRP", {'a': 1, 't': 2, 'g': 1, 'c': 1}),
    ("GQD", 4), ("IMT", (4, 3)), ("HRP", {'a': 1, 't': 1, 'g': 2, 'c': 1}),
    ("GQD", 5), ("IMT", (2, 2)), ("HRP", {'a': 1, 't': 1, 'g': 1, 'c': 2}),
    ("GQD", 6), ("IMT", (3, 3)), ("IMT", (4, 4)), ("IMT", (5, 5)),
]

REPEATS = 3


def build_patterns(k, ctx):
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


def measure_round2(big):
    """Time round-2 BFS: find_all_min_strings returning at least 1 string."""
    # big.min_strings() is the round-2 iterator API defined in shared.py:Automata.min_strings,
    # backed by dafna_min_strings_iterator_create_n_first in internal.py (C++ round-2 BFS).
    # It is not part of the public dfa_window API surface but is the correct baseline here.
    gc.collect()
    t0 = time.perf_counter()
    strings = list(big.min_strings(n_limit=1))
    t1 = time.perf_counter()
    result = strings[0] if strings else None
    return (t1 - t0) * 1000, result


def measure_lb_unit(big, budget):
    """Time LB augmented BFS with unit cost and budget=budget."""
    gc.collect()
    t0 = time.perf_counter()
    result = find_min_string_under_budget(big, UNIT_COST, budget, LENGTH_CAP)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000, result


def main():
    parser = argparse.ArgumentParser(description="Experiment E6: LB augmented BFS vs round-2 BFS overhead")
    parser.add_argument("--max-k", type=int, default=8,
                        help="Maximum number of patterns (default 8)")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: max-k=3")
    args = parser.parse_args()

    if args.quick:
        args.max_k = 3

    # k values: use a subset that covers range but stays fast
    all_k = [1, 2, 4, 6, 8, 10, 12]
    k_values = [k for k in all_k if k <= args.max_k and k <= len(PATTERN_CONFIGS)]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for k in k_values:
        print(f"  k={k} ...", end=" ", flush=True)
        try:
            ctx = Context()
            ctx.create_pattern("a|c|g|t", simple=True, name="X")
            patterns = build_patterns(k, ctx)

            big = pintersect(patterns, lazy=False)
            big.minimize()
            n_states = big.state_count()

            # Budget = LENGTH_CAP (with unit cost, all strings up to length LENGTH_CAP are reachable)
            budget = LENGTH_CAP

            # Warm up then measure REPEATS times
            t_round2_list = []
            t_lb_list = []
            for _ in range(REPEATS):
                t_r, res_r = measure_round2(big)
                t_lb, res_lb = measure_lb_unit(big, budget)
                t_round2_list.append(t_r)
                t_lb_list.append(t_lb)

            t_round2 = min(t_round2_list)
            t_lb = min(t_lb_list)
            ratio = t_lb / t_round2 if t_round2 > 0 else float('inf')

            print(f"states={n_states}  t_round2={t_round2:.3f}ms  t_lb={t_lb:.3f}ms  ratio={ratio:.2f}x")

            # Escalation check: structural ratio ~16x is expected (O(budget) augmentation
            # overhead, budget=LENGTH_CAP=40). Threshold set to 25x per Week 5 verification.
            if ratio > 25.0:
                print(f"  WARNING: ratio={ratio:.2f} > 25x at k={k}. Escalation trigger!")

        except Exception as exc:
            print(f"ERROR: {exc}")
            n_states, t_round2, t_lb, ratio = -1, -1, -1, -1

        rows.append({
            "n_patterns": k,
            "time_round2_ms": round(t_round2, 4),
            "time_lb_unit_ms": round(t_lb, 4),
            "ratio": round(ratio, 4),
            "n_states": n_states,
        })

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["n_patterns", "time_round2_ms", "time_lb_unit_ms", "ratio", "n_states"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")

    # Final escalation summary (structural ratio ~16x expected; >25x is anomalous)
    max_ratio = max((r["ratio"] for r in rows if r["ratio"] >= 0), default=0)
    if max_ratio > 25.0:
        print(f"ESCALATION: max ratio {max_ratio:.2f}x exceeds 25x threshold.")
    else:
        print(f"Max ratio: {max_ratio:.2f}x (expected structural range ~16x).")


if __name__ == "__main__":
    main()
