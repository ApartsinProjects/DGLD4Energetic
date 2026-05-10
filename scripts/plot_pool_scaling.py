"""ED Fig. 2 - Pool-size scaling.

Brought over from `EnergeticDiffusion2/docs/paper/make_figures.py:fig_pool_scaling()`.
Self-contained: the four data points are inline (no external data file needed).

The internal version codes "joint v3 + v4-B, cfg=7" used in the original
title have been replaced with the published "DGLD-H + DGLD-P, cfg=7" naming
to match NMIPaper / NMIPaperSI; this is the same correction that
scripts/patch_ed_labels.py applies post-hoc, but baked into the source so a
clean regeneration is reproducible.
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
    runs = [
        ("Initial (pool=1.5k)", 1500, 4.11, 80,  "registry initial"),
        ("pool=8k",             8000, 0.79, 196, "this work"),
        ("pool=20k",           20000, 0.70, 983, "this work"),
        ("pool=40k",           40000, 0.92, 1667,"this work"),
    ]
    pools  = [r[1] for r in runs]
    scores = [r[2] for r in runs]
    finals = [r[3] for r in runs]

    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax2 = ax1.twinx()
    l1 = ax1.plot(pools, scores, "o-", color="#1f77b4",
                  label="best composite score (lower = better)")
    l2 = ax2.plot(pools, finals, "s--", color="#d62728",
                  label="candidates kept after all filters")
    ax1.set_xscale("log")
    ax1.set_xlabel("pool size (samples per denoiser)")
    ax1.set_ylabel("best composite score", color="#1f77b4")
    ax2.set_ylabel("# candidates after chem + SA/SC + Tanimoto", color="#d62728")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.set_title("Pool size scaling (DGLD-H + DGLD-P, cfg=7)")
    lines = l1 + l2
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper right")
    fig.tight_layout()

    base = os.path.join(OUT_DIR, "fig1_pool_scaling")
    fig.savefig(base + ".svg")
    fig.savefig(base + ".png", dpi=300)
    plt.close(fig)
    print(f"Saved: {base}.svg + .png")


if __name__ == "__main__":
    main()
