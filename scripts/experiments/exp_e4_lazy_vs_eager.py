"""E4 — эффект ленивого пересечения.

Те же входы, что в E1, но обе ветки: lazy=False (полный product) и
lazy=True (только достижимые пары). Сравнение времени, пиковой памяти и
числа состояний промежуточного ДКА (до минимизации).
"""

from _common import measure, write_csv, EXPERIMENTS_DIR
from dafna.shared import Context, pintersect


def make_gqd(m: int, ctx: Context):
    ggg = "g" * m
    return ctx.create_pattern(f"X*{ggg}X+{ggg}X+{ggg}X+{ggg}X*")


def run(k: int, lazy: bool):
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    patterns = [make_gqd(m, ctx) for m in range(2, 2 + k)]

    def work():
        return pintersect(patterns, lazy=lazy).minimize()

    result, elapsed, peak = measure(work)
    return elapsed, peak, result.state_count()


def main():
    rows = []
    for k in [2, 3, 4, 5]:
        for lazy in [False, True]:
            elapsed, peak, states = run(k, lazy)
            mode = "lazy" if lazy else "eager"
            rows.append([k, mode, f"{elapsed:.4f}", peak, states])
            print(f"k={k} {mode}: {elapsed:.4f}s  peak={peak/1024:.1f}KiB  final_states={states}")
    write_csv(
        f"{EXPERIMENTS_DIR}/e4.csv",
        ["k_patterns", "mode", "time_sec", "peak_bytes", "final_states"],
        rows,
    )


if __name__ == "__main__":
    main()
