# Claude Code Cloud execution directive: reference-based redesign of an architecture thesis midterm presentation

## 0. Objective and deliverable

Complete a production-ready redesign of the existing 18-page Korean presentation PDF. This is a **논문 중간발표** for architecture research. It is not a final defense, a conference presentation, or a corporate pitch deck. Do not stop at a proposal or feasibility review.

Required final file:

`presentation/midterm_reference_redesign_2026-11-05/vertical_flow_midterm_reference_refined.pdf`

Keep the final deck at 18 pages unless a genuinely necessary change is documented with an explicit old-to-new page mapping. Preserve all input files.

## 1. Inputs and evidence boundary

Use only files that are present in this repository or sources that you actually open in the cloud environment.

- Main 18-page source PDF: `inputs/vertical_flow_presentation_clear_titles.pdf`
- Latest corrected 8-page paper available for this task: `inputs/paper_revised_8pages_v3_column_fixed.pdf`
- Earlier 8-page paper retained for comparison: `inputs/paper_revised_8pages_v2.pdf`
- Prior presentation PDF and PPTX: `inputs/vertical_flow_final_modern_academic.pdf`, `inputs/vertical_flow_final_modern_academic.pptx`
- Final confirmed speaker script: `inputs/final_speaker_script.md`
- Claim provenance map: `inputs/claim_source_map.csv`
- Current editable generator and QA files: `source/`
- Authoritative analysis CSV files: repository path `analysis/outputs/aik/`
- Simulation and analysis code: repository paths `simulation/` and `analysis/R/`

The originally named `paper_revised_8pages_v2(2).pdf` was not present in the local upload set. Do not claim that you opened it. Use the two explicitly supplied papers above, giving priority to the later v3 corrected version while verifying quantitative claims against the tracked CSV outputs and code.

## 2. Errors that must be removed

### 2.1 Midterm framing

- Replace any remaining `대한건축학회 학술 발표` or similar conference framing with `논문 중간발표`.
- Do not invent an institution, event, affiliation, or conference.
- Present completed model experiments, current analytical findings, interpretation limits, and future validation.
- Keep a real conclusion: TOP1 was most favorable for top-boundary flow among the four tested scenarios, but do not generalize it into a universal optimum for real buildings.

### 2.2 Audience-facing titles

Search all visible and invisible text objects, chart labels, notes, duplicated PDF layers, legends, tables, and annotations.

- Page 2 item 04 must read `층간 상행유량 감소와 프로그램 구성`.
- Page 2 item 05 must read `이동 저항과 앵커 배치에 따른 차이`.
- Use this six-part audience-facing structure, adjusting line breaks without changing meaning:
  1. 연구 배경과 핵심 질문
  2. 선행연구와 분석 방법
  3. 시뮬레이션 조건과 실험 설계
  4. 층간 상행유량 감소와 프로그램 구성
  5. 이동 저항과 앵커 배치에 따른 차이
  6. 현재까지의 분석 결과와 향후 검증
- RQ1-RQ4 and E1/E2 may remain only as small traceability labels or footnotes.
- Do not use `RQ1 · RQ2`, `RQ3 · RQ4`, `E1`, `E2`, `gamma`, or `AUFR` as unexplained main titles.
- Write natural Korean titles of roughly 25 characters where possible. Split long wording into a short title and one-line subtitle.
- Do not imply causality, field validation, or universal optimization when the evidence is model-based association or scenario comparison.

## 3. Reference research required before generation

Open and inspect real references before redesigning. Record the result in:

`presentation/midterm_reference_redesign_2026-11-05/references_review.md`

Minimum coverage:

- At least four architecture diagram references.
- At least four scientific/data-visualization references.
- Prefer original or authoritative sources.
- For each reference record: URL, creator/source, access status (`opened and visually inspected`, `opened as text only`, or `search result only`), representational purpose, principle applied here, and element not copied.
- Re-open the URLs listed in `references_seed.md` when network access permits. Do not convert a seed note into a claim of cloud access.
- Reuse only principles such as line hierarchy, alignment, whitespace, direct labeling, common comparison axes, minimal legends, and scale consistency.
- Do not copy, trace, or reuse copyrighted diagrams. Build new vector diagrams from this study's data.
- Do not borrow literal stairs, escalators, floor plans, or building sections. The model is a synthetic floor-choice model without real spatial geometry.

Core sources to inspect:

- https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
- https://www.nature.com/documents/natrev-artworkguide.pdf
- https://www.cccarchitecture.org/analyzing-architecture-through-diagrams
- https://es.aap.cornell.edu/research/erciyes/
- https://www.datawrapper.de/academy/how-to-create-a-dot-plot
- https://www.datawrapper.de/academy/confidence-intervals-error-bars-datawrapper-bar-charts

