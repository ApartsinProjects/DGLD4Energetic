# Scientific Reports submission — DGLD4Energetic

Target: **Scientific Reports** (Springer Nature / Nature Portfolio), Collection
**"Generative Modeling for Chemistry Discovery."**

- Call page: https://communities.springernature.com/posts/call-for-papers-generative-modeling-for-chemistry-discovery-collection
- Collection (login-gated): https://www.nature.com/collections/acbdjacihj
- Official author instructions (login-gated): https://www.nature.com/srep/author-instructions/submission-guidelines

> Caveat: nature.com/srep pages sit behind a login redirect, so the numbers
> below marked **[VERIFY]** were corroborated from Springer Nature policy pages
> and third-party formatting summaries, not read live. Confirm each on the
> logged-in author-instructions page before submitting. Several widely-quoted
> "limits" (4,500-word main text, 8 display items) appear to be borrowed from
> *Nature Communications*; **Scientific Reports historically imposes no main-text
> length or display-item cap** — treat those as soft/aspirational, not hard.

## Collection specifics

| Item | Value | Source |
|---|---|---|
| Journal | Scientific Reports | call page |
| Collection name to select at submission | "Generative Modeling for Chemistry Discovery" | call page |
| Article types | **Original research only** (Sci Rep publishes no Reviews) | call page |
| Deadline | **21 October 2026** | call page |
| Guest Editors | R. H. French (Case Western); J. Guevara-Pulido (El Bosque); C. Mahanty (GITAM); Q. D. Tran (Case Western) | call page |
| Scope | "algorithmic innovations, integration with quantum chemical simulations and experimental workflows, and applications to drug design, catalysis, energy storage, and advanced materials" — VAEs, GANs, RL, **diffusion models** on molecular graphs | call page |

Scope fit: DGLD is domain-gated latent **diffusion** for energetic-materials
(advanced-materials / energy) discovery with **first-principles (DFT) validation**
— squarely in "diffusion models" + "integration with quantum chemical
simulations" + "advanced materials." Strong fit.

## Manuscript requirements (Scientific Reports)

- **Title**: < 20 words, no abbreviations. [VERIFY]
- **Abstract**: single **unstructured** paragraph, **≤ 200 words**, no references, no headings. [VERIFY — 200 is the standard Sci Rep number]
- **Section order (Nature Portfolio style)**:
  Title → Abstract → Introduction → Results → Discussion → **Methods (AFTER Discussion)** → References → Acknowledgements → Author contributions → Competing interests → **Data availability** (+ **Code availability**) → Figure legends → Tables.
  - Results and Discussion may be separate or combined; a standalone
    "Conclusions" is optional (Nature style folds it into Discussion).
  - **This differs from the MDPI Molecules version**, which used
    Intro → Results → Discussion → Materials and Methods → **Conclusions**.
- **Main text length**: no hard limit at Scientific Reports. [VERIFY] (Third-party "4,500 words" is not a Sci Rep rule.)
- **Display items**: no strict cap. [VERIFY] (Third-party "≤8" looks borrowed from Nature Comms.)
- **References**: **Nature superscript-numbered** style, sentence-case titles,
  ISO4 journal abbreviations, all authors if ≤5 else first 5 + "et al.", DOIs
  encouraged. LaTeX: `sn-nature.bst`. Soft cap ~60. [VERIFY]
- **Initial submission format is flexible** (Nature Portfolio): a single readable
  PDF (text + figures inline) is fine; strict formatting and separate hi-res
  figures are only needed at revision/acceptance.
- **Figures** (for revision): TIFF/EPS/PDF/JPEG/PNG, RGB; ≥300 dpi halftone,
  ≥600 dpi line art; single col ≤ 88 mm, double ≤ 180 mm; panel labels lowercase
  bold (a, b, c). [VERIFY]
- **Data availability statement**: mandatory, before References; must say where
  data are (not "on request"). Our Zenodo concept DOI `10.5281/zenodo.19821952`
  satisfies this.
- **Code availability statement**: required (code is central here); public repo
  — GitHub `ApartsinProjects/DGLD4Energetic` + Zenodo.
- **Peer review**: single-blind (author identities visible to reviewers). No
  anonymisation needed.
- **Ethics/back-matter**: Competing interests + Author contributions (CRediT ok)
  required.

## Templates

- **LaTeX (official)**: `templates/sn-article-template/` — Springer Nature
  authoring template (Dec 2024). Use `\documentclass[sn-nature]{sn-jnl}` for the
  Nature superscript-numbered reference style. Key files: `sn-jnl.cls`,
  `sn-article.tex` (sample), `bst/sn-nature.bst`, `user-manual.pdf`.
  Download source: https://www.springernature.com/gp/authors/campaigns/latex-author-support
- **MS Word**: **Nature Portfolio provides NO mandatory Word template.** Word is
  accepted/preferred, but formatting follows the guidelines above rather than a
  fixed `.dotx`. Options: (a) generate a Sci-Reports-styled `.docx` from our
  `html2doc` pipeline (as we did for MDPI), or (b) a third-party shell
  (SciSpace / AJE) — not official. See note below.

## Open access / fees

- Fully open access, CC BY 4.0. APC ~**£2,290 / US$2,850 / €2,490** + tax. [VERIFY on https://www.nature.com/srep/open-access]
- Waivers: Research4Life country waivers; many institutional Transformative
  Agreements cover the APC (check Afeka / HIT eligibility).

## What changes from the MDPI Molecules version

1. **Move Methods to AFTER Discussion** (Nature order), drop the standalone
   "Materials and Methods" heading in favour of "Methods"; fold Conclusions into
   Discussion (or keep a short one).
2. **Abstract → ≤200 words, unstructured** (the NMI 134-word abstract is close;
   the Molecules ~205-word one needs trimming to ≤200 and de-structuring).
3. **References → Nature superscript style** (currently numbered `[n]`).
4. Add explicit **Code availability** statement (separate from Data availability).
5. Title < 20 words (current title length to check).
6. No Conclusions-as-separate-section requirement; no MDPI keywords block.

## Submission steps

1. Prepare single combined PDF (text + inline figures) — flexible format ok.
2. Go to the Scientific Reports submission portal ("Submit manuscript").
3. In the questionnaire, **select the Collection "Generative Modeling for
   Chemistry Discovery."** [confirm exact control on the login-gated how-to page]
4. Provide Data + Code availability (Zenodo `10.5281/zenodo.19821952`, GitHub repo).
5. Suggest reviewers if prompted; single-blind (no anonymisation).
6. Deadline 21 Oct 2026; budget ~US$2,850 APC or apply TA/waiver.
