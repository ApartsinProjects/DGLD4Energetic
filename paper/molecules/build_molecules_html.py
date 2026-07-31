#!/usr/bin/env python
"""Assemble an MDPI *Molecules* -structured manuscript HTML from long_paper.html.

Strategy: reuse the long paper's body content VERBATIM (paragraphs, figures,
tables, math, citations), but reorganise into the MDPI Article section order
  1. Introduction  ->  2. Results  ->  3. Discussion
  ->  4. Materials and Methods  ->  5. Conclusions
and attach MDPI front matter (title/authors/abstract/keywords) and end matter
(Author Contributions, Funding, Data Availability, Conflicts of Interest, etc.).
The Appendix A-F is lifted out to a companion Supplementary Information file.

Section cross-references (e.g. "SS5.3") are remapped to the new numbers, and
figures/tables are renumbered sequentially by order of appearance. A verification
pass at the end reports any leftover stale references.

Run:  python build_molecules_html.py
Reads ../long_paper.html ; writes ../molecules/molecules_paper.html and
../molecules/molecules_paper_SI.html
"""
import re, sys, pathlib, html as _html

HERE = pathlib.Path(__file__).resolve().parent
SRC  = HERE.parent / "long_paper.html"
OUT_MAIN = HERE / "molecules_paper.html"
OUT_SI   = HERE / "molecules_paper_SI.html"

# Citation-order renumbering (the Molecules section order differs from the long
# paper's, so citations must be renumbered by first appearance per document).
sys.path.insert(0, str(HERE.parent))
from normalize_citations import normalize as _normalize_cites

text = SRC.read_text(encoding="utf-8")
lines = text.splitlines(keepends=True)

def line_of(pat):
    rx = re.compile(pat)
    for i, l in enumerate(lines):
        if rx.search(l):
            return i
    raise RuntimeError(f"pattern not found: {pat}")

# --- structural breakpoints (match on stable heading text) ---
i_intro   = line_of(r'<h2 id="sec-intro">1\.')
i_related = line_of(r'>2\.&nbsp;Related work<')
i_dataset = line_of(r'>3\.&nbsp;Dataset<')
i_method  = line_of(r'>4\.&nbsp;Methodology<')
i_exp     = line_of(r'>5\.&nbsp;Experiments<')
i_limit   = line_of(r'<h2 id="sec-disc">6\.')
i_conc    = line_of(r'<h2 id="sec-conc">7\.')
i_appendix= line_of(r'<h2 id="sec-app">Appendix</h2>')
i_refs    = line_of(r'<h2[^>]*>References</h2>')
i_bodyend = line_of(r'</body>')

def block(a, b):
    return "".join(lines[a:b])

intro_html    = block(i_intro, i_related)     # SS1 content (keeps Figs 1,2 + contribution list)
related_html  = block(i_related, i_dataset)   # SS2 Related work
dataset_html  = block(i_dataset, i_method)    # SS3 Dataset
method_html   = block(i_method, i_exp)        # SS4 Methodology
exp_html      = block(i_exp, i_limit)         # SS5 Experiments -> Results
limit_html    = block(i_limit, i_conc)        # SS6 Limitations -> Discussion
conc_html     = block(i_conc, i_appendix)     # SS7 Conclusion (incl 7.1)
appendix_html = block(i_appendix, i_refs)     # Appendix A-F -> SI
refs_html     = block(i_refs, i_bodyend)      # References list

# ---------------------------------------------------------------------------
# 1) Heading renumbering. We rewrite the top-level numbers and subsection
#    numbers so the assembled document reads 1..5 with clean subsections.
# ---------------------------------------------------------------------------

def strip_h2(htmlblock):
    """Remove the leading <h2>..</h2> heading from a section block."""
    return re.sub(r'^\s*<h2[^>]*>.*?</h2>\s*', '', htmlblock, count=1, flags=re.DOTALL)

# ---- Introduction: keep as-is (already "1. Introduction"), drop its number style to MDPI ----
intro_body = strip_h2(intro_html)

# ---- Related work -> fold under Introduction as "1.1. Related Work" ----
related_body = strip_h2(related_html)
# turn "2.N Title" h3 subheadings into "1.1.N Title"
def _rel_sub(m):
    n = m.group(1); title = m.group(2)
    return f'<h3>1.1.{n}&nbsp;{title}</h3>'
related_body = re.sub(r'<h3[^>]*>2\.(\d+)&nbsp;(.*?)</h3>', _rel_sub, related_body)

# ---- Experiments -> "2. Results", subsections 5.N -> 2.N ----
results_body = strip_h2(exp_html)
def _res_sub(m):
    return f'<h3>2.{m.group(1)}&nbsp;{m.group(2)}</h3>'