Also investigate architecture program-distribution matrices, non-spatial floor abstractions, minimal multipanel scientific figures, uncertainty/forest plots, categorical coefficient plots, and architectural program-zoning comparisons.

## 4. Required 18-page redesign

1. **Cover**: typography only. Remove section/arrow graphics. Show the research title, `논문 중간발표`, and the presenter clearly.
2. **Presentation structure**: replace internal-code headings with the six Korean topics above. Prefer a numbered editorial list or two-column document layout, not six decorative cards. Verify item 04 and 05 wording, line breaks, and width.
3. **Research background**: compare two explanatory situations showing why a ratio is needed in addition to absolute flow. Mark any non-study numbers as a hypothetical example.
4. **Analytical units**: compare boundary flow U, adjacent-boundary ratio AUFR, and top-boundary relative flow T as answers to different questions. Typeset b-1, Greek symbols, and subscripts correctly.
5. **Prior study and scope**: contrast Chang & Penn (1998)'s observed multilevel complexes with this synthetic floor-choice model. Consider both Barbican and South Bank. Do not present the observed study as validation of this model.
6. **Research questions**: show four plain-language questions. Keep RQ1-RQ4 only as small labels.
7. **Agent model**: this is the only page allowed to use the full nine-floor abstraction. Distinguish eight measured boundaries from probabilistic destination/exit choices. Do not use one long arrow that suggests everyone travels from 1F to 9F. Do not draw a real plan or escalator.
8. **AUFR definition**: use a three-floor crop and two adjacent boundaries to show AUFR4 = U4/U3. Avoid repeating the full nine-floor figure. If page 4 overlaps, use page 8 for the worked local example.
9. **Experiment design**: use a clear title such as `이동 저항과 앵커 배치를 나누어 비교했다`. Separate E1 as a resistance-by-attraction-factor matrix and E2 as fixed-total placement variants. Verify E1 1,600 runs, E2 1,000 runs, total 2,600.
10. **Baseline absolute flow**: line chart of boundary U values with correct population and four-day aggregation wording.
11. **Baseline AUFR**: separate local AUFR profile from absolute flow. Directly label 51.7% as the last local AUFR, not U8/U1.
12. **Adjacent-floor program and AUFR**: show +6.0%, +10.9%, and +18.4% as relative multipliers/effect sizes with 95% confidence intervals where the verified data support them. Do not call them percentage-point increases. Make the evidence larger than decorative number panels.
13. **Absolute-flow auxiliary analysis**: clearly state that 10.2%, 60.1%, and 39.7% are reductions in residual deviance for U relative to the baseline model. Do not mix them with AUFR results.
14. **Moderation by movement friction**: forest plot with point estimates, 95% CIs, a zero line, and direct indication of whether intervals include zero. Do not write that gamma=4 or gamma=8 has no effect.
15. **Anchor placement**: compare TOP1, STEP3, UNIFORM, LOW3 in one floor-by-scenario proportion matrix with horizontal lengths and direct labels. Verify each 2F-9F sum is approximately 1.60. Do not repeat four building sections.
16. **Anchor-placement results**: connect placement, boundary-level relative-flow trajectories, and final T plus absolute U8. Prefer four aligned trajectories and a small final-value table. Define every metric before using it.
17. **Limits and validation tasks**: include lack of real plan geometry, no congestion/capacity, assumed attraction and TOP1=0.85, and boundary crossings not being unique visitors. Link each limit to a future validation task.
18. **Current findings and next validation**: avoid `종합 결론`. State the conditional TOP1 advantage. Separate measured-data validation, geometric vertical-circulation modeling, and congestion/capacity modeling as subsequent work.

Before implementation, write a page matrix with `current issue -> source reference -> design principle -> new figure type -> verified data` for all 18 pages.

## 5. Design specification

- 16:9 landscape, all backgrounds `#FFFFFF`.
- Black titles and body text. Use size, weight, opacity, and whitespace for hierarchy.
- Use color only when needed to distinguish data or research comparisons. No colored cover/TOC accents.
- Keep the present restrained title scale: around 22 pt on normal slides and 28 pt on the cover. Do not enlarge headings merely to fill space.
- Use one Korean-capable sans-serif consistently. Resolve the current Pretendard/NanumBarunGothic mixture. Verify availability and font embedding or an equivalent reliable Korean font.
- Use presentation-readable graph labels. Do not blindly apply journal-only 5-7 pt text sizes.
- Standardize margins, text start lines, axes, and stroke hierarchy.
- Remove meaningless arrows, generic icons, colored cards, shadows, decorative slogans, and unnecessary segmentation.
- Repair broken equations, tildes, missing subscripts, boxes, or spacing before export.
- Layout variety must follow information type, not decoration.
- The final PDF must retain searchable text.

