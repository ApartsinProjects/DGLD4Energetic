#!/usr/bin/env python
"""Build the MDPI Molecules Word pair from the molecules HTML sources.

One reproducible command for the docx half of the Molecules deliverable:

  1. molecules-template.dot -> _molecules_template.docx
     (MDPI ships the template with a Word *template* content-type that
     python-docx refuses to open; we flip that one content-type override so the
     package loads as a normal document. Style/front-matter content is
     untouched.)
  2. html2doc mdpi_from_html.py: transplant each HTML body onto the MDPI styles
     (native OMML equations, embedded figures, MDPI paragraph styles).
  3. _mdpi_frontmatter.py: move the real title/authors/affiliations/abstract/
     keywords into the template's MDPI_1.x front-matter styles and drop the
     placeholder + editorial-note duplicates.

Run:  python build_molecules_docx.py
Prereq: build_molecules_html.py has been run (molecules_paper*.html exist) and
the html2doc skill is installed at ~/.claude/skills/html2doc.
"""
import subprocess, sys, zipfile, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SKILL = pathlib.Path.home() / ".claude" / "skills" / "html2doc"
MDPI_FROM_HTML = SKILL / "scripts" / "mdpi_from_html.py"
NODE_MODULES = SKILL / "node_modules"

DOT = HERE / "molecules-template.dot"
TEMPLATE_DOCX = HERE / "_molecules_template.docx"   # build intermediate (gitignored)
PAIRS = [
    ("molecules_paper.html",    "molecules_paper.docx"),
    ("molecules_paper_SI.html", "molecules_paper_SI.docx"),
]

TPL_CT = b"application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"
DOC_CT = b"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"

def dot_to_docx(dot_path, out_path):
    zin = zipfile.ZipFile(dot_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == "[Content_Types].xml":
                data = data.replace(TPL_CT, DOC_CT)
            zout.writestr(it, data)
    print(f"template: {dot_path.name} -> {out_path.name}")

def run(cmd, env_node=False):
    import os
    env = dict(os.environ)
    if env_node:
        env["NODE_PATH"] = str(NODE_MODULES)
    r = subprocess.run(cmd, cwd=str(HERE), env=env)
    if r.returncode != 0:
        sys.exit(f"step failed: {' '.join(str(c) for c in cmd)}")

def main():
    if not DOT.exists():
        sys.exit(f"missing MDPI template: {DOT}")
    for src, _ in PAIRS:
        if not (HERE / src).exists():
            sys.exit(f"missing {src} - run build_molecules_html.py first")

    dot_to_docx(DOT, TEMPLATE_DOCX)
    py = sys.executable
    for src, out in PAIRS:
        print(f"\n=== {src} -> {out} ===")
        run([py, str(MDPI_FROM_HTML), "--input", src, "--output", out,
             "--template", str(TEMPLATE_DOCX)], env_node=True)
        run([py, str(HERE / "_mdpi_frontmatter.py"), src, out])
    print("\nBuilt: molecules_paper.docx, molecules_paper_SI.docx")

if __name__ == "__main__":
    main()
