"""ED Fig. 3 - CFG-scale sweep at pool=8k.

Brought over from `EnergeticDiffusion2/docs/paper/make_figures.py:fig_cfg_sweep()`.
Self-contained: the three sweep points are inline (no external data file).

Bar = number of final candidates kept after the full filter funnel.
Line = best top-1 composite score (lower is better in the underlying metric).
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = r"E:\Projects\DGLD4Energetic-public\paper\figs"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 130,
})


def main():
    # (cfg_scale, raw_pool, after_chem, after_funnel, best_composite)
    runs = [
        (5, 802,  758,  528, 0.92),
        (7, 1533, 1429, 983, 0.70),
        (9, 673,  650,  427, 0.79),
    ]
    cfgs  = [r[0] for r in runs]
    final = [r[3] for r in runs]
    score = [r[4] for r in runs]

    fig, ax1 = plt.subplots(figsize=(6, 3.6))
    ax2 = ax1.twinx()
    ax1.bar([c - 0.18 for c in cfgs], final, width=0.36,
            color="#2ca02c", alpha=0.7, label="# final candidates")
    ax2.plot(cfgs, score, "o-", color="#d62728",
             label="best composite", markersize=8)
    ax1.set_xticks(cfgs)
    ax1.set_xlabel("CFG scale")
    ax1.set_ylabel("# final candidates", color="#2ca02c")
    ax2.set_ylabel("best composite score (lower = better)", color="#d62728")
    ax1.tick_params(axis="y", labelcolor="#2ca02c")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Classifier-free guidance scale sweep (pool=8k each)")
    fig.tight_layout()

    base = os.path.join(OUT_DIR, "fig2_cfg_sweep")
    fig.savefig(base + ".svg")
    fig.savefig(base + ".png", dpi=300)
    plt.close(fig)
    print(f"Saved: {base}.svg + .png")


if __name__ == "__main__":
    main()
