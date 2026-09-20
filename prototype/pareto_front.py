"""Exact achievability map / Pareto front over the four DAFNA strengths.

Replaces the naive candidate sampling of ``scripts/measure_second.py``.
A grid point is a threshold vector (GQD >= g, IMT >= i, TRP >= t, HRP >= h);
each threshold is a union of *nominal* patterns:

* GQD(g):  canonical ``X* g^k X+ ... X*``  plus tandem ``X*(gY)^{4k-1}gX*``;
* IMT(i):  ``X* c{i} X+ c{i} XX+ c{i} X+ c{i} X*`` (createIMT with a=b=i);
* TRP(t):  the ``createTRPs(t)`` triples (2*2^t + 2*4^t patterns);
* HRP(h):  every concrete stem: at-part u in {a,t}^na, gc-part v in {g,c}^ng,
  na+ng = h, laid out as ``.* u .{0,3} v .{3,7} rc(v) .{0,3} rc(u) .*``
  mirroring the real hairpin checker's structure ((h-1) * 2^h patterns).

Feasibility of a point at fixed length L is decided by the bound-ordered
disjunctive decomposition (stop at first witness, state budget for the
undecided band).  Feasibility is monotone (lower thresholds are easier), so
dominated points inherit answers; the report is the set of maximal feasible
vectors with witness strings, each verified by the *real* strength functions.

Run:  venv/bin/python prototype/pareto_front.py [--length 30]
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from minstr import formula as F
from minstr.trackers import RegexTracker
from minstr.decompose import solve_dnf

from blowup_bench import trp_triples, trp_regex, gqd_regex

ALPHA = "acgt"
RC = {"a": "t", "t": "a", "g": "c", "c": "g"}


def revcomp(s):
    return "".join(RC[c] for c in reversed(s))


def gqd_union(g):
    tandem = "(g[act])" + "{" + str(4 * g - 1) + "}g"
    return [gqd_regex(g), f".*{tandem}.*"]


def imt_union(i):
    c = "c" * i
    return [f".*{c}.+{c}..+{c}.+{c}.*"]


def trp_union(t):
    return [trp_regex(*tr) for tr in trp_triples(t)]


def hrp_union(h):
    out = []
    for na in range(1, h):
        ng = h - na
        for u in itertools.product("at", repeat=na):
            for v in itertools.product("gc", repeat=ng):
                us, vs = "".join(u), "".join(v)
                out.append(f".*{us}.{{0,3}}{vs}.{{3,7}}"
                           f"{revcomp(vs)}.{{0,3}}{revcomp(us)}.*")
    return out


AXES = {  # axis -> (union builder, grid levels; 0 means unconstrained)
    "GQD": (gqd_union, (0, 2, 3, 4)),
    "IMT": (imt_union, (0, 2, 3, 4)),
    "TRP": (trp_union, (0, 2, 3)),
    "HRP": (hrp_union, (0, 2, 3, 4)),
}
AXIS_NAMES = tuple(AXES)


def build_query(point):
    """-> (trackers, formula) for one threshold vector."""
    trackers, groups = [], []
    for axis, level in zip(AXIS_NAMES, point):
        if level == 0:
            continue
        build = AXES[axis][0]
        leaves = []
        for j, pat in enumerate(build(level)):
            leaves.append(F.leaf(len(trackers)))
            trackers.append(RegexTracker(pat, ALPHA, name=f"{axis}{level}_{j}"))
        groups.append(F.OR(*leaves))
    return trackers, (F.AND(*groups) if groups else F.TRUE)


def dominates(p, q):
    return all(a >= b for a, b in zip(p, q)) and p != q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=30)
    ap.add_argument("--budget", type=int, default=300_000)
    ap.add_argument("--no-inherit", action="store_true",
                    help="solve every point exactly instead of inheriting the status "
                         "from a dominating/dominated one; the inheritance is only "
                         "sound when every pattern of level l implies some pattern of "
                         "level l-1, which check_monotone.py shows to fail for hairpins")
    args = ap.parse_args()
    L = args.length

    points = list(itertools.product(*(AXES[a][1] for a in AXIS_NAMES)))
    points.sort(key=lambda p: sum(p))          # easy points first
    status = {}                                # point -> "yes" | "no" | "undecided"
    witness = {}
    t_start = time.time()

    for pt in points:
        inherited = None
        for q, s in ({} if args.no_inherit else status).items():
            if s == "yes" and (q == pt or dominates(q, pt)):
                inherited = "yes"
                break
            if s == "no" and (q == pt or dominates(pt, q)):
                inherited = "no"
                break
        if inherited:
            status[pt] = inherited
            continue
        trackers, formula = build_query(pt)
        if not trackers:
            status[pt] = "yes"
            witness[pt] = "a" * L
            continue
        # Every axis pattern is .*-flanked, so its language is closed under
        # extension; a monotone AND/OR of such constraints is too.  Hence
        # "feasible at length exactly L" == "minimal witness <= L", and the
        # much cheaper minimum search decides the point; the witness is
        # padded back to length L.
        word, st = solve_dnf(trackers, formula, ALPHA, min_len=0, max_len=L,
                             stop_at_first=True, state_budget=args.budget)
        if word is not None:
            status[pt] = "yes"
            witness[pt] = word + "a" * (L - len(word))
        else:
            status[pt] = "undecided" if st.exhausted else "no"
        print(f"{pt} -> {status[pt]:<9} "
              f"(conjuncts={st.conjuncts}, solved={st.solved}, "
              f"{st.seconds:.2f}s)", flush=True)

    feasible = [p for p, s in status.items() if s == "yes"]
    front = [p for p in feasible
             if not any(dominates(q, p) for q in feasible)]
    front.sort(reverse=True)

    # Verify witnesses with the real strength functions.
    from dafna.lib.strength.strength import (
        gqd_max_strength, i_motif_max_strength, hairpin_max_strength,
        triplex_max_strength)

    def real_strengths(w):
        return (gqd_max_strength(w),
                max(i_motif_max_strength(w, False), i_motif_max_strength(w, True)),
                triplex_max_strength(w)[0],
                hairpin_max_strength(w))

    print("\n== Pareto front of achievable nominal strengths, "
          f"length {L} ==")
    rows = []
    for p in front:
        w = witness.get(p)
        real = real_strengths(w) if w else None
        rows.append({"point": p, "witness": w, "real": real})
        print(f"  {dict(zip(AXIS_NAMES, p))}  witness={w!r}  "
              f"real(GQD,IMT,TRP,HRP)={real}")
    undecided = [p for p, s in status.items() if s == "undecided"]
    if undecided:
        print(f"  undecided (budget {args.budget:,} states): "
              + ", ".join(map(str, sorted(undecided))))
    print(f"total {time.time()-t_start:.1f}s over {len(points)} grid points")

    out = {"length": L, "axes": {a: AXES[a][1] for a in AXIS_NAMES},
           "front": rows,
           "undecided": undecided,
           "status": {str(p): s for p, s in status.items()}}
    path = os.path.join(ROOT, "research", f"pareto_L{L}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("saved", path)


if __name__ == "__main__":
    main()
