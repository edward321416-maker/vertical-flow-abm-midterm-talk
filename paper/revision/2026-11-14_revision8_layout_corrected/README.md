# Revision 8 — diagram clipping and Korean line-break correction

Audit date: 2026-11-14 (Asia/Seoul). This is a layout-only correction derived from the approved Revision 7 eight-page PDF. It is not a new experiment or external validation.

## Delivered artifacts
- `Thesis_Revision8_Fixed_8pages.pdf`: final A4, two-column, 8-page PDF (PDF 1.4, unencrypted).
- `Thesis_Revision8_Layout_Audit.pdf`: three-page before/after visual comparison and QA.
- `figures/fig1_concept.png`: concept diagram redrawn, complete right box and arrows outside text.
- `figures/fig_metric_sequence.png`: labels and box padding corrected.
- `figures/fig2_boundary.png`: nine-floor diagram redrawn with separate boundary labels.
- `figures/fig6_rq4.png`: four program-pattern rows re-laid out, cell text contained.

## Text-flow edits
- RQ2 heading shortened to `RQ2: 인접층 차이와 목적지 유인의 설명력 비교`.
- RQ3 heading shortened to `RQ3: 동선비용에 따른 유량과 프로그램 반응`.
- RQ4 and discussion headings shortened without changing substantive claims.
- Ten prose sentences shortened where 1–5 characters were stranded on a separate line.
- Table 1's `Program explanatory constructs` shortened to `Program indicators` to avoid internal English word hyphenation.
- Repository source-path exposition shortened to a clickable fixed GitHub reference.
- Korean cover title broken explicitly at a meaningful phrase boundary.

## Verification
- Before/after PDF page count: 8/8 (A4 595.28 x 841.89pt).
- Korean isolated short lines (<=5 characters excluding subsection markers): 13 to 0 in the 8-page PDF.
- Text line bounding boxes outside the page: 0.
- Detected text bounding-box overlaps: 2 numerator/denominator intersections of two displayed fractions on p6; not prose collisions.
- Final XeLaTeX: 0 missing-character, undefined-control, overfull hbox or overfull vbox warnings.
- Before/after LaTeX source numeric-token multiset: identical.
- PDF 1.5 source vs PDF 1.4 compatibility conversion: exact extracted text match on all 8 pages.
- Original RQ1–RQ4 numerical results were not edited.
- The original HWP font Human Myeongjo is still unavailable in the runtime; numerical template sizes/margins retained with a substitute font.
- A complete locally bundled editable TeX source, unified text patch, figure-building script and seven figure PNGs is delivered separately as `Thesis_Revision8_Complete_Package.zip`. This remote commit archives the final PDF, QA, and four modified figure files.

Base Revision 7 commit: `9c0c99375c5eabdf536363ec97543c90183519df`. No change to `main` or preceding paper revisions.
