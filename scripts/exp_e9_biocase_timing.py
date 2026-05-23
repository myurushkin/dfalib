"""
Experiment E9: Detailed runtime breakdown for 3 biocases.

For each biocase (hairpin, primer, GQD canonical):
  - Build DFA (timed separately)
  - Run find_min_string_in_gc_window (timed separately)
  - Run 3 times, report min and std-dev

Output CSV columns:
  biocase, time_dfa_build_ms, time_dfa_build_std_ms,
  time_find_ms, time_find_std_ms, n_states, returned_string_length
"""

import sys
import pathlib
import argparse
import csv
import time
import math
import gc

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context
from dafna.window import find_min_string_in_gc_window

EXPERIMENTS_DIR = ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_DIR / "e9.csv"

REPEATS = 3

# Hairpin parameters (same as case_hairpin_gc.py)
HAIRPIN_ALPHA = 0.4
HAIRPIN_BETA = 0.6
HAIRPIN_LENGTH_CAP = 60
STEMS_AND_RCS = [
    ('acgt',   'acgt'),
    ('aacgt',  'acgtt'),
    ('aaacgt', 'acgttt'),
]
LOOP_LENS = list(range(4, 8))

# Primer parameters (same as case_primer_gc.py)
PRIMER_ALPHA = 0.4
PRIMER_BETA = 0.6
PRIMER_LENGTH = 18
PRIMER_LENGTH_CAP = 30

# GQD canonical parameters (same as test_window_gc.py TestGCWindowGQDCanonical)
GQD_ALPHA = 0.5
GQD_BETA = 0.8
GQD_STRENGTH = 3
GQD_LENGTH_CAP = 80


def _one(n=1):
    return '(a|c|g|t)' * n


def _stdev(values):
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1))


def build_hairpin_dfa(ctx):
    patterns = []
    for stem, rc in STEMS_AND_RCS:
        for ll in LOOP_LENS:
            patterns.append(ctx.create_pattern(stem + _one(ll) + rc))
    result = patterns[0].minimize()
    for p in patterns[1:]:
        result = result.add(p).minimize()
    return result


def build_primer_dfa(ctx):
    return ctx.create_pattern(_one(PRIMER_LENGTH))


def build_gqd_dfa(ctx):
    from dafna.lib.generation import gqd_canonocal_gen
    patterns = gqd_canonocal_gen.create(GQD_STRENGTH, ctx)
    return patterns[0]


def measure_biocase(name, build_fn, alpha, beta, length_cap, repeats):
    build_times = []
    find_times = []
    n_states = -1
    result_str = None

    for i in range(repeats):
        gc.collect()
        ctx = Context()
        ctx.create_pattern('a|c|g|t', simple=True, name='X')

        t0 = time.perf_counter()
        big = build_fn(ctx)
        t_build = (time.perf_counter() - t0) * 1000
        build_times.append(t_build)

        if i == 0:
            n_states = big.state_count()

        gc.collect()
        t0 = time.perf_counter()
        result_str = find_min_string_in_gc_window(big, alpha, beta, length_cap)
        t_find = (time.perf_counter() - t0) * 1000
        find_times.append(t_find)

    t_build_min = min(build_times)
    t_build_std = _stdev(build_times)
    t_find_min = min(find_times)
    t_find_std = _stdev(find_times)
    result_len = len(result_str) if result_str else -1

    print(f"  {name}: build={t_build_min:.2f}ms±{t_build_std:.2f}  "
          f"find={t_find_min:.2f}ms±{t_find_std:.2f}  "
          f"states={n_states}  result_len={result_len}  result={result_str!r}")

    return {
        "biocase": name,
        "time_dfa_build_ms": round(t_build_min, 4),
        "time_dfa_build_std_ms": round(t_build_std, 4),
        "time_find_ms": round(t_find_min, 4),
        "time_find_std_ms": round(t_find_std, 4),
        "n_states": n_states,
        "returned_string_length": result_len,
    }


def main():
    parser = argparse.ArgumentParser(description="Experiment E9: biocase timing breakdown")
    parser.add_argument("--repeats", type=int, default=REPEATS,
                        help=f"Number of repetitions per biocase (default {REPEATS})")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                        help="Output CSV path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: 1 repeat per biocase")
    args = parser.parse_args()

    repeats = 1 if args.quick else args.repeats
    args.output.parent.mkdir(parents=True, exist_ok=True)

    cases = [
        ("hairpin",  build_hairpin_dfa, HAIRPIN_ALPHA, HAIRPIN_BETA, HAIRPIN_LENGTH_CAP),
        ("primer",   build_primer_dfa,  PRIMER_ALPHA,  PRIMER_BETA,  PRIMER_LENGTH_CAP),
        ("gqd",      build_gqd_dfa,     GQD_ALPHA,     GQD_BETA,     GQD_LENGTH_CAP),
    ]

    rows = []
    for name, build_fn, alpha, beta, length_cap in cases:
        print(f"\nBiocase: {name} (alpha={alpha}, beta={beta}, length_cap={length_cap})")
        try:
            row = measure_biocase(name, build_fn, alpha, beta, length_cap, repeats)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            row = {
                "biocase": name,
                "time_dfa_build_ms": -1, "time_dfa_build_std_ms": -1,
                "time_find_ms": -1, "time_find_std_ms": -1,
                "n_states": -1, "returned_string_length": -1,
            }
        rows.append(row)

    fieldnames = [
        "biocase", "time_dfa_build_ms", "time_dfa_build_std_ms",
        "time_find_ms", "time_find_std_ms", "n_states", "returned_string_length",
    ]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
