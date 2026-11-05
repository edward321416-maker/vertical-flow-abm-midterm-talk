# Final report — 논문 중간발표 deck, reference-based redesign

## Deliverable

- **PDF:** `presentation/midterm_reference_redesign_2026-11-05/vertical_flow_midterm_reference_refined.pdf`
  (SHA-256 `47404ded…f6c50839`, 433,599 bytes)
- **18 pages**, every page 960 × 540 pt (**16:9**, ratio 1.777778); page order unchanged, so no old-to-new mapping
  is needed.
- White backgrounds, black titles/body, one embedded typeface (Pretendard), searchable and tagged text.
- Rebuild: `source_refined/README.md`. QA: `QA_REPORT.md` (44/44 machine checks, 201/201 value checks, 0 layout
  issues, all 18 final renders inspected). Cloud facts: `CLOUD_EXECUTION_REPORT.md`.

## Title and TOC changes

Page 2 (presentation structure):

| No. | Before | After |
|---|---|---|
| 01 | 문제와 분석 단위 | 연구 배경과 핵심 질문 (3–4쪽) |
| 02 | 선행연구와 모형 | 선행연구와 분석 방법 (5–6쪽) |
| 03 | E1 · E2 실험 | 시뮬레이션 조건과 실험 설계 (7–9쪽) |
| **04** | **RQ1 · RQ2** | **층간 상행유량 감소와 프로그램 구성** (10–13쪽) — one line, 236 pt |
| **05** | **RQ3 · RQ4** | **이동 저항과 앵커 배치에 따른 차이** (14–16쪽) — one line, 226 pt |
| 06 | 시사점과 한계 | 현재까지의 분석 결과와 향후 검증 (17–18쪽) |

Page titles:

| Page | Before (source PDF; prior PPTX layer in brackets) | After |
|---|---|---|
| 1 | 다층 상업시설의 프로그램 배치와 수직동선 마찰이 층간 상행유량에 미치는 영향 · kicker "연구 발표" [대한건축학회 학술 발표] | 다층 상업시설의 프로그램 구성과 수직동선 저항에 따른 층간 상행유량비(AUFR) · kicker **논문 중간발표** |
| 2 | 발표 구성 | 발표 구성 |
| 3 | 왜 층간 상행유량비를 살펴봐야 하는가 | 절대 유량만으로는 구간별 감소를 비교하기 어렵다 |
| 4 | 유량의 크기와 비율을 구분해 분석했다 | 세 지표는 서로 다른 질문에 답한다 |
| 5 | 실제 공간 연구를 층 단위 가상 실험으로 연결했다 | 관측된 다층 복합공간과 가상 층 선택 모형 |
| 6 | 네 가지 질문으로 감쇠와 프로그램 배치를 분석했다 [연구 질문 RQ1–RQ4] | 핵심 질문을 네 가지로 나누어 분석했다 |
| 7 | 가상 방문객의 이동 선택을 9층 모형으로 구현했다 | 가상 방문 그룹의 층 선택과 경계 기록 |
| 8 | 바로 아래 경계와 비교해 상행유량비를 계산한다 | 상행유량비(AUFR)는 바로 아래 경계와 비교한다 |
| 9 | 이동 저항과 프로그램 배치를 나누어 실험했다 [E1 · E2 실험 설계] | 이동 저항과 앵커 배치를 나누어 비교했다 |
| 10 | 추가 유인이 없어도 위층으로 갈수록 상행유량이 감소했다 [RQ1 — …] | 추가 유인이 없어도 위층일수록 통과량이 줄었다 |
| 11 | 상행유량은 층마다 같은 비율로 줄지 않았다 | 감소 비율은 경계마다 달랐다 |
| 12 | 인접층 앵커 비중 차이가 클수록 유량비가 높았다 [RQ2 — …] | 인접층 앵커 차이가 클수록 상행유량비가 높았다 |
| 13 | 절대 유량은 바로 위층 앵커 비중과 더 밀접했다 | 절대 유량은 바로 위층 비중과 더 밀접했다 |
| 14 | 이동 저항이 커져도 프로그램과 유량비의 관계는 항상 약해지지 않았다 (37자) | 이동 저항이 커져도 관계가 늘 약해지지는 않았다 |
| 15 | 같은 양의 앵커 프로그램을 네 가지로 배치했다 | 같은 앵커 총량을 네 가지로 배치했다 |
| 16 | 최상층 집중 배치가 최상단 유량을 가장 높였다 | 네 배치 중 최상층 집중형의 상단 유량이 가장 컸다 |
| 17 | 이 결과를 실제 건물에 그대로 적용할 수는 없다 | 네 가지 한계마다 검증 과제가 남아 있다 |
| 18 | 상층부 유량은 이동 조건과 목적지 배치를 함께 봐야 한다 [종합 결론] | 현재까지의 결과와 다음 검증 |

