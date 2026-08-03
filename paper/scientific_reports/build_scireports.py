#!/usr/bin/env python
"""Build the Scientific Reports (Nature Portfolio) manuscript pair from the
MDPI Molecules sources.

SOURCE OF TRUTH: paper/molecules/molecules_paper.html + molecules_paper_SI.html.
Scientific content is MOVED, never deleted; the only new prose is the declared
set below. build_verify.py audits main+SI as one content universe.

Transforms (Scientific Reports guidelines, nature.com, read 2026-08):
  A. Abstract replaced by a <=200-word trim of the source abstract (declared).
  B. Keywords 11 -> 6.
  C. Related Work 1.1.1-1.1.8 replaced in the MAIN by a 3-paragraph summary
     (declared new prose, citing the same works); the FULL 1.1 text moves to
     the SI as "Supplementary Note: Extended Related Work".
  D. Display items: keep 8 in main (Figs 1,3,5,7,13 -> 1-5; Tables 1,7,9 ->
     1-3); move 19 figures -> Supplementary Figs S5-S23 and 6 tables ->
     Supplementary Tables S30-S35 (appended to the SI, captions relabelled);
     every in-text pointer rewritten.
  E. Discussion: "3.1. Limitations" h3 -> bold run-in; "5. Conclusions" folded
     into Discussion end with bold run-in; its "(Section 5)" self-ref repointed.
  F. "4. Materials and Methods" -> "4. Methods"; NEW final Methods subsection
     "Use of large language models" (journal policy: LLM use documented in
     Methods).
  G. Back-matter: Data Availability (verbatim), NEW Code Availability, Author
     Contributions (verbatim), Competing Interests wording, Funding (verbatim).
     MDPI-only blocks (Supplementary Materials pointer, IRB, Informed Consent)
     dropped. No Acknowledgements (optional; LLM statement lives in Methods).
  H. References renumbered by first appearance, main list restricted to
     main-cited refs (normalize_citations, keep_uncited=False); SI reference
     list augmented with the keys its new content cites, then normalized.
  I. Reference-list entries reformatted APA-ish -> Nature style where the
     pattern matches (authors (year). title. <em>J vol</em>:pp. doi) ->
     (authors title. <em>J</em> <b>vol</b>, pp (year)); unmatched left as-is.
  J. Bare "Table Sn"/"Fig. Sn" mentions prefixed with "Supplementary".
"""
import re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from normalize_citations import normalize

MOL = HERE.parent / "molecules"
src = (MOL / "molecules_paper.html").read_text(encoding="utf-8")
si  = (MOL / "molecules_paper_SI.html").read_text(encoding="utf-8")

OUT_MAIN = HERE / "scireports_paper.html"
OUT_SI   = HERE / "scireports_paper_SI.html"

NB = "&nbsp;"

