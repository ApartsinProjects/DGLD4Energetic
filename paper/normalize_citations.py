#!/usr/bin/env python
"""Citation-order bibliography normalization for the DGLD paper HTML.

Numbers references by order of first appearance in the text (Vancouver / Nature /
MDPI numbered style): every inline <a class="cite" href="#ref-KEY">[...]</a> is
renumbered to a sequential integer, and the <ol class="refs"> entries are
reordered to match. Refs never cited in the document (should be none) are
appended in their original order after the cited ones.

Must be run PER DOCUMENT: the long paper and the Molecules version order their
sections differently, so their first-appearance sequences differ.

Reusable: `from normalize_citations import normalize`  ->  normalize(html_str).
CLI: `python normalize_citations.py <file.html>` rewrites the file in place.
"""
import re, sys, pathlib

CITE = re.compile(r'<a class="cite" href="#(ref-[a-z0-9-]+)">\[[^\]]*\]</a>')
LI   = re.compile(r'<li id="(ref-[a-z0-9-]+)">.*?</li>', re.S)

def normalize(html, keep_uncited=True):
    m = re.search(r'<ol class="refs">(.*?)</ol>', html, re.S)
    if not m:
        raise SystemExit("no <ol class=\"refs\"> reference list found")
    list_start = m.start()
    body = html[:list_start]              # first-appearance is measured over the body only

    # 1) first-appearance order of cited refs
    order, seen = [], set()
    for cm in CITE.finditer(body):
        k = cm.group(1)
        if k not in seen:
            seen.add(k); order.append(k)

    # 2) uncited-but-listed refs: keep them (default) or drop them. Dropping gives a
    #    Vancouver-compliant "every listed reference is cited in text" list; used for the
    #    Molecules main document, where SI-only citations must not appear in the main list.
    listed = LI.findall(m.group(1))
    if keep_uncited:
        for k in listed:
            if k not in seen:
                seen.add(k); order.append(k)
    num = {k: i + 1 for i, k in enumerate(order)}

    # 3) reorder the <li> entries to the new numbering (dropping any not in `order`)
    items = {mm.group(1): mm.group(0) for mm in LI.finditer(m.group(1))}
    missing = [k for k in order if k not in items]
    if missing:
        raise SystemExit(f"cited refs absent from the list: {missing[:5]}")
    new_list = "\n".join(items[k] for k in order)
    html = html[:m.start(1)] + "\n" + new_list + "\n" + html[m.end(1):]

    # 4) renumber every inline citation display (whole document)
    html = CITE.sub(lambda cm: f'<a class="cite" href="#{cm.group(1)}">[{num[cm.group(1)]}]</a>',
                    html)
    return html

if __name__ == "__main__":
    p = pathlib.Path(sys.argv[1])
    out = normalize(p.read_text(encoding="utf-8"))
    p.write_text(out, encoding="utf-8")
    n = len(re.findall(r'<li id="ref-', out))
    print(f"normalized {p.name}: {n} references numbered by first appearance")
