"""
Experiment E4: Lazy vs eager intersection, scaling by k.

Uses the same pattern set as E1 (alternating GQD/IMT).
For each k, measures both eager (lazy=False) and lazy (lazy=True) pintersect.

Output CSV columns: k, mode (eager/lazy), time_s, peak_rss_kb_delta, states_final
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

from dafna.shared import Context

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e4.csv"


def build_pair(ctx, k):
    """Build a contrast pair: exact-length-k string vs substring-of-g^k.

    p_len(a|c|g|t)^k accepts every string of length exactly k (4^k minimal strings)
    and has k+1 states. p_g X*g^kX* accepts strings containing k consecutive 'g'
    and has k+1 states. Their intersection has exactly one minimal string g^k.

    Eager intersection materializes the full Cartesian product (≈(k+1)^2 states).
    Lazy intersection only follows reachable transitions and stays O(k+1).
    """
    p_len = ctx.create_pattern("(a|c|g|t)" * k)
    p_g = ctx.create_pattern("X*" + "g" * k + "X*")
    return [p_len, p_g]


def measure_k_mode(k, lazy):
    """One raw intersection (NO minimize) at given k. Returns (time_s, rss_delta_kb, states_raw).

    We deliberately skip minimize so that state_count reflects the *intermediate*
    automaton — eager builds the full Cartesian product, lazy only the reachable
    subset. After minimize both collapse to the same minimal DFA, hiding the
    contrast.
    """
    gc.collect()
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    p1, p2 = build_pair(ctx, k)

    rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    t0 = time.perf_counter()

    if lazy:
        result = p1.intersect_lazy(p2)
    else:
        result = p1.intersect(p2)

    t1 = time.perf_counter()
    rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    states_raw = result.state_count()
    elapsed = t1 - t0
    rss_delta = rss_after - rss_before

    del result, ctx
    gc.collect()

    return elapsed, rss_delta, states_raw


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
        for lazy, mode_name in [(False, "eager"), (True, "lazy")]:
            print(f"  k={k}  mode={mode_name} ...", end=" ", flush=True)
            time_s, rss_delta, states = measure_k_mode(k, lazy)
            print(f"time={time_s:.4f}s  rss_delta={rss_delta}KB  states={states}")
            rows.append({
                "k": k,
                "mode": mode_name,
                "time_s": round(time_s, 6),
                "peak_rss_kb_delta": rss_delta,
                "states_raw": states,
            })

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["k", "mode", "time_s", "peak_rss_kb_delta", "states_raw"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
