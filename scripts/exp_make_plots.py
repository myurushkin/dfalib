"""
Plotting script: reads E1–E4 CSVs and produces PDF figures.

Output files in /home/ilya/storage/pappers/dfa_pappepr/manuscript/figures/:
  exp_e1_time.pdf  — log-log: time vs k (E1)
  exp_e1_mem.pdf   — log-log: peak_rss vs k (E1)
  exp_e2.pdf       — linear: time vs regex_length (E2)
  exp_e3.pdf       — bar chart: time per n_limit (E3), label -1 as "full"
  exp_e4.pdf       — grouped bar chart: eager vs lazy time per k (E4);
                     a second panel shows memory if dynamic range > 100x.

Charts skip gracefully if their CSV is missing.
All titles and axis labels are in Russian.
"""

import sys
import pathlib
import csv
import math

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

EXPERIMENTS_DIR = ROOT / "experiments"
FIGURES_DIR = ROOT.parent / "manuscript" / "figures"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def read_csv(path):
    """Read CSV into list of dicts. Returns None if file missing."""
    if not path.exists():
        print(f"  [пропуск] CSV не найден: {path}")
        return None
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def savefig(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path), bbox_inches="tight")
    plt.close(fig)
    print(f"  Сохранён: {path}")


# ── E1 ────────────────────────────────────────────────────────────────────────

def plot_e1(rows):
    ks = [int(r["k"]) for r in rows]
    times = [float(r["time_s"]) for r in rows]
    rss = [float(r["peak_rss_kb"]) for r in rows]

    # Time plot
    fig, ax = plt.subplots()
    ax.plot(ks, times, marker="o")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Число шаблонов k")
    ax.set_ylabel("Время (с)")
    ax.set_title("Эксперимент E1: масштабирование по числу шаблонов\n(время)")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e1_time.pdf")

    # Memory plot — use absolute values so log scale works even with 0 delta
    rss_plot = [max(v, 1) for v in rss]
    fig, ax = plt.subplots()
    ax.plot(ks, rss_plot, marker="s", color="tab:orange")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Число шаблонов k")
    ax.set_ylabel("Пик RSS дочернего процесса (КБ)")
    ax.set_title("Эксперимент E1: масштабирование по числу шаблонов\n(память)")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e1_mem.pdf")


# ── E2 ────────────────────────────────────────────────────────────────────────

def plot_e2(rows):
    lengths = [int(r["regex_length"]) for r in rows]
    times = [float(r["time_s"]) for r in rows]

    fig, ax = plt.subplots()
    ax.plot(lengths, times, marker="o", color="tab:green")
    ax.set_xlabel("Длина регулярного выражения L")
    ax.set_ylabel("Время (с)")
    ax.set_title("Эксперимент E2: масштабирование по длине регулярного выражения")
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e2.pdf")


# ── E3 ────────────────────────────────────────────────────────────────────────

def plot_e3(rows):
    labels = ["full" if int(r["n_limit"]) == -1 else r["n_limit"] for r in rows]
    times = [float(r["time_s"]) for r in rows]

    fig, ax = plt.subplots()
    x = range(len(labels))
    bars = ax.bar(x, times, color="tab:purple")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_xlabel("Ограничение n_limit (\"full\" = без ограничения)")
    ax.set_ylabel("Время (с)")
    ax.set_title("Эксперимент E3: полный перебор vs N-first min_strings")
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e3.pdf")


# ── E4 ────────────────────────────────────────────────────────────────────────

def plot_e4(rows):
    import numpy as np

    ks = sorted(set(int(r["k"]) for r in rows))
    eager_states, lazy_states = [], []
    eager_mem, lazy_mem = [], []

    for k in ks:
        for r in rows:
            if int(r["k"]) == k and r["mode"] == "eager":
                eager_states.append(float(r["states_raw"]))
                eager_mem.append(max(float(r["peak_rss_kb"]), 1))
            if int(r["k"]) == k and r["mode"] == "lazy":
                lazy_states.append(float(r["states_raw"]))
                lazy_mem.append(max(float(r["peak_rss_kb"]), 1))

    x = np.arange(len(ks))
    width = 0.35
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # States panel — the dramatic contrast: O(k^2) vs O(k)
    ax = axes[0]
    ax.bar(x - width / 2, eager_states, width, label="eager", color="tab:blue")
    ax.bar(x + width / 2, lazy_states, width, label="lazy", color="tab:red")
    ax.set_xticks(x)
    ax.set_xticklabels([str(k) for k in ks])
    ax.set_xlabel("Длина шаблона k")
    ax.set_ylabel("Состояний промежуточного ДКА")
    ax.set_title("Размер промежуточного ДКА")
    ax.legend()

    # Memory panel
    ax = axes[1]
    ax.bar(x - width / 2, eager_mem, width, label="eager", color="tab:blue", alpha=0.7)
    ax.bar(x + width / 2, lazy_mem, width, label="lazy", color="tab:red", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([str(k) for k in ks])
    ax.set_xlabel("Длина шаблона k")
    ax.set_ylabel("Пик RSS дочернего процесса (КБ)")
    ax.set_title("Пик памяти дочернего процесса")
    ax.legend()

    fig.suptitle("Эксперимент E4: ленивое vs полное пересечение (без минимизации)", fontsize=12)
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e4.pdf")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Генерация графиков...\n")

    e1 = read_csv(EXPERIMENTS_DIR / "e1.csv")
    if e1:
        plot_e1(e1)

    e2 = read_csv(EXPERIMENTS_DIR / "e2.csv")
    if e2:
        plot_e2(e2)

    e3 = read_csv(EXPERIMENTS_DIR / "e3.csv")
    if e3:
        plot_e3(e3)

    e4 = read_csv(EXPERIMENTS_DIR / "e4.csv")
    if e4:
        plot_e4(e4)

    print("\nГотово.")


if __name__ == "__main__":
    main()