results_body = re.sub(r'<h3[^>]*>5\.(\d+)&nbsp;(.*?)</h3>', _res_sub, results_body)

# ---- Limitations -> "3. Discussion" ----
discussion_body = strip_h2(limit_html)

# ---- Materials and Methods = Dataset(SS3) + Methodology(SS4), renumbered 4.1.. ----
dataset_body = strip_h2(dataset_html)
method_body  = strip_h2(method_html)
# Dataset subsections 3.N -> 4.(1..) ; Methodology 4.N -> 4.(k..)
# We renumber sequentially: dataset gives 4.1 (main), 4.2, 4.3 ; methodology continues 4.4..4.15
# First relabel dataset h3 "3.N Title" -> placeholder, methodology h3 "4.N Title" -> placeholder,
# then assign sequential 4.k in document order over the concatenation.
mm_concat = ('<p><em>Dataset construction (Section&nbsp;4.1&ndash;4.3) and the DGLD model, '
             'sampler, and validation funnel (Section&nbsp;4.4 onward) are described below; '
             'full per-component hyperparameters and the DFT protocol are in the Supplementary '
             'Information.</em></p>\n'
             + dataset_body + "\n" + method_body)
# collapse any "3.N" and "4.N" h3 to sequential 4.k, recording old->new so that
# inline "&sect;3.N"/"&sect;4.N" references can be remapped to the same numbers.
mm_counter = [0]
mm_map = {}   # "3.N" / "4.N"  ->  "4.k"
def _mm_sub(m):
    mm_counter[0] += 1
    mm_map[f'{m.group(1)}.{m.group(2)}'] = f'4.{mm_counter[0]}'
    return f'<h3>4.{mm_counter[0]}&nbsp;{m.group(3)}</h3>'
mm_concat = re.sub(r'<h3[^>]*>([34])\.(\d+)&nbsp;(.*?)</h3>', _mm_sub, mm_concat)

# ---- Conclusion -> "5. Conclusions" ; drop 7.1 code/data (moves to Data Availability) ----
conc_body = strip_h2(conc_html)
conc_body = re.sub(r'<h3[^>]*>7\.1.*?</h3>.*', '', conc_body, flags=re.DOTALL)  # cut 7.1 subsection

# ---- Discussion: interpretive opening (grounded in the paper's own results),
#      placed before the migrated Limitations content so Section 3 reads as an
#      MDPI-style Discussion rather than a bare caveats list. ----
DISCUSSION_OPENING = (
    '<p>DGLD&rsquo;s central result is that tier-gated training and switchable sample-time '
    'steering together let a latent diffusion model act as a <em>productive-quadrant generator</em>: '
    'it proposes molecules that are simultaneously novel relative to the labelled corpus and '
    'competitive with the HMX/PETN reference class under first-principles validation. The two '
    'top-ranked leads, L1 (3,4,5-trinitro-1,2-isoxazole) and E1 (4-nitro-1,2,3,5-oxatriazole), come '
    'from disjoint chemotype families on a single sampling run, so DGLD&rsquo;s productive-quadrant '
    'coverage spans multiple scaffold classes. The mechanism that makes this possible is the label-trust '
    'gate: routing only the ~3,000 rows that carry a trustworthy experimental or DFT label on the '
    'target detonation channels into the conditional gradient, while the remaining lower-confidence '
    'labels train only the unconditional prior, prevents miscalibrated '
    'Kamlet&ndash;Jacobs and surrogate labels from steering generation toward physically implausible '
    'high-scoring regions, the failure mode visible in the SELFIES-GA baseline, whose best novel '
    'candidate loses 3.5&nbsp;km&nbsp;s<sup>&minus;1</sup> under DFT audit.</p>\n'
    '<p>Relative to prior work, DGLD occupies a distinct position. Discriminative property surrogates '
    'score candidates but do not propose them; generative language models trained on energetic '
    'corpora tend to memorise, as the SMILES-LSTM baseline&rsquo;s 18.3% exact-rediscovery rate shows; '
    'and standard classifier guidance degrades over the short trajectories molecular generation '
    'requires. By coupling generative inverse design to a graded validation funnel that ends in '
    'density-functional theory, DGLD converts a sparse-label liability into a usable training signal '
    'and returns a ranked, physics-checked candidate list rather than an unvalidated pool. Because '
    'the gating mechanism depends only on the availability of a trust hierarchy over labels (not on '
    'any energetic-materials-specific structure), the recipe should transfer to other data-limited '
    'inverse-design settings, with only the validation funnel changing per domain.</p>'
)

