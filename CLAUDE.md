# DGLD4Energetic - project conventions for Claude

Project-scoped instructions. These override generic defaults.

## Paper deliverables: TWO documents, each as a main + SI pair

There are two HTML sources of record in `paper/`, each producing its own
main + SI Word pair via the `html2doc` skill:

### 1. Long-form preprint (`paper/long_paper.html`)

| File | Contents | Notes |
|---|---|---|
| `paper/long_paper.docx` | Title, authors, abstract, sections 1-7 (Intro through Conclusion), References. | Long-form preprint version (~14k words main text). |
| `paper/long_paper_SI.docx` | "Supplementary Information for: ..." title block, Appendix A-F, References (duplicated for self-containment). | Long-form preprint SI. |

Built by `paper/_split_html.py` -> html2doc pipeline.

### 2. Molecules submission (ACTIVE TARGET) (`paper/molecules/molecules_paper.html` + `_SI.html`)

The active submission target is an MDPI *Molecules* Article, generated from the
long-form preprint by `paper/molecules/build_molecules_html.py` (HTML) then
`build_molecules_docx.py` (Word, on the official `molecules-template.dot`):

| File | Contents |
|---|---|
| `paper/molecules/molecules_paper.docx` | MDPI Article: abstract, keywords, 1. Introduction, 2. Results, 3. Discussion, 4. Materials and Methods, 5. Conclusions, end matter. |
| `paper/molecules/molecules_paper_SI.docx` | Supplementary Information (Appendix A-F content; tables numbered Table S1..S29). |

Conventions: SI tables are the S-series (`build_molecules_html.py`); the long-form
preprint keeps its Appendix A-F lettering. Citations are renumbered per document
by first appearance. Rebuild both from `long_paper.html` whenever it changes:
`python build_molecules_html.py && python build_molecules_docx.py`.

GitHub Pages serves the Molecules page as the front (root `index.html` redirects
to `molecules_paper.html`), with a top-right download panel (main/SI docx, SI
html, cover letter).

The former **NMI-compliant submission is retired** to `paper/nmi_archive/`
(the project retargeted from Nature Machine Intelligence to Molecules).

Never produce a single combined Word file. Reviewers, editors, and the
journal's typesetting pipeline expect main + SI as separate files.

### How to build

```bash
cd paper
python _split_html.py                           # produces _body.html + _supplementary.html

SKILL=/c/Users/apart/.claude/skills/html2doc

for stem in body supplementary; do
  case $stem in
    body)          OUT=long_paper.docx ;;
    supplementary) OUT=long_paper_SI.docx ;;
  esac
  IN=_${stem}.html
  NODE_PATH="$SKILL/node_modules" node "$SKILL/scripts/katex_to_mathml.js" \
      --input "$IN" --output "_${stem}_mathml.html"
  python "$SKILL/scripts/convert_to_docx.py" \
      --input "_${stem}_mathml.html" --output "_${stem}_converted.docx" \
      --profile review-manuscript
  python "$SKILL/scripts/apply_academic_style.py" \
      --input "_${stem}_converted.docx" --output "$OUT" \
      --profile review-manuscript
  rm "_${stem}_mathml.html" "_${stem}_converted.docx"
done
```

The `review-manuscript` profile gives Times New Roman, 1.5x line spacing, and
auto-injects continuous line numbers (NMI/Nature/Science compatible). Both
files share these settings so reviewers see consistent formatting across main
and SI.

### What to commit

The two final Word files **are committed** so the published HTML paper can
serve them as downloads (top-right corner of `long_paper.html`, served by
GitHub Pages):

- `paper/long_paper.docx`
- `paper/long_paper_SI.docx`

Rebuild and re-commit both whenever `long_paper.html` changes. The HTML is
still the source of record; the .docx files are derived snapshots that need
to stay in sync.

### What NOT to commit

Build intermediates are gitignored (see `.gitignore`):

- `paper/_body.html`, `paper/_supplementary.html` (split intermediates)
- `paper/long_paper.pdf` (if produced)
- `paper/~$*.docx` (Word lock files while a doc is open)

## Author list

Two authors only: Yehudit Aperstein (Afeka), Alexander Apartsin (HIT). No
third author. If a third author surfaces during a chat, ask before adding -
this list is intentional.

## Math delimiters

The HTML uses KaTeX `\(...\)` for inline and `\[...\]` for display math. The
html2doc skill's `katex_to_mathml.js` handles both styles plus `$...$` and
`$$...$$`. Do not switch delimiter style without updating the rest of the
paper.

## Repository visibility

Public on GitHub at `github.com/ApartsinProjects/DGLD4Energetic`. Pages
deployed at `apartsinprojects.github.io/DGLD4Energetic/` (root index.html
redirects to `paper/long_paper.html`).
