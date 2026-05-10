"""ED Fig. 8 - Merged top-100 source-pool provenance.

Brought over from `EnergeticDiffusion2/docs/paper/make_figures.py:fig_merged_provenance()`.
Reads `data/experiments/final_merged_topN.md` (column 13 = source pool).

The raw source identifiers in the markdown ("phaseAonly", "unguided80k",
"guided40k", "sa015_pool20k") are mapped here to readable labels before
plotting. This bakes into the source the same correction that
scripts/patch_ed_labels.py applies post-hoc.
"""
from __future__ import annotations
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(r"E:\Projects\DGLD4Energetic-public")
OUT_DIR = ROOT / "paper" / "figs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SRC_MD  = ROOT / "data" / "experiments" / "final_merged_topN.md"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 130,
})

# Map raw source-pool identifiers -> reader-friendly labels.
LABEL_MAP = {
    "phaseAonly":     "Phase-A only",
    "unguided80k":    "Unguided 80k",
    "guided40k":      "Guided 40k",
    "sa015_pool20k":  "SA-0.15 pool 20k",
}


def main():
    if not SRC_MD.exists():
        raise FileNotFoundError(SRC_MD)

    src_count: dict[str, int] = {}
    for line in SRC_MD.read_text(encoding="utf-8").split("\n")[5:]:
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 14:
            src = cells[13]
            for s in src.split(","):
                s = s.strip()
                if s:
                    src_count[s] = src_count.get(s, 0) + 1

    items = sorted(src_count.items(), key=lambda x: -x[1])
    if not items:
        raise RuntimeError("No source-pool counts parsed from markdown")

    # Apply pretty-label mapping; unknown codes pass through unchanged so
    # any new pool name added later is at least visible.
    names  = [LABEL_MAP.get(k, k) for k, _ in items]
    counts = [c for _, c in items]

    fig, ax = plt.subplots(figsize=(7, 3.4))
    colors = ["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e"][:len(names)]
    ax.bar(names, counts, color=colors, edgecolor="black", linewidth=0.4)
    for i, c in enumerate(counts):
        ax.text(i, c + 1, str(c), ha="center", fontsize=10)
    ax.set_ylabel("# of merged top-100 from this source")
    ax.set_title("Merged top-100 paper-ready set by source pool")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()

    base = OUT_DIR / "fig9_merged_provenance"
    fig.savefig(str(base) + ".svg")
    fig.savefig(str(base) + ".png", dpi=300)
    plt.close(fig)
    print(f"Saved: {base}.svg + .png")


if __name__ == "__main__":
    main()
