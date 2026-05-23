"""
Plotting script: E7b binding-budget pseudo-polynomial scaling.

Reads dfalib/experiments/e7b.csv and produces:
  manuscript/figures/exp_e7b_binding_budget.pdf

Chart: time (ms) vs budget B (linear scale) with linear fit annotation.
Complements E7 (early-termination plateau) by showing the binding-budget regime.
"""

import sys
import pathlib
import csv

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

EXPERIMENTS_DIR = ROOT / "experiments"
FIGURES_DIR = ROOT.parent / "manuscript" / "figures"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_csv(path):
    if not path.exists():
        print(f"  CSV not found: {path}")
        return None
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def savefig(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path), bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def compute_linear_fit(xs, ys):
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / \
            sum((x - mean_x) ** 2 for x in xs)
    intercept = mean_y - slope * mean_x
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return slope, intercept, r2


def plot_e7b(rows):
    valid = [(int(r["budget"]), float(r["time_lb_ms"]))
             for r in rows if float(r["time_lb_ms"]) >= 0]
    if not valid:
        print("  E7b: no valid data rows")
        return

    bs, ts = zip(*valid)
    bs, ts = list(bs), list(ts)

    slope, intercept, r2 = compute_linear_fit(bs, ts)

    fig, ax = plt.subplots(figsize=(5, 3.5))

    ax.plot(bs, ts, "o-", color="#2563eb", markersize=5, linewidth=1.5,
            label="время BFS (мс)")

    # Linear fit line
    fit_ys = [slope * b + intercept for b in bs]
    ax.plot(bs, fit_ys, "--", color="#dc2626", linewidth=1.2,
            label=f"линейный fit ($R^2={r2:.3f}$)")

    ax.set_xlabel("Бюджет $B$ (единичная стоимость, «связывающий» режим)", fontsize=9)
    ax.set_ylabel("Время поиска (мс)", fontsize=9)
    ax.set_title("E7b: псевдополиномиальное масштабирование\n"
                 "(связывающий бюджет, фиксированный DFA k=4)", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Annotation
    ax.annotate(f"$R^2={r2:.3f}$\n~линейно по $B$",
                xy=(bs[-1], ts[-1]),
                xytext=(bs[len(bs)//2], max(ts)*0.6),
                fontsize=7.5,
                arrowprops=dict(arrowstyle="->", color="gray", lw=0.8),
                color="gray")

    fig.tight_layout()
    savefig(fig, FIGURES_DIR / "exp_e7b_binding_budget.pdf")


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    rows = read_csv(EXPERIMENTS_DIR / "e7b.csv")
    if rows:
        print("Plotting E7b...")
        plot_e7b(rows)
    else:
        print("E7b CSV missing — skipping.")


if __name__ == "__main__":
    main()