# ---------------------------------------------------------------------------
# 2) Section cross-reference remap over the WHOLE assembled body.
#    old-> new section numbers (as they appear in "SSX" or "Section X" refs):
#      2.x (related) -> 1.1.x        3.x (dataset)  -> 4.x
#      4.x (method)  -> 4.x (approx) 5.x (experim.) -> 2.x
#      6 (limits)    -> 3            7 / 7.1 (concl)-> 5
#    Appendix refs (A.., B.., C.., D.., E.., F..) -> "Supplementary Information"
# ---------------------------------------------------------------------------
# NOTE: dataset/method subsection numbers were re-sequenced to 4.k above, so a
# purely numeric remap of "SS4.7" is unreliable. We therefore convert method/dataset
# section refs to the generic "the Methods (Section 4)" and appendix refs to the SI.

def remap_refs(s):
    # Appendix / SI-section references -> "Supplementary Section X.Y". Keep the
    # specific label (the SI retains its lettered A-F subsections) and do NOT
    # consume surrounding parentheses (the old rule ate the closing paren).
    s = re.sub(r'Appendix(?:&nbsp;|\s+)([A-F](?:\.\d+)?)', r'Supplementary&nbsp;Section&nbsp;\1', s)
    s = re.sub(r'(?:§|&sect;)\s*([A-F]\.\d+)', r'Supplementary&nbsp;Section&nbsp;\1', s)
    s = re.sub(r'\bSS([A-F]\.\d+)', r'Supplementary&nbsp;Section&nbsp;\1', s)
    # Experiments §5.x -> Section 2.x
    s = re.sub(r'(?:§|&sect;)\s*5\.(\d+)', r'Section&nbsp;2.\1', s)
    # Dataset/Methodology §3.x / §4.x -> the renumbered Materials-and-Methods
    # subsection (via the map built during the methods renumber); fall back to
    # the bare section if a subsection is not in the map.
    def _mm_ref(m):
        return 'Section&nbsp;' + mm_map.get(f'{m.group(1)}.{m.group(2)}', '4')
    s = re.sub(r'(?:§|&sect;)\s*([34])\.(\d+)', _mm_ref, s)
    # Related work §2.x -> Section 1.1  (before bare 2)
    s = re.sub(r'(?:§|&sect;)\s*2\.\d+', 'Section&nbsp;1.1', s)
    # ---- bare section numbers (no subsection) ----
    s = re.sub(r'(?:§|&sect;)\s*5\b', 'Section&nbsp;2', s)        # Experiments  -> Results
    s = re.sub(r'(?:§|&sect;)\s*6\b', 'Section&nbsp;3', s)        # Limitations  -> Discussion
    s = re.sub(r'(?:§|&sect;)\s*7(?:\.1)?\b', 'Section&nbsp;5', s)# Conclusion   -> Conclusions
    s = re.sub(r'(?:§|&sect;)\s*[34]\b', 'Section&nbsp;4', s)     # Dataset/Method
    s = re.sub(r'(?:§|&sect;)\s*2\b', 'Section&nbsp;1.1', s)      # Related work
    # tidy artifacts: double article "the Section 4", a degenerate "Section 4
    # and Section 4" (Dataset+Methodology both fold into Materials and Methods),
    # and a stray "the the".
    s = s.replace('the Section&nbsp;4', 'Section&nbsp;4')
    s = re.sub(r'Section&nbsp;4(?:\.\d+)? and Section&nbsp;4\b', 'Section&nbsp;4', s)
    s = re.sub(r'\bthe the\b', 'the', s)
    return s

def to_si_units(s):
    """MDPI prefers SI unit style (g cm^-3, km s^-1) over the solidus form."""
    s = s.replace('g/cm<sup>3</sup>', 'g&nbsp;cm<sup>&minus;3</sup>')
    s = s.replace('km/s', 'km&nbsp;s<sup>&minus;1</sup>')
    s = s.replace('kJ/mol', 'kJ&nbsp;mol<sup>&minus;1</sup>')
    s = s.replace('kcal/mol', 'kcal&nbsp;mol<sup>&minus;1</sup>')
    return s

# ---------------------------------------------------------------------------
# 3) Assemble body in MDPI order, then renumber figures & tables by appearance.
# ---------------------------------------------------------------------------
# --- Appendix figures used PLAIN global numbers (e.g. 18, 26) that collide with
#     the renumbered main figures. Relabel them to the supplementary S-series
#     (Figure S1, S2, ...) across BOTH documents *before* the main renumber, so
#     main-body references to them no longer clash with the new main figures.
# The appendix figures use MIXED labels in the source: some plain-numbered (18, 26)
# and some lettered (A.1, F.1). Map ALL of them to a clean supplementary S-series
# (S1..Sn) in order of appearance, so the SI numbering is consistent.
app_fig_labels = list(dict.fromkeys(
    re.findall(r'<strong>Figure(?:&nbsp;|\s+)([0-9]+|[A-F]\.[0-9]+)\.', appendix_html)))
