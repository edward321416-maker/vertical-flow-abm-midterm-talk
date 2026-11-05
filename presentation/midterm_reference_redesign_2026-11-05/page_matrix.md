# Page matrix — written before implementation

Format per page: **current issue → source reference → design principle → new figure type → verified data**.
Reference IDs are defined in `references_review.md` (A = architecture, D = data visualisation, I = internal).
All values come from `source_refined/verified_values.json`, produced by `verify_values.py` from
`analysis/outputs/aik/*.csv` (201 checks, all PASS; see `qa/value_checks.csv`).

Page count stays **18**; page order is unchanged, so no old-to-new mapping is required.

## Audience-facing structure (page 2) and section ranges

| No. | Audience-facing topic (exact wording) | Pages |
|---|---|---|
| 01 | 연구 배경과 핵심 질문 | 3–4 |
| 02 | 선행연구와 분석 방법 | 5–6 |
| 03 | 시뮬레이션 조건과 실험 설계 | 7–9 |
| 04 | 층간 상행유량 감소와 프로그램 구성 | 10–13 |
| 05 | 이동 저항과 앵커 배치에 따른 차이 | 14–16 |
| 06 | 현재까지의 분석 결과와 향후 검증 | 17–18 |

RQ1–RQ4 and E1/E2 appear only as small grey traceability labels in page footers or table margins.

## Global design system

- 960 × 540 pt (16:9), background `#FFFFFF` on every page; titles and body black; grey only for secondary text.
- One typeface: Pretendard 1.3.9 (Regular 400 / Medium 500 / SemiBold 600 / Bold 700), embedded.
- Title 22 pt SemiBold (cover 28 pt); subtitle 12 pt; body 12–14 pt; chart labels 10.5–14 pt (secondary tick lines 9.5 pt); footnotes 8.5 pt.
- Fixed margins: 56 pt left/right; section kicker at y = 28 pt; title at y = 42 pt; subtitle at y = 76 pt; content from y ≈ 112–124 pt; footer rule at y = 506 pt.
  (Sizes and positions in this list are the as-built values; the plan used 12.5 pt subtitles and 9 pt footnotes.)
- Colour only for data: continuous = navy `#1F4E79`, segmented = brown `#9C5A2E` (repository convention, I4), redundant shape coding (circle vs square, solid vs dashed). Everything else black/grey.
- No cards, shadows, icons, decorative arrows or slogans (D1, D2, D3).
- Math typeset with real subscripts (`U<sub>r,b</sub>`, `b−1` with U+2212), Greek γ, Δ; no fake glyphs (old deck used U+1D66 ᵦ, absent from the font).

## Matrix

