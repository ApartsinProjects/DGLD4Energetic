#!/usr/bin/env python
"""Audit: the Scientific Reports pair (main + SI) must preserve ALL scientific
content of the Molecules pair (main + SI) and invent nothing beyond the
declared additions in build_scireports.py.

Content universe = main+SI union on each side. Because the build RENUMBERS
figures/tables/citations and adds "Supplementary" prefixes, both sides are
normalized before comparison: figure/table pointers and [n] citation labels
collapse to placeholder tokens, so a segment matches iff its scientific text
is identical modulo the declared renumbering.

Checks:
  1. LOST:   source segments absent from the derived union (beyond declared drops)
  2. ADDED:  derived segments absent from the source union (beyond declared adds)
  3. REFS:   every source citation KEY survives somewhere in the derived pair;
             no derived key is new; per-entry DOIs preserved.
Exit non-zero on any failure.
"""
import re, sys, pathlib, html

HERE = pathlib.Path(__file__).resolve().parent
MOL = HERE.parent / "molecules"

def read(p): return p.read_text(encoding="utf-8")
src_main = read(MOL / "molecules_paper.html")
src_si   = read(MOL / "molecules_paper_SI.html")
out_main = read(HERE / "scireports_paper.html")
out_si   = read(HERE / "scireports_paper_SI.html")

def strip_headmisc(s):
    s = re.sub(r'<head>.*?</head>', '', s, flags=re.S)
    s = re.sub(r'<aside\b.*?</aside>', '', s, flags=re.S)
    return s

