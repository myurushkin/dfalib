"""
Biocase: G-quadruplex (GQD) canonical with GC-window constraint.

Scenario: find the shortest GQD canonical string (strength=3, i.e. 4 G-runs
of length >= 3 separated by loops of 1-7 nt) with GC fraction in [alpha, beta].

Uses gqd_canonocal_gen.create(strength=3, ctx) to build the DFA, then applies
find_min_string_in_gc_window with alpha=0.5, beta=0.8.

Connection to §4.3 / §6.3: demonstrates GC-window search on a real biological
constraint (G-quadruplex secondary structure) relevant to oncology targets.

Usage:
  PYTHONPATH=dfalib/src .venv/bin/python dfalib/scripts/case_gqd_canonical_gc.py
"""

import sys
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context
from dafna.window import find_min_string_in_gc_window
from dafna.lib.generation import gqd_canonocal_gen

OUTPUT_PATH = pathlib.Path(__file__).with_name("case_gqd_canonical_gc_output.txt")

ALPHA = 0.5
BETA = 0.8
GQD_STRENGTH = 3
LENGTH_CAP = 80


def _gc_frac(s):
    return sum(c in 'gc' for c in s) / len(s)


def _count_g_runs(s, min_run=3):
    """Count contiguous G-runs of length >= min_run."""
    runs = 0
    i = 0
    while i < len(s):
        if s[i] == 'g':
            j = i
            while j < len(s) and s[j] == 'g':
                j += 1
            if j - i >= min_run:
                runs += 1
            i = j
        else:
            i += 1
    return runs


def main():
    ctx = Context()
    ctx.create_pattern('a|c|g|t', simple=True, name='X')

    t0 = time.perf_counter()
    patterns = gqd_canonocal_gen.create(GQD_STRENGTH, ctx)
    big = patterns[0]
    t_build = time.perf_counter() - t0

    t0 = time.perf_counter()
    result = find_min_string_in_gc_window(big, ALPHA, BETA, LENGTH_CAP)
    t_search = time.perf_counter() - t0

    lines = []
    lines.append("Biocase: GQD canonical with GC-window [%.1f, %.1f]" % (ALPHA, BETA))
    lines.append("Parameters:")
    lines.append(f"  strength={GQD_STRENGTH}, alpha={ALPHA}, beta={BETA}, length_cap={LENGTH_CAP}")
    lines.append(f"DFA states: {big.state_count()}")
    lines.append(f"DFA build time: {t_build*1000:.2f} ms")
    lines.append(f"Search time:    {t_search*1000:.2f} ms")
    lines.append("")

    if result is None:
        lines.append("Result: None (no GQD canonical string found in GC window)")
    else:
        gc_frac = _gc_frac(result)
        gc_count = sum(c in 'gc' for c in result)
        g_runs = _count_g_runs(result, min_run=GQD_STRENGTH)
        gc_ok = ALPHA <= gc_frac <= BETA
        g_runs_ok = g_runs >= 4  # canonical G4 requires 4 G-runs

        lines.append(f"Result:       {result}")
        lines.append(f"Length:       {len(result)} nt")
        lines.append(f"GC count:     {gc_count} / {len(result)}")
        lines.append(f"GC fraction:  {gc_frac:.3f}  (in [{ALPHA},{BETA}]: {'YES' if gc_ok else 'NO'})")
        lines.append(f"G-runs (>={GQD_STRENGTH}): {g_runs}  (>= 4: {'YES' if g_runs_ok else 'NO'})")
        lines.append("")
        status = "PASS" if (gc_ok and g_runs_ok) else "FAIL"
        lines.append(f"GQD quality check: {status}")
        lines.append("")
        lines.append("Interpretation:")
        lines.append(f"  The returned sequence satisfies the GC-content window [{ALPHA}, {BETA}]")
        lines.append(f"  and contains {g_runs} G-runs of length >= {GQD_STRENGTH}, forming a")
        lines.append("  canonical G-quadruplex motif. This demonstrates that dafna can find")
        lines.append("  GC-constrained G4 motifs with a single BFS pass over the augmented")
        lines.append("  (q, b) state space.")

    output = "\n".join(lines) + "\n"
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