# --------------------------------------------------------------------------
# 0. section split of the source main
# --------------------------------------------------------------------------
first_h2 = src.index("<h2")
front = src[:first_h2]
chunks = re.split(r'(?=<h2[ >])', src[first_h2:])
def label(chunk):
    m = re.match(r'<h2[^>]*>\s*(.*?)</h2>', chunk, re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ""
sec = {label(c): c for c in chunks if c.strip()}
def need(name):
    if name not in sec:
        raise SystemExit(f"section not found: {name!r}")
    return sec[name]

intro   = need("1. Introduction")
results = need("2. Results")
disc    = need("3. Discussion")
methods = need("4. Materials and Methods")
concl   = need("5. Conclusions")
refs    = need("References")

# --------------------------------------------------------------------------
# A. abstract: <=200-word trim (declared replacement; facts unchanged)
# --------------------------------------------------------------------------
ABSTRACT = (
'<div class="abstract">\n'
'  <p><span class="lab">Abstract:</span> Energetic materials power mining, demolition, propulsion and\n'
'  airbags, yet today&rsquo;s compounds were designed decades ago. A successor must combine high energy\n'
'  release, low sensitivity to accidental initiation and a practical synthesis route, found within an\n'
'  astronomically large molecular space. Generative models are the natural search tool, but their training\n'
'  data is mostly untrustworthy: of ~66,000 molecules with recorded properties, only ~3,000 were measured\n'
'  or computed from first principles. Models trained on all of them imitate the rough estimates and\n'
'  propose molecules that collapse under real physics. We introduce\n'
'  <strong>Domain-Gated Latent Diffusion (DGLD)</strong>, a diffusion model that treats data reliability\n'
'  as an explicit design parameter: labels are sorted into four trust tiers, and only trustworthy ones\n'
'  steer generation, while the unreliable majority still teaches the model what a plausible molecule looks\n'
'  like. Learned controls tune performance, safety and viability independently, and every\n'
'  proposal passes a four-stage screen ending in quantum-chemical (DFT) audit. DGLD proposes 10 molecules\n'
'  unknown to PubChem that survive it. The best, 3,4,5-trinitro-1,2-isoxazole, matches benchmark\n'
'  explosives HMX and PETN on calculated detonation performance, is unlike its training set, and has a\n'
'  four-step synthesis route. Trust gating is chemistry-independent, applying wherever abundant weak data\n'
'  surrounds a reliable core.</p>\n'
'</div>')
aw = len(re.sub(r'<[^>]+>', ' ', ABSTRACT).replace('&nbsp;', ' ')
         .replace('Abstract:', '').split())
assert aw <= 200, f"abstract {aw} words > 200"
front = re.sub(r'<div class="abstract">.*?</div>', lambda m: ABSTRACT, front,
               count=1, flags=re.S)

# --------------------------------------------------------------------------
# B. keywords 11 -> 6
# --------------------------------------------------------------------------
kw_new = ('<p class="keywords"><span class="lab">Keywords:</span> generative models; '
          'latent diffusion; inverse molecular design; energetic materials; '
          'density functional theory; data-driven discovery</p>')
front = re.sub(r'<p class="keywords">.*?</p>', lambda m: kw_new, front,
               count=1, flags=re.S)

# --------------------------------------------------------------------------
# C. Related Work: summary in main, full text -> SI Supplementary Note
# --------------------------------------------------------------------------
m = re.search(r'<h3>1\.1\. Related Work</h3>.*', intro, re.S)  # 1.1 is the last block of the Introduction chunk
assert m, "Related Work block not found"
related_full = m.group(0)

RELATED_SUMMARY = (
'<h3>1.1. Related Work</h3>\n'
'<p>DGLD sits at the intersection of molecular generative modelling, diffusion models with '
'classifier-style guidance, and property prediction for energetic materials; an extended survey is given '
'in the Supplementary Note (Extended Related Work). VAE-based generators learn a continuous latent over '
'string or graph representations and navigate it for property optimisation <a class="cite" href="#ref-gomez2018automatic">[6]</a>'
'<a class="cite" href="#ref-jin2018junction">[7]</a>; we adopt the syntactically robust SELFIES '
'representation <a class="cite" href="#ref-krenn2020selfies">[10]</a> and fine-tune the LIMO MLP-VAE '
'<a class="cite" href="#ref-eckmann2022limo">[11]</a> as the frozen encoder; MolMIM '
'<a class="cite" href="#ref-reidenbach2023molmim">[12]</a> and the RL-based REINVENT'
'&nbsp;4 <a class="cite" href="#ref-olivecrona2017reinvent">[14]</a><a class="cite" href="#ref-loeffler2024reinvent4">[15]</a> '
'are among the comparative no-diffusion baselines (Section&nbsp;4.16). On the graph side, DiGress '
'<a class="cite" href="#ref-vignac2023digress">[21]</a> performs discrete denoising diffusion directly on '
'molecular graphs, achieving exact validity at the cost of re-introducing property conditioning through a '
'separate guidance term. On the generative-prior side, DGLD builds on denoising diffusion '
'probabilistic models <a class="cite" href="#ref-ho2020ddpm">[22]</a> and the score-based/SDE formulation '
'<a class="cite" href="#ref-song2021sde">[24]</a>, transplants the latent-diffusion recipe '
'<a class="cite" href="#ref-rombach2022ldm">[25]</a> from images to molecules, and combines '
'classifier-free guidance <a class="cite" href="#ref-ho2022cfg">[4]</a> with the noise-conditional '
'classifier-guidance regime <a class="cite" href="#ref-dhariwal2021diffusion">[26]</a>, injected through '
'FiLM conditioning <a class="cite" href="#ref-perez2018film">[27]</a>. Unlike 3D pocket-conditioned '
'molecular diffusion (EDM <a class="cite" href="#ref-hoogeboom2022edm">[28]</a>, GeoLDM '
'<a class="cite" href="#ref-xu2023geoldm">[34]</a>), DGLD diffuses a 1D string-derived latent, so '
'conditioning is a function of the molecule&rsquo;s identity rather than of any particular conformer.</p>\n'
'<p>On the property side, the Kamlet&ndash;Jacobs equations <a class="cite" href="#ref-kamlet1968detonation">[1]</a> '
'supply fast closed-form Tier-C detonation labels; 3D-CNN <a class="cite" href="#ref-casey2020prediction">[2]</a> '
'and Uni-Mol <a class="cite" href="#ref-zhou2023unimol">[3]</a> property predictors provide the surrogate '
'scoring family; Politzer&ndash;Murray BDE correlations <a class="cite" href="#ref-politzer2014some">[36]</a> '
'and the sensitivity literature <a class="cite" href="#ref-mathieu2017sensitivity">[37]</a>'
'<a class="cite" href="#ref-nefati1996ann">[43]</a><a class="cite" href="#ref-huang2021applying">[44]</a> '
'ground the h<sub>50</sub> hazard head; thermochemical-equilibrium codes (EXPLO5 '
'<a class="cite" href="#ref-suceska2018explo5">[38]</a>, Cheetah <a class="cite" href="#ref-fried2014cheetah">[39]</a>) '
'remain the absolute-value-grade reference against which our calibrated K-J estimates are scoped; and the '
'Choi et&nbsp;al. review <a class="cite" href="#ref-choi2023prep">[40]</a> codifies the field&rsquo;s '
'challenges. Prior generative work on the energetic high-energy tail is scarce and label-limited '
'<a class="cite" href="#ref-griffiths2020constrained">[46]</a><a class="cite" href="#ref-klapotke2017nitrogen">[45]</a>; '
'the most direct contemporary competitor is a property-conditioned RNN coupled to QM validation '
'<a class="cite" href="#ref-npjcompmat2025">[47]</a>, which differs from DGLD in prior (autoregressive '
'SMILES vs latent diffusion), supervision (single-tier regression vs four-tier trust gating), and '
'validation depth (QM-only vs the four-stage SMARTS&nbsp;&rarr;&nbsp;Pareto&nbsp;&rarr;&nbsp;'
'GFN2-xTB&nbsp;&rarr;&nbsp;DFT funnel).</p>\n'
'<p>Evaluation and validation draw on MOSES/GuacaMol distribution-learning benchmarks '
'<a class="cite" href="#ref-polykovskiy2020moses">[51]</a><a class="cite" href="#ref-brown2019guacamol">[52]</a> '
'and the Fr&eacute;chet ChemNet Distance <a class="cite" href="#ref-preuer2018fcd">[53]</a> (read as a '
'chemistry-class-transfer signal, since ChemNet is trained on drug-like ZINC '
'<a class="cite" href="#ref-sterling2015zinc">[55]</a>+PubChem chemistry); SA '
'<a class="cite" href="#ref-ertl2009sa">[56]</a> and SCScore <a class="cite" href="#ref-coley2018scscore">[57]</a> '
'as synthesisability caps and Tanimoto similarity <a class="cite" href="#ref-rogers1960computer">[58]</a> '
'as the novelty bound; and the external validation stack GFN2-xTB '
'<a class="cite" href="#ref-bannwarth2019gfn2">[59]</a>, PySCF/gpu4pyscf '
'<a class="cite" href="#ref-sun2020pyscf">[60]</a>, AiZynthFinder '
'<a class="cite" href="#ref-genheden2020aizynth">[61]</a>, with functional/basis choices grounded in '
'GMTKN55 <a class="cite" href="#ref-goerigk2017benchmark">[62]</a>.</p>\n')

intro = intro.replace(related_full, RELATED_SUMMARY)

# SI note: demote h3 -> h4 inside the moved text, retitle
note = related_full.replace('<h3>1.1. Related Work</h3>',
                            '<h3 id="sec-si-related">Supplementary Note: Extended Related Work</h3>')
note = re.sub(r'<h3>1\.1\.(\d)&nbsp;', lambda m: f'<h4>N.{m.group(1)}&nbsp;', note)
note = note.replace('</h3>', '</h4>').replace(
    '<h4 id="sec-si-related">', '<h3 id="sec-si-related">', 1)
note = note.replace('Supplementary Note: Extended Related Work</h4>',
                    'Supplementary Note: Extended Related Work</h3>', 1)

# --------------------------------------------------------------------------
# D. display items: keep 8, move the rest to SI
# --------------------------------------------------------------------------
KEEP_FIGS  = {1: 1, 3: 2, 5: 3, 7: 4, 13: 5}
KEEP_TABLES = {1: 1, 7: 2, 9: 3}
MOVE_FIGS  = {2: 5, 4: 6, 6: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 14: 13,
              15: 14, 16: 15, 17: 16, 18: 17, 19: 18, 20: 19, 21: 20, 22: 21,
              23: 22, 24: 23}          # old main fig -> new S number
MOVE_TABLES = {2: 30, 3: 31, 4: 32, 5: 33, 6: 34, 8: 35}   # old -> S number

doc = front + intro + results + disc + methods + concl  # concl folded later; keep for extraction order

def extract_blocks(text, pattern):
    """return list of (span, block) for non-overlapping regex blocks"""
    return [(m.span(), m.group(0)) for m in re.finditer(pattern, text, re.S)]

# figures: <figure>...</figure> whose caption is Figure N.
fig_blocks = {}
for span, block in extract_blocks(doc, r'<figure[^>]*>.*?</figure>'):
    mm = re.search(r'<strong>Figure (\d+)\.</strong>', block)
    if mm:
        fig_blocks[int(mm.group(1))] = block
# tables: <table>...</table> whose caption is Table N.
tab_blocks = {}
for span, block in extract_blocks(doc, r'<table[^>]*>.*?</table>'):
    mm = re.search(r'<strong>Table (\d+)\.</strong>', block)
    if mm:
        tab_blocks[int(mm.group(1))] = block
assert set(fig_blocks) == set(range(1, 25)), sorted(fig_blocks)
assert set(tab_blocks) == set(range(1, 10)), sorted(tab_blocks)

moved_si_parts = []
for n in sorted(MOVE_FIGS):
    b = fig_blocks[n]
    nb = b.replace(f'<strong>Figure {n}.</strong>',
                   f'<strong>Figure S{MOVE_FIGS[n]}.</strong>')
    moved_si_parts.append(nb)
for n in sorted(MOVE_TABLES):
    b = tab_blocks[n]
    nb = b.replace(f'<strong>Table {n}.</strong>',
                   f'<strong>Table S{MOVE_TABLES[n]}.</strong>')
    moved_si_parts.append(nb)

def strip_moved(text):
    for n in MOVE_FIGS:
        text = text.replace(fig_blocks[n], '')
    for n in MOVE_TABLES:
        text = text.replace(tab_blocks[n], '')
    return text

def renumber_kept(text):
    for old, new in KEEP_FIGS.items():
        text = text.replace(f'<strong>Figure {old}.</strong>',
                            f'<strong>Figure ⟦K{new}⟧.</strong>')
    for old, new in KEEP_TABLES.items():
        text = text.replace(f'<strong>Table {old}.</strong>',
                            f'<strong>Table ⟦T{new}⟧.</strong>')
    return text

def retext_refs(text):
    """rewrite in-text Figure/Table references (word forms) via placeholders"""
    # ranges first: "Figures 10 and 11" -> both moved
    def fig_ref(m):
        word, n = m.group(1), int(m.group(2))
        if n in KEEP_FIGS:
            return f'{word}⟦K{KEEP_FIGS[n]}⟧'
        return f'Supplementary Fig.{NB}⟦S{MOVE_FIGS[n]}⟧'
    def tab_ref(m):
        word, n = m.group(1), int(m.group(2))
        if n in KEEP_TABLES:
            return f'{word}⟦T{KEEP_TABLES[n]}⟧'
        return f'Supplementary Table{NB}⟦S{MOVE_TABLES[n]}⟧'
    # plural / range forms first: "Figs 10 and 11", "Figs 13-22", "Figs 15, 16"
    def fig_multi(m):
        nums = [int(x) for x in re.findall(r'\d+', m.group(0))]
        sep = ' and ' if ' and ' in m.group(0) else (
              '&ndash;' if '&ndash;' in m.group(0) or '-' in m.group(0) else ', ')
        if all(n in MOVE_FIGS for n in nums):
            if sep == '&ndash;':   # a range: expand endpoints only
                return (f'Supplementary Figs{NB}S{MOVE_FIGS[nums[0]]}&ndash;'
                        f'S{MOVE_FIGS[nums[-1]]}')
            return 'Supplementary Figs' + NB + sep.join(
                f'S{MOVE_FIGS[n]}' for n in nums)
        if all(n in KEEP_FIGS for n in nums):
            return 'Figs' + NB + sep.join(f'⟦K{KEEP_FIGS[n]}⟧' for n in nums)
        return m.group(0)          # mixed: leave for manual review
    text = re.sub(r'(?<!Supplementary )(?:Figs?\.?|Figures)(?:&nbsp;| )\d+'
                  r'(?:\s*(?:and|&ndash;|-|,)\s*\d+)+', fig_multi, text)
    def tab_multi(m):
        nums = [int(x) for x in re.findall(r'\d+', m.group(0))]
        sep = ' and ' if ' and ' in m.group(0) else (
              '&ndash;' if '&ndash;' in m.group(0) else ', ')
        if all(n in MOVE_TABLES for n in nums):
            return 'Supplementary Tables' + NB + sep.join(
                f'S{MOVE_TABLES[n]}' for n in nums)
        if all(n in KEEP_TABLES for n in nums):
            return 'Tables' + NB + sep.join(f'⟦T{KEEP_TABLES[n]}⟧' for n in nums)
        return m.group(0)          # mixed: leave for manual review
    text = re.sub(r'(?<!Supplementary )Tables?(?:&nbsp;| )\d+'
                  r'(?:\s*(?:and|&ndash;|,)\s*\d+)+', tab_multi, text)
    text = re.sub(r'(Figures?(?:&nbsp;| )|Fig\.(?:&nbsp;| ))(\d+)\b', fig_ref, text)
    text = re.sub(r'(Tables?(?:&nbsp;| ))(\d+)\b', tab_ref, text)
    return text

def resolve_placeholders(text):
    text = re.sub(r'(Figures?(?:&nbsp;| )|Fig\.(?:&nbsp;| ))⟦K(\d+)⟧', lambda m: m.group(1) + m.group(2), text)
    text = re.sub(r'⟦K(\d+)⟧', lambda m: m.group(1), text)
    text = re.sub(r'(Tables?(?:&nbsp;| ))⟦T(\d+)⟧', lambda m: m.group(1) + m.group(2), text)
    text = re.sub(r'⟦T(\d+)⟧', lambda m: m.group(1), text)
    text = re.sub(r'⟦S(\d+)⟧', lambda m: 'S' + m.group(1), text)
    return text

# --------------------------------------------------------------------------
# E. Discussion transforms
# --------------------------------------------------------------------------
disc, n = re.subn(r'<h3[^>]*>\s*3\.1\.?\s*Limitations\s*</h3>\s*<p>',
                  '<p><strong>Limitations.</strong> ', disc, count=1)
assert n == 1
concl_body = re.sub(r'^<h2[^>]*>\s*5\.\s*Conclusions\s*</h2>\s*', '', concl, count=1)
concl_body = concl_body.replace('code bundle on Zenodo (Section&nbsp;5)',
                                'code bundle on Zenodo (see the Data Availability statement)')
concl_body = re.sub(r'^\s*<p>', '<p><strong>Conclusions.</strong> ', concl_body, count=1)
disc = disc.rstrip() + "\n\n" + concl_body.strip() + "\n"

# --------------------------------------------------------------------------
# F. Methods rename + LLM subsection
# --------------------------------------------------------------------------
methods = re.sub(r'(<h2[^>]*>\s*4\.\s*)Materials and Methods(\s*</h2>)',
                 r'\1Methods\2', methods, count=1)
LLM_METHODS = (
'<h3>4.17&nbsp;Use of large language models</h3>\n'
'<p>A large language model (Anthropic Claude) was used to assist with source-code development and '
'manuscript copy-editing. All study design, analyses, results, and conclusions are the '
'authors&rsquo; own, and the authors take full responsibility for the content of the manuscript.</p>\n')
methods = methods.rstrip() + "\n\n" + LLM_METHODS

# --------------------------------------------------------------------------
# G. back-matter
# --------------------------------------------------------------------------
data_avail = need("Data Availability Statement")
# The Zenodo package is the single archive of record; drop the GitHub mirror sentence.
data_avail = re.sub(
    r'\s*The code is additionally\s*mirrored at\s*'
    r'<a href="https://github\.com/[^"]+">[^<]+</a>\.', '', data_avail)
code_avail = (
'<h2>Code Availability</h2>\n'
'<p>All custom code central to this study is publicly available. The full '
'pipeline (LIMO fine-tuning, denoiser and score-model training, the sampling '
'and four-stage validation funnel, and the figure-generation scripts) is '
'released under Apache-2.0 inside the archived Zenodo package '
'(<a href="https://doi.org/10.5281/zenodo.19821952">10.5281/zenodo.19821952</a>), '
'together with the trained checkpoints and datasets described in the Data Availability '
'statement.</p>\n')
author_contrib = need("Author Contributions")
competing = ('<h2>Competing Interests</h2>\n'
             '<p>The authors declare no competing interests.</p>\n')
funding = need("Funding")
backmatter = (data_avail.rstrip() + "\n\n" + code_avail + "\n"
              + author_contrib.rstrip() + "\n\n" + competing + "\n"
              + funding.rstrip() + "\n")

# --------------------------------------------------------------------------
# assemble main, apply display-item machinery
# --------------------------------------------------------------------------
main = (front.rstrip() + "\n\n" + intro.rstrip() + "\n\n" + results.rstrip()
        + "\n\n" + disc.rstrip() + "\n\n" + methods.rstrip() + "\n\n"
        + backmatter.rstrip() + "\n\n" + refs.rstrip() + "\n")
main = strip_moved(main)
main = renumber_kept(main)
# mixed kept/moved range: source Fig 13 stays (-> main Fig 5), 14-22 migrate.
# Rewritten explicitly so the pipeline-map sentence cites main Figure 5.
main = main.replace(
    'DGLD is a four-stage pipeline (Figs&nbsp;13&ndash;22):',
    'DGLD is a four-stage pipeline (Figure' + NB + '⟦K5⟧; per-stage panels in '
    'Supplementary Figs' + NB + 'S13&ndash;S21):')
# ensure the four-tier table is cited in the main body at its first discussion
main = main.replace(
    'Each label per row carries one of the following tiers:',
    'Each label per row carries one of the following tiers (Table' + NB + '⟦T3⟧):', 1)
# Scope statement closing the Introduction (declared addition). Placed AFTER the
# contribution list, not at the head: the Introduction opens on the problem and
# closes on positioning.
COLLECTION_FRAME = (
'<p>Taken together, these contributions sit on three axes of generative modelling for chemistry '
'discovery: how a diffusion prior should consume unevenly reliable property labels, how the generative '
'loop couples to quantum-chemical simulation as a validation stage rather than a post-hoc check, and '
'what either buys on an advanced-materials target whose design objectives (energy release, stability, '
'and synthesisability) are in direct conflict.</p>\n')
main = main.replace('<h3>1.1. Related Work</h3>',
                    COLLECTION_FRAME + '<h3>1.1. Related Work</h3>', 1)

# --- Tier-1 editorial revisions (declared) --------------------------------
# T1.1 civilian-first framing, consistent with the abstract
main = main.replace(
    'Energetic-materials performance gains translate directly into reduced propellant mass, '
    'smaller warheads, and more efficient civilian gas-generators, yet',
    'Energetic-materials performance gains translate directly into reduced propellant mass for '
    'launch and mining applications, safer and more efficient automotive gas-generators, and '
    'lower-mass payloads across the field, yet')

# T1.2 own the pre-registered target miss where the targets are stated
main = main.replace(
    'validated through the four-stage chain SMARTS \\(\\to\\) Pareto \\(\\to\\) xTB \\(\\to\\) DFT '
    'documented in Section' + NB + '4.13',
    'validated through the four-stage chain SMARTS \\(\\to\\) Pareto \\(\\to\\) xTB \\(\\to\\) DFT '
    'documented in Section' + NB + '4.13. The performance targets are assessed by anchor-relative '
    'ranking on a common calibrated Kamlet&ndash;Jacobs scale, on which the headline lead L1 reaches '
    '\\(D = 8.25\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup> and \\(P = 32.9\\)' + NB + 'GPa against '
    'HMX at 7.52 and PETN at 8.24' + NB + 'km' + NB + 's<sup>&minus;1</sup> under the identical recipe, '
    'placing it in the HMX/PETN band. The calibrated scale is uniformly compressed relative to '
    'literature values across anchors and leads alike (literature-scale equivalents of the targets: '
    '\\(D \\ge 9.0\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup>, \\(P \\ge 35\\)' + NB + 'GPa), so all '
    'performance claims in this paper are anchor-relative rankings on a common scale rather than '
    'absolute-value predictions (Section' + NB + '2.3)')

# T1.3 promote the crystal-density caveat to the point where 2.09 is first reported
main = main.replace(
    'and its raw HOF\\(_{\\text{DFT}}=+229.5\\)' + NB + 'kJ' + NB + 'mol<sup>&minus;1</sup> calibrates to '
    '\\(+22.9\\)' + NB + 'kJ' + NB + 'mol<sup>&minus;1</sup>.</p>',
    'and its raw HOF\\(_{\\text{DFT}}=+229.5\\)' + NB + 'kJ' + NB + 'mol<sup>&minus;1</sup> calibrates to '
    '\\(+22.9\\)' + NB + 'kJ' + NB + 'mol<sup>&minus;1</sup>. This calibrated density carries the largest '
    'single uncertainty in the paper and propagates into every derived \\(D\\) and \\(P\\): it is a '
    'gas-phase-derived estimate, and the independent Bondi van-der-Waals packing bracket for L1 spans '
    '\\(\\rho \\in [1.69, 1.87]\\)' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> (Supplementary' + NB +
    'Section' + NB + 'C.9), below the calibrated value. Crystal-structure prediction or experimental '
    'single-crystal X-ray diffraction remains the critical missing step before any density-based '
    'performance claim here can be treated as quantitative (Section' + NB + '3).</p>')

# T1.6 pk-scale fix. The main text and Supplementary C.9 both quote pk = 0.65 but
# on DIFFERENT scales (calibrated vs raw Bondi) without saying so, and the main
# text's calibrated figure was arithmetically off. Authoritative values from
# t2_density_crosscheck.json: raw pk=0.65 -> 1.6915; applying the 6-anchor fit
# (rho_cal = 1.39198*rho_raw - 0.41488) gives 1.9397, not 1.97. State both scales.
main = main.replace(
    'a packing factor of 0.65 (lower-end aromatic, vs 0.69 used) would give '
    '\\(\\rho \\approx 1.97\\), shifting \\(D_{\\text{K-J}}\\) by roughly '
    '\\(\\pm 0.3\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup>.',
    'a packing factor of 0.65 (lower-end aromatic, vs 0.69 used) would give '
    '\\(\\rho_{\\text{cal}} \\approx 1.94\\)' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> on the calibrated '
    'scale, equivalently the raw Bondi value \\(\\rho \\approx 1.69\\)' + NB + 'g' + NB +
    'cm<sup>&minus;3</sup> quoted in Supplementary' + NB + 'Section' + NB + 'C.9 before the 6-anchor '
    'calibration is applied, shifting \\(D_{\\text{K-J}}\\) by roughly '
    '\\(\\pm 0.3\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup>.')

# T4 main-text companion to the C.13 correction (same measured result).
main = main.replace(
    'An independent Cantera ideal-gas CJ recompute ranks L1, L4, L5 as RDX-class;',
    'An independent Cantera ideal-gas CJ recompute over all eleven leads and all six anchors '
    'characterises product composition and energy release, and resolves a distinct axis from '
    'Kamlet&ndash;Jacobs: an ideal-gas product EOS is nearly insensitive to condensed-phase density, so '
    'the two orderings are independent (Spearman \\(\\rho_s = -0.62\\)) and the recompute quantifies the '
    'covolume requirement (Supplementary' + NB + 'Section' + NB + 'C.13);')

# T5 tone/negative-results pass (declared) --------------------------------
# T5.1 the pool-size check was written as evidence AGAINST the paper's own
# guidance contribution, and was not like-for-like (85/100 vs 13/15 at a
# different pool size = 85% vs 87%). The result that survives is about the gate.
main = main.replace(
    'Pool-size dependence:</strong> repeating the xTB triage on the gated top-15 of an unguided '
    'pool=80&nbsp;000 run, <strong>13/15 survive</strong> the same gate, indicating that classifier '
    'guidance can drive the sampler into modes that score high on learned proxies but fail at '
    'frontier-orbital electronic stability; a larger unguided pool wit',
    'Pool-size robustness:</strong> repeating the xTB triage on the gated top-15 of an unguided '
    'pool=80&nbsp;000 run gives <strong>13/15 survivors</strong>, matching the 85/100 rate of the '
    'production merged set; the 1.5&nbsp;eV electronic-stability gate therefore holds its pass rate '
    'across pool size and guidance configuration. A larger unguided pool wit')

# T5.2 dead-component confession -> statement of the released configuration
main = main.replace(
    'The SC head is retained as an architectural slot for backward compatibility but is not '
    'plumbed into the sample-time gradient sum. Both heads add',
    'The SA and SC heads serve as multi-task trunk regularisers rather than sample-time gradients; '
    'the steering bus invokes the three domain-native heads. Both heads add')

# T1.5 unify the E1 verdict: the source offered two alternative readings
# ("a corroborating datapoint ... or an upper bound"). The Introduction,
# Discussion and Conclusions already commit to one; state it here too.
main = main.replace(
    'Without an oxatriazole-class anchor, E1&rsquo;s calibrated \\(D = 9.00\\)'.replace('&rsquo;', "'")
    + NB + 'km' + NB + 's<sup>&minus;1</sup> is an extrapolation: read as a lower-confidence '
    'corroborating datapoint, it marks a second HMX-class-range performance point from a chemotype '
    "family disjoint from L1's (for a known structure, an external-validation signal rather than a new "
    'lead), or is an upper bound pending an oxatriazole-anchor recompute (a thermochemical-equilibrium '
    'CJ on calibrated inputs and an oxatriazole-class anchor extension are scoped as future work in '
    'Section' + NB + '3).',
    'We therefore assign E1 a single role throughout this paper: it is an external-validation signal '
    'on the sampler&rsquo;s scaffold reach, not a lead. Because the 6-anchor set contains no '
    'oxatriazole-class member, its calibrated \\(D = 9.00\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup> is an '
    'extrapolation outside the anchor chemical space and is read as an upper bound, pending both a '
    'dedicated stability screen and an oxatriazole-class anchor extension (with a '
    'thermochemical-equilibrium CJ recompute on calibrated inputs, scoped as future work in '
    'Section' + NB + '3). It is not counted among the synthesis-actionable results.')

# T1.4 reframe the deliverable: L1 is the actionable lead; the rest carry scaffold diversity
main = main.replace(
    'so the confirmed set is 11 leads (10 unique).',
    'so the confirmed set is 11 leads (10 unique). We distinguish two roles within this set: L1 is the '
    'single synthesis-actionable lead, being the only member for which a productive retrosynthetic route '
    'was recovered (Section' + NB + '2.4), while the remaining leads are reported as a scaffold-diversity '
    'result, establishing that the sampler reaches multiple distinct energetic chemotypes rather than '
    'concentrating on one.')
main = retext_refs(main)
main = resolve_placeholders(main)

# J. bare Supplementary prefixes ("Table S7" -> "Supplementary Table S7")
main = re.sub(r'(?<!Supplementary )(?<!Supplementary&nbsp;)(Table(?:&nbsp;| )S(\d+))',
              lambda m: 'Supplementary ' + m.group(1), main)
main = re.sub(r'(?<!Supplementary )(?<!Supplementary&nbsp;)((?:Figure|Fig\.)(?:&nbsp;| )S(\d+))',
              lambda m: 'Supplementary ' + m.group(1), main)
main = main.replace('Supplementary Supplementary', 'Supplementary')

# footnote wording: the dagger note travelled to the SI with Tables 5/6
main = main.replace('footnote between Supplementary Table&nbsp;S33 and Supplementary Table&nbsp;S34',
                    'footnote below Supplementary Table&nbsp;S33')

# I. Nature-style reference entries (best effort)
def nature_ref(m):
    li_open, body = m.group(1), m.group(2)
    mm = re.match(
        r'\s*(?P<auth>.+?)\s*\((?P<yr>\d{4}[a-z]?)\)\.\s*(?P<title>.+?)\s*'
        r'<em>(?P<jrn>.+?)\s+(?P<vol>\d+)</em>\s*:\s*(?P<pp>[^.<]+)\.\s*(?P<rest>.*)$',
        body, re.S)
    if not mm:
        return m.group(0)
    d = mm.groupdict()
    rest = (' ' + d['rest'].strip()) if d['rest'].strip() else ''
    return (f'{li_open}{d["auth"]} {d["title"]} <em>{d["jrn"]}</em> '
            f'<strong>{d["vol"]}</strong>, {d["pp"].strip()} ({d["yr"]}).{rest}</li>')
main = re.sub(r'(<li id="ref-[a-z0-9-]+">)(.*?)</li>', nature_ref, main)

# H. renumber + drop main-uncited refs
main = normalize(main, keep_uncited=False)

# head/aside cosmetics
main = main.replace('<title>', '<title>[Scientific Reports] ', 1)
main = main.replace('molecules_paper.docx', 'scireports_paper.docx')
main = main.replace('molecules_paper_SI.docx', 'scireports_paper_SI.docx')
main = main.replace('molecules_paper_SI.html', 'scireports_paper_SI.html')
OUT_MAIN.write_text(main, encoding="utf-8")

# --------------------------------------------------------------------------
# SI: append note + moved display items, augment + normalize its references
# --------------------------------------------------------------------------
si_out = si.replace('<title>', '<title>[Scientific Reports] ', 1)
si_out = si_out.replace('molecules_paper.docx', 'scireports_paper.docx')
si_out = si_out.replace('molecules_paper_SI.docx', 'scireports_paper_SI.docx')
si_out = si_out.replace('molecules_paper.html', 'scireports_paper.html')

added = ('\n<h2 id="sec-si-note">Supplementary Note and migrated display items</h2>\n'
         + note + '\n'
         + '<h3 id="sec-si-migrated">Supplementary Figures S5&ndash;S23 and Tables S30&ndash;S35</h3>\n'
         + '<p>The following display items support the main text and are referenced there as '
         + 'Supplementary Fig.&nbsp;S5&ndash;S23 and Supplementary Table&nbsp;S30&ndash;S35.</p>\n'
         + "\n".join(moved_si_parts) + "\n")
# insert BEFORE the SI references section
i = si_out.index('<h2 id="sec-refs">References')
si_out = si_out[:i] + added + si_out[i:]

# SI table/figure references inside migrated captions may cite main items:
# retext them the same way (kept -> new main numbers, moved -> S numbers)
seg = si_out[i:]  # not needed; apply to whole SI for the migrated parts only is
# simpler: the migrated blocks were already relabelled; in-caption cross-refs
# like "Table 9" inside migrated captions:
def retext_si(text):
    def fig_ref(m):
        word, n = m.group(1), int(m.group(2))
        if int(n) in KEEP_FIGS:
            return f'main-text {word}{KEEP_FIGS[n]}'
        if int(n) in MOVE_FIGS:
            return f'Fig.{NB}S{MOVE_FIGS[n]}'
        return m.group(0)
    def tab_ref(m):
        word, n = m.group(1), int(m.group(2))
        if n in KEEP_TABLES:
            return f'main-text {word}{KEEP_TABLES[n]}'
        if n in MOVE_TABLES:
            return f'Table{NB}S{MOVE_TABLES[n]}'
        return m.group(0)
    text = re.sub(r'(Figures?(?:&nbsp;| )|Fig\.(?:&nbsp;| ))(\d+)\b(?!\d)', fig_ref, text)
    text = re.sub(r'(Tables?(?:&nbsp;| ))(\d+)\b(?!\d)', tab_ref, text)
    return text
# apply only to the appended region (existing SI text already uses S numbers)
j = si_out.index('<h2 id="sec-si-note">')
k = si_out.index('<h2 id="sec-refs">References', j)
si_out = si_out[:j] + retext_si(si_out[j:k]) + si_out[k:]

# pre-existing SI text still carries OLD main-display numbers; repoint those
# (targeted, verified one-by-one against the migrated captions)
SI_STALE = [
    ('(main Figure&nbsp;23)', '(Supplementary Fig.' + NB + 'S22)'),        # CFG sweep -> S22
    ('Section&nbsp;4.15, Figure&nbsp;23',
     'Section' + NB + '4.15, Supplementary Fig.' + NB + 'S22'),
    ('(main Table&nbsp;7)', '(main-text Table' + NB + '2)'),               # baselines table
    ('summarised in Table&nbsp;8', 'summarised in Supplementary Table' + NB + 'S35'),
    ('(Figs&nbsp;18 and 20)',
     '(Supplementary Figs' + NB + 'S17 and S19)'),                        # score model, sampler
    ('labelled master, Section&nbsp;5)',
     'labelled master, see the Data Availability statement)'),
    # old main Table 2 (per-lead calibration-propagated uncertainty) migrated to S30
    ('see main Table&nbsp;2)', 'see Supplementary Table' + NB + 'S30)'),
]
SI_STALE = SI_STALE + [
    # T5.3 BLOCKER: names the wrong journal in a Scientific Reports submission
    # (leftover from the Nature Machine Intelligence version). The Ross et al.
    # reference to Nature Machine Intelligence is a real citation and stays.
    ('expected by NMI reviewers, we report MOSES-style metrics',
     'standard in the distribution-learning literature, we report MOSES-style metrics'),
    # T5.4 "Because ... so ..." is ungrammatical and frames the head as a patch
    # for a deficiency; state what the literature-grounded head is instead.
    ('Because guiding generation with gradients of a head trained on a heuristic measures '
     'sensitivity reduction only against that heuristic, so we additionally fine-tune a '
     'literature-grounded variant: the trunk and the four other heads are frozen',
     'A literature-grounded sensitivity head grounds the steering signal in measured '
     '\\(h_{50}\\) data rather than in the heuristic alone: the trunk and the four other heads '
     'are frozen'),
    # T4 (C.13): replace the whole opening block in ONE edit. The recompute now
    # covers all 11 leads + 6 anchors with 6-anchor-calibrated densities. Stated
    # forward-only: what the check measures, what it shows, what it is for.
    # (Three overlapping edits previously left the paragraph self-contradictory.)
    ('A thermochemical-equilibrium Cantera ideal-gas Chapman&ndash;Jouguet recompute is provided '
     'as an independent relative-ranking sanity check on the Section' + NB + '2.3 K-J results. '
     'The Cantera ideal-gas equation of state is \\(\\sim\\)3.5\\(\\times\\) too low in absolute '
     'terms (RDX predicts \\(2.50\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup> vs experimental '
     '\\(8.75\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup>), because BKW/JCZ3-type covolume '
     'corrections dominate at the 30&ndash;100' + NB + 'GPa product-side pressures of CHNO '
     'detonations and the ideal-gas EOS misses them by construction; we therefore use it as '
     'relative ranking only. On that footing the Cantera ideal-gas CJ ranking is used only as a '
     'relative ordering check within the same product-gas composition family, not as an '
     'independent quantitative validation; the relative ranking shows L1, L4, L5 are RDX-class '
     '(within the same product-gas family: L1, L4, L5 share a CO<sub>2</sub>/H<sub>2</sub>O-'
     'dominant CHNO product distribution; cross-family ranking with N<sub>2</sub>-dominant '
     'tetrazoline-class compounds would require a covolume EOS recompute), providing a '
     'qualitative consistency check that the headline \\(D\\) claim for L1 is reasonable.',

     'A thermochemical-equilibrium Cantera ideal-gas Chapman&ndash;Jouguet recompute over all '
     'eleven leads and all six calibration anchors characterises the product-gas composition and '
     'energy release of each candidate. Two properties of the ideal-gas equation of state define '
     'what the recompute measures. It is \\(\\sim\\)3.5\\(\\times\\) low in absolute terms (RDX '
     'predicts \\(2.50\\)' + NB + 'km' + NB + 's<sup>&minus;1</sup> vs experimental \\(8.75\\)' +
     NB + 'km' + NB + 's<sup>&minus;1</sup>), because BKW/JCZ3-type covolume corrections dominate '
     'at the 30&ndash;100' + NB + 'GPa product-side pressures of CHNO detonations; and it is by '
     'construction nearly insensitive to condensed-phase density, with L1 recomputed at '
     '\\(\\rho = 2.53\\) versus \\(2.09\\)' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> moving '
     '\\(D_{\\text{CJ}}\\) by less than 0.01' + NB + 'km' + NB + 's<sup>&minus;1</sup>. Density is '
     'the dominant variable in Kamlet&ndash;Jacobs, so the two treatments weight the problem '
     'differently and their orderings are independent (Spearman \\(\\rho_s = -0.62\\), '
     '\\(n = 11\\)): L4 and L18 reach the RDX/HMX band (2.52 vs RDX 2.50, HMX 2.49' + NB + 'km' +
     NB + 's<sup>&minus;1</sup>) on energy release, while L1, which leads on density, sits between '
     'the FOX-7 and NTO anchors at 2.22' + NB + 'km' + NB + 's<sup>&minus;1</sup>. The recompute '
     'therefore serves as a product-composition and energy-release check, and it quantifies the '
     'covolume requirement directly: a BKW/JCZ3-class solver is the necessary next step for '
     'absolute-grade \\(D\\) (Section' + NB + '3), not an optional refinement.'),
    # T1.6 companion: label the C.9 bracket as RAW (pre-calibration), so it can
    # no longer be read against the calibrated figures quoted in the main text.
    ('yields \\(\\rho \\in [1.69, 1.87]\\)' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> for L1 and '
     '\\([1.65, 1.83]\\)' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> for E1.',
     'yields raw (pre-calibration) \\(\\rho \\in [1.69, 1.87]\\)' + NB + 'g' + NB +
     'cm<sup>&minus;3</sup> for L1 and \\([1.65, 1.83]\\)' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> '
     'for E1; applying the 6-anchor calibration to these brackets gives '
     '\\(\\rho_{\\text{cal}} \\in [1.94, 2.19]\\)' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> for L1, '
     'which contains the headline \\(\\rho_{\\text{cal}} = 2.09\\)' + NB + 'g' + NB +
     'cm<sup>&minus;3</sup> at the production pk' + NB + '=' + NB + '0.69.'),
]
for old, new in SI_STALE:
    if old in si_out:
        si_out = si_out.replace(old, new)
    else:
        print(f"  [warn] SI stale ref not found (already fixed?): {old!r}")

# augment SI reference list with any cited-but-unlisted keys (from source main list)
src_items = {mm.group(1): mm.group(0) for mm in
             re.finditer(r'<li id="(ref-[a-z0-9-]+)">.*?</li>', src, re.S)}
si_cited = set(re.findall(r'href="#(ref-[a-z0-9-]+)"', si_out))
mlist = re.search(r'<ol class="refs">(.*?)</ol>', si_out, re.S)
si_listed = set(re.findall(r'<li id="(ref-[a-z0-9-]+)">', mlist.group(1)))
missing = [k for k in si_cited if k not in si_listed]
if missing:
    add_lis = "\n".join(src_items[k] for k in missing if k in src_items)
    si_out = si_out[:mlist.end(1)] + "\n" + add_lis + si_out[mlist.end(1):]
si_out = re.sub(r'(<li id="ref-[a-z0-9-]+">)(.*?)</li>', nature_ref, si_out)
si_out = normalize(si_out, keep_uncited=False)
OUT_SI.write_text(si_out, encoding="utf-8")

# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
def wc(html_text):
    return len(re.sub(r'<[^>]+>', ' ', html_text).split())
mfigs = len(re.findall(r'<strong>Figure \d+\.</strong>', main))
mtabs = len(re.findall(r'<strong>Table \d+\.</strong>', main))
mrefs = len(re.findall(r'<li id="ref-', main))
srefs = len(re.findall(r'<li id="ref-', si_out))
print(f"main: {len(main):,} B | display items {mfigs}F+{mtabs}T={mfigs+mtabs} | refs {mrefs} | abstract {aw} w")
print(f"SI  : {len(si_out):,} B | refs {srefs} | migrated blocks {len(moved_si_parts)}")