def norm(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    for ch in (' ', ' ', '–', '—'):
        t = t.replace(ch, ' ')
    # --- renumbering-aware canonicalisation (both sides) ---
    t = re.sub(r'\[\d+\]', '⟨C⟩', t)                                   # citation labels
    # "main "/"main-text " prefixes and "Figs"/"Fig."/"Figures" all collapse
    t = re.sub(r'(?:main(?:-text)? )?(?:Supplementary )?(?:Figures?|Figs?\.?)\s*S?\d+[a-z]?', '⟨F⟩', t)
    t = re.sub(r'(?:main(?:-text)? )?(?:Supplementary )?Tables?\s*S?\d+[a-z]?', '⟨T⟩', t)
    # collapse ranges/lists, incl. residual bare endpoints ("⟨F⟩ 22", "⟨F⟩ S21")
    t = re.sub(r'⟨F⟩(\s*(?:and|,|–|-|to)?\s*(?:⟨F⟩|S?\d+))+', '⟨F⟩', t)
    t = re.sub(r'⟨T⟩(\s*(?:and|,|–|-|to)?\s*(?:⟨T⟩|S?\d+))+', '⟨T⟩', t)
    # declared SI-note heading demotion: "1.1.N Title" and "N.N Title" -> "Title"
    t = re.sub(r'^(?:1\.1\.|N\.)(\d)\s+', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def segments(s, include_refs=False):
    s = strip_headmisc(s)
    if not include_refs:
        s = re.sub(r'<ol class="refs">.*?</ol>', '', s, flags=re.S)
    segs = []
    for m in re.finditer(r'<(p|li|td|th|caption|figcaption|h3|h4)\b[^>]*>(.*?)</\1>', s, re.S):
        txt = norm(m.group(2))
        if len(txt) >= 12:
            segs.append(txt)
    return segs

src_segs = segments(src_main) + segments(src_si)
out_segs = segments(out_main) + segments(out_si)
SRC_ALL = " ".join(src_segs)
OUT_ALL = " ".join(out_segs)

# ---- 1. LOST ---------------------------------------------------------------
DROP_OK = [
    "following supporting information can be downloaded",  # MDPI SI pointer
    "Institutional Review Board", "Informed Consent", "Not applicable",
    "Keywords: generative models",       # trimmed keyword line (replacement in ADD_OK)
    "3.1. Limitations",                  # heading -> run-in
    "declare no conflicts of interest",  # -> competing interests wording
    "Abstract: Designing high-energy-density materials",  # replaced by trimmed abstract
    "1.1. Related Work",                 # heading re-emitted in summary
    "DGLD draws on, and departs from",   # 2-sentence intro of old 1.1 (covered by summary)
    "DGLD sits at the intersection of three lines of work",  # old 1.1 framing para (summary covers)
    "footnote between",                  # dagger pointer reworded for SI numbering
    "on Zenodo (Section",                # repointed self-ref (tail check below)
    "Abstract: Designing high-energy-density materials",  # source abstract -> rewritten (ADD_OK)
    "DGLD is a four-stage pipeline",     # pipeline-map sentence rewritten (ADD_OK)
    "We assemble the training data",     # (superseded anchor, kept harmless)
    "Available property labels in the energetic-materials literature",  # Table 3 citation inserted
    "All code, data, and trained models are released together",          # GitHub mirror sentence dropped
    "labelled master, Section",          # SI "Section 5" -> Data Availability
    # --- Tier-1 editorial revisions (source side) ---
    "Energetic-materials performance gains translate directly into reduced propellant mass",  # T1.1
    "Section 2 is structured results-first",                       # T1.2/T5.2 target framing
    "Pool-size dependence",                       # T5.1 reframed to gate robustness
    "The SC head is retained as an architectural slot",  # T5.2 dead-code line removed
    "expected by NMI reviewers",                  # T5.3 wrong-journal leftover removed
    "Because guiding generation with gradients",  # T5.4 grammar + framing
    # ---- T6 SI polish (source side) ----
    "not yet supported in the gpu4pyscf release",   "doubles the compute time and was deferred",
    "2-anchor fit (RDX/TATB only) is under-determined",
    "within-cluster scale magnitude does not alter",
    "Within each cluster, per-head scale magnitude does not alter",
    "standard ZINC drug-like negatives we used",
    "does not re-emerge at the larger sample size",
    "The guidance patching of Section",
    "was added to test whether sample-time gradient",
    "The cost of retaining is low",
    "Neither route is authoritative for a novel chemotype",
    "6-anchor calibration",                                        # T1.3 density caveat added
    "Of the merged top-100, 96/97 are absent from PubChem",        # T1.4 lead-role reframe
    "E1 oxatriazole: independent recovery of a known structure",   # T1.5 verdict unified
    "C.9 Bondi-vdW packing-factor bracket",                        # T1.6 raw/calibrated scales labelled
    "the relative ranking shows L1, L4, L5 are RDX-class",         # T4 corrected at full coverage
    "An independent Cantera ideal-gas CJ recompute ranks L1",      # T4 main-text companion
    "as an independent relative-ranking sanity check",             # T4 C.13 opener re-scoped
    "The Uni-Mol surrogate is well-calibrated on the labelled distribution",  # T1.6 pk arithmetic corrected
]
lost = [s for s in src_segs if s not in OUT_ALL
        and not any(d in s for d in DROP_OK)]
# repointed Conclusions paragraph: verify head+tail survive
_p = [s for s in src_segs if s.startswith("Three extensions would close")]
if _p and _p[0] not in OUT_ALL:
    if _p[0][:100] in OUT_ALL and _p[0][-100:] in OUT_ALL:
        lost = [s for s in lost if not s.startswith("Three extensions")]

# ---- 2. ADDED --------------------------------------------------------------
RUNIN = re.compile(r'^(Conclusions|Limitations)\.\s+')
ADD_OK = [
    # declared new prose (build_scireports.py):
    "Energetic materials power mining, demolition",   # rewritten <=200-w plain-language abstract
    "generative models; latent diffusion; inverse molecular design; energetic",
    "an extended survey is given in the Supplementary Note",   # summary para 1
    "On the property side, the Kamlet",                        # summary para 2
    "Evaluation and validation draw on MOSES",                 # summary para 3
    "All custom code central to this study is publicly available",
    "Use of large language models", "Anthropic Claude",
    "declare no competing interests",
    "see the Data Availability statement",
    "Supplementary Note: Extended Related Work",
    "Supplementary Note and migrated display items",
    "The following display items support the main text",
    "⟨F⟩ S23 and ⟨T⟩ S35",                                     # migrated-items section header
    "footnote below",                                          # reworded dagger pointer
    "per-stage panels in",              # pipeline-map sentence: mixed kept/moved range made explicit
    "carries one of the following tiers",   # added main-body citation of Table 3
    "Taken together, these contributions sit on three axes",  # Collection scope statement (closes Intro)
    # --- Tier-1 editorial revisions (derived side) ---
    "launch and mining applications",          # T1.1 civilian-first framing
    "placing it in the HMX/PETN band",         # T1.2/T5.2 anchor-relative framing
    "Pool-size robustness",                    # T5.1 gate holds across pool size
    "serve as multi-task trunk regularisers",  # T5.2 released-configuration statement
    "standard in the distribution-learning literature",  # T5.3 journal-neutral
    "grounds the steering signal in measured",  # T5.4 literature-grounded head
    # ---- T6 SI polish (derived side) ----
    "absorbed by the 6-anchor calibration",  "at twice the compute cost",
    "spans the nitramine, nitroaromatic",
    "independent on/off levers over chemistry",
    "invariant to per-head scale magnitude",
    "own posterior teach a gradient that generic",
    "gives the stable estimate used throughout",
    "production guidance configuration of Section",
    "quantifies the domain-transfer penalty",
    "act as multi-task trunk regularisers: each contributes",
    "bracket L1 at 30",
    "largest single uncertainty in the paper", # T1.3 density caveat promoted to Results
    "single synthesis-actionable lead",        # T1.4 L1-vs-scaffold-diversity roles
    "single role throughout this paper",       # T1.5 unified E1 verdict (replaced an either/or)
    "raw (pre-calibration)",                   # T1.6 SI bracket scale labelled
    "their orderings are independent (Spearman",  # T4 measured Spearman -0.62 (SI C.13)
    "product-composition and energy-release cross-check",  # T4 C.13 opener re-scoped
    "characterises the product-gas composition and energy release",  # T4 SI C.13 rewrite
    "resolves a distinct axis from Kamlet",  # T4 main-text companion
    "on the calibrated scale, equivalently the raw Bondi value",  # T1.6 main-text scale + 1.97->1.94
    "single archived package on Zenodo",    # Data Availability minus the GitHub mirror
    "inside the archived Zenodo package",   # Code Availability minus the GitHub mirror
]
added = []
for o in out_segs:
    probe = RUNIN.sub('', o)
    if probe in SRC_ALL:
        continue
    if any(a in o for a in ADD_OK):
        continue
    added.append(o)

# ---- 3. references ---------------------------------------------------------
def keys(s):
    m = re.search(r'<ol class="refs">(.*?)</ol>', s, re.S)
    return dict((k, v) for k, v in
                ((mm.group(1), mm.group(0)) for mm in
                 re.finditer(r'<li id="(ref-[a-z0-9-]+)">.*?</li>', m.group(1), re.S)))
src_keys = set(keys(src_main)) | set(keys(src_si))
out_keys = set(keys(out_main)) | set(keys(out_si))
refs_lost = sorted(src_keys - out_keys)
refs_new  = sorted(out_keys - src_keys)
# DOI preservation per surviving key
def dois(s):
    out = {}
    m = re.search(r'<ol class="refs">(.*?)</ol>', s, re.S)
    for mm in re.finditer(r'<li id="(ref-[a-z0-9-]+)">(.*?)</li>', m.group(1), re.S):
        d = re.search(r'10\.\d{4,}/[^\s<"]+', mm.group(2))
        if d: out[mm.group(1)] = d.group(0).rstrip('.')
    return out
src_dois = {**dois(src_si), **dois(src_main)}
out_dois = {**dois(out_si), **dois(out_main)}
doi_mismatch = [k for k in (src_keys & out_keys)
                if k in src_dois and out_dois.get(k) not in (None, src_dois[k])]

print(f"source segments: {len(src_segs)} | derived segments: {len(out_segs)}")
print(f"\nLOST (scientific content missing from main+SI union): {len(lost)}")
for s in lost: print("  - " + s[:150])
print(f"\nADDED (not in source, not declared): {len(added)}")
for s in added: print("  + " + s[:150])
print(f"\nREFS lost: {refs_lost or 'none'} | new: {refs_new or 'none'} | "
      f"DOI mismatches: {doi_mismatch or 'none'}")

ok = not lost and not added and not refs_lost and not refs_new and not doi_mismatch
print("\nRESULT:", "PASS - nothing lost, nothing invented" if ok else "FAIL")
sys.exit(0 if ok else 1)
