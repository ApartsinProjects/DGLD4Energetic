# Scientific Reports submission — DGLD4Energetic

Target: **Scientific Reports** (Springer Nature / Nature Portfolio), Collection
**"Generative Modeling for Chemistry Discovery."**

- Call page: https://communities.springernature.com/posts/call-for-papers-generative-modeling-for-chemistry-discovery-collection
- Collection: https://www.nature.com/collections/acbdjacihj
- Official author instructions (read live 2026-08, via browser): https://www.nature.com/srep/author-instructions/submission-guidelines

All values below are from the **official guidelines page read directly** unless
marked otherwise. A Collection uses the **standard journal guidelines** — there
is no chemistry-specific or collection-specific template.

## Collection specifics

| Item | Value |
|---|---|
| Journal | Scientific Reports (open access, CC BY 4.0) |
| Collection to select at submission | "Generative Modeling for Chemistry Discovery" |
| Article types | **Original research only** (Article or Registered Report; no Reviews) |
| Deadline | **21 October 2026** |
| Guest Editors | R. H. French (Case Western); J. Guevara-Pulido (El Bosque); C. Mahanty (GITAM); Q. D. Tran (Case Western) |
| Scope | algorithmic innovations, integration with quantum-chemical simulation + experimental workflows; VAEs, GANs, RL, **diffusion**; drug design, catalysis, energy storage, advanced materials |

Fit: domain-gated latent **diffusion** for energetic-materials (advanced-
materials / energy) discovery with **first-principles DFT** validation. Strong.

## Format of articles (authoritative)

Scientific Reports does **not impose strict** word/page limits, but **strongly
recommends**:

| Limit | Value | Nature of limit |
|---|---|---|
| Typeset pages | ideally ≤ 11 | recommendation |
| **Main text** | ≤ **4,500 words** (excl. Abstract, Methods, References, figure legends) | recommendation |
| **Title** | ≤ **20 words**, one scientifically accurate sentence, no puns/idioms | recommendation |
| **Abstract** | ≤ **200 words**, **unstructured** (no subheadings), **no references** | recommendation |
| **Display items** | **limited to 8** (figures and/or tables combined) | **stated as a limit**; scale to word count (≤2,000-word article → ≤4 items) |
| **References** | ≤ **60** (not strictly enforced) | soft |
| Figure legends | ≤ 350 words each | limit |
| Tables | ≤ one page each | limit |
| Keywords | up to **6** | limit |

(Mandatory-vs-recommended: the page points to a "submission checklist" for the
definitive mandatory list — check it when logged in. No graphical abstract.
No footnotes.)

## Required structure (authoritative)

Main body has "no specific requirements," but the recommended (and expected)
order is:

1. **Title page** — author affiliations + contact; corresponding author marked `*`
2. **Abstract** (≤200 w, unstructured)
3. **Keywords** (≤6)
4. **Introduction**
5. **Results** — *with* subheadings
6. **Discussion** — *without* subheadings
7. **Methods** — **after** Discussion (no word limit on Methods)

then, in order:

8. **References** (Nature style, square brackets, ≤60)
9. **Acknowledgements** (optional; brief; grant numbers ok; no thanks to referees)
10. **Author contributions** (mandatory)
11. **Data availability statement** (mandatory; before References conceptually — the page lists it here in back-matter; place at end of main text before References)
12. **Additional Information** including **Competing Interests** statement (mandatory, per author)
13. **Figure legends** (after references, numerical order)
14. **Tables** (editable Word/TeX, not images)

> **Differences from the MDPI Molecules version**: Methods stays after
> Discussion (same), but drop the standalone **"Conclusions"** section (Nature
> folds it into Discussion), Discussion carries **no subheadings**, references
> switch to **Nature square-bracket** style, and **all appendices move to the
> SI** (see below). Include page/line numbers (recommended, not auto-added).

## Appendices & Supplementary Information (authoritative — answers "separate file?")

> "We do **not** support inclusion of any additional information or **appendices
> in the main body** of the paper; **all supplementary information should be
> included in the dedicated Supplementary Information files.**"

- **No appendices in the main manuscript.** Our Appendices A–F move wholesale
  into **one composite SI file** (preferably **PDF**, ≤ 50 MB).
- SI items numbered **separately** from the main article: `Supplementary Table S1`,
  `Supplementary Fig. S1`, `Supplementary Note`, `Supplementary Methods`, etc.
- Every in-text mention must include the word **"Supplementary"** (abbreviate
  "Figure"→"Fig." mid-sentence). Do not refer to individual panels of SI figures.
- SI is submitted **with** the manuscript (goes to reviewers), is **not**
  copy-edited/typeset — present it cleanly at submission.
- This matches our existing **main + SI split**; the SI = current Appendices A–F.

## Files at submission (authoritative)

- **First submission**: may combine manuscript text + figures into a **single
  file ≤ 3 MB** (figures inline or grouped at end). **Word preferred**; LaTeX or
  PDF accepted. → watch the 3 MB cap; our figure-heavy PDF may need compression.
