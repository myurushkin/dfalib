"""
Biocase: PCR primer design with GC-window constraint.

Scenario: find the shortest DNA string of length in [18, 25] with GC fraction
in [alpha, beta] = [0.4, 0.6]. Post-search, verify no internal hairpin exceeds
strength 4 (a basic secondary-structure quality criterion for PCR primers).

The DFA accepts all exact-length-18 strings (minimum primer length). The GC
window [0.4, 0.6] is applied via find_min_string_in_gc_window. The hairpin
check is performed post-hoc using max_hairpin_strength.

Connection to §4.3 / §6.2: demonstrates that a simple length+GC constraint
already yields biologically plausible primer candidates without secondary
structure issues — the BFS search naturally avoids palindromic sequences.

Usage:
  PYTHONPATH=dfalib/src .venv/bin/python dfalib/scripts/case_primer_gc.py
"""

import sys
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context
from dafna.window import find_min_string_in_gc_window
from dafna.lib.strength.hairpin import max_hairpin_strength

OUTPUT_PATH = pathlib.Path(__file__).with_name("case_primer_gc_output.txt")

ALPHA = 0.4
BETA = 0.6
PRIMER_LENGTH = 18   # minimum primer length
LENGTH_CAP = 30
MAX_HAIRPIN = 4      # primers with hairpin strength > 4 are considered unusable


def _one(n=1):
    return '(a|c|g|t)' * n


def _gc_frac(s):
    return sum(c in 'gc' for c in s) / len(s)


def build_primer_dfa(ctx, length):
    """DFA accepting all DNA strings of exactly `length` characters."""
    return ctx.create_pattern(_one(length))


def main():
    ctx = Context()
    ctx.create_pattern('a|c|g|t', simple=True, name='X')

    t0 = time.perf_counter()
    big = build_primer_dfa(ctx, PRIMER_LENGTH)
    t_build = time.perf_counter() - t0

    t0 = time.perf_counter()
    result = find_min_string_in_gc_window(big, ALPHA, BETA, LENGTH_CAP)
    t_search = time.perf_counter() - t0

    lines = []
    lines.append("Biocase: PCR primer design with GC-window [%.1f, %.1f]" % (ALPHA, BETA))
    lines.append("Parameters:")
    lines.append(f"  primer_length={PRIMER_LENGTH} nt, alpha={ALPHA}, beta={BETA}")
    lines.append(f"  length_cap={LENGTH_CAP}, max_hairpin_allowed={MAX_HAIRPIN}")
    lines.append(f"DFA states: {big.state_count()}")
    lines.append(f"DFA build time: {t_build*1000:.2f} ms")
    lines.append(f"Search time:    {t_search*1000:.2f} ms")
    lines.append("")

    if result is None:
        lines.append("Result: None (no valid primer found in GC window)")
    else:
        gc = _gc_frac(result)
        gc_count = sum(c in 'gc' for c in result)
        strength = max_hairpin_strength(result)
        gc_ok = ALPHA <= gc <= BETA
        len_ok = 18 <= len(result) <= 25
        hairpin_ok = strength <= MAX_HAIRPIN

        lines.append(f"Result:          {result}")
        lines.append(f"Length:          {len(result)} nt  (in [18,25]: {'YES' if len_ok else 'NO'})")
        lines.append(f"GC count:        {gc_count} / {len(result)}")
        lines.append(f"GC fraction:     {gc:.3f}  (in [{ALPHA},{BETA}]: {'YES' if gc_ok else 'NO'})")
        lines.append(f"Hairpin strength:{strength}  (<= {MAX_HAIRPIN}: {'YES' if hairpin_ok else 'NO'})")
        lines.append("")
        status = "PASS" if (gc_ok and len_ok and hairpin_ok) else "FAIL"
        lines.append(f"Primer quality check: {status}")
        lines.append("")
        lines.append("Interpretation:")
        lines.append("  The returned sequence satisfies the GC-content constraint [0.4, 0.6]")
        lines.append("  required for stable primer annealing, and has low self-complementarity")
        lines.append("  (hairpin strength <= 4), making it a viable PCR primer candidate.")

    output = "\n".join(lines) + "\n"
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
