# Revision 13 — exact 8-page thesis (2026-11-14)

This branch archives the eight-page corrected Korean thesis in a new PDF, without replacing Revision 12 or main.

## Scope
- Revision 12 original: 6 pages; Revision 13: exactly 8 A4 pages, 2 columns.
- Preserved conclusion then References; no appendix after conclusion and no page-padding.
- Body measurements: 9pt / 13.5pt; 16mm side margins; 10mm column gap (official HWP extracted numeric settings; substitute fonts Noto Serif CJK KR and Tinos).
- 7 figures, 10 tables, 2 equations, 8 references.
- Additional evidence-based methods and results: input controls, repeated sampling and uncertainty, RQ1 boundary AUFR, RQ2 attraction sensitivity and upper-floor predictor comparison, preplanned RQ4 Holm contrasts, and external validation criteria.
- **Important RQ1 correction:** fixed CSV `analysis/outputs/aik/aik_a1_shape.csv` flags both gamma=0 profiles `stepped=TRUE` (max deviations 0.1309 / 0.1515). Earlier wording incorrectly suggested the predeclared criterion was not met.
- Source dataset commit: `ee4ea3255afbc359d0924a81b98de01c94281322`.
- PDF 1.4, 8 pages; independent render/inspect and PyMuPDF span bounds pass; no Overfull hbox/vbox, missing glyph, undefined command. Exact text retained across XeLaTeX and PDF1.4 conversion.
- **Limitations:** originally specified HWP fonts not installed, so pixel-perfect HWP fidelity remains unverified; existing 2,600 model runs were not re-executed and no field study validation was conducted.
- A human-readable 2-page QA report and source unified diff are provided alongside the main PDF in the conversation. This PDF is the auditable eight-page revision, not a new scientific validation of the model.
