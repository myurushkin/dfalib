"""
Plotting script: reads E6–E9 CSVs and produces PDF figures.

Output files in manuscript/figures/:
  exp_e6_overhead.pdf          — line graph: ratio time_lb/time_round2 vs n_patterns
                                  with secondary y-axis for absolute times
  exp_e7_budget_scaling.pdf    — log-log: time vs budget B
  exp_e8_window_scaling.pdf    — linear: time vs window width
  exp_e9_biocase_timing.pdf    — grouped bar chart: DFA build vs find time per biocase

Charts skip gracefully if their CSV is missing.
Russian labels to match manuscript visual style (same as exp_make_plots.py).
"""

import sys
import pathlib
import csv

ROOT = pathlib.Path(__file__).resolve().parents[1]  # dfalib/
sys.path.insert(0, str(ROOT / "src"))

EXPERIMENTS_DIR = ROOT / "experiments"
FIGURES_DIR = ROOT.parent / "manuscript" / "figures"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def read_csv(path):
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


# ── E6 ────────────────────────────────────────────────────────────────────────

def plot_e6(rows):
    ns = [int(r["n_patterns"]) for r in rows]
    t_round2 = [float(r["time_round2_ms"]) for r in rows]
    t_lb = [float(r["time_lb_unit_ms"]) for r in rows]
    ratios = [float(r["ratio"]) for r in rows]

    fig, ax1 = plt.subplots(figsize=(7, 4))

    color_r2 = "tab:blue"
    color_lb = "tab:orange"
    color_ratio = "tab:red"

    ax1.plot(ns, t_round2, marker="o", color=color_r2, label="round-2 BFS (без измерения стоимости)")
    ax1.plot(ns, t_lb, marker="s", color=color_lb, label="LB augmented BFS (cost=1)")
    ax1.set_xlabel("Число шаблонов n")
    ax1.set_ylabel("Время (мс)")
    ax1.set_yscale("log")
    ax1.yaxis.set_major_formatter(ticker.ScalarFormatter())

    ax2 = ax1.twinx()
    ax2.plot(ns, ratios, marker="^", color=color_ratio, linestyle="--", label="Отношение LB/round-2")
    ax2.set_ylabel("Отношение времён (LB / round-2)", color=color_ratio)
    ax2.tick_params(axis="y", labelcolor=color_ratio)
    ax2.axhline(y=10, color=color_ratio, linestyle=":", alpha=0.5, label="Порог 10×")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    ax1.set_title("Эксперимент E6: накладные расходы LB augmented BFS при cost=1\n"
                  "(«LB augmented BFS» vs «round-2 BFS» по числу шаблонов)")
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e6_overhead.pdf")


# ── E7 ────────────────────────────────────────────────────────────────────────

def plot_e7(rows):
    budgets = [int(r["budget"]) for r in rows]
    times = [float(r["time_lb_ms"]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(budgets, times, marker="o", color="tab:green")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Бюджет B")
    ax.set_ylabel("Время LB (мс)")
    ax.set_title("Эксперимент E7: время LB по бюджету B\n(режим раннего завершения при ненасыщенном бюджете)")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e7_budget_scaling.pdf")


# ── E8 ────────────────────────────────────────────────────────────────────────

def plot_e8(rows):
    widths = [int(r["window_width"]) for r in rows]
    times = [float(r["time_lw_ms"]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(widths, times, marker="o", color="tab:purple")
    ax.set_xlabel("Ширина окна (cost_hi − cost_lo)")
    ax.set_ylabel("Время LW (мс)")
    ax.set_title("Эксперимент E8: масштабирование LW по ширине окна")
    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e8_window_scaling.pdf")


# ── E9 ────────────────────────────────────────────────────────────────────────

def plot_e9(rows):
    try:
        import numpy as np
    except ImportError:
        import array as _arr
        # fallback without numpy
        np = None

    labels_map = {"hairpin": "Шпилька (hairpin)", "primer": "Праймер (primer)", "gqd": "G-квадруплекс (GQD)"}
    labels = [labels_map.get(r["biocase"], r["biocase"]) for r in rows]
    build_times = [float(r["time_dfa_build_ms"]) for r in rows]
    find_times = [float(r["time_find_ms"]) for r in rows]
    build_std = [float(r["time_dfa_build_std_ms"]) for r in rows]
    find_std = [float(r["time_find_std_ms"]) for r in rows]

    x = list(range(len(labels)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))
    bars1 = ax.bar([xi - width / 2 for xi in x], build_times, width,
                   label="Построение ДКА", color="tab:blue",
                   yerr=build_std, capsize=4)
    bars2 = ax.bar([xi + width / 2 for xi in x], find_times, width,
                   label="Поиск строки", color="tab:orange",
                   yerr=find_std, capsize=4)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Время (мс)")
    ax.set_title("Эксперимент E9: время выполнения биологических сценариев\n"
                 "(построение ДКА vs поиск строки, 3 повторения)")
    ax.legend()

    # Add value labels on top of bars
    for bar in bars1:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7)
    for bar in bars2:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7)

    plt.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e9_biocase_timing.pdf")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Генерация графиков E6–E9...\n")

    e6 = read_csv(EXPERIMENTS_DIR / "e6.csv")
    if e6:
        plot_e6(e6)

    e7 = read_csv(EXPERIMENTS_DIR / "e7.csv")
    if e7:
        plot_e7(e7)

    e8 = read_csv(EXPERIMENTS_DIR / "e8.csv")
    if e8:
        plot_e8(e8)

    e9 = read_csv(EXPERIMENTS_DIR / "e9.csv")
    if e9:
        plot_e9(e9)

    print("\nГотово.")


if __name__ == "__main__":
    main()
