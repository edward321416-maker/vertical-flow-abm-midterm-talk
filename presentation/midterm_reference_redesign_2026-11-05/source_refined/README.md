# Refined deck pipeline (HTML/SVG → Chromium PDF)

Rebuilds `../vertical_flow_midterm_reference_refined.pdf` from the tracked analysis outputs. Nothing in
`../inputs/`, `../source/` or `analysis/` is modified.

| Step | Command (run from this folder) | Output |
|---|---|---|
| 1. Font | `./fetch_fonts.sh` | `fonts/Pretendard-{Regular,Medium,SemiBold,Bold}.ttf` (OFL 1.1, checksum-pinned; git-ignored) |
| 2. Values | `python3 -I verify_values.py` | `verified_values.json` (the only numeric source of the deck) and `../qa/value_checks.csv` |
| 3. Deck | `node build_deck.mjs` | `build/deck.html`, `build/layout_audit.json`, `../vertical_flow_midterm_reference_refined.pdf` |
| 4. QA | `python3 -I qa_refined.py` | `../qa/qa_results.json`, `../qa/final_renders/`, contact sheets, extracted text |
| — | `python3 -I extract_title_inventory.py` | `../title_inventory.csv` (inventory of the *source* deck) |

Requirements: Node 18+ with `playwright` and its Chromium; Python 3.11+ with `numpy`, `pandas`, `pymupdf`,
`pypdf`, `fonttools`, `Pillow`; poppler-utils (`pdffonts`, `pdftotext`) for the QA report.

Design rules encoded in `build_deck.mjs`: 960 × 540 pt pages, white background, 56 pt side margins, 22 pt
titles (28 pt cover), one typeface, colour only for data (continuous `#1F4E79`, segmented `#9C5A2E`), real
subscripts and U+2212 minus, no tildes. The build runs a layout audit (overflow, margins, text overlap,
multi-line titles) and prints every issue as a warning; `qa_refined.py` treats a non-empty audit as a failure and
exits non-zero if any check fails.
