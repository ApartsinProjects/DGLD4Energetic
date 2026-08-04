#!/usr/bin/env python
"""Produce REVIEW copies of the Scientific Reports pair with every editorial fix
highlighted in red.

The submission files stay clean: this writes *_marked.html alongside them.
Never submit the marked copies.

Source of truth for "what counts as a fix": the ADD_OK list in build_verify.py,
which is the audited register of every declared addition/rewrite made on top of
the Molecules source. Each phrase there anchors one edit, so we highlight the
enclosing sentence (or the whole block for the large rewrites).

Run: /c/Python314/python mark_fixes.py
"""
from __future__ import annotations
import re, pathlib

HERE = pathlib.Path(__file__).resolve().parent

# Pull the declared-additions register out of build_verify.py so the two files
# cannot drift apart.
vsrc = (HERE / "build_verify.py").read_text(encoding="utf-8")
m = re.search(r'ADD_OK = \[(.*?)\n\]', vsrc, re.S)
if not m:
    raise SystemExit("could not locate ADD_OK in build_verify.py")
PHRASES = [s for s in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
           if len(s) >= 12]
PHRASES = [p.encode().decode('unicode_escape') if '\\\\' in p else p for p in PHRASES]

CSS = """
<style id="fixmarks">
  mark.fix { background: #ffd6d6; box-shadow: 0 0 0 1px #e5484d inset;
             border-radius: 2px; padding: 0 .12em; }
  .fixbanner { position: sticky; top: 0; z-index: 99; background: #e5484d;
               color: #fff; font: 600 13px/1.5 system-ui, sans-serif;
               padding: .5rem .9rem; margin: 0 0 1rem; border-radius: .25rem; }
  @media print { .fixbanner { position: static; } }
</style>
"""
BANNER = ('<div class="fixbanner">REVIEW COPY &mdash; editorial fixes are '
          'highlighted in red. This is not the submission file; submit '
          'scireports_paper.docx / scireports_paper_SI.docx.</div>')

def mark(html: str) -> tuple[str, int]:
    """Highlight the sentence containing each declared fix phrase."""
    n = 0
    for ph in PHRASES:
        if ph not in html:
            continue
        start = 0
        while True:
            i = html.find(ph, start)
            if i < 0:
                break
            # already inside a mark?
            if html.rfind('<mark class="fix">', 0, i) > html.rfind('</mark>', 0, i):
                start = i + len(ph); continue
            # expand to sentence bounds, without crossing tags
            lo = i
            while lo > 0 and html[lo - 1] not in '>.' :
                lo -= 1
            hi = i + len(ph)
            while hi < len(html) and html[hi] not in '.<':
                hi += 1
            if hi < len(html) and html[hi] == '.':
                hi += 1
            seg = html[lo:hi]
            if '<' in seg or '>' in seg:      # keep it simple: mark the phrase only
                lo, hi, seg = i, i + len(ph), ph
            html = html[:lo] + '<mark class="fix">' + seg + '</mark>' + html[hi:]
            start = lo + len(seg) + 30
            n += 1
    return html, n

for stem in ("scireports_paper", "scireports_paper_SI"):
    src = HERE / f"{stem}.html"
    html = src.read_text(encoding="utf-8")
    html, n = mark(html)
    html = html.replace('</head>', CSS + '</head>', 1)
    html = re.sub(r'(<body[^>]*>)', r'\1\n' + BANNER, html, count=1)
    html = html.replace('<title>', '<title>[MARKED] ', 1)
    out = HERE / f"{stem}_marked.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out.name}: {n} fixes highlighted")
print(f"\n{len(PHRASES)} declared fixes tracked (from build_verify.py ADD_OK)")
