"""ED Fig. 1 - DGLD pipeline overview (4-box flow diagram).

Standalone NMI-version generator. Two bugs fixed relative to the long-form
plot_fig4_system_overview.py:fig4_1_pipeline_overview():

  - Box 3 used "per-step\\,$\\nabla$\\,bus" which rendered with literal
    backslash-comma sequences. Replaced with a clean mathmode expression.
  - Bottom-of-box "Fig 6" / "Figs 7, 8, 12" / etc. references were
    long-form-paper figure numbers that do not exist in the NMI version.
    Replaced with NMI-relative Methods-section pointers.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = r"E:\Projects\DGLD4Energetic-public\paper\figs"
os.makedirs(OUT_DIR, exist_ok=True)

NAVY        = "#27445d"
PURPLE      = "#6a3690"
GOLD        = "#b88a1f"
RED         = "#993333"
PALE_NAVY   = "#dde6ed"
PALE_PURPLE = "#e6ddee"
PALE_GOLD   = "#f4ecd6"
PALE_RED    = "#efd9d9"
TEXT_NAVY   = "#1f2c3a"
TEXT_SLATE  = "#5c6770"
TEXT_LIGHT  = "#7a8590"


def add_arrow(ax, x0, y0, x1, y1, color, lw=2.0):
    arrow = FancyArrowPatch((x0, y0), (x1, y1),
                            arrowstyle="-|>", mutation_scale=18,
                            linewidth=lw, color=color, zorder=3)
    ax.add_patch(arrow)


def main():
    fig, ax = plt.subplots(figsize=(14.0, 4.4), dpi=200)
    ax.set_xlim(0, 32.0)
    ax.set_ylim(0, 10.0)
    ax.set_aspect("auto")
    ax.axis("off")

    # Header
    ax.text(16.0, 9.20,
            r"DGLD pipeline overview: encode  $\to$  generate  $\to$  guide  $\to$  filter",
            ha="center", va="center", fontsize=12.0, fontweight=600,
            color=TEXT_NAVY, family="serif", zorder=3)

    # Geometry
    y_main = 5.2
    box_w = 6.6
    box_h = 4.4
    gap = 1.4
    span = 4 * box_w + 3 * gap
    x0 = (32.0 - span) / 2 + box_w / 2
    centers = [x0 + i * (box_w + gap) for i in range(4)]

    # Stages: (title, edge_color, fill_color, subtitle, math_line, tagline, math_fs)
    # Per-box figure/section pointers removed -- the figcaption in NMIPaper.html
    # already directs readers to Methods.
    # math_fs overrides the default math font size (11.2pt) for boxes whose
    # math line would otherwise overflow; box 4's filter chain is the long one.
    stages = [
        ("1. ENCODE",   NAVY,   PALE_NAVY,
         "LIMO VAE",
         r"SMILES $\to\,\mu$",
         "encode-once,\ncached", 11.2),
        ("2. GENERATE", PURPLE, PALE_PURPLE,
         "latent DDPM",
         r"$z_T \to z_0$",
         "40 DDIM steps", 11.2),
        ("3. GUIDE",    GOLD,   PALE_GOLD,
         "score model",
         r"per-step $\nabla$ bus",
         "viab + sens + haz", 11.2),
        ("4. FILTER",   RED,    PALE_RED,
         "physics funnel",
         r"SMARTS$\,\cdot\,$Pareto$\,\cdot\,$xTB$\,\cdot\,$DFT",
         r"40k $\to$ 12 leads", 9.8),
    ]

    for x_c, (title, edge, fill, sub, math, tag, math_fs) in zip(centers, stages):
        # drop shadow
        ax.add_patch(FancyBboxPatch(
            (x_c - box_w/2 + 0.10, y_main - box_h/2 - 0.10), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.30",
            linewidth=0, facecolor="#0a1620", alpha=0.10, zorder=1,
        ))
        ax.add_patch(FancyBboxPatch(
            (x_c - box_w/2, y_main - box_h/2), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.30",
            linewidth=1.8, facecolor=fill, edgecolor=edge, zorder=2,
        ))
        ax.text(x_c, y_main + box_h/2 - 0.55, title,
                ha="center", va="center",
                fontsize=13.5, fontweight=700, color=edge,
                family="serif", zorder=3)
        ax.text(x_c, y_main + box_h/2 - 1.30, sub,
                ha="center", va="center",
                fontsize=10.5, fontstyle="italic", color=TEXT_SLATE,
                family="serif", zorder=3)
        ax.text(x_c, y_main + 0.05, math,
                ha="center", va="center",
                fontsize=math_fs, fontweight=600, color=TEXT_NAVY,
                family="serif", zorder=3)
        ax.text(x_c, y_main - 1.00, tag,
                ha="center", va="center",
                fontsize=9.8, color=TEXT_NAVY,
                family="serif", zorder=3)

    for i in range(3):
        x_a = centers[i]   + box_w/2 + 0.05
        x_b = centers[i+1] - box_w/2 - 0.05
        add_arrow(ax, x_a, y_main, x_b, y_main, color=NAVY, lw=2.2)

    ax.text(16.0, 1.80,
            "Tier-A/B labels drive the conditional gradient; "
            "Tier-C/D drive the unconditional CFG branch only",
            ha="center", va="center",
            fontsize=9.4, fontstyle="italic", color=TEXT_SLATE,
            family="serif", zorder=3)

    base = os.path.join(OUT_DIR, "fig4_1_pipeline_overview")
    fig.savefig(base + ".png", dpi=240, bbox_inches="tight", facecolor="white")
    fig.savefig(base + ".svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {base}.png + .svg")


if __name__ == "__main__":
    main()
