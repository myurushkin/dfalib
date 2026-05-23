"""E3 — полный поиск vs N-первых.

Берём шаблон с большим числом минимальных строк и замеряем время на
извлечение полного списка против первых N для разных N.
"""

from _common import measure, write_csv, EXPERIMENTS_DIR
from dafna.shared import Context


def main():
    ctx = Context()
    ctx.create_pattern("a|c|g|t", simple=True, name="X")
    # Длина 8: 4^8 = 65536 минимальных строк.
    pattern = ctx.create_pattern("X" * 8).minimize()

    rows = []
    for n_limit in [None, 10, 100, 1000, 5000]:
        def work(lim=n_limit):
            return list(pattern.min_strings(n_limit=lim))

        result, elapsed, peak = measure(work)
        n_returned = len(result)
        label = "full" if n_limit is None else str(n_limit)
        rows.append([label, f"{elapsed:.4f}", peak, n_returned])
        print(f"n_limit={label}: {elapsed:.4f}s  peak={peak/1024:.1f}KiB  returned={n_returned}")

    write_csv(
        f"{EXPERIMENTS_DIR}/e3.csv",
        ["n_limit", "time_sec", "peak_bytes", "n_returned"],
        rows,
    )


if __name__ == "__main__":
    main()