- **Supplementary**: one separate composite file, preferably PDF.
- **Cover letter** (required): corresponding-author contact; why the work suits
  Scientific Reports; suggested reviewers; referees to exclude; whether there
  were prior discussions with a Sci Rep Editorial Board Member.
- **Revised** manuscripts: single Word/LaTeX file (no PDF), single-column,
  unjustified, page-numbered, Computer Modern font, figures as separate files.

## References (authoritative — Nature style)

- Sequential, numerical, **within square brackets** `[1]`; one publication per
  number. (Our current `[n]` numbering already matches the bracket style.)
- List format: authors last-name-first (initials with full stops); **all authors
  unless ≥ 6, then first author + "et al."**; article/dataset titles in Roman,
  sentence case, ending in a full stop; journal names italic + abbreviated;
  **volume bold**; full page range or article number; year in parentheses.
- LaTeX: `\documentclass[sn-nature]{sn-jnl}` + `bst/sn-nature.bst`.

## Chemistry-specific guidance (authoritative) — how it applies to us

The journal has a chemistry section, but most of it targets **experimental
synthesis** papers and **does not apply** to our computational/generative work:

- **New-compound characterisation** (¹H/¹³C NMR, HRMS, melting point, purity /
  elemental analysis): required only for **synthesised** new compounds. **We
  synthesise nothing** — our leads are *computationally predicted* candidates, so
  NMR/HRMS/mp/purity are **N/A**. State clearly that no compounds were made.
- **Nomenclature**: use **systematic IUPAC** names (we already do, e.g.
  "3,4,5-trinitro-1,2-isoxazole"); define non-standard abbreviations at first use.
- **Chemical structures**: no "schemes" — present reaction/structure graphics as
  **figures**; structures may be uncaptioned but must carry a name / defined
  abbreviation / **bold Arabic numeral**. For publication: ChemDraw → 300 dpi RGB
  TIFF.
- **Statistics** (applies to our correlations): report test name, **n**,
  one/two-tailed, and the **actual P value** (we already give Pearson r,
  p = 4×10⁻²⁷, n = 575); pair "significant" with a P value.

## AI / LLM policy (authoritative)

LLMs cannot be authors; **use of an LLM must be documented in the Methods**.
Decision needed: whether/how to disclose AI assistance used in manuscript
preparation. (Model/tool assistance in *writing/editing* is disclosed; the
generative *research* pipeline is the paper's own method, described normally.)

## Figures (publication specs)

- Line art/graphs/schematics: **vector** (EPS/AI). Photos/bitmaps: TIFF/JPG/PSD,
  RGB or CMYK. Sans-serif (Helvetica) lettering, consistent size; lower-case
  panel labels **a, b, c** (bold); SI units with a space; thousands with commas;
  scale bars on the bar; white background; no 3-D histograms; thinnest line ≥ 1 pt.
- Each figure a separate file at revision; multi-panel arranged as one file.

## Peer review / OA / fees

- **Single-blind** review (no anonymisation needed).
- Open access, **CC BY 4.0**. APC ≈ **£2,290 / US$2,850 / €2,490** + tax
  (confirm on https://www.nature.com/srep/open-access). Waivers: Research4Life
  country waivers; institutional Transformative Agreements (check Afeka / HIT).

## Best starting base = the NMI-compliant version, not the long-form

The archived **NMI version** (`paper/nmi_archive/NMIPaper.html` + SI) already
fits Sci Rep almost exactly and is a far better base than the long-form:

| Metric | Sci Rep | NMI version | Long-form Molecules |
|---|---|---|---|
| Abstract | ≤ 200 w | 134 w ✓ | ~205 w (trim) |
| Main text | ≤ 4,500 w | ~2,462 w ✓ (room to expand) | ~14,000 w ✗ |
| Display items (main) | ≤ 8 | 5 fig + 1 table = 6 ✓ | 24 fig + 9 tables ✗ |
| Methods after Discussion | yes | yes ✓ | yes |
| Appendices → SI | required | already split ✓ | already split |
| References | ≤ 60 | 50 ✓ | 71 |

Plan: adapt the NMI main text → Sci Rep (drop Conclusions into Discussion,
remove Discussion subheadings, keywords ≤6, square-bracket Nature refs, add Code
availability); move full Appendices A–F into the single SI file.

## Submission checklist

1. Original research; ≤200-w unstructured abstract; title ≤20 w; ≤6 keywords.
2. Intro → Results(subheads) → Discussion(no subheads) → Methods; ≤4,500 w main.
3. ≤8 display items in main; everything else (Appendices A–F) → one SI PDF.
4. Nature square-bracket references, ≤60.
5. Data availability + Code availability (Zenodo `10.5281/zenodo.19821952`,
   GitHub `ApartsinProjects/DGLD4Energetic`).
6. Author contributions + Competing interests (per author).
7. State no compounds were synthesised (characterisation N/A); IUPAC names.
8. Cover letter (fit + suggested reviewers); select the Collection in the portal.
9. First submission ≤3 MB combined; SI separate PDF. Deadline 21 Oct 2026.