RQ1–RQ4 and E1/E2 now appear only as 8.5–9 pt grey traceability labels. Full before-inventory: `title_inventory.csv`
(1,007 text objects incl. the prior PPTX slide text and speaker notes).

## Most influential references (all reachable only as search results in this session)

| Reference | URL | Principle applied |
|---|---|---|
| Nature Reviews artwork guide | https://www.nature.com/documents/natrev-artworkguide.pdf | Left→right / top→bottom flow; every element explained by a direct label |
| Kastellec & Leoni (2007), *Perspectives on Politics* 5(4) | https://jkastellec.scholar.princeton.edu/document/50 | Estimates as point + interval against a reference line instead of number panels (pp. 12, 14) |
| Wilke, *Fundamentals of Data Visualization*, ch. 21 | https://clauswilke.com/dataviz/multi-panel-figures.html | Identical axes across panels (p. 16 small multiples; pp. 10–11) |
| Natapov et al. (2020), *Architectural Science Review* 63(1) | https://discovery.ucl.ac.uk/id/eprint/10085475/3/Natapov%20Circulation%20Typology%20and%20Wayfinding_publication.pdf | One comparison frame for variants (pp. 15–16) |
| Zook & Sailer (eds.) (2022), *The Covert Life of Hospital Architecture* | https://discovery.ucl.ac.uk/10145356/1/The-Covert-Life-of-Hospital-Archiecture.pdf | Ghosted context, bold analytical layer (pp. 7–8) |
| Nature figure specifications | https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/ | Live, embedded, vector text (whole PDF) |

Details, statuses and "element not copied" for all 17 external sources (plus 5 internal files that were opened
and inspected): `references_review.md`.

## Page-by-page diagram changes

| Page | Change |
|---|---|
| 1 | Typography only (kicker, title, subtitle, presenter, affiliation, date); prior floor/arrow graphic removed |
| 2 | Six decorative blocks → one numbered editorial list with page ranges |
| 3 | Normalised bars → 2 × 2 comparison (absolute decrease vs ratio) of two hypothetical situations + core question |
| 4 | Fake subscripts → three typeset question/formula/definition/"아님" columns |
| 5 | Barbican-only table → Barbican + South Bank observed study vs synthetic model, with shared / not-shared row |
| 6 | RQ-code rows → plain-language questions with 지표/조건 columns |
| 7 | One long 1F→9F arrow → the only nine-floor diagram: short trips (1F→4F→6F, exit via 1F), choice points, eight measured boundaries with +n |
| 8 | Arrows + broken "AUFR 4" → 3F–5F crop, proportional U₃/U₄ bars, stacked fraction, worked mean 0.659 |
| 9 | Two lists → E1 2 × 4 run matrix and E2 4 × 3 run matrix with totals |
| 10 | Direct-labelled U line chart, −20.6% bracket, population and 4-day wording |
| 11 | AUFR profile with per-repetition 2.5–97.5% bands, 51.7% labelled as last local AUFR, constant-ratio reference |
| 12 | Coefficient plot (γ = 0 control, 2, 4, 8) with CIs replaces the number panel; relative-vs-%p worked note |
| 13 | Dot plot of U residual-deviance reduction across six conditions (γ = 4 continuous highlighted) |
| 14 | Forest plot with CI-inclusion statement per row + separate level-gap panel |
| 15 | One-scale floor × scenario matrix with direct labels, fixed 1F row and Σ 2–9F = 1.60 row |
| 16 | Four aligned RUI trajectories (others ghosted, anchor boundaries marked) + final T / U₈ table; undefined "R" column removed |
| 17 | Limit → interpretive scope → validation task table |
| 18 | Findings with values + three separate next-validation streams + conditional TOP1 statement |

