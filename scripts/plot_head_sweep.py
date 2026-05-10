"""ED Fig. 4 - Per-head guidance scale top-1 sweep.

Reproduces `paper/figs/fig8_head_sweep.png`. The original generator
script that produced this PNG was not present in EnergeticDiffusion2;
this is a fresh implementation that parses the per-condition run logs
in `data/logs/sweep_head_*.log` (top-5 composite v2 table) and reads
the [1] (top-1) row for each condition.

Layout matches the existing PNG: two bar panels side-by-side
(left = composite, right = detonation velocity), with a horizontal
HMX-class reference line at D=9.0 km/s.
"""
from __future__ import annotations
import os
import re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT    = Path(r"E:\Projects\DGLD4Energetic-public")
LOG_DIR = ROOT / "data" / "logs"
OUT_DIR = ROOT / "paper" / "figs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# (log basename, short label, bar color)
CONDITIONS = [
    ("ungUNG",  "ung",  "#888888"),
    ("default", "def",  "#1f77b4"),
    ("low",     "low",  "#9467bd"),
    ("viabhi",  "v↑",  "#d62728"),  # v↑
    ("senshi",  "s↑",  "#ff7f0e"),  # s↑
    ("withSA",  "+SA",  "#2ca02c"),
]

TOP1_RE = re.compile(
    r"\[1\]\s+comp=(?P<comp>[-\d.]+).*?D=(?P<D>[-\d.]+)"
)


def parse_top1(log_path: Path) -> tuple[float, float]:
    """Return (composite, D_km_s) parsed from the 'Top 5 by composite v2' block."""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    # Skip to the 'Top 5 by composite v2' block, then grab the [1] line.
    idx = text.find("Top 5 by composite v2")
    if idx < 0:
        raise RuntimeError(f"no 'Top 5 by composite v2' block in {log_path.name}")
    m = TOP1_RE.search(text, idx)
    if not m:
        raise RuntimeError(f"no [1] row found in {log_path.name}")
    return float(m["comp"]), float(m["D"])


def main():
    rows = []
    for stem, label, color in CONDITIONS:
        log = LOG_DIR / f"sweep_head_{stem}.log"
        if not log.exists():
            raise FileNotFoundError(log)
        comp, D = parse_top1(log)
        rows.append((label, color, comp, D))

    labels = [r[0] for r in rows]
    colors = [r[1] for r in rows]
    comps  = [r[2] for r in rows]
    Ds     = [r[3] for r in rows]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    fig.suptitle("Per-head guidance scale top-1 sweep (pool=2.5k each per denoiser)",
                 fontsize=12.5, y=0.995)

    # Left panel: composite score
    ax = axes[0]
    ax.bar(labels, comps, color=colors, edgecolor="black", linewidth=0.4)
    ax.set_ylabel("top-1 composite score")
    ax.set_title("Composite score per head condition (higher is better)")
    ax.set_ylim(0, max(comps) * 1.15)
    for i, c in enumerate(comps):
        ax.text(i, c + 0.005, f"{c:.2f}", ha="center", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Right panel: detonation velocity with HMX-class reference line
    ax = axes[1]
    ax.bar(labels, Ds, color=colors, edgecolor="black", linewidth=0.4)
    ax.set_ylabel("top-1 detonation velocity D (km/s)")
    ax.set_title("Detonation velocity per head condition")
    ax.set_ylim(0, max(Ds) * 1.10)
    ax.axhline(9.0, color="#bbbbbb", linestyle=":", linewidth=1.2,
               label="HMX-class D=9.0")
    for i, d in enumerate(Ds):
        ax.text(i, d + 0.05, f"{d:.2f}", ha="center", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.85)

    plt.tight_layout(rect=(0, 0, 1, 0.95))
    base = OUT_DIR / "fig8_head_sweep"
    fig.savefig(str(base) + ".svg")
    fig.savefig(str(base) + ".png", dpi=200)
    plt.close(fig)
    print(f"Saved: {base}.svg + .png")


if __name__ == "__main__":
    main()
