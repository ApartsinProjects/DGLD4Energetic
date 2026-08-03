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
'  <p><span class="lab">Abstract:</span> Designing high-energy-density materials is data-limited: of\n'
'  ~66,000 labelled CHNO molecules, only ~3,000 carry trustworthy experimental\n'
'  or density functional theory (DFT) values, so models memorise the high-performance tail or extrapolate\n'
'  uncalibrated. We introduce <strong>Domain-Gated Latent Diffusion (DGLD)</strong>, coupling generative\n'
'  design to first-principles validation. A four-tier label-trust gate routes only high-quality labels\n'
'  into the conditional gradient while noisy labels train the unconditional prior; a score model adds\n'
'  switchable steering over viability, sensitivity, and hazard; and a four-stage funnel (SMARTS filter,\n'
'  Pareto reranker, GFN2-xTB triage, two-level DFT) validates every candidate. DGLD yields 10 unique\n'
'  DFT-confirmed leads, novel against PubChem; the headline compound, 3,4,5-trinitro-1,2-isoxazole,\n'
'  reaches a calibrated density of 2.09' + NB + 'g' + NB + 'cm<sup>&minus;3</sup> and a Kamlet&ndash;Jacobs detonation\n'
'  velocity of 8.25' + NB + 'km' + NB + 's<sup>&minus;1</sup> (HMX and PETN anchors: 7.52 and 8.24' + NB + 'km' + NB + 's<sup>&minus;1</sup>),\n'
'  and is distinct from all 65,980 training molecules (Tanimoto 0.27). Against four\n'
'  baselines on the same corpus, DGLD is the only method with productive-quadrant coverage (novel and\n'
'  on-target) confirmed at the DFT level; the sole baseline whose best novel candidate was carried to DFT\n'
'  collapsed from 9.73 to 6.28' + NB + 'km' + NB + 's<sup>&minus;1</sup>. The label-trust gate is domain-agnostic,\n'
'  transferring to any task with abundant weak and scarce trustworthy labels.</p>\n'
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
'<a class="cite" href="#ref-eckmann2022limo">[11]</a> as the frozen encoder, with MolMIM '
'<a class="cite" href="#ref-reidenbach2023molmim">[12]</a>, the RL-based REINVENT'
'&nbsp;4 <a class="cite" href="#ref-olivecrona2017reinvent">[14]</a><a class="cite" href="#ref-loeffler2024reinvent4">[15]</a>, '
'and graph diffusion (DiGress <a class="cite" href="#ref-vignac2023digress">[21]</a>) as the comparative '
'no-diffusion and diffusion baselines. On the generative-prior side, DGLD builds on denoising diffusion '
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
code_avail = (
'<h2>Code Availability</h2>\n'
'<p>All custom code central to this study is publicly available. The full '
'pipeline (LIMO fine-tuning, denoiser and score-model training, the sampling '
'and four-stage validation funnel, and the figure-generation scripts) is '
'released in the archived Zenodo package '
'(<a href="https://doi.org/10.5281/zenodo.19821952">10.5281/zenodo.19821952</a>, '
'Apache-2.0) and mirrored on GitHub at '
'<a href="https://github.com/ApartsinProjects/DGLD4Energetic">github.com/ApartsinProjects/DGLD4Energetic</a>.</p>\n')
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
