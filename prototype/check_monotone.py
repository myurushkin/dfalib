"""Does every pattern of strength level l imply some pattern of level l-1?

Lemma 2 (downward closedness of the achievable-threshold set) rests on that
implication.  It is checked here exactly and *per pattern*, which is what the
lemma actually asks for: for a pattern P at level l we look for some pattern
Q at level l-1 such that no word up to length L satisfies P and not Q.  With
two leaves the search stays small; checking the whole unions at once would
not, because under a negation the lower bound degenerates to zero and the
search loses its guidance.

Run:  venv/bin/python prototype/check_monotone.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))

from minstr import formula as F
from minstr.search import Problem, find_minimal
from minstr.trackers import RegexTracker
from pareto_front import AXES, AXIS_NAMES, ALPHA

L = 30          # длина, на которой строилась решётка порогов


def implies(p_hi, p_lo):
    """Нет ли слова длины <= L, удовлетворяющего p_hi и не удовлетворяющего p_lo?"""
    trackers = [RegexTracker(p_hi, ALPHA, name="hi"),
                RegexTracker(p_lo, ALPHA, name="lo")]
    prob = Problem(trackers, F.AND(F.leaf(0), F.NOT(F.leaf(1))), ALPHA,
                   min_len=0, max_len=L)
    word, _ = find_minimal(prob)
    return word is None


def main():
    print(f"{'семейство':<12}{'уровни':>9}{'шаблонов':>10}   результат (длины до {L})")
    bad_total = 0
    for axis in AXIS_NAMES:
        build, levels = AXES[axis][0], [x for x in AXES[axis][1] if x]
        for hi, lo in zip(levels[1:], levels[:-1]):
            hi_pats, lo_pats = build(hi), build(lo)
            bad = [p for p in hi_pats if not any(implies(p, q) for q in lo_pats)]
            bad_total += len(bad)
            print(f"{axis:<12}{f'{hi}->{lo}':>9}{len(hi_pats):>10}   "
                  + ("все влекут какой-нибудь шаблон нижнего уровня" if not bad
                     else f"НЕ ВЛЕКУТ: {len(bad)} шт., напр. {bad[0]}"), flush=True)
    print("\nвывод:", "условие леммы выполнено" if not bad_total
          else f"условие НАРУШЕНО, шаблонов-исключений: {bad_total}")


if __name__ == "__main__":
    main()