| Page | Current issue | Source reference | Design principle | New figure type | Verified data |
|---|---|---|---|---|---|
| 1 Cover | Kicker "연구 발표" (prior layer: "대한건축학회 학술 발표"); title is the v2 causal wording "…에 미치는 영향"; mixed fonts | I1 (v3 title page), D1 | Typography only; one face; hierarchy by size/weight/whitespace | Text only: kicker `논문 중간발표`, v3 title + subtitle, presenter, affiliation (from paper author line), date | Title/subtitle/author/affiliation from v3 p.1; date 2026-11-05 from README |
| 2 Presentation structure | Items 04/05 read `RQ1 · RQ2`, `RQ3 · RQ4`; item 03 `E1 · E2 실험`; six card-like blocks | D2, A2 | Numbered editorial list read top→bottom; one line per item; page ranges | Single-column numbered list (No. · topic · one-line description · pages) | Topics exactly as specified; ranges above |
| 3 Research background | Two cases shown with normalised bars only; core question absent | D2, D5 | Two situations compared on two views (absolute vs ratio) on aligned rows | 2 × 2 comparison: rows "절대 감소량" / "상행유량비", columns 상황 A / 상황 B; core question line | Hypothetical, labelled `가상 예시 · 본 연구 수치 아님`: A 100→50, B 1,000→950 |
| 4 Analytical units | Broken subscripts ("U  r,b"), parenthesised pseudo-subscripts | I1 Eq. 3–4, D1 | Each metric = question → formula → what it is not; same three-column grid | Three typographic columns with typeset formulas U<sub>r,b</sub>, AUFR<sub>r,b</sub>=U<sub>r,b</sub>/U<sub>r,b−1</sub>, T<sub>r</sub>=U<sub>r,8</sub>/U<sub>r,1</sub> | Definitions from v3 §3.3 |
| 5 Prior study & scope | Barbican only; "IMCM과 관찰 보행 흐름 비교" table reads like validation | A5, A9, I1 (v3 §2.1) | Observed study and synthetic model in separate columns; shared vs not-shared stated | Two-column comparison (observed complexes Barbican + South Bank vs synthetic floor-choice model) + "shared / not shared" strip | v3 §2.1: sites, gate counts, IMCM terms, "수평 방향 전환 깊이 > 수직 층 분리", pp. 507–538 |
| 6 Research questions | RQ codes as large row heads | A2, D2 | Plain-language questions lead; codes reduced to grey labels | Numbered question list with right-aligned metric · condition column | Metrics/conditions per v3 Table 1 |
| 7 Agent model | Full 9-floor stack with one long 1F→9F arrow; γ glyph fallback; `x_j` | A3, D3, I5 | Only full nine-floor abstraction; faint floors, bold measured boundaries; short variable trips; choices drawn separately from measurement | Thin 9-floor diagram: 8 boundary gates U₁–U₈; one example group path (1F→4F→6F, exit via 1F) marking which gates it adds to; choice fan at one decision point; four-step model list | v3 §3.1, Table 2; GAML lines 346–371, 484–495, 549–600 |
| 8 AUFR definition | Fake subscripts "AUFR  4"; generic arrows | A3, D2 | Three-floor crop only; numerator/denominator placed on their boundaries | 3F–5F crop with two boundary gates + stacked-fraction formula + worked value | γ=0 cont means U₃ 4,654, U₄ 3,068; mean per-rep AUFR₄ = 0.659 |
| 9 Experiment design | Two label/value lists; E1/E2 as headings | A7, A2, D2 | Each experiment as its own matrix of runs; totals reconciled | E1: 2 resistance × 4 γ matrix (200 per cell); E2: 4 placements × {γ4 cont, γ4 frag, γ0 cont control} (100 per cell) | E1 1,600; E2 800 + 200 = 1,000; total 2,600; 0 missing boundaries; 0 zero-U |
| 10 Baseline absolute flow | Population/aggregation wording missing; big side numbers | D6, D2 | One line chart, two series, direct end labels; definition of U in subtitle | Line chart U by boundary b (linear), continuous vs segmented | U₁ 12,346 / U₈ 448 (cont); 9,802 / 408 (frag); −20.6% first-boundary gap; U₈/U₁ 3.6% (mean of per-rep ratios); 200 reps, 4-day totals |
| 11 Baseline AUFR | 51.7% only in side panel; no interval | D5, D6, I1 Fig. 1b | Local ratio profile separated from absolute flow; direct label on the last point; interval band | AUFR profile b=2…8 with 2.5–97.5% per-rep bands; constant-ratio reference line | AUFR means/quantiles from aik_a1_profile; last local AUFR 51.7%; reference (U₈/U₁)^(1/7) ≈ 62.3%; F = 1,302 / 1,977, p < 0.001 |
| 12 Adjacent-floor program & AUFR | Decorative +6.0/+10.9/+18.4 panels larger than evidence; "%p" risk | D8, D5 | Coefficient plot dominates; estimates + CI printed next to points; reference line ×1.00 | Multiplier dot-and-interval plot (γ = 0 control, 2, 4, 8) + worked note on relative vs percentage-point change | ×0.9993 [0.9985, 1.0002], ×1.060 [1.058, 1.062], ×1.109 [1.104, 1.115], ×1.184 [1.168, 1.200] |
| 13 Absolute-flow auxiliary | Bars without statistic definition; risk of mixing with AUFR | D4, D8 | Dot plot on one axis; statistic named in subtitle; six conditions as context, γ=4 cont highlighted | Dot plot: rows x_upper, M_b, Δx_b; six conditions per row (γ = 2·4·8 × circulation): γ = 4 continuous as a labelled navy dot, the other five as grey rings | γ=4 cont: 60.1%, 39.7%, 10.2% residual-deviance reduction for U; ranges 46–71%, 29–57%, 4–22% |
| 14 Moderation by friction | Claims could read as "no effect"; CI inclusion only in side text | D8, D5 | Forest plot with 0 line; CI inclusion stated at each row; level effect shown separately | Forest plot of erosion (γ = 2, 4, 8) + small dot panel of first-boundary U level gap | 6.7% [2.7, 10.5], 0.8% [−4.1, 5.2], 1.7% [−6.4, 8.6]; U₁ gap −20.6, −18.5, −14.8, −9.2% |
| 15 Anchor placement | Bars short and detached from labels; 1F row missing | A6, A4 | One floor × scenario matrix; horizontal length on one scale; column sums | Proportion matrix 9F…2F (+1F fixed) × TOP1/STEP3/UNIFORM/LOW3 with Σ row | Weights from PATTERN_X; Σ 2F–9F = 1.60 each (TOP1 1.600001) |
| 16 Anchor-placement results | Bars + undefined "R" column; no trajectories | D6, A4, A3 | Four aligned trajectories on identical axes; context ghosted; small final table; metrics defined on page | Small multiples of RUI<sub>b</sub> by boundary (anchor boundaries marked) + final T / U₈ table | T 58.7 / 14.0 / 5.9 / 1.5%; U₈ 9,112 / 2,197 / 975 / 286; TOP1 U₆ 7,077 → U₇ 7,209 → U₈ 9,112 |
| 17 Limits | Limits not linked to validation | A2, I1 §5.2 | Each limit paired with one validation task on the same row | Three-column table: limit → interpretive scope → validation task (4 rows) | No plan geometry; no congestion/capacity; γ and TOP1 0.85 assumed (E1 range 0–0.5); crossings ≠ unique visitors |
| 18 Current findings & next validation | Titled "종합 결론" in prior layer; generalised wording | A2, D2 | Findings and next work separated; conditional TOP1 statement | Left: four findings with key values; right: three separate next-validation streams | Values as pages 10–16 |
