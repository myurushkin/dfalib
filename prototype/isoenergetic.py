"""Isoenergetic conformers: strings whose alternative non-canonical folds have
nearly equal energy.

Setting proposed by our chemist collaborator.  Each motif family gets an
additive per-unit stabilisation energy; the energy of the best fold of type a
in a string w is  E_a * s_a(w), where s_a is the strength (number of units).
A string is *isoenergetic* when these products are close to each other across
families, i.e. the molecule has several competing folds of comparable energy.

This script:
  1. enumerates candidate exact strength vectors and ranks them by energy spread;
  2. for the most balanced ones, finds the minimal length at which the threshold
     vector (s_a or more) is realisable;
  3. enumerates minimal-length solutions and keeps those whose strengths, as
     measured by the *real* dafna strength functions, equal the target exactly;
  4. reports the witness, its verified strengths and energies.

Per-unit energies are placeholders supplied as an example (GQD 40, IMT 20,
TRP 15, HRP 10) and are meant to be replaced by computed values.

Run:  venv/bin/python prototype/isoenergetic.py
"""

from __future__ import annotations

import itertools
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from minstr import formula as F
from minstr.search import Problem, all_minimal
from minstr.decompose import solve_dnf
from pareto_front import build_query, AXIS_NAMES, ALPHA

from dafna.lib.strength.strength import (
    gqd_max_strength, i_motif_max_strength, hairpin_max_strength,
    triplex_max_strength)

ENERGY = {"GQD": 40.0, "IMT": 20.0, "TRP": 15.0, "HRP": 10.0}   # example values
MAX_LEN = 48
ENUM_LIMIT = 4000


def real_strengths(w):
    return {
        "GQD": gqd_max_strength(w),
        "IMT": max(i_motif_max_strength(w, False), i_motif_max_strength(w, True)),
        "TRP": triplex_max_strength(w)[0],
        "HRP": hairpin_max_strength(w),
    }


def energies(strengths):
    return {a: ENERGY[a] * strengths[a] for a in AXIS_NAMES}


def spread(vec):
    e = [ENERGY[a] * s for a, s in zip(AXIS_NAMES, vec)]
    return max(e) - min(e), sum(e) / len(e)


def candidates(g_rng, i_rng, t_rng, h_rng, top):
    out = []
    for v in itertools.product(g_rng, i_rng, t_rng, h_rng):
        sp, mean = spread(v)
        out.append((sp / mean, sp, v))
    out.sort()
    return out[:top]


def main():
    cands = candidates(range(1, 3), range(1, 5), range(1, 4), range(2, 7), 8)
    print("candidate exact strength vectors, ranked by relative energy spread")
    print(f"per-unit energies (example): {ENERGY}\n")
    print(f"{'(GQD,IMT,TRP,HRP)':<20}{'энергии':<28}{'разброс':<10}{'мин. длина':<12}"
          f"{'свидетель с точными силами'}")
    rows = []
    for rel, sp, vec in cands:
        e = [int(ENERGY[a] * s) for a, s in zip(AXIS_NAMES, vec)]
        trackers, formula = build_query(vec)
        t0 = time.perf_counter()
        word, st = solve_dnf(trackers, formula, ALPHA, min_len=0, max_len=MAX_LEN,
                             stop_at_first=True, state_budget=2_000_000)
        dt = time.perf_counter() - t0
        if word is None:
            print(f"{str(vec):<20}{str(e):<28}{sp:<10.0f}{'нет до ' + str(MAX_LEN):<12}—")
            rows.append({"vector": vec, "energies": e, "spread": sp, "min_len": None})
            continue
        L = len(word)
        # enumerate minimal-length solutions; keep those matching the target exactly
        exact, checked = None, 0
        p = Problem(trackers, formula, ALPHA, min_len=L, max_len=L)
        try:
            graph, _ = all_minimal(p, length=L)
            total = graph.count()
            for w in graph.enumerate(limit=ENUM_LIMIT):
                checked += 1
                rs = real_strengths(w)
                if all(rs[a] == s for a, s in zip(AXIS_NAMES, vec)):
                    exact = (w, rs)
                    break
        except Exception as err:
            total = f"(не перечислено: {err})"
        note = (f"{exact[0]} (проверено: "
                + ", ".join(f"{a}={exact[1][a]}" for a in AXIS_NAMES) + ")") if exact \
            else f"среди {checked} мин. решений точного нет"
        print(f"{str(vec):<20}{str(e):<28}{sp:<10.0f}{L:<12}{note}", flush=True)
        rows.append({"vector": vec, "energies": e, "spread": sp, "min_len": L,
                     "n_minimal": total if isinstance(total, int) else str(total),
                     "witness": exact[0] if exact else None,
                     "verified": exact[1] if exact else None,
                     "search_seconds": round(dt, 2),
                     "conjuncts": st.conjuncts, "solved": st.solved})
    with open(os.path.join(ROOT, "research", "isoenergetic.json"), "w") as f:
        json.dump({"energies": ENERGY, "rows": rows}, f, ensure_ascii=False, indent=2,
                  default=str)
    print("\nsaved research/isoenergetic.json")


if __name__ == "__main__":
    main()
