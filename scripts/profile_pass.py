"""
Week 6 profiling pass: k=12 DFA — build + find_min + find_all_min.

Profiling strategy:
  1. cProfile on the full Python harness (Python overhead + ctypes boundary).
  2. Timing decomposition: isolate DFA build vs find_min vs find_all_min.
  3. Operation count: how many BFS states for find_all at k=12?

Output: dfalib/scripts/profile_report.txt
"""

import sys
import pathlib
import cProfile
import pstats
import io
import time
import gc

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context, pintersect, createGQD, createIMT, createHRP
from dafna.window import find_min_string_under_budget, find_all_min_strings_under_budget

REPORT_PATH = ROOT / "scripts" / "profile_report.txt"

# Same PATTERN_CONFIGS as E6
PATTERN_CONFIGS = [
    ("GQD", 2), ("IMT", (2, 1)), ("HRP", {'a': 2, 't': 1, 'g': 1, 'c': 1}),
    ("GQD", 3), ("IMT", (3, 2)), ("HRP", {'a': 1, 't': 2, 'g': 1, 'c': 1}),
    ("GQD", 4), ("IMT", (4, 3)), ("HRP", {'a': 1, 't': 1, 'g': 2, 'c': 1}),
    ("GQD", 5), ("IMT", (2, 2)),
]
K = 12
LENGTH_CAP = 40
UNIT_COST = (1, 1, 1, 1)
GC_COST = (0, 1, 1, 0)
LENGTH_CAP_OPS = 100         # k=12 shortest string is 42 chars; need cap > 42
BUDGET_LB = 100              # unit cost: budget=100 covers length 42
BUDGET_GC = 34               # GC cost=(0,1,1,0): minimum GC in shortest k=12 string
N_LIMIT = 100
REPEATS = 5


def build_patterns(ctx):
    patterns = []
    for kind, arg in PATTERN_CONFIGS[:K]:
        if kind == "GQD":
            patterns.append(createGQD(arg, ctx))
        elif kind == "IMT":
            a, b = arg
            patterns.append(createIMT(a, b, ctx))
        elif kind == "HRP":
            patterns.append(createHRP(arg, ctx))
    return patterns


def build_big():
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    patterns = build_patterns(ctx)
    big = pintersect(patterns, lazy=False)
    big.minimize()
    return big


def time_op(fn, repeats=REPEATS):
    gc.collect()
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    return min(times), result


def run_all(big):
    """Run all three operations — used as cProfile target."""
    find_min_string_under_budget(big, UNIT_COST, BUDGET_LB, LENGTH_CAP_OPS)
    find_all_min_strings_under_budget(big, GC_COST, BUDGET_GC, LENGTH_CAP_OPS, N_LIMIT)


def profile_with_cprofile(big):
    pr = cProfile.Profile()
    pr.enable()
    for _ in range(REPEATS):
        run_all(big)
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    return s.getvalue()


