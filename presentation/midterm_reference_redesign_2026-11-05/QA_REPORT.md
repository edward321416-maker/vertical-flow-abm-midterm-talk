# QA report — `vertical_flow_midterm_reference_refined.pdf`

- File: `presentation/midterm_reference_redesign_2026-11-05/vertical_flow_midterm_reference_refined.pdf`
- SHA-256: `47404dedce5212be630e2c44ec1fb2c3905ba7c4875f764e552e0e0af6c50839` (433,599 bytes)
- Producer: Chromium 153.0.8010.12 (Skia/PDF m153), PDF 1.4, tagged, document outline from page titles
- Machine QA: `source_refined/qa_refined.py` → `qa/qa_results.json` — **44 / 44 checks PASS**
- Value QA: `source_refined/verify_values.py` → `qa/value_checks.csv` — **201 / 201 checks PASS**
- Layout audit (in-browser, during build): `qa/layout_audit.json` — **0 issues on 18 pages**
- Visual inspection: all 18 final renders (`qa/final_renders/slide_01.png` … `slide_18.png`, 150 dpi, 2000 × 1125 px,
  rendered by MuPDF — an engine independent of the Chromium that wrote the PDF) were opened and inspected at full size.

## 1. Machine-verifiable checks (`qa/qa_results.json`)