APP_FIG_MAP = {old: f'S{i + 1}' for i, old in enumerate(app_fig_labels)}

# Figure-label token: a plain number, an S-number, or a lettered appendix label.
_FIGLAB = r'([0-9]+|[A-F]\.[0-9]+)'

def apply_fig_refmap(s, mapping):
    """Rewrite figure captions and inline 'Figure N'/'Fig. N' refs via mapping.

    Single pass (each label looked up once, so chained maps like 19->3, 3->10 do
    not double-apply). Handles plain numbers and lettered labels (A.1, F.1); the
    lookahead stops '18' from matching inside '180' and 'A.1' inside 'A.10'.
    """
    s = re.sub(r'(<strong>Figure(?:&nbsp;|\s+))' + _FIGLAB + r'(\.)',
               lambda m: m.group(1) + mapping.get(m.group(2), m.group(2)) + m.group(3), s)
    s = re.sub(r'\b(Figure|Fig\.?)(&nbsp;|\s+)' + _FIGLAB + r'(?![0-9A-Za-z])',
               lambda m: f'{m.group(1)}{m.group(2)}{mapping.get(m.group(3), m.group(3))}', s)
    return s

def apply_tab_refmap(s, mapping):
    """Rewrite plain 'Table N' refs via mapping (leaves lettered 'Table B.1' alone)."""
    s = re.sub(r'(<strong>Table(?:&nbsp;|\s+))(\d+)(\.)',
               lambda m: m.group(1) + mapping.get(m.group(2), m.group(2)) + m.group(3), s)
    s = re.sub(r'\b(Table)(&nbsp;|\s+)(\d+)\b',
               lambda m: f'{m.group(1)}{m.group(2)}{mapping.get(m.group(3), m.group(3))}', s)
    return s

body_main = "\n".join([
    '<h2 id="sec-intro">1. Introduction</h2>', intro_body,
    '<h3>1.1. Related Work</h3>',
    '<p>DGLD draws on, and departs from, several strands of prior work, reviewed below.</p>',
    related_body,
    '<h2 id="sec-results">2. Results</h2>', results_body,
    '<h2 id="sec-discussion">3. Discussion</h2>', DISCUSSION_OPENING,
    '<h3>3.1. Limitations</h3>', discussion_body,
    '<h2 id="sec-methods">4. Materials and Methods</h2>', mm_concat,
    '<h2 id="sec-conc">5. Conclusions</h2>', conc_body,
])
body_main = remap_refs(body_main)
# main-body references to appendix figures 18/26 -> S1/S2 (before main renumber)
body_main = apply_fig_refmap(body_main, APP_FIG_MAP)

# Renumber figures: find caption labels "<strong>Figure N.</strong>" in order,
# build old->new map, then rewrite BOTH captions and inline "Figure N"/"Fig. N" refs.
fig_labels = re.findall(r'<strong>Figure\s+(\d+)\.', body_main)
fig_map = {}
for old in fig_labels:
    if old not in fig_map:
        fig_map[old] = str(len(fig_map) + 1)
# apply (guard: rewrite longest-first to avoid partial clobber)
def _renumber(s, mapping, word):
    # captions
    def caprepl(m):
        return f'<strong>{word} {mapping.get(m.group(1), m.group(1))}.'
    s = re.sub(rf'<strong>{word}\s+(\d+)\.', caprepl, s)
    # inline refs "Figure N" / "Fig. N" / "Table N"
    def refrepl(m):
        pre = m.group(1); num = m.group(2)
        return f'{pre}{mapping.get(num, num)}'
    s = re.sub(rf'((?:{word}|{word[:3]}\.?)&nbsp;|(?:{word}|{word[:3]}\.?)\s+)(\d+)', refrepl, s)
    return s

# (figure inline refs handled generically below to avoid double touching captions)
# Simpler robust approach: two-phase token replacement with sentinels.
def renumber_labels(s, kind):
    labels = re.findall(rf'<strong>{kind}\s+(\d+)\.', s)
    mp = {}
    for old in labels:
        if old not in mp:
            mp[old] = str(len(mp) + 1)
    # sentinel captions + inline refs
    # captions:
    s = re.sub(rf'<strong>{kind}\s+(\d+)\.',
               lambda m: f'<strong>{kind} {mp.get(m.group(1), m.group(1))}.', s)
    # inline "Figure N", "Fig. N", "Fig N", "Table N"
    abbr = 'Fig' if kind == 'Figure' else kind
    s = re.sub(rf'\b(?:{kind}|{abbr}\.?)(&nbsp;|\s+)(\d+)\b',
               lambda m: f'{kind}{m.group(1)}{mp.get(m.group(2), m.group(2))}', s)
    # unwrap sentinels
    s = s.replace('', '').replace('', '')
    return s, mp

