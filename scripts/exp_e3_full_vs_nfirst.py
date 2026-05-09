"""
Experiment E3: Full enumeration vs N-first min_strings.

Builds an automaton whose minimal-strings set is large (>= 100).
For each n_limit in [None, 10, 100, 1000], measures time to consume
the min_strings generator and records number of strings returned.

Output CSV columns: n_limit (-1 means None/full), time_s, num_strings_returned
"""

import sys
import pathlib
import argparse
import csv
import time
import gc

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e3.csv"

STRING_LENGTH = 6  # 4^6 = 4096 minimal strings of length 6


def build_automaton():
    """Build automaton accepting all strings of fixed length over the DNA alphabet.

    Pattern (a|c|g|t)^L gives 4^L minimal strings of length L. With L=6 this
    yields 4096 minimal strings — enough to distinguish full enumeration
    from N-first with N in {10, 100, 1000}.
    """
    ctx = Context()
    pattern_str = "(a|c|g|t)" * STRING_LENGTH
    return ctx.create_pattern(pattern_str)


def measure_limit(automaton, n_limit):
    """Measure time to consume min_strings(n_limit). Returns (time_s, count)."""
    gc.collect()
    t0 = time.perf_counter()
    strings = list(automaton.min_strings(n_limit=n_limit))
    t1 = time.perf_counter()
    return t1 - t0, len(strings)


def main():
    parser = argparse.ArgumentParser(description="Experiment E3: full vs N-first min_strings")
    parser.add_argument("--limits", type=str, default="None,10,100,1000",
                        help="Comma-separated n_limit values; use 'None' for full (default: None,10,100,1000)")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: drop the None (full) case")
    args = parser.parse_args()

    # Parse limits
    raw_limits = [x.strip() for x in args.limits.split(",")]
    limits = []
    for x in raw_limits:
        if x.lower() == "none":
            limits.append(None)
        else:
            limits.append(int(x))

    if args.quick:
        limits = [lim for lim in limits if lim is not None]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    print("Building automaton...", flush=True)
    automaton = build_automaton()
    print(f"  state_count={automaton.state_count()}")

    rows = []
    for n_limit in limits:
        label = "full" if n_limit is None else str(n_limit)
        print(f"  n_limit={label} ...", end=" ", flush=True)
        time_s, count = measure_limit(automaton, n_limit)
        print(f"time={time_s:.4f}s  strings={count}")
        csv_limit = -1 if n_limit is None else n_limit
        rows.append({"n_limit": csv_limit, "time_s": round(time_s, 6),
                     "num_strings_returned": count})

    del automaton
    gc.collect()

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["n_limit", "time_s", "num_strings_returned"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
