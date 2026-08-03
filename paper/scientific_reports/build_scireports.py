#!/usr/bin/env python
"""Reformat the MDPI Molecules main article into a Scientific Reports (Nature
Portfolio) HTML manuscript.

SOURCE OF TRUTH: paper/molecules/molecules_paper.html (content is copied
verbatim; only STRUCTURE/LABELS change). Nothing scientific is added or removed.

Structural transforms (Scientific Reports guidelines, read 2026-08 from
nature.com/srep/author-instructions/submission-guidelines):
  1. Keywords trimmed 11 -> 6 (journal limit).
  2. Discussion 'Limitations' subheading -> bold run-in (Discussion without
     subheadings, per Nature style).
  3. 'Conclusions' section folded into the end of Discussion (Nature style: no
     separate Conclusions; Methods becomes the last narrative section). This
     keeps Methods at section 4 and Discussion at section 3, so every numbered
     'Section N' cross-reference stays valid. The single self-referential
     '(Section 5)' inside the folded text is repointed to the Data Availability
     statement.
  4. 'Materials and Methods' -> 'Methods'.
  5. Back-matter rebuilt in Nature order: Data Availability (kept verbatim),
     Code Availability (NEW - required boilerplate, derived from the existing
     Zenodo/GitHub facts), Author Contributions (kept), Competing Interests
     (renamed from 'Conflicts of Interest', text kept), Funding (kept),
     Acknowledgements incl. required LLM-use disclosure (NEW - required
     boilerplate). MDPI-only 'Supplementary Materials', 'Institutional Review
     Board Statement', and 'Informed Consent Statement' (all N/A) are dropped.
  6. References kept last, verbatim (Nature square-bracket numbered style, which
     the source already uses).

All added text is confined to items (5) marked NEW and the bold run-in labels;
the audit script build_verify.py checks that every source text block survives
and that every output block is either from the source or a declared addition.
"""
import re, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "molecules" / "molecules_paper.html"
OUT = HERE / "scireports_paper.html"

src = SRC.read_text(encoding="utf-8")

# ---- split into front (before first <h2>) + section chunks -----------------
first_h2 = src.index("<h2")
front = src[:first_h2]
rest = src[first_h2:]
# chunks each begin with a <h2 ...>
chunks = re.split(r'(?=<h2[ >])', rest)
def label(chunk):
    m = re.match(r'<h2[^>]*>\s*(.*?)</h2>', chunk, re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ""
sec = {label(c): c for c in chunks if c.strip()}

def need(name):
    if name not in sec:
        raise SystemExit(f"section not found: {name!r}; have {list(sec)}")
    return sec[name]

intro   = need("1. Introduction")
results = need("2. Results")
disc    = need("3. Discussion")
methods = need("4. Materials and Methods")
concl   = need("5. Conclusions")
refs    = need("References")

# ---- (1) keywords: 11 -> 6 -------------------------------------------------
kw_old_re = re.compile(r'<p class="keywords">.*?</p>', re.S)
assert kw_old_re.search(front), "keywords block not found"
kw_new = ('<p class="keywords"><span class="lab">Keywords:</span> generative models; '
          'latent diffusion; inverse molecular design; energetic materials; '
          'density functional theory; data-driven discovery</p>')
front = kw_old_re.sub(kw_new, front, count=1)

# ---- (2) Discussion 'Limitations' subheading -> bold run-in ----------------
disc, n = re.subn(r'<h3[^>]*>\s*3\.1\.?\s*Limitations\s*</h3>\s*<p>',
                  '<p><strong>Limitations.</strong> ', disc, count=1)
assert n == 1, "Limitations subheading not found/!=1"

# ---- (3) fold Conclusions into end of Discussion ---------------------------
# strip the <h2>5. Conclusions</h2> header, keep the paragraphs
concl_body = re.sub(r'^<h2[^>]*>\s*5\.\s*Conclusions\s*</h2>\s*', '', concl, count=1)
# repoint the lone self-referential "(Section 5)" -> Data Availability
concl_body = concl_body.replace('code bundle on Zenodo (Section&nbsp;5)',
                                'code bundle on Zenodo (see the Data Availability statement)')
# bold run-in on the first paragraph so Discussion carries no subheading
concl_body = re.sub(r'^\s*<p>', '<p><strong>Conclusions.</strong> ', concl_body, count=1)
disc = disc.rstrip() + "\n\n" + concl_body.strip() + "\n"

# ---- (4) Materials and Methods -> Methods ----------------------------------
methods = re.sub(r'(<h2[^>]*>\s*4\.\s*)Materials and Methods(\s*</h2>)',
                 r'\1Methods\2', methods, count=1)

# ---- (5) new Scientific Reports back-matter --------------------------------
data_avail = need("Data Availability Statement")
# keep the DA statement verbatim
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
acks = (
'<h2>Acknowledgements</h2>\n'
'<p>The authors used a large language model (Anthropic Claude) to assist with '
'source-code development and manuscript copy-editing. All study design, '
'analyses, results, and conclusions are the authors’ own, and the authors '
'take full responsibility for the content of the manuscript.</p>\n')

backmatter = (data_avail.rstrip() + "\n\n" + code_avail + "\n"
              + author_contrib.rstrip() + "\n\n" + competing + "\n"
              + funding.rstrip() + "\n\n" + acks)

# ---- reassemble ------------------------------------------------------------
# front already ends before the first <h2>; sections carry their own trailing ws.
body = (front.rstrip() + "\n\n"
        + intro.rstrip() + "\n\n"
        + results.rstrip() + "\n\n"
        + disc.rstrip() + "\n\n"
        + methods.rstrip() + "\n\n"
        + backmatter.rstrip() + "\n\n"
        + refs.rstrip() + "\n")

# ---- head/title/aside cosmetics --------------------------------------------
body = body.replace('<title>', '<title>[Scientific Reports] ', 1)
# repoint the downloads aside to the Scientific Reports files
body = body.replace('molecules_paper.docx', 'scireports_paper.docx')
body = body.replace('molecules_paper_SI.docx', 'scireports_paper_SI.docx')
body = body.replace('molecules_paper_SI.html', 'scireports_paper_SI.html')

OUT.write_text(body, encoding="utf-8")

# quick self-report
def wc(s):
    return len(re.sub(r'<[^>]+>', ' ', s).split())
print(f"wrote {OUT.name}: {len(body):,} bytes")
print(f"  sections: 1 Introduction, 2 Results, 3 Discussion (+folded "
      f"Conclusions), 4 Methods, References")
print(f"  refs: {body.count(chr(60)+'li id=\"ref-')}")
print(f"  keywords: {kw_new.count(';')+1}")
