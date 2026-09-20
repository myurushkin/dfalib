"""Is there a ceiling on jointly achievable strengths as the sequence grows?

The question was posed by our chemist collaborator: in a "complete DNA
transformer" (a sequence supporting all four non-canonical structures at once),
does the achievable strength keep growing with length, or does it saturate?
Sampling cannot answer this — absence of a find is not proof.  Exact search can.

We measure the growth curve directly: for k = 1, 2, 3, ... find the *minimal
length* L(k) at which all four families reach strength k simultaneously, and,
for comparison, the minimal length of each family alone.  A linear L(k) means no
ceiling; a superlinear blow-up or infeasibility within the budget marks a limit.

Run:  venv/bin/python prototype/ceiling.py
"""

from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from minstr.decompose import solve_dnf, DecompositionTooLarge
from pareto_front import build_query, AXIS_NAMES, ALPHA

from dafna.lib.strength.strength import (
    gqd_max_strength, i_motif_max_strength, hairpin_max_strength,
    triplex_max_strength)

MAX_LEN = 120
BUDGET = 4_000_000


def real_strengths(w):
    return (gqd_max_strength(w),
            max(i_motif_max_strength(w, False), i_motif_max_strength(w, True)),
            triplex_max_strength(w)[0],
            hairpin_max_strength(w))


def minimal_length(vec, max_len=MAX_LEN):
    trackers, formula = build_query(vec)
    t0 = time.perf_counter()
    try:
        word, st = solve_dnf(trackers, formula, ALPHA, min_len=0, max_len=max_len,
                             stop_at_first=True, state_budget=BUDGET,
                             max_conjuncts=2_000_000)
    except DecompositionTooLarge as e:
        return None, None, time.perf_counter() - t0, f"ДНФ слишком велика: {e}"
    dt = time.perf_counter() - t0
    if word is None:
        return None, None, dt, ("бюджет исчерпан" if st.exhausted
                                else f"нет решения до длины {max_len}")
    return len(word), word, dt, f"конъюнктов {st.conjuncts}, решено {st.solved}"


def main():
    rows = []
    print("Минимальная длина строки, в которой все четыре структуры "
          "одновременно достигают силы k\n")
    print(f"{'k':<4}{'L(k)':<8}{'прирост':<10}{'секунд':<10}{'свидетель'}")
    prev = None
    # hairpin strength is na+ng with na,ng >= 1, so k = 1 is impossible by
    # construction for that family; the joint curve starts at k = 2.
    for k in range(2, 7):
        L, w, dt, note = minimal_length((k, k, k, k))
        delta = "—" if (L is None or prev is None) else str(L - prev)
        print(f"{k:<4}{str(L or note):<8}{delta:<10}{dt:<10.2f}{w or ''}", flush=True)
        rows.append({"k": k, "joint_min_len": L, "witness": w, "seconds": round(dt, 2),
                     "note": note,
                     "verified": list(real_strengths(w)) if w else None})
        if L is None:
            break
        prev = L

    print("\nДля сравнения: каждое семейство по отдельности")
    print(f"{'k':<4}{'GQD':<8}{'IMT':<8}{'TRP':<8}{'HRP':<8}")
    singles = []
    for k in range(1, 7):
        line = {}
        for i, axis in enumerate(AXIS_NAMES):
            vec = [0, 0, 0, 0]
            vec[i] = k
            L, _, _, note = minimal_length(tuple(vec), max_len=80)
            line[axis] = L if L is not None else note
        singles.append({"k": k, **line})
        print(f"{k:<4}" + "".join(f"{str(line[a]):<8}" for a in AXIS_NAMES), flush=True)

    out = os.path.join(ROOT, "research", "ceiling.json")
    with open(out, "w") as f:
        json.dump({"joint": rows, "singles": singles}, f, ensure_ascii=False, indent=2)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