## 6. Locked scientific definitions and values

Verify every occurrence against the paper, CSVs, and analysis code.

- Synthetic 9-floor model, eight upward boundaries. U1 is 1F-to-2F boundary throughput. U8 is 8F-to-9F boundary throughput. Neither is building entrants.
- AUFR(r,b) = U(r,b) / U(r,b-1), computed within the same repetition. It is not individual-visitor survival.
- RQ1, gamma=0, continuous: U1 approximately 12,346, U8 approximately 448, U8/U1 approximately 3.6%, last local AUFR approximately 51.7%, segmented first boundary approximately 20.6% lower.
- RQ2, continuous, gamma=2/4/8: a 0.1 increase in adjacent program contrast is associated with AUFR relative multipliers approximately +6.0%, +10.9%, +18.4%. These are not field-validated effects.
- RQ2 U auxiliary analysis at gamma=4, continuous: residual deviance reductions approximately 10.2% for delta-x, 60.1% for x-upper, and 39.7% for M-above. These are different statistics from the AUFR multipliers.
- RQ3 segmented, original-scale slope erosion: gamma=2 is 6.7% (95% CI 2.7 to 10.5), gamma=4 is 0.8% (-4.1 to 5.2), gamma=8 is 1.7% (-6.4 to 8.6).
- RQ4, gamma=4, continuous: mean per-repetition U8/U1 values are TOP1 58.7%, STEP3 14.0%, UNIFORM 5.9%, LOW3 1.5%. TOP1 mean U8 is approximately 9,112. These are not visitor arrival probabilities.
- Anchor-proportion sum across 2F-9F is approximately 1.60. TOP1: 9F=0.85, others approximately 0.107143. STEP3: 3F/6F/9F=0.45, others=0.05. UNIFORM=0.20. LOW3: 2F/3F/4F=0.45, others=0.05.
- Gamma is an assumed sensitivity parameter, not a measured attraction coefficient. This study does not validate Doota Mall plans, arrivals, or individual trajectories.

## 7. Execution and QA

1. Render the current 18-page deck and both supplied papers at 150-200 dpi before editing.
2. Extract every page's title, TOC item, internal heading, legend, chart label, table heading, and footnote into `title_inventory.csv`. Include invisible/duplicated text where discoverable.
3. Complete `references_review.md` before implementation.
4. Rebuild content at the source/vector level. Do not patch the PDF with opaque rectangles.
5. Use the supplied generator/PPTX or a new vector pipeline. Temporary sources and images may remain inside this task folder. The only public deliverable is the final PDF.
6. Render the final PDF again to 18 individual page images at 150-200 dpi and create a contact sheet.
7. Visually inspect all pages at full size. Fix clipping, overflow, broken equations, tiny labels, repeated diagrams, color violations, and numeric errors.
8. Write `QA_REPORT.md` with machine-verifiable checks and the visual inspection result.

Final pass criteria:

- Page 2 has zero `RQ1 · RQ2` and zero `RQ3 · RQ4` audience-facing labels.
- Cover states `논문 중간발표` and has no invented conference framing.
- Full nine-floor abstraction appears at most once.
- AUFR formulas and subscripts are correct.
- Values match tracked CSVs and analysis code.
- Exactly 18 pages, 16:9.
- White backgrounds and primarily black text.
- Searchable final PDF text.
- All 18 final renders visually inspected.
- Fonts enumerated and embedding/substitution reported.
- No source PDF, paper, or tracked analysis output overwritten.

## 8. Cloud, model, cost, and Modal boundaries

- This task is running in Claude Code cloud. Record the session URL/ID in `CLOUD_EXECUTION_REPORT.md` when available.
- Use the highest model and maximum effort actually supported by the session. Record what the runtime reports; do not guess a model name or effort level.
- Do not confuse a local Claude process or API billing with cloud-session subscription usage.
- Use Modal only if the cloud environment already has working authentication and the use is clearly beneficial for parallel rendering or QA. Do not create credentials, change plans, activate paid services, or use a GPU for ordinary SVG/PDF generation.
- Credit balance and consumption are `UNKNOWN` unless the runtime exposes a verified value. Do not infer them.

## 9. Final completion report

In `FINAL_REPORT.md`, report concisely:

- final PDF repository path;
- final page count and 16:9 verification;
- title/TOC change table, especially page 2 items 04 and 05;
- 4-6 most influential references with URLs and the applied principle;
- page-by-page diagram changes;
- scientific value checks and remaining limits;
- final render, font, text-searchability, and overflow checks;
- any source or reference that could not be accessed.

Do not claim completion unless `vertical_flow_midterm_reference_refined.pdf` exists and the latest 18-page render has been inspected.
