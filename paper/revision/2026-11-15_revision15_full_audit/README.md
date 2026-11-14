# Thesis Revision 15 — full scholarly and typesetting QA (2026-11-15)

Base: Revision 14, commit 97b46725d879b8e00d402087aa1547f2987d170e.
Source evidence: frozen simulation commit ee4ea3255afbc359d0924a81b98de01c94281322 (nine CSV files independently checked).

## Result
- Main paper: exact A4, 2-column, 8 pages. PDF is unencrypted and has embedded substitute fonts. SHA-256 `9494170eefeb4e9ad487f752c1ae56db3fbc45d0d80a856c05a1b8807382a3ca`.
- Figure captions 1–7; table captions 1–10; two mathematical equations; 8 references.
- Reflowed Table 2 to separate parameter names and values, restoring readable rows and spacing.
- Reflowed 2→3-page reference-profile paragraph and 3→4-page E2 introduction so page starts use complete sentences.
- Separated the Table 10 note from its rule; clarified group-level person-weighted upward boundary counts.
- PDF 1.4 text equals its preconversion TeX-produced PDF on all 8 pages; zero out-of-page text blocks and zero horizontal overflow warnings.

## Limitations that must remain explicit
- Six underfull hbox notices and one approximately 0.57pt output vbox notice remain; no visible clipping detected.
- The last page retains whitespace. It was not filled artificially.
- PDF substitutes Noto Serif CJK KR and Tinos for the official HWP proprietary typefaces; pixel equivalence is NOT verified.
- Copy/paste may conflate Korean spaces in PDF text extraction.
- 2,600 original simulations were not independently re-run; no observed pedestrian data was used for external validation.
- Report PDF in this GitHub branch is the verified XeLaTeX source PDF. A PDF-1.4 compatibility copy of the same report text is available in the conversation deliverables.

All changes are on a separate audit branch. The previous revision and main have not been modified. Editable TeX, a unified patch, seven figures, and machine preflight JSON are provided in the conversation ZIP.
