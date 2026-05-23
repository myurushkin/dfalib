"""E1 — масштабирование по числу шаблонов в AND.

Берём GQD канонические шаблоны strength=2 при разных m (длине g-блока) и
объединяем k штук через pintersect (lazy=True). Замеряем суммарное время и
пиковую Python-память на стороне Python (tracemalloc).
"""

from _common import measure, write_csv, EXPERIMENTS_DIR
from dafna.shared import Context, pintersect


def make_gqd(m: int, ctx: Context):
    ggg = "g" * m
    return ctx.create_pattern(f"X*{ggg}X+{ggg}X+{ggg}X+{ggg}X*")


def run(k: int):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    patterns = [make_gqd(m, ctx) for m in range(2, 2 + k)]

    def work():
        return pintersect(patterns, lazy=True).minimize()

    result, elapsed, peak = measure(work)
    return elapsed, peak, result.state_count()


def main():
    rows = []
    for k in [1, 2, 3, 4, 5]:
        elapsed, peak, states = run(k)
        rows.append([k, f"{elapsed:.4f}", peak, states])
        print(f"k={k}: {elapsed:.4f}s  peak={peak/1024:.1f}KiB  states={states}")
    write_csv(
        f"{EXPERIMENTS_DIR}/e1.csv",
        ["k_patterns", "time_sec", "peak_bytes", "result_states"],
        rows,
    )


if __name__ == "__main__":
    main()
