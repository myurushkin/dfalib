"""Scaling benchmark: unions of real DAFNA motif patterns vs three engines.

The workload reproduces ``scripts/measure_second.py`` / ``measure_complexity.py``:
a union of K parameterised motif patterns, intersected with a union of GQD
patterns and a fixed string length L.  K is scaled; the engines are

* ``cpp``   -- the original dfalib pipeline (psum/pintersect over the C++
               automata library, minimising after every operation);
* ``eager`` -- the minstr eager baseline (explicit product DFA, minimised);
* ``lazy``  -- the minstr lazy search (no product, folding, A*).

Every cell runs in a subprocess with a wall-clock timeout and an address-space
limit, so a blow-up is recorded instead of taking the machine down.

Driver:      venv/bin/python prototype/blowup_bench.py
Single cell: venv/bin/python prototype/blowup_bench.py --cell FAMILY SCALE ENGINE
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
sys.path.insert(0, os.path.join(ROOT, "src"))

TIMEOUT = 120          # seconds per cell
MEM_BYTES = 8 << 30    # address-space cap per cell
EAGER_LIMIT = 300_000  # abandon the explicit product above this many states

IMT_LENGTH = 20        # string length for the i-motif family (measure_second)
TRP_LENGTH = 24        # string length for the triplex family


# ---------------------------------------------------------------------------
# Workload definitions (paths kept identical between engines).
# ---------------------------------------------------------------------------

def imt_params(k):
    """First k parameter tuples of the measure_second grid (243 total)."""
    grid = [(n, m, a, b, c)
            for n in (2, 3, 4) for m in (2, 3, 4)
            for a in (1, 2, 3) for b in (1, 2, 3) for c in (1, 2, 3)]
    return grid[:k]


def trp_triples(n):
    """Pattern triples of createTRPs(n, tt=0) from measure_complexity."""
    comp = {"g": "c", "a": "t"}
    comp2 = {"g": ["g", "a"], "a": ["t", "a"]}
    mains = ["".join(p) for p in itertools.product("ga", repeat=n)]
    out = []
    for ms in mains:
        cs = "".join(comp[c] for c in ms)
        out.append((ms, cs[::-1], cs))
        out.append((cs, ms[::-1], cs))
        for c2 in itertools.product(*[comp2[c] for c in ms]):
            c2s = "".join(c2)
            out.append((cs, ms[::-1], c2s))
            out.append((ms, cs[::-1], c2s))
    return out


def gqd_scales():
    return (2, 3)


# dfalib pattern strings (X macros expanded by the Context).

def imt_pattern_dfalib(n, m, a, b, c):
    return "X*" + "c" * n + "X" * a + "c" * m + "X" * b + "c" * n + "X" * c + "c" * m + "X*"


def gqd_pattern_dfalib(k):
    g = "g" * k
    return f"X*{g}X+{g}X+{g}X+{g}X*"


def trp_pattern_dfalib(v1, v2, v3):
    return "X*" + "XXX+".join((v1, v2, v3)) + "X*"


# minstr regexes (same languages, '.'-based).

def imt_regex(n, m, a, b, c):
    cn, cm = "c" * n, "c" * m
    return f".*{cn}.{{{a}}}{cm}.{{{b}}}{cn}.{{{c}}}{cm}.*"


def gqd_regex(k):
    g = "g" * k
    return f".*{g}.+{g}.+{g}.+{g}.*"


def trp_regex(v1, v2, v3):
    return ".*" + "...+".join((v1, v2, v3)) + ".*"


def family_cell(family, scale):
    """-> (list of union regexes/dfalib patterns, gqd part, length)."""
    if family == "imt":
        params = imt_params(scale)
        return ([imt_regex(*p) for p in params],
                [imt_pattern_dfalib(*p) for p in params],
                IMT_LENGTH)
    if family == "trp":
        triples = trp_triples(scale)
        return ([trp_regex(*t) for t in triples],
                [trp_pattern_dfalib(*t) for t in triples],
                TRP_LENGTH)
    raise ValueError(family)


# ---------------------------------------------------------------------------
# Engines.
# ---------------------------------------------------------------------------

def run_cpp(family, scale):
    from dafna.shared import Context, psum, pintersect

    union_re, union_df, length = family_cell(family, scale)
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    t0 = time.perf_counter()
    motifs = [ctx.create_pattern(p) for p in union_df]
    gqds = [ctx.create_pattern(gqd_pattern_dfalib(k)) for k in gqd_scales()]
    size = ctx.create_pattern("X" * length)
    result = pintersect([psum(motifs), psum(gqds), size])
    build_t = time.perf_counter() - t0
    t0 = time.perf_counter()
    word = next(iter(result.min_strings()), None)
    return {"seconds": build_t + (time.perf_counter() - t0),
            "states": result.state_count(),
            "answer": None if word is None else len(word)}


def _minstr_problem(family, scale):
    from minstr import formula as F
    from minstr.trackers import RegexTracker

    union_re, _, length = family_cell(family, scale)
    trackers = [RegexTracker(p, "acgt", name=f"U{i}") for i, p in enumerate(union_re)]
    n_union = len(trackers)
    trackers += [RegexTracker(gqd_regex(k), "acgt", name=f"G{k}") for k in gqd_scales()]
    formula = F.AND(F.OR(*[F.leaf(i) for i in range(n_union)]),
                    F.OR(*[F.leaf(n_union + j) for j in range(len(gqd_scales()))]))
    return trackers, formula, length


def run_eager(family, scale):
    from minstr.baseline import find_minimal_eager, TooLarge

    trackers, formula, length = _minstr_problem(family, scale)
    t0 = time.perf_counter()
    try:
        word, stats = find_minimal_eager(trackers, formula, "acgt",
                                         min_len=length, max_len=length,
                                         limit=EAGER_LIMIT)
    except TooLarge:
        return {"seconds": time.perf_counter() - t0, "states": f">{EAGER_LIMIT}",
                "answer": "abandoned"}
    d = stats.as_dict()
    if d.get("failed"):
        return {"seconds": time.perf_counter() - t0,
                "states": d.get("peak_states"), "answer": "abandoned"}
    return {"seconds": time.perf_counter() - t0,
            "states": d.get("peak_states"),
            "answer": None if word is None else len(word)}


def run_lazy(family, scale):
    from minstr.search import Problem, find_minimal

    trackers, formula, length = _minstr_problem(family, scale)
    t0 = time.perf_counter()
    p = Problem(trackers, formula, "acgt", min_len=length, max_len=length)
    word, st = find_minimal(p)
    return {"seconds": time.perf_counter() - t0,
            "states": st.distinct,
            "answer": None if word is None else len(word)}


def run_lazy_dnf(family, scale):
    """Full sweep over conjuncts at the fixed length (conservative: no early
    exit, no ordering) — kept for comparison with the smarter modes below."""
    from minstr import formula as F
    from minstr.search import Problem, find_minimal
    from minstr.trackers import RegexTracker

    union_re, _, length = family_cell(family, scale)
    motifs = [RegexTracker(p, "acgt", name=f"U{i}") for i, p in enumerate(union_re)]
    gqds = [RegexTracker(gqd_regex(k), "acgt", name=f"G{k}") for k in gqd_scales()]
    pair_formula = F.AND(F.leaf(0), F.leaf(1))
    t0 = time.perf_counter()
    best, states = None, 0
    feasible = 0
    for m in motifs:
        for g in gqds:
            p = Problem([m, g], pair_formula, "acgt",
                        min_len=length, max_len=length)
            word, st = find_minimal(p)
            states += st.distinct
            if word is not None:
                feasible += 1
                if best is None or len(word) < len(best):
                    best = word
    return {"seconds": time.perf_counter() - t0, "states": states,
            "answer": None if best is None else len(best),
            "conjuncts": len(motifs) * len(gqds), "feasible": feasible}


def _run_decompose(family, scale, fixed_length):
    from minstr.decompose import solve_dnf

    trackers, formula, length = _minstr_problem(family, scale)
    t0 = time.perf_counter()
    word, st = solve_dnf(trackers, formula, "acgt",
                         min_len=length if fixed_length else 0,
                         max_len=length,
                         stop_at_first=fixed_length)
    d = st.as_dict()
    return {"seconds": time.perf_counter() - t0, "states": st.distinct,
            "answer": None if word is None else len(word),
            "conjuncts": d["conjuncts"], "solved": d["solved"],
            "pruned": d["pruned"]}


def run_dnf_first(family, scale):
    """Feasibility at the fixed length: bound-ordered, stop at first witness."""
    return _run_decompose(family, scale, fixed_length=True)


def run_dnf_min(family, scale):
    """True minimal word (no fixed length): bound-ordered with pruning."""
    return _run_decompose(family, scale, fixed_length=False)


ENGINES = {"cpp": run_cpp, "eager": run_eager, "lazy": run_lazy,
           "lazy_dnf": run_lazy_dnf,
           "dnf_first": run_dnf_first, "dnf_min": run_dnf_min}


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def cell_main(family, scale, engine):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (MEM_BYTES, MEM_BYTES))
    out = ENGINES[engine](family, int(scale))
    print("RESULT " + json.dumps(out))


def driver():
    cells = []
    for scale in (9, 27, 81, 243):
        cells.append(("imt", scale))
    for n in (2, 3, 4):
        cells.append(("trp", n))

    rows = []
    for family, scale in cells:
        n_pat = len(family_cell(family, scale)[0])
        row = {"family": family, "scale": scale, "patterns": n_pat}
        for engine in ("cpp", "eager", "lazy"):
            t0 = time.time()
            try:
                pr = subprocess.run(
                    [sys.executable, os.path.abspath(__file__),
                     "--cell", family, str(scale), engine],
                    capture_output=True, text=True, timeout=TIMEOUT)
                line = next((l for l in pr.stdout.splitlines()
                             if l.startswith("RESULT ")), None)
                if line:
                    row[engine] = json.loads(line[len("RESULT "):])
                else:
                    err = (pr.stderr or "").strip().splitlines()
                    row[engine] = {"error": err[-1][:120] if err else
                                   f"no result (rc={pr.returncode})"}
            except subprocess.TimeoutExpired:
                row[engine] = {"error": f"timeout >{TIMEOUT}s"}
            row[engine]["wall"] = time.time() - t0
            r = row[engine]
            print(f"{family}/{scale} [{n_pat} patterns] {engine:>5}: "
                  + (f"{r['seconds']:.2f}s states={r['states']} answer={r['answer']}"
                     if "seconds" in r else r["error"]),
                  flush=True)
        rows.append(row)

    print()
    print("| family | patterns | cpp (dfalib) | eager (minstr) | lazy (minstr) |")
    print("|---|---|---|---|---|")
    for row in rows:
        def fmt(r):
            if "error" in r:
                return r["error"]
            st = r["states"]
            st = f"{st:,}" if isinstance(st, int) else st
            return f"{r['seconds']:.2f}s, {st} st"
        print(f"| {row['family']} | {row['patterns']} | "
              f"{fmt(row['cpp'])} | {fmt(row['eager'])} | {fmt(row['lazy'])} |")
    with open(os.path.join(ROOT, "research", "blowup_results.json"), "w") as f:
        json.dump(rows, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cell":
        cell_main(*sys.argv[2:5])
    else:
        driver()