body_main, fmap = renumber_labels(body_main, 'Figure')
body_main, tmap = renumber_labels(body_main, 'Table')

# Multi-figure references ("Figs 3 and 4", "Figs 6-15", "Figures 8, 9 and 11")
# are skipped by the single-ref pass in renumber_labels (its regex only matches
# singular "Fig N"/"Figure N"), so their numbers survive un-renumbered. Remap
# every number inside a plural Figs/Figures list-or-range span using the same
# old->new map. Safe because these spans were untouched above (no double-apply).
def remap_fig_lists(s, mp):
    SEP = r'(?:\s*(?:,|&ndash;|&mdash;|-|and|&nbsp;)\s*)+'
    def repl(m):
        # remap only standalone figure numbers; the lookbehind keeps the digit
        # inside an S-series label ('S1') or lettered label ('A.1') untouched.
        return m.group(1) + re.sub(r'(?<![A-Za-z.])\d+',
                                   lambda d: mp.get(d.group(0), d.group(0)),
                                   m.group(2))
    return re.sub(r'\b((?:Figures|Figs)\.?(?:&nbsp;|\s+))((?:\d+)(?:' + SEP + r'\d+)*)',
                  repl, s)
body_main = remap_fig_lists(body_main, fmap)

# Files live in paper/molecules/ ; images are in paper/figs/ -> use ../figs/
body_main = body_main.replace('src="figs/', 'src="../figs/')
body_main = re.sub(r'<!--.*?-->', '', body_main, flags=re.DOTALL)  # drop stale section-divider comments
body_main = to_si_units(body_main)

# ---------------------------------------------------------------------------
# 4) Front matter, end matter, and page shell (MDPI-flavoured, KaTeX-enabled).
# ---------------------------------------------------------------------------
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Domain-Gated Latent Diffusion for the Inverse Design of Novel HMX-Class Energetic Materials with First-Principles Validation</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body,{delimiters:[
          {left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false},
          {left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}],
          throwOnError:false});"></script>
