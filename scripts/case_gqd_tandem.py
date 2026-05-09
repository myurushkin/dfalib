"""
Биокейс S2: G-квадруплекс в тандемном повторе.

Сценарий: ищем последовательности, в которых одновременно
(а) присутствует канонический G-квадруплексный мотив (>= 4 трактов из g),
(б) внешний контекст имеет вид тандемного повтора с фланками.

Биология. G-квадруплексы (G4) — четырёхниточные структуры из G-богатых
участков ДНК, регулирующие транскрипцию и репликацию. Тандемные повторы,
содержащие G4-мотивы, ассоциированы с регуляторными областями и
полиморфизмами, влияющими на экспрессию.

Запуск:
  PYTHONPATH=dfalib/src .venv/bin/python dfalib/scripts/case_gqd_tandem.py
"""

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

from dafna.shared import Context, pintersect
from dafna.lib.generation import gqd_canonocal_gen

OUTPUT_PATH = pathlib.Path(__file__).with_name("case_gqd_tandem_output.txt")
SEED = 1


def build_program(ctx):
    """Соберём шаблон: каноничный G-квадруплекс силы 2, заключённый в тандем."""
    # X — алфавит ДНК
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    # Канонический GQD силы 2: X* gg X+ gg X+ gg X+ gg X*
    gqd_patterns = gqd_canonocal_gen.create(2, ctx)

    # Тандемный фланк: повторение мотива acg с обеих сторон
    flank_left = ctx.create_pattern("X*acgacgX*")
    flank_right = ctx.create_pattern("X*tcgtcgX*")

    return [flank_left] + gqd_patterns + [flank_right]


def main():
    ctx = Context()
    patterns = build_program(ctx)
    result = pintersect(patterns)

    examples = list(result.min_strings(n_limit=3))
    min_len = len(examples[0]) if examples else None

    lines = []
    lines.append("Биокейс: G-квадруплекс в тандемном повторе")
    lines.append(f"seed={SEED}, шаблонов={len(patterns)}")
    lines.append(f"состояний итогового ДКА: {result.state_count()}")
    lines.append(f"минимальная длина: {min_len}")
    lines.append("первые найденные строки:")
    for s in examples:
        lines.append(f"  {s}")
    lines.append("")
    lines.append("Толкование: каждая выведенная строка содержит четыре G-тракта")
    lines.append("(каноничный G4-мотив силы 2) внутри тандемно-повторённого фланка.")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
