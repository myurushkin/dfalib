"""E2 — масштабирование по длине одного шаблона.

Шаблон вида (a|c|g|t)^k = `X X X ... X` (k раз) с внешними `X*`.
Замеряем построение ДКА и поиск всех минимальных строк.
"""

from _common import measure, write_csv, EXPERIMENTS_DIR
from dafna.shared import Context


def run(k: int):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")

    pat = "X*" + "X" * k + "X*"

    def work():
        p = ctx.create_pattern(pat).minimize()
        return p, len(list(p.min_strings()))

    (p, n_min), elapsed, peak = measure(work)
    return elapsed, peak, p.state_count(), n_min


def main():
    rows = []
    for k in [4, 8, 12, 16, 20, 24]:
        elapsed, peak, states, n_min = run(k)
        rows.append([k, f"{elapsed:.4f}", peak, states, n_min])
        print(f"k={k}: {elapsed:.4f}s  peak={peak/1024:.1f}KiB  states={states}  min_strings={n_min}")
    write_csv(
        f"{EXPERIMENTS_DIR}/e2.csv",
        ["regex_length", "time_sec", "peak_bytes", "result_states", "n_min_strings"],
        rows,
    )


if __name__ == "__main__":
    main()
