"""Experiment E5: compare greedy SCS baseline vs dafna automata approach.

Note on methodology: greedy_scs is order-invariant (it tries all pair orders).
The dafna approach implemented here fixes a single ordering of the input strings
(lexicographic sort) to build the pattern X* s1 X* s2 X* ... sk X*.
This is acceptable for the paper comparison: the claim is only that the dafna
approach generalises to a strictly broader class of pattern languages than SCS.
"""

import argparse
import csv
import os
import random
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# Allow running from anywhere: add dfalib/src and dfalib/scripts to path
_SCRIPT_DIR = Path(__file__).resolve().parent
_DFALIB_SRC = _SCRIPT_DIR.parent / "src"
if str(_DFALIB_SRC) not in sys.path:
    sys.path.insert(0, str(_DFALIB_SRC))
# _SCRIPT_DIR is the scripts/ directory; add it so `baselines` subpackage is importable
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from baselines.greedy_scs import greedy_scs  # noqa: E402


ALPHABET = "acgt"
DEFAULT_OUTPUT = str(_SCRIPT_DIR.parent / "experiments" / "e5.csv")


def random_strings(seed: int) -> List[str]:
    rng = random.Random(seed)
    num = rng.randint(4, 8)
    return ["".join(rng.choice(ALPHABET) for _ in range(rng.randint(6, 12))) for _ in range(num)]


def run_greedy(strings: List[str]) -> Tuple[str, float]:
    t0 = time.perf_counter()
    result = greedy_scs(strings)
    elapsed = time.perf_counter() - t0
    return result, elapsed


def run_dafna(strings: List[str]) -> Tuple[Optional[str], float]:
    """Build dafna automata for X* s1 X* s2 X* ... sk X* (sorted strings) and find one minimal string."""
    try:
        from dafna.shared import Context, pintersect  # noqa: F401 — used below
    except ImportError as e:
        print(f"[E5] dafna import failed: {e}", file=sys.stderr)
        return None, -1.0

    t0 = time.perf_counter()
    try:
        ctx = Context()
        X = ctx.create_pattern(f"[{''.join(ALPHABET)}]", simple=True, name="X")

        # Build X* s1 X* s2 X* ... sk X*
        sorted_strings = sorted(strings)
        pattern_str = "X*" + "X*".join(sorted_strings) + "X*"
        p = ctx.create_pattern(pattern_str)

        found: Optional[str] = None
        for s in p.min_strings(n_limit=1):
            found = s
            break

        elapsed = time.perf_counter() - t0
        return found, elapsed
    except Exception as e:
        elapsed = time.perf_counter() - t0
        print(f"[E5] dafna construction error: {e}", file=sys.stderr)
        return None, elapsed


def run_cases(seeds: List[int], output_path: str) -> List[dict]:
    rows = []
    for case_id, seed in enumerate(seeds, start=1):
        strings = random_strings(seed)
        num_strings = len(strings)
        print(f"Case {case_id} (seed={seed}, n={num_strings}): {strings}")

        greedy_result, t_greedy = run_greedy(strings)
        scs_len_greedy = len(greedy_result)
        print(f"  greedy: len={scs_len_greedy}, time={t_greedy:.4f}s, result={greedy_result!r}")

        dafna_result, t_dafna = run_dafna(strings)
        if dafna_result is not None:
            scs_len_dafna = len(dafna_result)
        else:
            scs_len_dafna = -1
        t_dafna_out = t_dafna if t_dafna >= 0 else -1
        print(f"  dafna:  len={scs_len_dafna}, time={t_dafna_out:.4f}s, result={dafna_result!r}")

        rows.append({
            "case_id": case_id,
            "num_strings": num_strings,
            "scs_len_greedy": scs_len_greedy,
            "scs_len_dafna": scs_len_dafna,
            "time_greedy_s": round(t_greedy, 6),
            "time_dafna_s": round(t_dafna_out, 6),
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = ["case_id", "num_strings", "scs_len_greedy", "scs_len_dafna", "time_greedy_s", "time_dafna_s"]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to {output_path}")
    print("\nSummary:")
    print(f"{'case_id':>7} {'n':>3} {'greedy_len':>10} {'dafna_len':>9} {'t_greedy':>10} {'t_dafna':>10}")
    for r in rows:
        print(f"{r['case_id']:>7} {r['num_strings']:>3} {r['scs_len_greedy']:>10} {r['scs_len_dafna']:>9} "
              f"{r['time_greedy_s']:>10.4f} {r['time_dafna_s']:>10.4f}")

    return rows


def main():
    parser = argparse.ArgumentParser(description="E5: greedy SCS vs dafna comparison")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--cases", default="1,2,3,4,5", help="Comma-separated list of seeds")
    args = parser.parse_args()

    seeds = [int(s.strip()) for s in args.cases.split(",")]
    run_cases(seeds, args.output)


if __name__ == "__main__":
    main()
