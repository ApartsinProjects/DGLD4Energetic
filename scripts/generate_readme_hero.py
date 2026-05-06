"""
Generate the README hero banner for DGLD4Energetic via Gemini.

One-off script. Output: figures/readme_hero.png at 16:9, ~2K.
"""
from __future__ import annotations

import json
from pathlib import Path

from google import genai
from google.genai import types


PROMPT = """Wide cinematic 16:9 hero banner for a scientific paper repository.
Subject: domain-gated latent diffusion for molecular generation. The
composition flows left to right.

LEFT THIRD: a soft cloud of small subtly glowing dots and tiny scattered
particles, distributed like a Gaussian point cloud in 2D latent space. Cool
muted blue tones. The points should feel like a denoising starting state,
never exploding or chaotic. Faint horizontal grid lines, very subtle, like a
scientific scatter-plot background.

CENTER THIRD: a smooth horizontal gradient flow connecting the dot cloud on
the left to a coherent molecular drawing on the right. The flow feels like a
denoising trajectory: dots gradually align, condense, and coalesce. Slight
diagonal motion-streaks in the same blue-grey palette. Negative space is OK.

RIGHT THIRD: a single clean black-ink chemistry-textbook line drawing of
**3,4,5-trinitro-1,2-isoxazole**, drawn with the following EXACT structural
rules — read carefully:

- The ring is a FIVE-membered aromatic ring with EXACTLY these five atoms in
  order: oxygen (O), nitrogen (N), carbon (C), carbon (C), carbon (C). Ring
  positions 1=O, 2=N, 3=C, 4=C, 5=C.
- The ring is fully aromatic with alternating double bonds; draw with two
  double bonds visible inside the ring (between N=C at positions 2-3 and
  between C=C at positions 4-5; or equivalent Kekule form).
- DO NOT draw any C=O carbonyl group anywhere. There is NO oxazolone, NO
  furanone, NO ketone in this molecule.
- DO NOT draw a hydrogen atom on the ring nitrogen. The nitrogen at position
  2 is sp2 aromatic with one lone pair; no N-H bond.
- Three nitro groups (-NO2) attached to the THREE ring carbon atoms (C3, C4,
  C5). Each nitro group: a nitrogen bonded to two oxygen atoms, drawn
  explicitly as N(=O)(=O) or with the standard charge-separated notation
  (N+=O ; N-O-). Three NO2 groups total. NOT four. NOT two.
- Draw the molecule cleanly, not stylized — standard chemistry-textbook line
  diagram style, dark navy ink, on near-white background.

The molecule sits inside a faint green-tinted rectangular highlight (very
pale sage), suggesting it's the converged endpoint of the diffusion process.
A few additional faint scatter dots near it.

OVERALL PALETTE: muted, professional, journal-cover-grade. Background is
warm off-white. No saturated reds, no fire/explosion imagery, no neon, no
sci-fi tropes. The mood is calm scientific precision.

NO TEXT, NO LABELS, NO LETTERS, NO NUMBERS in the image. The README provides
the title separately.

STYLE: clean modern infographic / journal cover art. Think Nature Machine
Intelligence cover or a Distill.pub explainer header. Minimal, lots of
negative space, vector-friendly aesthetic but raster-rendered. High contrast
between the dark molecule and the off-white background.

NEGATIVE SPACE: keep the top and bottom 15% of the image relatively quiet
(low detail, just the gradient flow continuing) so the README headline
placed above and any caption placed below have a clean canvas.

CRITICAL: The molecule is the focal point of the right third. Get it
chemically correct. Three nitro groups, five-membered ring with O-N-C-C-C
heteroatom sequence, no carbonyl, no extra substituents. If you are tempted
to add a fourth NO2 or a C=O group, RESIST.
"""


def main() -> None:
    cfg_path = Path.home() / ".gemini-imagegen.json"
    cfg = json.loads(cfg_path.read_text())
    client = genai.Client(api_key=cfg["api_key"])

    out_path = Path(r"E:\Projects\DGLD4Energetic-public\figures\readme_hero.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Generating hero banner via gemini-3-pro-image-preview at 16:9 / 2K...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=PROMPT,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
        ),
    )

    saved = False
    for part in response.parts:
        if part.inline_data:
            part.as_image().save(out_path)
            saved = True
            print(f"  saved -> {out_path}")
            break

    if not saved:
        print("  ERROR: no image returned")
        for part in response.parts:
            if hasattr(part, "text") and part.text:
                print(f"  text: {part.text[:300]}")


if __name__ == "__main__":
    main()
