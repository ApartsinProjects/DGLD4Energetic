"""Split short_paper.html into a main-body HTML and a Supplementary HTML.

Project convention (see ../CLAUDE.md): every Word build for journal submission
produces two .docx files:

  - short_paper.docx       Main article: title, authors, abstract, sections
                           1-7, references.
  - short_paper_SI.docx    Supplementary Information: title (with "SI for:"
                           prefix), Appendix A-F, references (duplicated for
                           reviewer self-containment).

This script generates the two intermediate HTML files used as input to the
html2doc skill. It does not produce DOCX directly -- run the html2doc pipeline
on each output afterwards.

Usage:
    python _split_html.py
        Reads short_paper.html, writes _body.html and _supplementary.html.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "short_paper.html"
OUT_BODY = HERE / "_body.html"
OUT_SI = HERE / "_supplementary.html"

# Marker patterns. Each marker matches a unique line in the source so we can
# split deterministically without a full HTML parser. Update if the source
# headings ever change.
APPENDIX_OPEN = re.compile(r'<h2 id="sec-app">Appendix</h2>')
REFERENCES_OPEN = re.compile(r'<h2 id="sec-refs">References</h2>')


def find_line_index(lines: list[str], pattern: re.Pattern) -> int:
    for i, line in enumerate(lines):
        if pattern.search(line):
            return i
    raise RuntimeError(f"marker not found: {pattern.pattern}")


def strip_html_only_chrome(text: str) -> str:
    """Remove HTML-only UI elements that don't belong in the Word builds.

    Currently strips the top-right "Word downloads" aside from short_paper.html
    so the .docx outputs don't carry self-referential download links.
    """
    return re.sub(
        r'<aside class="downloads"[\s\S]*?</aside>\s*',
        "",
        text,
        count=1,
    )


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    text = strip_html_only_chrome(text)
    lines = text.splitlines(keepends=True)

    # Locate the three structural breakpoints
    head_close = next(i for i, l in enumerate(lines) if "</head>" in l) + 1
    body_close = next(i for i, l in enumerate(lines) if "</body>" in l)
    appendix_at = find_line_index(lines, APPENDIX_OPEN)
    references_at = find_line_index(lines, REFERENCES_OPEN)

    # Region map (half-open ranges into `lines`):
    #   prelude   = [0, head_close)                 doctype + head + opening tags
    #   header    = [head_close, abstract_start)    we keep as-is for body, rewrite title for SI
    #   main_body = [head_close, appendix_at)       header + abstract + sections 1-7
    #   appendix  = [appendix_at, references_at)    Appendix A-F
    #   refs      = [references_at, body_close)     References list
    #   tail      = [body_close, end)               </body></html>

    prelude = "".join(lines[:head_close])
    main_body = "".join(lines[head_close:appendix_at])
    appendix = "".join(lines[appendix_at:references_at])
    refs = "".join(lines[references_at:body_close])
    tail = "".join(lines[body_close:])

    # Body file: everything except the appendix
    body_html = prelude + main_body + refs + tail
    OUT_BODY.write_text(body_html, encoding="utf-8")
    print(f"  wrote {OUT_BODY.name} ({len(body_html):,} bytes)")

    # Supplementary file: original prelude (so styles + math rendering stay
    # identical) + a rewritten title block + appendix + references.
    # The original <header class="title"> is re-derived from the source so
    # author/affiliation order matches exactly.
    title_match = re.search(
        r'<header class="title">.*?</header>',
        text, flags=re.DOTALL,
    )
    if title_match is None:
        raise RuntimeError("could not locate <header class='title'> in source")
    si_header = title_match.group(0).replace(
        "<h1>",
        '<p style="font-size:0.95rem; letter-spacing:.04em; text-transform:uppercase; '
        'color:#27445d; margin-bottom:.2em;">Supplementary Information for</p>\n  <h1>',
        1,
    )

    si_html = prelude + si_header + "\n" + appendix + refs + tail
    OUT_SI.write_text(si_html, encoding="utf-8")
    print(f"  wrote {OUT_SI.name} ({len(si_html):,} bytes)")


if __name__ == "__main__":
    main()