| Check | Result | Evidence |
|---|---|---|
| Exactly 18 pages | PASS | 18 |
| All pages 16:9 | PASS | 960 × 540 pt on every page (ratio 1.777778) |
| Tagged PDF | PASS | `/StructTreeRoot` present |
| Searchable text on every page | PASS | 111–834 extracted characters per page (PyMuPDF); `pdftotext` extracts Korean with spaces |
| Page 2: zero `RQ1 · RQ2` | PASS | 0 occurrences |
| Page 2: zero `RQ3 · RQ4` | PASS | 0 occurrences |
| Page 2: no RQ/E codes at all | PASS | none |
| Page 2: six audience-facing topics, exact wording | PASS | all six present |
| Page 2 item 04 = `층간 상행유량 감소와 프로그램 구성` | PASS | exact, one line, 236.4 pt wide |
| Page 2 item 05 = `이동 저항과 앵커 배치에 따른 차이` | PASS | exact, one line, 225.8 pt wide |
| Cover states `논문 중간발표` | PASS | kicker line on page 1 |
| No conference / defense framing anywhere | PASS | no `학회`, `학술 발표`, `학술대회`, `컨퍼런스`, `conference`, `심포지엄`, `최종 심사`, `defense` |
| No `종합 결론` | PASS | absent |
| Cover is typography only | PASS | 0 drawn graphics, 0 images (the three full-page white fills are html/body/slide background paint and are excluded) |
| No internal code as main title | PASS | no title starts with RQ/E/gamma/AUFR or uses `RQ · RQ` / `E1 · E2` |
| Titles about 25 characters | PASS | every title ≤ 25 non-space characters; all single-line |
| RQ/E codes only as small labels | PASS | RQ1–4 / E1–2 appear only as 8.5–9 pt grey labels: p.6 question margin, p.9 table tags, footer traceability labels on pp. 6 and 8–16, and the p.17 source footnote |
| Full nine-floor abstraction at most once | PASS | only p.7 has nine floor labels each sitting on a drawn floor line; p.15 lists 9F–1F as rows of the required floor × scenario table (no drawn floors) |
| AUFR formula typeset (p.4) | PASS | text layer `AUFRr,b = Ur,b / Ur,b−1` (real subscripts, U+2212 minus) |
| T formula typeset (p.4) | PASS | `Tr = Ur,8 / Ur,1` |
| AUFR₄ = U₄/U₃ worked example (p.8) | PASS | stacked fraction with 0.659, U₃ 4,654, U₄ 3,068 |
| No fake Unicode subscripts | PASS | no `ᵦ ᵣ ₍ ₎` (the old deck used U+1D66 *beta* for "b", absent from the font) |
| Proper minus in `b−1` | PASS | U+2212 used, no ASCII `b-1` |
| No tildes | PASS | 0 (`2~9층` ranges → en dash `2–9층`; R-formula `~` reworded) |
| Displayed values present on their pages | PASS | every expected string found on pp. 8–16, 18 |
| Locked values match verified JSON | PASS | U₁, U₈, U₈/U₁, last AUFR, −20.6%, ×1.060/1.109/1.184, 10.2/60.1/39.7%, 6.7/0.8/1.7%, T, U₈, budgets 1.60, 1,600/1,000/2,600 |
| Value-check table all PASS | PASS | 201 rows |
| `%p` only in a negated sentence | PASS | 1 occurrence: "+10.9%p가 아니다" |
| "효과가 없다" only negated | PASS | "‘효과가 없다’는 증명이 아니라" |
| "최적" only negated | PASS | "실제 최적 배치가 아니다", "보편적 최적 배치를 뜻하지 않는다" |
| All fonts embedded | PASS | 4 of 4 embedded subsets |
| Single typeface | PASS | Pretendard only |
| No fallback fonts | PASS | no Nanum/Gulim/Batang/WenQuanYi/DejaVu/Noto/Times/Arial |
| Primarily black text | PASS | characters: 65.7% black (≤ #3D3D3D), 32.5% grey, 1.8% data colour |
| No colour on cover or TOC | PASS | 0 coloured spans on pp. 1–2 |
| 18 final renders at 150 dpi | PASS | 18 × 2000 × 1125 px |
| White backgrounds | PASS | all corners #FFFFFF; dominant colour #FFFFFF on every page (≥ 71.2% of pixels) |
| Layout audit: no overflow/overlap | PASS | 0 issues; all four weights loaded (`document.fonts.check`) |
| Inputs unchanged | PASS | SHA-256 of all 7 files in `inputs/` identical to the values recorded before editing |
| Tracked sources and outputs unmodified | PASS | `git status` clean for `inputs/`, `source/`, `analysis/`, `paper/`, `simulation/` |
| Contact sheets written | PASS | `qa/contact_sheet_final.png`, `qa/contact_sheet_source.png` |

## 2. Fonts — enumeration, embedding, substitution

`pdffonts vertical_flow_midterm_reference_refined.pdf`:

```
name                          type          encoding    emb sub uni
AAAAAA+Pretendard-SemiBold    CID TrueType  Identity-H  yes yes yes
BAAAAA+Pretendard-Bold        CID TrueType  Identity-H  yes yes yes
CAAAAA+Pretendard-Regular     CID TrueType  Identity-H  yes yes yes
DAAAAA+Pretendard-Medium      CID TrueType  Identity-H  yes yes yes
```

- One family, four weights, all embedded as subsets with ToUnicode maps (searchable, copyable).
- Source: Pretendard 1.3.9 (SIL OFL 1.1) from the npm package `pretendard@1.3.9`, tarball SHA-256
  `0ffc240c…bb3bd53`, OS/2 `fsType 0` (installable embedding). Fetched by `source_refined/fetch_fonts.sh`.
- Substitution: none. Glyph coverage was checked before building; the three glyphs Pretendard lacks
  (`∼` U+223C, `∈` U+2208, `ᵦ` U+1D66) are not used. Italic variables are Chromium-synthesised obliques of the
  same face (no second font file). No Korean fallback font is present in the container besides WenQuanYi, and
  it does not appear in the PDF.
- Before: the source deck embedded NanumBarunGothic (Regular, Bold; TrueType and CID copies) **and** Pretendard
  (Regular, SemiBold; two encodings each); the prior PPTX export also embedded TimesNewRomanPS-BoldMT.

## 3. Text searchability

- Every page has a live text layer; `pdftotext -layout` reproduces the Korean wording with word spaces
  (the source deck's text layer had no spaces: "발표구성", "연구질문과분석지표를…").
- Subscripts are real markup, so the text layer reads `AUFRr,b`, `U8 / U1`, which keeps formulas searchable.
- Full extracted text: `qa/final_extracted_text.txt`.

## 4. Overflow, clipping and spacing

The build (`build_deck.mjs`) runs an in-browser audit before printing: every HTML text box is checked for
horizontal overflow and slide bounds; every HTML and SVG text box is checked against the 40–920 pt safe margin
and against every other text box on the page (overlap > 1.5 pt in both axes); titles and subtitles must be one
line. The first build reported 20 issues (stacked tick labels 2 pt too close, page 14 level-gap labels past the
right margin, page 8 label spacing, page 16 annotation). All were fixed; the final build reports **0**.

## 5. Visual inspection (final renders, full size)

| Page | Result |
|---|---|
| 1 | Typography only; kicker, two-line 28 pt title, subtitle, presenter, affiliation, date. No graphics. |
| 2 | Six-item numbered list, single column; items 04/05 exact, one line each; page ranges right-aligned. |
| 3 | Hypothetical A/B comparison on two aligned rows; "가상 예시" label present; value labels clear of tracks. |
| 4 | Three question → formula → definition → "아님" columns; subscripts and `b−1` correct; product formula on its own line. |
| 5 | Observed (Barbican, South Bank) vs synthetic columns; "not validation" statement; citation pp. 507–538. |
| 6 | Four plain-language questions; RQ labels small grey; 지표/조건 aligned. |
| 7 | Only nine-floor diagram; short trips 1F→4F→6F and exit via 1F; choice points distinct from the eight measured boundaries; no stairs, escalators or plans. |
| 8 | 3F–5F crop, two boundary bars, stacked fraction AUFR₄ = U₄/U₃, worked value 0.659. |
| 9 | E1 2 × 4 matrix (200 each, 1,600) and E2 4 × 3 matrix with row/column totals (1,000); total 2,600. |
| 10 | Linear U profile, direct labels 12,346 / 9,802 / 448 / 408, −20.6% bracket; population and 4-day wording in subtitle. |
| 11 | AUFR profile with 2.5–97.5% bands; 51.7% labelled as last local AUFR (U₈/U₇); constant-ratio reference. |
| 12 | Coefficient plot dominates; ×1.060/×1.109/×1.184 with 95% CIs; γ = 0 control includes 1; "not %p" note. |
| 13 | Dot plot of residual-deviance reduction for U; γ = 4 continuous highlighted; "not AUFR, do not add" notes. |
| 14 | Forest plot with zero line; CI inclusion stated per row; separate level-gap panel; "not 'no effect'" note. |
| 15 | Floor × scenario proportion matrix, one scale, Σ 2–9F = 1.60 per column; 1F fixed in grey. |
| 16 | Four aligned RUI trajectories (identical axes, others ghosted), anchor boundaries marked, T in headers, final T/U₈ table. |
| 17 | Four limits, each paired with one validation task. |
| 18 | Four findings with values; three separate next-validation streams; conditional TOP1 statement. |

No clipping, overflow, broken equation, repeated diagram, colour violation or numeric discrepancy remains.
Smallest text: 8.5 pt footers and 9.5 pt secondary chart labels; only subscript digits are smaller (≈ 0.68 em).

## 6. Scientific value checks (summary of `qa/value_checks.csv`)

Independent recomputation from `analysis/outputs/aik/aik_boundary_rep.csv` (20,800 rows) reproduces the tracked
summary CSVs: profile means and per-repetition quantiles (exact), log-linear F tests (F = 1,301.6 / 1,976.8),
AUFR multipliers with cluster-robust HC1 95% CIs, t(199) (to 1e-9 / 1e-6), quasi-Poisson residual-deviance
reductions (to 1e-6), additive slope erosion (to 1e-9) with an independent cluster bootstrap (B = 600) within
0.5 pp of the reported B = 2,000 CIs, T and U₈ by placement, anchor proportions against the realised inputs, and
run counts (1,600 + 1,000 = 2,600; 0 missing boundaries; 0 zero-U).

## 7. Residual notes

- The deck uses the v3 paper title; the confirmed speaker script opens with a different title
  (see `FINAL_REPORT.md`, decision D1).
- External design references could only be reached as search results (network policy; see `references_review.md`).
