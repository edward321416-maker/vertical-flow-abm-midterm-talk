# Revision 9: Korean interword spacing and natural reading flow

Date: 2026-11-14 (KST)

## What was checked

The Revision 8 XeLaTeX source retains spaces in the RQ3 original sentence, but the PDF's Korean two-column typography compresses or poorly represents visual spacing. This is a typesetting defect, not missing source spaces.

## Targeted correction

- Added explicit body interword glue: \spaceskip=3.2pt plus 1.5pt minus .4pt and \xspaceskip with the same parameters, immediately after the one-column title and abstract.
- Shortened the RQ3 opening into two explicit study questions, and protected a few meaningful terms with \mbox. Numeric findings and methodological interpretations were not changed.
- Tested CJKword no-break as an alternative but rejected it: it produced excessive gaps and worse justified text.
- Preserved original figures (7), tabularx environments (7), original TeX numeric tokens (706), A4 paper and 8 pages.

## Measured checks

- New PDF: 8 A4 pages, PDF 1.4 compatible.
- Text lines outside page bounds: 0.
- LaTeX Overfull \hbox: 0; Missing character: 0; Undefined control sequence: 0.
- Remaining Underfull \hbox warnings: 13, mostly narrow appendix tables or English text.
- PDF 1.4 conversion retained identical per-page extractable strings.
- **Limitation:** copied/extracted PDF Korean text may still merge some spaces; print/visual word spacing is the corrected scope.
- Proprietary official HWP font is still unavailable; Noto Serif CJK KR substitution remains.

## Provenance

Prior source: Revision 8 layout-corrected TeX (included with source patch in the local delivery package).
Underlying model and figures unchanged.
Previous Revision 8 commit: 4d722e6a9618b3c8f58116ede82f2b89a2d42d79.
