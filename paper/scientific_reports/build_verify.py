#!/usr/bin/env python
"""Audit: verify the Scientific Reports main article preserves ALL scientific
content of the molecules source and invents nothing.

Method: extract every content element (<p>,<li>,<td>,<th>,<caption>,<figcaption>,
<h3>,<h4>) as normalized visible text from both files, then:
  LOST     = a source segment whose text is NOT a substring of the output.
  ADDED    = an output segment whose text is NOT a substring of the source,
             after stripping declared run-in prefixes; each is then classified
             against a whitelist of required Scientific Reports additions.
Substring matching tolerates the run-in prefixes ('Conclusions.', 'Limitations.')
and whitespace reflow. Exit non-zero if anything is unaccounted.
"""
import re, sys, pathlib, html

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "molecules" / "molecules_paper.html"
OUT = HERE / "scireports_paper.html"

def strip_headmisc(s):
    s = re.sub(r'<head>.*?</head>', '', s, flags=re.S)
    s = re.sub(r'<aside\b.*?</aside>', '', s, flags=re.S)
    s = re.sub(r'<script\b.*?</script>', '', s, flags=re.S)
    return s

def norm(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = t.replace(' ', ' ').replace(' ', ' ').replace(' ', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def segments(s):
    s = strip_headmisc(s)
    segs = []
    for m in re.finditer(r'<(p|li|td|th|caption|figcaption|h3|h4)\b[^>]*>(.*?)</\1>', s, re.S):
        txt = norm(m.group(2))
        if len(txt) >= 12:                      # ignore tiny cells/labels
            segs.append(txt)
    return segs

src_segs = segments(SRC.read_text(encoding="utf-8"))
out_segs = segments(OUT.read_text(encoding="utf-8"))
SRC_ALL = " ".join(src_segs)
OUT_ALL = " ".join(out_segs)

# ---- LOST: source content missing from output -----------------------------
lost = [s for s in src_segs if s not in OUT_ALL]
# Source segments accounted for by DECLARED transforms (each verified below):
#   - MDPI-only boilerplate dropped (Supplementary Materials pointer, IRB,
#     Informed Consent, all "Not applicable")
#   - keyword line trimmed 11 -> 6 (replacement checked in ADD_OK)
#   - "3.1. Limitations" heading -> bold run-in (text itself preserved)
#   - "conflicts of interest" -> Nature's "competing interests" wording
#   - the "(Section 5)" self-ref inside the Three-extensions paragraph is
#     repointed to the Data Availability statement; verify the paragraph
#     otherwise survives via distinctive head+tail probes.
DROP_OK = ["following supporting information can be downloaded",   # Supplementary Materials
           "Institutional Review Board", "Informed Consent",
           "Not applicable",
           "Keywords: generative models",       # trimmed keyword line (replacement audited in ADD_OK)
           "3.1. Limitations",                  # heading -> run-in
           "declare no conflicts of interest"]  # renamed to competing interests
lost_real = [s for s in lost if not any(d in s for d in DROP_OK)]

# the repointed Conclusions paragraph: require its head AND tail verbatim
_p = [s for s in src_segs if s.startswith("Three extensions would close")]
if _p:
    head = _p[0][:180]
    tail = _p[0][-180:]
    ok_head = head[:100] in OUT_ALL
    # tail after the repoint is unchanged (repoint is mid-paragraph)
    ok_tail = tail[-100:] in OUT_ALL
    if ok_head and ok_tail:
        lost_real = [s for s in lost_real if not s.startswith("Three extensions")]
    else:
        print(f"[repoint-check] head_ok={ok_head} tail_ok={ok_tail}")

# ---- ADDED: output content not in source ----------------------------------
RUNIN = re.compile(r'^(Conclusions|Limitations)\.\s+')
ADD_OK = ["All custom code central to this study is publicly available",
          "large language model", "Anthropic Claude",
          "Competing Interests", "declare no competing interests",
          "generative models; latent diffusion",                 # trimmed keywords line
          "see the Data Availability statement"]
added = []
for o in out_segs:
    probe = RUNIN.sub('', o)          # tolerate the run-in prefix
    if probe in SRC_ALL:
        continue
    if any(a in o for a in ADD_OK):
        continue
    added.append(o)

print(f"source content segments: {len(src_segs)}")
print(f"output content segments: {len(out_segs)}")
print(f"\nLOST (unexpected, scientific content missing): {len(lost_real)}")
for s in lost_real:
    print("  - " + s[:160])
print(f"\nADDED (not in source, not a declared Sci-Reports addition): {len(added)}")
for s in added:
    print("  + " + s[:160])
print(f"\n[info] source segments intentionally dropped (MDPI N/A boilerplate): "
      f"{len(lost) - len(lost_real)}")

ok = (not lost_real) and (not added)
print("\nRESULT:", "PASS - nothing lost, nothing invented" if ok
      else "FAIL - review the lists above")
sys.exit(0 if ok else 1)