<style>
:root{--fg:#1a1a1a;--bg:#ffffff;--muted:#555;--accent:#0b5394;--rule:#d5d8dc;--mono:'JetBrains Mono','Consolas',monospace;}
html{scroll-behavior:smooth}
body{font:15px/1.55 'Palatino Linotype',Palatino,Georgia,'Times New Roman',serif;color:var(--fg);background:var(--bg);max-width:50rem;margin:2rem auto;padding:0 1.2rem}
header.title{text-align:left;margin-bottom:1.4rem;border-bottom:2px solid var(--accent);padding-bottom:1rem}
header.title .artType{font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;color:var(--accent);font-weight:700}
header.title h1{font-size:1.5rem;line-height:1.25;font-weight:700;margin:.4rem 0}
header.title .authors{font-size:1.0rem;margin:.4rem 0 .1rem}
header.title .affil{color:var(--muted);font-size:.86rem;font-style:italic;margin:.1rem 0}
header.title .corr{color:var(--muted);font-size:.82rem;margin-top:.3rem}
h2{font-size:1.12rem;margin-top:2.0rem;color:var(--accent);font-weight:700}
h3{font-size:1.0rem;margin-top:1.3rem;color:#123;font-weight:700}
h4{font-size:.94rem;margin-top:1.0rem;font-style:italic}
p{margin:.6rem 0;text-align:justify;hyphens:auto}
code,pre,.smi{font-family:var(--mono);font-size:.86em}
pre{background:#f4f6f8;padding:.6rem .8rem;border-radius:.3rem;overflow:auto;border-left:3px solid var(--accent)}
.smi{background:#f4f6f8;padding:.05em .25em;border-radius:.18em;font-size:.82em;word-break:break-all}
table{border-collapse:collapse;margin:1rem 0;font-size:.86rem;width:100%}
table caption{font-size:.84rem;text-align:left;margin-bottom:.3rem;color:var(--fg)}
th,td{border:1px solid var(--rule);padding:.35rem .5rem;text-align:left}
th{font-weight:700;background:#eef3f8}
figure{margin:1.3rem 0;text-align:center}
figure img{max-width:100%;height:auto}
figcaption{font-size:.83rem;color:var(--fg);margin-top:.4rem;text-align:left;padding:0 .4rem}
.abstract{background:#f4f6f8;border:1px solid var(--rule);padding:.9rem 1.1rem;margin:1.2rem 0;font-size:.9rem}
.abstract .lab{font-weight:700;color:var(--accent)}
.keywords{font-size:.9rem;margin:.6rem 0 1.4rem}
.keywords .lab{font-weight:700;color:var(--accent)}
.cite{font-size:.9em;color:var(--accent);text-decoration:none}
.endmatter h2{font-size:1.0rem;border:none;margin-top:1.3rem}
.endmatter p{font-size:.9rem}
.refs{font-size:.84rem}
.refs li{margin-bottom:.35rem}
.mdpi-note{background:#fff8e6;border-left:3px solid #d9a441;padding:.6rem .9rem;margin:1rem 0;font-size:.86rem}
.downloads{position:fixed;top:1rem;right:1rem;z-index:100;
  display:flex;flex-direction:column;gap:.25rem;
  background:rgba(255,255,255,.94);border:1px solid var(--rule);
  border-radius:.4rem;padding:.55rem .75rem;font-size:.82rem;
  box-shadow:0 1px 4px rgba(0,0,0,.06)}
.downloads .label{font-size:.68rem;color:var(--muted);letter-spacing:.06em;
  text-transform:uppercase;margin-bottom:.15rem}
.downloads a{color:var(--accent);text-decoration:none;display:block;line-height:1.35}
.downloads a:hover{text-decoration:underline}
.downloads .ext{color:var(--muted);font-size:.75em}
@media print{body{font-size:10pt;max-width:none}.downloads{display:none}}
@media (max-width:60rem){.downloads{position:static;margin:0 auto 1rem auto;max-width:48rem;box-shadow:none;border-radius:.3rem}}
</style>
</head>
<body>
'''

DOWNLOADS_ASIDE = '''<aside class="downloads no-docx no-print" aria-label="Downloads for this submission">
  <span class="label">Submission files</span>
  <a href="molecules_paper.docx" download>Main article <span class="ext">(.docx)</span></a>
  <a href="molecules_paper_SI.docx" download>Supplementary Information <span class="ext">(.docx)</span></a>
  <a href="molecules_paper_SI.html">Supplementary Information <span class="ext">(.html)</span></a>
  <a href="cover_letter.html">Cover letter <span class="ext">(.html)</span></a>
</aside>

'''

SI_DOWNLOADS_ASIDE = '''<aside class="downloads no-docx no-print" aria-label="Downloads for this submission">
  <span class="label">Submission files</span>
  <a href="molecules_paper.html">Main article <span class="ext">(.html)</span></a>
  <a href="molecules_paper.docx" download>Main article <span class="ext">(.docx)</span></a>
  <a href="molecules_paper_SI.docx" download>Supplementary Information <span class="ext">(.docx)</span></a>
  <a href="cover_letter.html">Cover letter <span class="ext">(.html)</span></a>
</aside>

'''

TITLEBLOCK = '''<header class="title">
  <div class="artType">Article</div>
  <h1>Domain-Gated Latent Diffusion for the Inverse Design of Novel HMX-Class Energetic Materials with First-Principles Validation</h1>
  <p class="authors">Yehudit Aperstein <sup>1,</sup>* and Alexander Apartsin <sup>2</sup></p>
  <p class="affil"><sup>1</sup> Department of Intelligent Systems, Afeka Tel-Aviv College of Engineering, Tel-Aviv, Israel</p>
  <p class="affil"><sup>2</sup> School of Computer Science, Faculty of Sciences, Holon Institute of Technology (HIT), Holon, Israel</p>
  <p class="corr">* Correspondence: apersteiny@afeka.ac.il</p>
</header>

<div class="abstract">
  <p><span class="lab">Abstract:</span> The design of new high-energy-density materials is a
  data-limited inverse-design problem: of roughly 66,000 CHNO molecules with reported detonation
  properties, only about 3,000 carry trustworthy experimental or quantum-chemistry values, so generative models trained on the full mixture
  either memorise the high-performance tail or extrapolate without calibration, and few new HMX-class
  compounds have been disclosed in the past fifteen years. Here we introduce
  <strong>Domain-Gated Latent Diffusion (DGLD)</strong>, a data-driven framework that couples
  generative inverse design to first-principles validation. A four-tier label-trust gate routes only
  high-quality labels into the conditional gradient while noisy labels train the unconditional prior;
  a multi-task score model supplies independently switchable sample-time steering over viability,
  sensitivity, and hazard; and a four-stage screening funnel (a substructure-pattern (SMARTS) filter,
  a Pareto reranker, semi-empirical GFN2-xTB triage, and two-level DFT (B3LYP/6-31G(d) geometry,
  &omega;B97X-D3BJ/def2-TZVP single-point)) validates every candidate. DGLD yields
  11 unique DFT-confirmed novel leads (12 lead cards); the headline compound, 3,4,5-trinitro-1,2-isoxazole, reaches a
  calibrated density of 2.09&nbsp;g&nbsp;cm<sup>&minus;3</sup> and a Kamlet&ndash;Jacobs detonation velocity of
  8.25&nbsp;km&nbsp;s<sup>&minus;1</sup> while remaining structurally distinct from all 65,980 training molecules
  (nearest-neighbour Tanimoto 0.27). On the identical Kamlet&ndash;Jacobs recipe the HMX and PETN reference
  anchors calibrate to 7.52 and 8.24&nbsp;km&nbsp;s<sup>&minus;1</sup>, so this lead ranks with the strongest
  anchors on the matched scale. Against four baselines on the same corpus, DGLD is the only
  method whose novel candidates stay competitive with the calibrated HMX/PETN class under DFT validation.
  The label-gating recipe is domain-agnostic, requiring only a domain-appropriate validation funnel;
  code, model checkpoints, and 918 mined hard negatives are released openly.</p>
</div>

<p class="keywords"><span class="lab">Keywords:</span> generative models; latent diffusion;
inverse molecular design; high-throughput screening; energetic materials; high-energy density
materials; density functional theory; materials informatics; structure&ndash;property relationships;
data-driven discovery</p>
'''

# End matter (MDPI standard blocks)
ENDMATTER = '''
<div class="endmatter">
<h2>Supplementary Materials</h2>
<p>The following supporting information can be downloaded alongside this article: Supplementary
Information (Appendix&nbsp;A&ndash;F) containing full dataset provenance, complete model architecture and
hyperparameter tables, the first-principles (DFT) methodology and uncertainty bounds, reproducibility
details and extended ablations, baseline-method example outputs, and the detailed per-condition
ablations. File: <code>molecules_paper_SI.html</code> (compiled to <code>molecules_paper_SI.docx</code>).</p>

<h2>Author Contributions</h2>
<p>Conceptualization, Y.A. and A.A.; methodology, Y.A. and A.A.; software, Y.A. and A.A.;
validation, Y.A. and A.A.; formal analysis, Y.A. and A.A.; investigation, Y.A. and A.A.;
data curation, Y.A. and A.A.; writing, original draft preparation, Y.A. and A.A.;
writing, review and editing, Y.A. and A.A.; visualization, Y.A. and A.A. All authors have read
and agreed to the published version of the manuscript.</p>

<h2>Funding</h2>
<p>This research received no external funding.</p>

<h2>Institutional Review Board Statement</h2>
<p>Not applicable.</p>

<h2>Informed Consent Statement</h2>
<p>Not applicable.</p>

<h2>Data Availability Statement</h2>
<p>All code, data, and trained models are released together as a single archived package on Zenodo at
DOI <a href="https://doi.org/10.5281/zenodo.19821952">10.5281/zenodo.19821952</a> (code under Apache-2.0;
data and model checkpoints under CC-BY-4.0). The package contains: the code (LIMO fine-tuning, denoiser
and score-model training, sampling, the four-stage validation funnel, and the figure-generation
pipeline); the trained checkpoints (the LIMO VAE, two conditional latent denoisers DGLD-H and DGLD-P,
two multi-head latent score models, the SELFIES alphabet, and run metadata); and the data (the
65,980-row labelled CHNO master, the augmented unlabelled corpus, and the 918 mined hard-negative
latents), redistributed in canonicalised form with row-level provenance. The code is additionally
mirrored at
<a href="https://github.com/ApartsinProjects/DGLD4Energetic">github.com/ApartsinProjects/DGLD4Energetic</a>.</p>

<h2>Conflicts of Interest</h2>
<p>The authors declare no conflicts of interest.</p>
</div>
'''

TAIL = "\n</body>\n</html>\n"

def renumber_si_tables(main_s, si_s):
    """Renumber the Supplementary tables from the appendix lettering (A.1, B.1a,
    C.1b, D.4b, ...) to a clean Supplementary series (Table S1, S2, ...) in
    physical order, updating captions and every 'Table X.Y' reference in both
    documents. Main tables (1-9) and Supplementary *Section* labels are untouched.
    """
    LBL = r'[A-F]\.[0-9]+[a-z]?'
    order = []
    for m in re.finditer(r'<strong>Table(?:&nbsp;|\s)(' + LBL + r')\.', si_s):
        if m.group(1) not in order:
            order.append(m.group(1))
    smap = {lbl: f'S{i+1}' for i, lbl in enumerate(order)}
    if not smap:
        return main_s, si_s
    SEP = r'(?:\s*(?:,|&ndash;|&mdash;|-|and|&nbsp;)\s*)+'
    def apply(s):
        # captions first
        s = re.sub(r'(<strong>Table)(?:&nbsp;|\s)(' + LBL + r')\.',
                   lambda m: f'{m.group(1)}&nbsp;{smap.get(m.group(2), m.group(2))}.', s)
        # then "Table X.Y" / "Tables X.Y and Z" / "Tables X.Y-X.Z" references
        s = re.sub(r'\b(Tables?(?:&nbsp;|\s))((?:' + LBL + r')(?:' + SEP + LBL + r')*)',
                   lambda m: m.group(1) + re.sub(LBL, lambda d: smap.get(d.group(0), d.group(0)), m.group(2)),
                   s)
        return s
    return apply(main_s), apply(si_s)

# References: retitle to MDPI plain "References" (already <h2>References</h2>) and keep list.
refs_out = refs_html
refs_out = remap_refs(refs_out)

full_main = HEAD + DOWNLOADS_ASIDE + TITLEBLOCK + body_main + "\n" + refs_out + ENDMATTER + TAIL
full_main = _normalize_cites(full_main)   # citation-order renumber (Molecules order)
# (OUT_MAIN is written after the SI is built, so SI-table references in the main
#  text can be renumbered to the S-series together with the SI captions.)

# ---------------------------------------------------------------------------
# 5) Supplementary Information file: appendix A-F + references (self-contained).
# ---------------------------------------------------------------------------
SI_TITLE = '''<header class="title">
  <div class="artType">Supplementary Information</div>
  <h1>Supplementary Information for:<br>Domain-Gated Latent Diffusion for the Inverse Design of Novel HMX-Class Energetic Materials with First-Principles Validation</h1>
  <p class="authors">Yehudit Aperstein <sup>1,</sup>* and Alexander Apartsin <sup>2</sup></p>
  <p class="affil"><sup>1</sup> Afeka Tel-Aviv College of Engineering, Tel-Aviv, Israel; <sup>2</sup> Holon Institute of Technology (HIT), Holon, Israel</p>
  <p class="corr">* Correspondence: apersteiny@afeka.ac.il</p>
</header>
'''
appendix_out = remap_refs(appendix_html)
# (1) relabel the SI's own figures (plain 18/26) to the S-series, captions + refs
appendix_out = apply_fig_refmap(appendix_out, APP_FIG_MAP)
appendix_out = remap_fig_lists(appendix_out, APP_FIG_MAP)   # plural SI-own refs
# (2) remaining plain 'Figure N'/'Table N' in the SI are references to MAIN items;
#     remap them to the renumbered main numbers so cross-refs stay correct.
appendix_out = apply_fig_refmap(appendix_out, fmap)
appendix_out = remap_fig_lists(appendix_out, fmap)          # plural main-figure refs
appendix_out = apply_tab_refmap(appendix_out, tmap)
# (3) the CFG-scale quantile table in the source (Section D.8) has no caption;
#     add one for MDPI compliance.
appendix_out = re.sub(
    r'(<table[^>]*>)(\s*<thead>\s*<tr>\s*<th>\s*Property\s*</th>)',
    r'\1<caption><strong>Table&nbsp;D.3a.</strong> Per-property quantile-match error '
    r'(mean relative error, %) for the v4b production-architecture classifier-free '
    r'guidance-scale sweep, at guidance scales g = 2.0, 5.0, and 7.0; lower is '
    r'better.</caption>\2',
    appendix_out, count=1)
# retitle the "Appendix" h2 to a supplementary heading
appendix_out = re.sub(r'<h2 id="sec-app">Appendix</h2>',
                      '<h2>Supplementary Notes</h2>', appendix_out, count=1)
appendix_out = appendix_out.replace('src="figs/', 'src="../figs/')
appendix_out = re.sub(r'<!--.*?-->', '', appendix_out, flags=re.DOTALL)
appendix_out = to_si_units(appendix_out)
full_si = HEAD + SI_DOWNLOADS_ASIDE + SI_TITLE + appendix_out + "\n" + refs_out + TAIL
full_si = _normalize_cites(full_si)       # citation-order renumber (SI order)

# Renumber the Supplementary tables (appendix lettering -> Table S1, S2, ...) in
# both documents, then write both.
full_main, full_si = renumber_si_tables(full_main, full_si)
OUT_MAIN.write_text(full_main, encoding="utf-8")
OUT_SI.write_text(full_si, encoding="utf-8")

# ---------------------------------------------------------------------------
# 6) Verification report.
# ---------------------------------------------------------------------------
def audit(name, s):
    stale_para = re.findall(r'(?:§|&sect;)\s*[0-9A-F]', s)
    stale_appendix = re.findall(r'Appendix&nbsp;[A-F]', s)
    print(f"  {name}: {len(s):,} bytes")
    print(f"    stale section-glyph refs (SS...) : {len(stale_para)}")
    print(f"    leftover 'Appendix X' mentions   : {len(stale_appendix)}")

print("Wrote:")
audit(OUT_MAIN.name, full_main)
audit(OUT_SI.name, full_si)
print(f"  figures renumbered: {len(fmap)}  (map: {fmap})")
print(f"  tables renumbered : {len(tmap)}  (map: {tmap})")
