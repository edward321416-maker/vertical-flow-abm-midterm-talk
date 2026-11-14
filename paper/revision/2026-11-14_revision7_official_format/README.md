# Thesis Revision 7 — JAIK HWP style-derived layout audit

Date: 2026-11-14 KST

## Deliverables and verification status

- `Thesis_Revision7_Official_8pages.pdf`: A4, **8 pages**, official HWP style *numeric values* applied. The PDF committed here is XeLaTeX PDF 1.5; a content-identical PDF 1.4 client-compatible download is also provided in the ChatGPT conversation.
- `Thesis_Revision7_OriginalText_5pages.pdf`: same research content as Revision 6 with style-only changes; 5 pages under genuine 9pt/150%-spacing layout. Does **not** satisfy journal's 6–12 page general range.
- `Thesis_Revision7_Format_Audit.pdf`: 2-page independent layout audit and limitations.

The 8-page version **adds explicit appendices A–J and supplementary tables A1–A4** grounded in the frozen experiment plan, ODD documentation, and CSV outputs. It does not fill pages by exaggerating line spacing. The original main-paper charts (7) and tables (3) and core RQ1–RQ4 numeric findings are retained.

## Extracted official HWP settings

Original source: `paper/format_audit/official_template/aik_journal_sample_20250218.hwp`.

- A4; left/right 16mm; top 19mm; bottom 15mm
- two columns, 10mm gap, 84mm width each
- body 9pt / 150% baseline (~13.5pt); title 16pt; subtitle 13pt; English title 13pt
- English abstract/keywords 8pt; figure/table captions 8pt; table content 8pt
- HWP's original fonts **not available** in the rendering environment. Noto Serif/Sans CJK and Tinos substitute for HumanMyeongjo/Malgun Gothic/Times New Roman. PDF is **not** an exact Hancom HWP rendering.

## Scientific provenance

Frozen analysis ref: `ee4ea3255afbc359d0924a81b98de01c94281322`.
See `docs/simulation/aik_experiment_plan.md`, `docs/simulation/ODD.md` and `analysis/outputs/aik/aik_checks.csv`.
The 18 experiment cells account for 2,600 replicates; there was **no** fresh independent simulation rerun in this revision. External validation against measured real-world flows remains unperformed.

## QA

- PDF: A4, 8 pages, all pages rendered and visually reviewed, text outside page bounds: 0
- Final XeLaTeX: Overfull 0, missing characters 0; reference-line Underfull 13
- Primary result numbers checked against existing CSVs; no new field-observation claims
- Reviewer/author approval of the additional appendices, original HWP-font parity and school submission rules remain outstanding

The user-facing full source ZIP, including the TeX and image assets and official HWP, is available as a separate downloadable artifact in ChatGPT. `main` and the prior thesis sources are unchanged.