## Scientific value checks

All recomputed from `analysis/outputs/aik/aik_boundary_rep.csv` and matched to the tracked CSVs
(`qa/value_checks.csv`): U₁ 12,346 and U₈ 448 (γ = 0, continuous, 200 reps, 4-day totals); U₈/U₁ 3.6% (mean of
per-repetition ratios; the ratio of means rounds the same); last local AUFR 51.7%; segmented first boundary
−20.6%; AUFR multipliers ×1.060 [1.058, 1.062], ×1.109 [1.104, 1.115], ×1.184 [1.168, 1.200] per +0.1 contrast
(relative, not %p; γ = 0 CI includes 1); U residual-deviance reductions 10.2% (Δx), 60.1% (x_upper), 39.7% (M_b)
at γ = 4 continuous; erosion 6.7% [2.7, 10.5], 0.8% [−4.1, 5.2], 1.7% [−6.4, 8.6]; T = 58.7 / 14.0 / 5.9 / 1.5%
and U₈ = 9,112 / 2,197 / 975 / 286 for TOP1 / STEP3 / UNIFORM / LOW3; TOP1 U₆ 7,077 → U₇ 7,209 → U₈ 9,112;
anchor sums 1.60 (TOP1 1.600001); runs 1,600 + 1,000 = 2,600.

Remaining limits stated in the deck: synthetic non-spatial floor-choice model (no plan or vertical-circulation
geometry); no congestion or capacity; γ and TOP1's 0.85 are assumptions (0.85 lies outside E1's 0–0.5); boundary
crossings are person-crossings, not unique visitors; because γ·x enters the destination utility, a response to
anchor share is partly constructive. TOP1's advantage is conditional on these four scenarios and this model.

## Render, font, text and overflow checks

- Final renders: `qa/final_renders/slide_01–18.png` (150 dpi, MuPDF), contact sheets `qa/contact_sheet_final.png`
  and `qa/contact_sheet_source.png` (before). All 18 inspected at full size; no defects remain.
- Fonts: Pretendard Regular / Medium / SemiBold / Bold, all embedded CID TrueType subsets; no substitution or
  fallback (source deck mixed NanumBarunGothic and Pretendard).
- Text: searchable on every page, with word spaces (the source text layer had none).
- Overflow: build-time audit of overflow, margins, overlaps and single-line titles: 0 issues.
- Inputs: all 7 files in `inputs/` byte-identical (SHA-256); `source/`, `analysis/`, `paper/`, `simulation/` untouched.

## Not accessible

- **All external references** could not be opened in this cloud session: the container proxy returned 403 and the
  WebFetch tool `ENOTFOUND` for every host. Only search-result summaries were available; CCC Architecture, OMA and
  the Space Syntax 1998 page did not appear in search at all. Nothing was marked as visually inspected that was not.
- `paper_revised_8pages_v2(2).pdf` is not in the repository (as the task stated) and was not used or claimed.
- R and GAMA are not installed; analyses were re-estimated in numpy instead (results match), simulations not re-run.

## Decisions for the presenter

- **D1 — cover title.** The cover now uses the v3 paper title ("…프로그램 구성과 수직동선 저항에 따른 층간
  상행유량비(AUFR)"), replacing the v2 wording "…에 미치는 영향", which reads as causal. The confirmed speaker script
  (`inputs/final_speaker_script.md`, unchanged) opens with a third title, "다층 상업시설의 층간 상행유량 감쇠와
  인접층 프로그램 구성의 관계"; you may want the spoken opening to match the slide.
- **D2 — cover details.** "성균관대학교 건축학과" is kept because the paper's author line states it; the date
  2026. 11. 5. comes from the repository README. No event or course name was added.
- **D3 — section ranges.** The research-question page (6) is grouped under 02 선행연구와 분석 방법, and the model
  and AUFR pages (7–8) under 03 시뮬레이션 조건과 실험 설계.
- **D4 — removed metric.** Page 16 no longer shows the mean relative flow R, which was never defined on the slide;
  T and U₈ (both defined on the page) carry the comparison.
