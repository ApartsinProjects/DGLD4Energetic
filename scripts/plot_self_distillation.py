"""ED Fig. 5 - Self-distillation refinement (3 rounds).

Brought over from `EnergeticDiffusion2/plot_fig4_system_overview.py:fig4f_self_distillation()`,
along with the small set of drawing helpers the function relies on
(palette constants, add_box, add_arrow, setup_axes, save).

The diagram is a static layout: no external data file is read. All
labels and counts (0 -> 137 -> 918 hard negatives, round 2 = production)
are inline.

Output: paper/figs/fig4f_self_distillation.{png,svg}
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT_DIR = r"E:\Projects\DGLD4Energetic-public\paper\figs"
os.makedirs(OUT_DIR, exist_ok=True)

# Palette (semantic, lifted verbatim from the source script)
NAVY        = "#27445d"
GOLD        = "#b88a25"
RED         = "#aa3a3a"
GREEN       = "#3a7a4a"
PURPLE      = "#6a4a8a"
PALE_GOLD   = "#fdf3d8"
PALE_GREY   = "#dde6e9"
PALE_RED    = "#f7e6e6"
PALE_GREEN  = "#e3f1e3"
PALE_PURPLE = "#ece4f3"
CREAM       = "#f6f3ed"
TEXT_NAVY   = "#1f2c3a"
TEXT_SLATE  = "#5a6a7a"
TEXT_LIGHT  = "#8a9aaa"


def add_box(ax, x_c, w, h, y_c, fill, edge, title, subtitle,
            title_size=11.5, sub_size=9.0):
    x = x_c - w / 2
    y = y_c - h / 2
    ax.add_patch(FancyBboxPatch(
        (x + 0.04, y - 0.04), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.16",
        linewidth=0, facecolor="#0a1620", alpha=0.10, zorder=1,
    ))
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.16",
        linewidth=1.5, facecolor=fill, edgecolor=edge, zorder=2,
    ))
    if subtitle:
        ax.text(x_c, y_c + h * 0.18, title, ha="center", va="center",
                fontsize=title_size, fontweight=600, color=TEXT_NAVY,
                family="serif", zorder=3)
        ax.text(x_c, y_c - h * 0.22, subtitle, ha="center", va="center",
                fontsize=sub_size, fontstyle="italic", color=TEXT_SLATE,
                family="serif", zorder=3)
    else:
        ax.text(x_c, y_c, title, ha="center", va="center",
                fontsize=title_size, fontweight=600, color=TEXT_NAVY,
                family="serif", zorder=3)


def add_arrow(ax, x0, y0, x1, y1, color=NAVY, dashed=False, lw=1.8,
              shrink=0.06):
    if x0 == x1:
        dy = shrink if y1 > y0 else -shrink
        start, end = (x0, y0 + dy), (x1, y1 - dy)
    elif y0 == y1:
        dx = shrink if x1 > x0 else -shrink
        start, end = (x0 + dx, y0), (x1 - dx, y1)
    else:
        dx = shrink if x1 > x0 else -shrink
        dy = shrink if y1 > y0 else -shrink
        start, end = (x0 + dx, y0 + dy), (x1 - dx, y1 - dy)
    ax.annotate("", xy=end, xytext=start,
                xycoords="data", textcoords="data",
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                linestyle=(0, (5, 3)) if dashed else "-",
                                shrinkA=0, shrinkB=0, mutation_scale=12),
                zorder=4)


def setup_axes(ax, xmax, ymax):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_aspect("equal")
    ax.axis("off")


def save(fig, base):
    fig.savefig(base + ".png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(base + ".svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Saved:", base + ".{png,svg}")


def main():
    fig, ax = plt.subplots(figsize=(16.0, 7.6), dpi=300)
    setup_axes(ax, xmax=32.0, ymax=15.2)

    ax.text(16.0, 14.65,
            "Figure 4(d2). Labeling for guidance head training "
            "(self-distilled hard negatives)",
            ha="center", va="center", fontsize=12.4, fontweight="bold",
            color=TEXT_NAVY, family="serif")
    ax.text(16.0, 14.05,
            "Self-distillation: 3 rounds of mine-then-retrain, refining "
            "the Viability head only.",
            ha="center", va="center", fontsize=10.2, fontstyle="italic",
            color=TEXT_SLATE, family="serif")

    fz_x, fz_y, fz_w, fz_h = 0.30, 1.2, 5.20, 12.2
    ax.add_patch(FancyBboxPatch(
        (fz_x + 0.05, fz_y - 0.05), fz_w, fz_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        linewidth=0, facecolor="#0a1620", alpha=0.08, zorder=1))
    ax.add_patch(FancyBboxPatch(
        (fz_x, fz_y), fz_w, fz_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        linewidth=1.4, facecolor="#eaf1f6", edgecolor=NAVY, zorder=2))
    ax.text(fz_x + fz_w / 2, fz_y + fz_h - 0.65,
            r"$\ast$  FROZEN  $\ast$",
            ha="center", va="center", fontsize=11.2, fontweight="bold",
            color=NAVY, family="serif", zorder=3)
    ax.text(fz_x + fz_w / 2, fz_y + fz_h - 1.30,
            "(no weight updates between rounds)",
            ha="center", va="center", fontsize=8.4, fontstyle="italic",
            color=TEXT_SLATE, family="serif", zorder=3)
    frozen_items = [
        "LIMO encoder",
        "LIMO decoder",
        "denoiser DGLD-H",
        "denoiser DGLD-P",
        "RF viability teacher",
        "SMARTS rulebook",
    ]
    for k, item in enumerate(frozen_items):
        yy = fz_y + fz_h - 2.20 - k * 0.85
        ax.text(fz_x + 0.50, yy, r"$\bullet$", ha="left", va="center",
                fontsize=10.0, color=NAVY, family="serif", zorder=3)
        ax.text(fz_x + 0.95, yy, item, ha="left", va="center",
                fontsize=9.6, color=TEXT_NAVY, family="serif", zorder=3)
    ax.text(fz_x + fz_w / 2, fz_y + 0.45,
            "[lock]  weights identical across rounds 0, 1, 2",
            ha="center", va="center", fontsize=8.2, fontstyle="italic",
            color=TEXT_SLATE, family="serif", zorder=3)

    tr_x, tr_y, tr_w, tr_h = 0.30, 0.05, 5.20, 1.05
    ax.add_patch(FancyBboxPatch(
        (tr_x + 0.05, tr_y - 0.05), tr_w, tr_h,
        boxstyle="round,pad=0.03,rounding_size=0.10",
        linewidth=0, facecolor="#0a1620", alpha=0.08, zorder=1))
    ax.add_patch(FancyBboxPatch(
        (tr_x, tr_y), tr_w, tr_h,
        boxstyle="round,pad=0.03,rounding_size=0.10",
        linewidth=1.4, facecolor=PALE_GOLD, edgecolor=GOLD, zorder=2))
    ax.text(tr_x + tr_w / 2, tr_y + tr_h - 0.30,
            "TRAINED EACH ROUND: score-model trunk + heads",
            ha="center", va="center", fontsize=9.0, fontweight="bold",
            color=TEXT_NAVY, family="serif", zorder=3)
    ax.text(tr_x + tr_w / 2, tr_y + 0.30,
            r"Viability head: $a_{\mathrm{viab}}\!=\!1$ on hard negs;  "
            r"others: $a_k\!=\!0$",
            ha="center", va="center", fontsize=7.8, fontstyle="italic",
            color=TEXT_SLATE, family="serif", zorder=3)

    rows_y = [11.4, 7.8, 4.2]
    round_labels = ["Round 0", "Round 1", "Round 2"]
    train_x  = 8.6
    probe_x  = 12.4
    samp_x   = 16.0
    mine_x   = 19.6
    encode_x = 23.4
    bw   = 2.8
    bh   = 1.45

    train_data_specs = [
        ("TRAIN",  "corpus + 0 hard negs"),
        ("TRAIN",  "corpus + 137 hard negs"),
        ("TRAIN",  "corpus + 918 hard negs"),
    ]
    mined_per_round = [137, 781, 0]
    cumulative      = [0, 137, 918]

    for i, (y, lbl, td) in enumerate(zip(rows_y, round_labels,
                                         train_data_specs)):
        ax.text(7.0, y, lbl, ha="right", va="center", fontsize=11.2,
                fontweight="bold", color=TEXT_NAVY, family="serif")
        if i == 2:
            ax.add_patch(FancyBboxPatch(
                (5.85, y + 0.20), 1.30, 0.42,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                linewidth=1.0, facecolor=PALE_GREEN, edgecolor=GREEN, zorder=2))
            ax.text(6.50, y + 0.41, r"$\checkmark$ production",
                    ha="center", va="center", fontsize=7.8, fontweight="bold",
                    color=GREEN, family="serif", zorder=3)

        add_box(ax, train_x, bw, bh, y, CREAM, NAVY, td[0], td[1],
                title_size=10.0, sub_size=8.4)
        if i == 0:
            ax.text(train_x, y - bh / 2 - 0.30,
                    "(round 0: zero hard negs)",
                    ha="center", va="center", fontsize=7.8,
                    fontstyle="italic", color=RED, family="serif")

        add_arrow(ax, train_x + bw / 2, y, probe_x - bw / 2, y, lw=1.5)
        add_box(ax, probe_x, bw, bh, y, PALE_GREEN, GREEN,
                "PROBE", "7 anchors / 5 cheats",
                title_size=10.0, sub_size=8.0)

        if i < 2:
            add_arrow(ax, probe_x + bw / 2, y, samp_x - bw / 2, y,
                      color=PURPLE, dashed=True, lw=1.5)
            add_box(ax, samp_x, bw, bh, y, PALE_PURPLE, PURPLE,
                    "SAMPLE",
                    f"diffusion + v{i} guide",
                    title_size=10.0, sub_size=8.0)
            add_arrow(ax, samp_x + bw / 2, y, mine_x - bw / 2, y, lw=1.5)
            add_box(ax, mine_x, bw, bh, y, PALE_RED, RED,
                    "MINE",
                    f"+{mined_per_round[i]} false pos.",
                    title_size=10.0, sub_size=8.0)
            ax.text(mine_x, y - bh / 2 - 0.32,
                    "FP iff Viab > 0.7  AND  SMARTS rejects",
                    ha="center", va="center", fontsize=7.4,
                    fontstyle="italic", color=RED, family="serif")
            add_arrow(ax, mine_x + bw / 2, y, encode_x - bw / 2, y,
                      color=RED, dashed=True, lw=1.5)
            add_box(ax, encode_x, bw, bh, y, PALE_GOLD, GOLD,
                    "ENCODE",
                    "via frozen LIMO; viab = 0",
                    title_size=10.0, sub_size=7.8)
            ax.annotate("", xy=(train_x, rows_y[i + 1] + bh / 2 + 0.05),
                        xytext=(encode_x - bw / 2 - 0.10,
                                y - bh / 2 - 0.05),
                        arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6,
                                        linestyle=(0, (4, 3)),
                                        shrinkA=0, shrinkB=0,
                                        connectionstyle="arc3,rad=0.22",
                                        mutation_scale=12),
                        zorder=4)
            ax.text((encode_x + train_x) / 2 + 0.4,
                    (y + rows_y[i + 1]) / 2 + 0.55,
                    "feed back as viab=0 latents",
                    ha="center", va="center", fontsize=8.2,
                    fontstyle="italic", color=RED, family="serif", zorder=5)
        else:
            add_arrow(ax, probe_x + bw / 2, y, samp_x - bw / 2, y,
                      color=GREEN, lw=1.6)
            add_box(ax, samp_x, bw, bh, y, PALE_GREEN, GREEN,
                    "STOP",
                    "anchors >= 0.86; cheats <= 0.84",
                    title_size=10.0, sub_size=7.6)
            add_arrow(ax, samp_x + bw / 2, y, mine_x - bw / 2, y,
                      color=GREEN, lw=1.5)
            add_box(ax, mine_x, bw, bh, y, "#fff8d8", GOLD,
                    "v2 = production",
                    "score model frozen here",
                    title_size=10.0, sub_size=7.6)

    tk_x, tk_y, tk_w, tk_h = 26.7, 4.4, 4.6, 9.0
    ax.add_patch(FancyBboxPatch(
        (tk_x + 0.05, tk_y - 0.05), tk_w, tk_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        linewidth=0, facecolor="#0a1620", alpha=0.08, zorder=1))
    ax.add_patch(FancyBboxPatch(
        (tk_x, tk_y), tk_w, tk_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        linewidth=1.4, facecolor=CREAM, edgecolor=NAVY, zorder=2))
    ax.text(tk_x + tk_w / 2, tk_y + tk_h - 0.45,
            "Hard-negative growth",
            ha="center", va="center", fontsize=10.0, fontweight="bold",
            color=TEXT_NAVY, family="serif", zorder=3)
    bar_xs = [tk_x + 1.0, tk_x + 2.4, tk_x + 3.8]
    bar_lbls = ["R0", "R1", "R2"]
    max_bar_h = 5.8
    cum_max = 918.0
    bar_base_y = tk_y + 1.05
    for k, (cnt, bx, lbl) in enumerate(zip(cumulative, bar_xs, bar_lbls)):
        h = max_bar_h * (cnt / cum_max) if cnt > 0 else 0.04
        ax.add_patch(Rectangle((bx - 0.40, bar_base_y), 0.80, h,
                               facecolor=RED if cnt > 0 else PALE_GREY,
                               edgecolor=NAVY, linewidth=1.0, zorder=3))
        ax.text(bx, bar_base_y + h + 0.30, str(cnt),
                ha="center", va="center", fontsize=9.4, fontweight="bold",
                color=RED if cnt > 0 else TEXT_SLATE, family="serif",
                zorder=3)
        ax.text(bx, bar_base_y - 0.30, lbl,
                ha="center", va="center", fontsize=9.2,
                color=TEXT_NAVY, family="serif", zorder=3)
    ax.text(tk_x + tk_w / 2, tk_y + 0.30,
            r"0  $\rightarrow$  137  $\rightarrow$  918",
            ha="center", va="center", fontsize=9.2, fontstyle="italic",
            color=TEXT_SLATE, family="serif", zorder=3)

    sc_x, sc_y, sc_w, sc_h = 26.7, 1.6, 4.6, 2.4
    ax.add_patch(FancyBboxPatch(
        (sc_x + 0.05, sc_y - 0.05), sc_w, sc_h,
        boxstyle="round,pad=0.03,rounding_size=0.12",
        linewidth=0, facecolor="#0a1620", alpha=0.08, zorder=1))
    ax.add_patch(FancyBboxPatch(
        (sc_x, sc_y), sc_w, sc_h,
        boxstyle="round,pad=0.03,rounding_size=0.12",
        linewidth=1.4, facecolor=PALE_GREEN, edgecolor=GREEN, zorder=2))
    ax.text(sc_x + sc_w / 2, sc_y + sc_h - 0.40,
            r"$\checkmark$ STOP criterion",
            ha="center", va="center", fontsize=10.0, fontweight="bold",
            color=GREEN, family="serif", zorder=3)
    ax.text(sc_x + sc_w / 2, sc_y + sc_h - 1.10,
            "held-out probe shows:",
            ha="center", va="center", fontsize=8.6, fontstyle="italic",
            color=TEXT_SLATE, family="serif", zorder=3)
    ax.text(sc_x + sc_w / 2, sc_y + sc_h - 1.55,
            r"7 anchors $\geq$ 0.86",
            ha="center", va="center", fontsize=9.0,
            color=TEXT_NAVY, family="serif", zorder=3)
    ax.text(sc_x + sc_w / 2, sc_y + sc_h - 1.95,
            r"AND   5 cheats $\leq$ 0.84",
            ha="center", va="center", fontsize=9.0,
            color=TEXT_NAVY, family="serif", zorder=3)
    ax.text(sc_x + sc_w / 2, sc_y + 0.20,
            r"(reached at round 2: production checkpoint)",
            ha="center", va="center", fontsize=7.8, fontstyle="italic",
            color=GREEN, family="serif", zorder=3)

    base = os.path.join(OUT_DIR, "fig4f_self_distillation")
    save(fig, base)


if __name__ == "__main__":
    main()
