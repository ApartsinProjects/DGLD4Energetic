# DGLD4Energetic - project conventions for Claude

Project-scoped instructions. These override generic defaults.

## Paper deliverables: TWO documents, each as a main + SI pair

There are two HTML sources of record in `paper/`, each producing its own
main + SI Word pair via the `html2doc` skill:

### 1. Long-form preprint (`paper/short_paper.html`)

| File | Contents | Notes |
|---|---|---|
| `paper/short_paper.docx` | Title, authors, abstract, sections 1-7 (Intro through Conclusion), References. | Long-form preprint version (~14k words main text). |
| `paper/short_paper_SI.docx` | "Supplementary Information for: ..." title block, Appendix A-F, References (duplicated for self-containment). | Long-form preprint SI. |

Built by `paper/_split_html.py` -> html2doc pipeline.

### 2. NMI-compliant submission (`paper/NMIPaper.html` + `paper/NMIPaperSI.html`)

| File | Contents | Notes |
|---|---|---|
| `paper/NMIPaper.docx` | NMI Article: title, authors, affiliations, abstract (<=150 w), bold first paragraph, unheaded introduction, Results (subheaded), Discussion (no subheadings), References (50 max), inline Table 1, 5 main figures, Methods (with subheadings; Data + Code availability at end), Methods references, Acknowledgements, Funding, Author contributions, Competing interests, Additional information, Extended Data legends (10 max). Main text ~2,500 words; whole document fits NMI Article limits. | Submission-ready manuscript. |
| `paper/NMIPaperSI.docx` | "Supplementary Information for: ..." title block, full Appendix A-F (the long-form's appendix lifted verbatim), References. | Submission-ready Supplementary Information. |

Built directly by html2doc on each of `NMIPaper.html` and `NMIPaperSI.html`
(no splitter needed; each HTML is already self-contained).

### NMI limits (verified)

| Metric | NMI limit | DGLD's NMI version |
|---|---|---|
| Abstract | <=150 words | 134 |
| Bold first paragraph | 75-100 words | 84 |
| Main text (intro + Results + Discussion) | <=3,500 words | 2,462 |
| References | ~50 recommended | exactly 50 |
| Display items in main | 6 max | 5 figures + 1 table = 6 |
| Extended Data items | 10 max | 9 figures + 1 table = 10 |

Both pairs are committed so GitHub Pages serves all four `.docx` files as
downloads from `paper/short_paper.html` (top-right corner).

Never produce a single combined Word file. Reviewers, editors, and the
journal's typesetting pipeline expect main + SI as separate files.

### How to build

```bash
cd paper
python _split_html.py                           # produces _body.html + _supplementary.html

SKILL=/c/Users/apart/.claude/skills/html2doc

for stem in body supplementary; do
  case $stem in
    body)          OUT=short_paper.docx ;;
    supplementary) OUT=short_paper_SI.docx ;;
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
serve them as downloads (top-right corner of `short_paper.html`, served by
GitHub Pages):

- `paper/short_paper.docx`
- `paper/short_paper_SI.docx`

Rebuild and re-commit both whenever `short_paper.html` changes. The HTML is
still the source of record; the .docx files are derived snapshots that need
to stay in sync.

### What NOT to commit

Build intermediates are gitignored (see `.gitignore`):

- `paper/_body.html`, `paper/_supplementary.html` (split intermediates)
- `paper/short_paper.pdf` (if produced)
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
redirects to `paper/short_paper.html`).
