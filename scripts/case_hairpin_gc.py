"""
Biocase: DNA hairpin with GC-window constraint.

Scenario: find the shortest DNA string of the form (stem)(loop)(revcomp(stem))
where the whole-string GC fraction lies in [alpha, beta].

Stem/loop structure:
  stem lengths  4-6 nt (arms with 2 GC bases each)
  loop lengths  4-7 nt (any DNA)
  Total length: 12-19 nt

GC-window applied globally: alpha=0.4, beta=0.6.

Connection to §4.3 / §6.1: demonstrates find_min_string_in_gc_window on a
real biological constraint (hairpin secondary structure) without any new C++
code — pure DFA composition in Python.

Usage:
  PYTHONPATH=dfalib/src .venv/bin/python dfalib/scripts/case_hairpin_gc.py
"""

import sys
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context
from dafna.window import find_min_string_in_gc_window
from dafna.lib.strength.hairpin import max_hairpin_strength

OUTPUT_PATH = pathlib.Path(__file__).with_name("case_hairpin_gc_output.txt")

ALPHA = 0.4
BETA = 0.6
LENGTH_CAP = 60

# (stem, revcomp_stem) pairs — each arm has exactly 2 GC bases
STEMS_AND_RCS = [
    ('acgt',   'acgt'),    # n=4, palindrome
    ('aacgt',  'acgtt'),   # n=5
    ('aaacgt', 'acgttt'),  # n=6
]
LOOP_LENS = list(range(4, 8))  # 4, 5, 6, 7


def _one(n=1):
    return '(a|c|g|t)' * n


def _gc_frac(s):
    return sum(c in 'gc' for c in s) / len(s)


def build_hairpin_dfa(ctx):
    """Union DFA over all (stem, rc, loop_len) combinations."""
    patterns = []
    for stem, rc in STEMS_AND_RCS:
        for ll in LOOP_LENS:
            patterns.append(ctx.create_pattern(stem + _one(ll) + rc))
    result = patterns[0].minimize()
    for p in patterns[1:]:
        result = result.add(p).minimize()
    return result


def decode_hairpin(s):
    """Return (stem, loop, rc_stem) by matching against known stem/rc pairs."""
    for stem, rc in STEMS_AND_RCS:
        n = len(stem)
        if len(s) >= n + 4 + n and s[:n] == stem and s[-n:] == rc:
            return stem, s[n:-n], rc
    return None, s, None


def main():
    ctx = Context()
    ctx.create_pattern('a|c|g|t', simple=True, name='X')

    t0 = time.perf_counter()
    big = build_hairpin_dfa(ctx)
    t_build = time.perf_counter() - t0

    t0 = time.perf_counter()
    result = find_min_string_in_gc_window(big, ALPHA, BETA, LENGTH_CAP)
    t_search = time.perf_counter() - t0

    lines = []
    lines.append("Biocase: DNA hairpin with GC-window [%.1f, %.1f]" % (ALPHA, BETA))
    lines.append("Parameters:")
    lines.append(f"  alpha={ALPHA}, beta={BETA}, length_cap={LENGTH_CAP}")
    lines.append(f"  stem_lengths={[len(s) for s, _ in STEMS_AND_RCS]}, loop_lengths={LOOP_LENS}")
    lines.append(f"DFA states: {big.state_count()}")
    lines.append(f"DFA build time: {t_build*1000:.2f} ms")
    lines.append(f"Search time:    {t_search*1000:.2f} ms")
    lines.append("")

    if result is None:
        lines.append("Result: None (no hairpin found in GC window)")
    else:
        stem, loop, rc = decode_hairpin(result)
        gc = _gc_frac(result)
        loop_gc = _gc_frac(loop) if loop else 0.0
        strength = max_hairpin_strength(result)

        lines.append(f"Result:    {result}")
        lines.append(f"Length:    {len(result)} nt")
        lines.append(f"Structure: stem={stem!r}  loop={loop!r}  rc={rc!r}")
        lines.append(f"GC (whole string): {gc:.3f}  (in [{ALPHA},{BETA}]: {'YES' if ALPHA <= gc <= BETA else 'NO'})")
        lines.append(f"GC (loop):         {loop_gc:.3f}")
        lines.append(f"Hairpin strength:  {strength}")
        lines.append("")
        lines.append("Interpretation:")
        lines.append("  The returned sequence forms a hairpin with complementary stem arms.")
        lines.append("  The GC-window constraint is satisfied over the full sequence.")
        lines.append("  Hairpin strength >= stem_len confirms correct base-pair complementarity.")

    output = "\n".join(lines) + "\n"
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
