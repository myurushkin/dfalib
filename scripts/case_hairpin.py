"""
Биокейс S2: ДНК-шпилька с заданной силой плеч.

Сценарий: ищем последовательности вида a^n X t^n при n из ограниченного
диапазона — комплементарные плечи a/t образуют ствол шпильки. После
поиска минимальных строк проверяем фактическую силу шпильки через
hairpin.max_hairpin_strength.

Связь с §4.3. Используется именно нерегулярный согласованный шаблон
a{n}Xt{n}: при произвольном n язык нерегулярен, но при n из конечного
диапазона — конечное объединение регулярных, см. формулу (1).

Запуск:
  PYTHONPATH=dfalib/src .venv/bin/python dfalib/scripts/case_hairpin.py
"""

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context
from dafna.lib.strength.hairpin import max_hairpin_strength

OUTPUT_PATH = pathlib.Path(__file__).with_name("case_hairpin_output.txt")
SEED = 1
LO, HI = 2, 4  # диапазон длины каждого плеча


def build_pattern(ctx, n):
    """Строит шаблон шпильки: плечо a^n, вставка XXXX, обратное плечо t^n."""
    arm_a = "a" * n
    arm_t = "t" * n
    # Жёстко: a^n . X^4 . t^n. X^4 — фиксированная длина петли для устойчивого поиска.
    return ctx.create_pattern(f"{arm_a}XXXX{arm_t}")


def main():
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    lines = []
    lines.append("Биокейс: ДНК-шпилька с комплементарными плечами")
    lines.append(f"seed={SEED}, диапазон n=[{LO}..{HI}]")
    lines.append("")

    for n in range(LO, HI + 1):
        pattern = build_pattern(ctx, n)
        examples = list(pattern.min_strings(n_limit=3))
        min_len = len(examples[0]) if examples else None
        strengths = [max_hairpin_strength(s) for s in examples]
        lines.append(f"n={n}: состояний={pattern.state_count()}, мин. длина={min_len}")
        for s, st in zip(examples, strengths):
            lines.append(f"  {s}    (сила шпильки = {st})")

    lines.append("")
    lines.append("Толкование: каждая строка имеет вид a^n XXXX t^n.")
    lines.append("Комплементарность a-t гарантирует ненулевую силу шпильки.")
    lines.append("Длина n параметризована через семейство шаблонов из §4.3 (формула 1).")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
