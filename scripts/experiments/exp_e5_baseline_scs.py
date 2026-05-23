"""E5 — сравнение с greedy SCS.

Для одних и тех же входных строк сравниваем:
- baseline: greedy_scs (Tournament) — производит конкретную надпоследовательность.
- наш подход: AND из шаблонов X* s_1 X* s_2 X* ... X* s_k X* — результат
  есть множество минимальных надпоследовательностей.

Одинаковая длина результатов — необходимое (не достаточное) условие
оптимальности; greedy SCS не гарантирует оптимум.
"""

import random

from _common import measure, write_csv, EXPERIMENTS_DIR
from baselines.greedy_scs import greedy_scs
from dafna.shared import Context, pintersect


def supersequence_pattern(s: str) -> str:
    return "X*" + "X*".join(s) + "X*"


def ours(strings):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    patterns = [ctx.create_pattern(supersequence_pattern(s)) for s in strings]
    result = pintersect(patterns, lazy=True).minimize()
    one = next(iter(result.min_strings(n_limit=1)), "")
    return one


def gen_strings(n: int, length: int, seed: int):
    rng = random.Random(seed)
    return ["".join(rng.choice("acgt") for _ in range(length)) for _ in range(n)]


def main():
    rows = []
    for n_strings, length in [(2, 4), (3, 4), (3, 6), (4, 5)]:
        strings = gen_strings(n_strings, length, seed=n_strings * 100 + length)

        baseline_str, t_b, _ = measure(lambda: greedy_scs(strings))
        ours_str, t_o, _ = measure(lambda: ours(strings))

        rows.append([
            n_strings, length,
            len(baseline_str), f"{t_b:.4f}",
            len(ours_str), f"{t_o:.4f}",
            ";".join(strings),
        ])
        print(
            f"n={n_strings} L={length}  "
            f"greedy: len={len(baseline_str)} t={t_b:.4f}s  |  "
            f"ours: len={len(ours_str)} t={t_o:.4f}s"
        )

    write_csv(
        f"{EXPERIMENTS_DIR}/e5.csv",
        ["n_strings", "length", "greedy_len", "greedy_time",
         "ours_len", "ours_time", "inputs"],
        rows,
    )


if __name__ == "__main__":
    main()
