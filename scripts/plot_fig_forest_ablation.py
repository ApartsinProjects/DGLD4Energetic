"""Forest plot: guidance ablation effect sizes vs unguided baseline.

Saves:
  paper/figs/fig_forest_ablation.png
  paper/figs/fig_forest_ablation.svg

Layout fixes in this revision (see code review notes Round 5):
  - Markers coloured by Hz/SA axis (matches legend) instead of by sign,
    with shape variation (square = SA, diamond = Hz) for colour-blind safety
  - Row labels rendered on left margin via explicit subplots_adjust
  - Panel letters (a)(b)(c)(d) added to each subplot title
  - Value labels nudged out of marker zone (offset = max(err_total, |delta|*0.10))
  - No suptitle; figcaption in NMIPaper.html carries the headline
  - "Table 5" reference removed (long-form-paper artefact)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------------------------------------------------------------
# Data (Table 5 of the long-form paper; verified Round 5 audit)
# ---------------------------------------------------------------------------

BASELINE = {
    "composite": (0.451, 0.126),
    "D_kms":     (9.44,  0.07),
    "rho":       (1.93,  0.01),
    "P_GPa":     (39.7,  0.6),
    "tani":      (0.61,  0.10),
}

CONDITIONS = [
    {"label": "SA-C1  viab-only",                "axis": "SA",
     "composite": (0.542, 0.184), "D_kms": (9.54, 0.04), "rho": (1.93, 0.01),
     "P_GPa": (39.8, 0.5), "tani": (0.63, 0.06)},
    {"label": "Hz-C1  viab+sens",                "axis": "Hz",
     "composite": (0.613, 0.106), "D_kms": (9.36, 0.06), "rho": (1.93, 0.01),
     "P_GPa": (38.7, 0.4), "tani": (0.46, 0.04)},
    {"label": "SA-C2  viab+sens",                "axis": "SA",
     "composite": (0.618, 0.056), "D_kms": (9.44, 0.05), "rho": (1.94, 0.01),
     "P_GPa": (38.5, 0.4), "tani": (0.41, 0.04)},
    {"label": "Hz-C2  viab+sens+hazard  (prod.)", "axis": "Hz",
     "composite": (0.485, 0.152), "D_kms": (9.39, 0.04), "rho": (1.91, 0.03),
     "P_GPa": (38.7, 0.6), "tani": (0.27, 0.03)},
    {"label": "Hz-C3  hazard-only",              "axis": "Hz",
     "composite": (0.503, 0.131), "D_kms": (9.32, 0.10), "rho": (1.95, 0.01),
     "P_GPa": (38.8, 0.4), "tani": (0.44, 0.05)},
    {"label": "SA-C3  viab+sens+SA",             "axis": "SA",
     "composite": (0.698, 0.015), "D_kms": (9.34, 0.07), "rho": (1.94, 0.01),
     "P_GPa": (38.7, 0.4), "tani": (0.49, 0.06)},
]

METRICS = [
    {"key": "composite", "letter": "a",
     "label": "Top-1 composite\n(delta, lower = better)",
     "baseline_key": "composite"},
    {"key": "D_kms",     "letter": "b",
     "label": "Top-1 $D$ (km/s)\n(delta vs unguided)",
     "baseline_key": "D_kms"},
    {"key": "tani",      "letter": "c",
     "label": "Max-Tanimoto to LM\n(delta, lower = more novel)",
     "baseline_key": "tani"},
    {"key": "P_GPa",     "letter": "d",
     "label": "Top-1 $P$ (GPa)\n(delta vs unguided)",
     "baseline_key": "P_GPa"},
]

# Axis-keyed marker styling (matches legend)
AXIS_STYLE = {
    "Hz": {"color": "#3a78b8", "marker": "D", "label": "Hazard-axis (Hz-) conditions"},
    "SA": {"color": "#e08442", "marker": "s", "label": "SA-axis (SA-) conditions"},
}

# ---------------------------------------------------------------------------
# Build figure
# ---------------------------------------------------------------------------

N_COND = len(CONDITIONS)
N_MET  = len(METRICS)

# Use a GridSpec with a dedicated left "label gutter" axis so the row
# labels survive bbox_inches="tight" cropping (subplots_adjust gets
# overridden by tight cropping when used with savefig).
fig = plt.figure(figsize=(15.0, 4.6), facecolor="white")
gs = fig.add_gridspec(1, N_MET + 1, width_ratios=[2.0] + [1.0] * N_MET, wspace=0.45)
ax_gutter = fig.add_subplot(gs[0, 0])
axes = [fig.add_subplot(gs[0, i + 1]) for i in range(N_MET)]
# Hide the gutter axis frame; use it only as a text canvas for row labels
ax_gutter.set_xlim(0, 1)
ax_gutter.set_ylim(-0.5, N_COND - 0.5)
ax_gutter.invert_yaxis()
ax_gutter.set_xticks([])
ax_gutter.set_yticks([])
for sp in ax_gutter.spines.values():
    sp.set_visible(False)

LABEL_FONT = {"fontfamily": "DejaVu Serif", "fontsize": 9}
TITLE_FONT = {"fontfamily": "DejaVu Serif", "fontsize": 9.5, "fontweight": "bold"}
TICK_FONT  = {"fontfamily": "DejaVu Serif", "fontsize": 8.5}

y_positions = np.arange(N_COND)

# Pre-compute deltas + propagated errors so we can decide axis x-limits with margin
all_deltas = {met["key"]: [] for met in METRICS}
for met in METRICS:
    bval, bstd = BASELINE[met["baseline_key"]]
    for cond in CONDITIONS:
        cval, cstd = cond[met["key"]]
        all_deltas[met["key"]].append((cval - bval, np.sqrt(bstd**2 + cstd**2)))

for col_idx, (ax, met) in enumerate(zip(axes, METRICS)):
    ax.set_facecolor("white")
    ax.axvline(0, color="black", linewidth=0.9, linestyle="--", zorder=2)

    deltas = all_deltas[met["key"]]
    abs_max = max(abs(d) + e for d, e in deltas) * 1.7  # extra room for value labels
    ax.set_xlim(-abs_max, abs_max)

    for row_idx, cond in enumerate(CONDITIONS):
        delta, err_total = deltas[row_idx]
        style = AXIS_STYLE[cond["axis"]]

        y = y_positions[row_idx]
        ax.errorbar(
            delta, y,
            xerr=err_total,
            fmt=style["marker"],
            color=style["color"],
            ecolor=style["color"],
            markersize=7,
            markeredgecolor="black",
            markeredgewidth=0.5,
            capsize=3.5,
            capthick=1.0,
            linewidth=1.0,
            zorder=3,
        )

        # Value label, placed OUTSIDE the error-bar whisker with a generous
        # margin to avoid the cap/marker visual envelope
        margin = abs_max * 0.09
        if delta >= 0:
            tx = delta + err_total + margin
            ha = "left"
        else:
            tx = delta - err_total - margin
            ha = "right"
        ax.text(
            tx, y, f"{delta:+.3f}",
            va="center", ha=ha,
            fontsize=7.5, fontfamily="DejaVu Serif",
            color="#222222", zorder=4,
        )

    ax.set_title(f"({met['letter']}) {met['label']}", **TITLE_FONT, pad=6, loc="left")
    ax.set_yticks(y_positions)
    ax.tick_params(axis="x", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(col_idx == 0)
    ax.grid(axis="x", color="#dddddd", linewidth=0.6, zorder=0)

    ax.set_yticklabels([])

# Invert all panels in lock-step
for ax in axes:
    ax.invert_yaxis()

# Render row labels in the dedicated gutter axis so bbox_inches="tight"
# cannot crop them off
for row_idx, cond in enumerate(CONDITIONS):
    style = AXIS_STYLE[cond["axis"]]
    ax_gutter.text(
        0.98, row_idx, cond["label"],
        ha="right", va="center",
        fontsize=8.8, fontfamily="DejaVu Serif",
        color=style["color"],
        fontweight="bold" if "(prod.)" in cond["label"] else "normal",
    )

# Legend: by axis only (matches marker colour + shape encoding)
hz_handle = mpatches.Patch(color=AXIS_STYLE["Hz"]["color"], label=AXIS_STYLE["Hz"]["label"])
sa_handle = mpatches.Patch(color=AXIS_STYLE["SA"]["color"], label=AXIS_STYLE["SA"]["label"])
fig.legend(
    handles=[hz_handle, sa_handle],
    loc="lower center",
    ncol=2,
    fontsize=8.5,
    frameon=False,
    bbox_to_anchor=(0.5, -0.04),
    prop={"family": "DejaVu Serif", "size": 8.5},
)

fig.text(
    0.5, -0.10,
    "Unguided baseline (Hz-C0 = SA-C0, 6 seeds): composite 0.451 ± 0.126   "
    "$D$ 9.44 ± 0.07 km/s   max-Tani 0.61 ± 0.10   $P$ 39.7 ± 0.6 GPa",
    ha="center", va="top",
    fontsize=7.5, fontfamily="DejaVu Serif", color="#444444",
)

plt.subplots_adjust(left=0.02, right=0.99, top=0.88, bottom=0.20)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "paper", "figs")
OUT_DIR = os.path.abspath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

png_path = os.path.join(OUT_DIR, "fig_forest_ablation.png")
svg_path = os.path.join(OUT_DIR, "fig_forest_ablation.svg")

fig.savefig(png_path, dpi=180, bbox_inches="tight", facecolor="white")
fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"Saved PNG: {png_path}")
print(f"Saved SVG: {svg_path}")