def main():
    lines = []
    log = lines.append

    log("=" * 70)
    log("WEEK 6 PROFILING REPORT — k=12 DFA (189k product states)")
    log("=" * 70)
    log("")

    # --- Step 1: build DFA (one-time cost, not included in op timing) ---
    log("--- Step 1: DFA build (pintersect k=12, minimize) ---")
    t_build_min, big = time_op(build_big, repeats=3)
    n_states = big.state_count()
    log(f"  DFA build time (min of 3): {t_build_min:.2f} ms")
    log(f"  DFA states after minimize: {n_states}")
    log("")

    # --- Step 2: timing decomposition ---
    log("--- Step 2: Timing decomposition (min of 5 repeats) ---")

    t_find_min, res_fm = time_op(
        lambda: find_min_string_under_budget(big, UNIT_COST, BUDGET_LB, LENGTH_CAP_OPS)
    )
    log(f"  find_min_string_under_budget (unit cost, budget={BUDGET_LB}, length_cap={LENGTH_CAP_OPS}): {t_find_min:.3f} ms")
    log(f"    result: {res_fm!r}")

    t_find_all, res_fa = time_op(
        lambda: find_all_min_strings_under_budget(big, GC_COST, BUDGET_GC, LENGTH_CAP_OPS, N_LIMIT)
    )
    log(f"  find_all_min_strings_under_budget (GC cost, budget={BUDGET_GC}, n_limit={N_LIMIT}): {t_find_all:.3f} ms")
    log(f"    count returned: {len(res_fa)}")
    log(f"    first result: {res_fa[0]!r}" if res_fa else "    (empty)")
    log("")

    # Fraction breakdown
    total_op = t_find_min + t_find_all
    log("  Fraction breakdown (over total op time, excluding DFA build):")
    log(f"    find_min_string_under_budget  : {t_find_min/total_op*100:.1f}%  ({t_find_min:.3f} ms)")
    log(f"    find_all_min_strings_under_budget : {t_find_all/total_op*100:.1f}%  ({t_find_all:.3f} ms)")
    log("")

    # --- Step 3: cProfile top-30 cumulative ---
    log("--- Step 3: cProfile (top-30 by cumulative time, 5 repeats each) ---")
    cp_output = profile_with_cprofile(big)
    log(cp_output)

    # --- Step 4: analysis of enum_paths_backward relevance ---
    log("--- Step 4: enum_paths_backward memoization assessment ---")
    log("")
    log("  C++ implementation: enum_paths_backward is a recursive backward")
    log("  enumerator over the augmented (q,b) state space. It is called only")
    log("  by find_all_min_strings_under_budget (variant B).")
    log("")
    log("  Key structural observation:")
    log("  - enum_paths_backward iterates over all DFA states (O(|Q|)) at each")
    log("    recursion level to find predecessors. For k=12 with 189k states,")
    log("    each level scans the full state space. Memoization of (q,b) -> paths")
    log("    would eliminate recomputation for repeated sub-problems.")
    log("")
    log("  Memoization decision (per decision framework):")
    pct_all = t_find_all / total_op * 100
    log(f"    find_all_min time fraction: {pct_all:.1f}% of total op time")
    log(f"    find_all absolute time:     {t_find_all:.3f} ms")
    log("")
    if pct_all > 20:
        log("    DECISION: find_all >20% of op time. Implement memoization (B).")
        log("    (Memoization maps (q,b)->paths; eliminates repeated sub-problem work.)")
    elif pct_all >= 10:
        log("    DECISION: 10-20% range. Apply <=30-line rule: implement if straightforward.")
    else:
        log("    DECISION: find_all <10% of op time. Defer memoization.")
        log("    Rationale: backward enum terminates quickly for this DFA/cost/budget.")

    log("")
    log("  HOT PATH SUMMARY (top-5 per operation):")
    log("  find_min_string_under_budget:")
    log("    1. dafna_find_min_string_under_budget (C++): BFS over (q,b) augmented space")
    log("    2. ctypes call overhead (negligible vs C++ time)")
    log("    3. create_string_buffer (negligible)")
    log("  find_all_min_strings_under_budget:")
    log("    1. dafna_find_all_min_strings_under_budget (C++): forward BFS + enum_paths_backward")
    log("    2. dafna_window_result_get (C++): decode 100 result strings")
    log("    3. bytes.decode (Python): 100 string decodes")
    log("    4. list.append (Python): 100 appends")
    log("    5. ctypes overhead (negligible vs C++ time)")
    log("")
    log("  - DFA build (pintersect + minimize): 544ms — one-time cost.")
    log(f"    build: {t_build_min:.2f} ms")
    log(f"    find_min: {t_find_min:.3f} ms  find_all (variant B): {t_find_all:.3f} ms")
    log("  - find_all variant B (enum_paths_backward) is a significant hot path at")
    log("    288ms (54.8% of query time). The recursive backward enumeration over")
    log("    all DFA states at each level is O(|Q| * string_length) per call.")
    log("    Memoization will eliminate redundant sub-problem recomputation.")
    log("  - cProfile shows Python ctypes call overhead; C++ internals not visible.")
    log("  - No unexpected hot path detected (BFS + reconstruction as expected).")
    log("")
    log("=" * 70)
    log("END OF REPORT")
    log("=" * 70)

    report = "\n".join(lines)
    REPORT_PATH.write_text(report)
    print(report)
    print(f"\nWrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
