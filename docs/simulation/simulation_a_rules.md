# Simulation A operational rules

Status: APPROVED (user, 2026-10-20) — frozen before the first A1–A5 run. Version 1.1 (user, 2026-10-20, D023): compute tier and run order, §8.
Spec: `../superpowers/specs/2026-10-20-simulation-track-design.md` (r1) §5. Model: `ODD.md`.
Thresholds are those of spec §5; this document fixes how they are applied.

## 1. Scope

These rules govern the first pass (2026-10-26 – 10-29) and the pilot-informed pass (2026-11-02 – 11-04). Results are design rules under the stated scenario ranges, not statements about real facilities (spec §2 principle 2).

## 2. Targets and aggregation

- Rate target: one (boundary, block) of the protocol's boundary set. Its truth is the declared-construct crossings over the protocol's observation days and full block durations (spec §4.4).
- `AUFR` target: one consecutive observed boundary pair in one block.
- Per target, over replicates, with truth taken per replicate: relative bias = mean((est − truth)/truth); relative RMSE = sqrt(mean(((est − truth)/truth)²)); coverage = share of 95 % intervals containing the truth; CV = sd(est)/mean(est).
- Cell statistics: the worst |relative bias| over targets; the worst relative RMSE over the targets that the rule names; and the number of targets that fail the coverage rule below. Pooled coverage (all target × replicate intervals) and worst-target coverage are reported as summaries and are not decision statistics.
- Coverage rule: every (boundary, block) rate target and every `AUFR` target is an estimand, and its coverage C_t is evaluated over its own n_t replicate intervals. A target fails when C_t < 0.90 − 2·sqrt(0.90 × 0.10 / n_t), which is 0.858 at n_t = 200 (`coverage_floor()` in `analysis/R/evaluate.R`). A cell meets the coverage criterion only if no target fails. The basis is the Monte Carlo standard error of a coverage estimate, sqrt(C(1 − C)/n_sim), and the practice of reporting performance measures per estimand (Morris, White and Crowther 2019; candidate reference pending review, §9). Applying a two-standard-error tolerance at the 0.90 threshold is this study's convention, not a rule quoted from that reference.
- Quiet targets are rate targets whose mean truth lies in the lowest third of the cell's targets; busy targets lie in the highest third.
- The boundary-profile Spearman agreement (estimate versus truth, per replicate and block, then averaged) is reported for every protocol (spec §4.4). It is not a decision rule.
- Scope: "at every point" and "across the scenario range" in a rule mean every design point, and every observer miss level, in that experiment's scope as defined in §3. They do not mean every point of the pass for every experiment.
- Exclusions: rows that `target_metrics` leaves out are counted by reason and reported per protocol and cell, for rates and for `AUFR`. The reasons are an estimate without a truth or a truth without an estimate, a non-finite estimate (a failed fit or a `rate_unavailable` ratio), a non-finite truth, and a zero truth. If more than 5 % of a cell's target × replicate rows that match a truth have a non-finite estimate (`rate_nonfinite_share` or `aufr_nonfinite_share` above 0.05), that protocol fails the cell. Zero-truth targets are excluded from the relative metrics and listed in the cell summary.

## 3. Design points and replicates

- Scenario ranges: `simulation/gama/VerticalFlow/includes/scenarios/ranges_first.csv` (table below). Fixed generator values: `FIXED_GEN` in `analysis/R/design.R` (listed below the table).

  | Parameter | Low | High | Meaning |
  |---|---:|---:|---|
  | `base_rate_gpm` | 2 | 12 | visitor groups per minute over all entries at profile factor 1 |
  | `group_extra_mean` | 0.3 | 1.2 | group size is 1 + Poisson(mean) |
  | `day_sd` | 0.10 | 0.40 | sd of the log day multiplier |
  | `dwell_meanlog` | 2.302585 | 3.401197 | log minutes per floor visit (10 to 30 min) |
  | `dwell_sdlog` | 0.5 | 1.0 | sd of log dwell |
  | `alpha` | 0.5 | 3.0 | floor-separation decay |
  | `beta` | 0.0 | 2.0 | composite-impedance exponent |
  | `theta0` | −1.5 | 1.0 | exit constant |
  | `theta1` | 0.00 | 0.04 | exit utility per minute since entry |
  | `delta_down` | −0.5 | 0.5 | downward-trip constant |

  Fixed generator values: `gamma` = 0, `theta2` = 0; impedances `imp_escalator` = 1.5, `imp_stairs` = 3.0, `imp_elevator` = 2.5; per-floor costs `tau_escalator` = 0.2, `tau_stairs` = 0.7, `tau_elevator` = −0.1; `mode_mu` = 2; `elevator_enabled` = 1; travel times `esc_s` = 45 s, `stair_s` = 60 s; elevator wait `elev_wait_mean_s` = 60 s plus `elev_s_per_floor` = 6 s per floor. The impedances are the first-semester values used as one scenario point only (spec §2 principle 3).
- Design points: a 16-point maximin Latin hypercube (`lhs::maximinLHS`, seed 20261026) plus two hard corners (`corner_quiet`, `corner_busy`; definitions in `hard_corners()`), all with the fixed generator values above. The centre point is the range midpoints (`center_point()`). The corners are:
  - `corner_quiet` (low flow, steep decay, noisy days; quiet upper boundaries): `base_rate_gpm` 2, `group_extra_mean` 1.2, `day_sd` 0.40, `dwell_meanlog` 3.401197, `dwell_sdlog` 1.0, `alpha` 3.0, `beta` 2.0, `theta0` 1.0, `theta1` 0.04, `delta_down` 0.
  - `corner_busy` (high flow, shallow decay, noisy days; busy boundaries and flow-dependent misses): `base_rate_gpm` 12, `group_extra_mean` 1.2, `day_sd` 0.40, `dwell_meanlog` 2.302585, `dwell_sdlog` 1.0, `alpha` 0.5, `beta` 0.0, `theta0` −1.5, `theta1` 0.00, `delta_down` 0.
- Scope per experiment (the points and observer miss levels at which an experiment's rules must hold):
  - A1 and A2: all 16 LHS points and both corners (18 points), at both miss levels.
  - A3: the centre point and both corners; generator only, no observer.
  - A4: the centre point and both corners, at both miss levels (lo and hi), for both protocols.
  - A5: the centre point and both corners, at miss hi. Observer misses thin the counts and reduce information, so power at hi is the conservative case.
  - Morris: its own design (§5).
  - Tier 3 (§6) drops the corners from A3 and A4. That is a declared scope reduction: the report states it and every affected result carries it as a deviation.
- Replicates: 200 per acceptance cell, with seeds `seed_for(cell_id, rep_id)`. Morris uses 50 per point, for screening only.
- Simulated days: 6 for A1/A2 (day types WE, WE, WD, WD, WE, WE), 2 for A3, and 4 for A4, A5 and Morris. A protocol with fewer days uses the first days.
- Boundary sets: B6 is all six Doota boundaries (B2-B1, B1-1F, 1F-2F, 2F-3F, 3F-4F, 4F-5F); B3 is 1F-2F, 2F-3F, 3F-4F (boundary orders 3–5); B2 is 2F-3F, 3F-4F (orders 4–5, a subset of B3).
- Observation constants: walk/reset time 120 s; blocks midday 12–14, afternoon 15–17, evening 19–21 (scenario); construct `primary_escalator_upward_flow` unless stated otherwise.

## 4. Observer error levels

- lo: `miss_base` = 0.074, `miss_flow` = 0.0005; realized window-average miss 0.08 ± 0.01 at the centre point (15-minute up-only rotation); 0.0811 realized in the final calibration iteration.
- hi: `miss_base` = 0.2381, `miss_flow` = 0.0010; realized 0.25 ± 0.01 at the centre point; 0.2468 realized in the final calibration iteration.
- Calibration: `analysis/R/experiments/calibrate_miss.R`, 2026-10-20, centre point, 50 replicates × 4 days, converged in the second of at most three iterations (first iteration from `miss_base` 0.06 / 0.20 gave 0.0660 / 0.2119). The levels are stored in `MISS_LEVELS` in `analysis/R/design.R`.
- Edge: +0.05 within the first and last 60 s of a window. Down counting multiplies the miss probability by 1.4.
- Realized miss is crossing-weighted: 1 − Σ observed up counts / Σ true up counts over all windows of a protocol, so every person crossing counts once. Because the miss probability includes `miss_flow` × load, busy points at hi may realize slightly above 0.25. Realized averages at every design point are reported; they are not used to exclude points.

## 5. Experiment grids and decision rules

- **A0** (already applied): |z| < 4 for every choice and mode cell; conservation, crossing sequence, window recount and seed checks exact; perfect-observer boundary-rate coverage meets the coverage rule of §2 (no rate target fails) at 2 and 6 days. Spec §5 requires the conservation and crossing-sequence checks "in every replicate"; in the campaigns they apply as follows. Conservation (entered = exited + forced exit, `conservation_ok()` in `analysis/R/a0_checks.R`) is checked in every replicate of every A1–A5 cell, and any failure fails that cell's run. The crossing-sequence check runs on the logged mechanism replicate only, because the crossing log is not written in campaign runs.
- **A1:** rotation protocols over boundary sets B6 and B2 (§3), each using every rotation pass that fits in a block; window 10 or 15 min × miss lo or hi × up-only or up+down × 2 or 4 days (32 protocols). The decision is made separately for each boundary set. Decision at 4 days: the shortest window whose worst quiet-target relative RMSE is ≤ 0.15 at every point and both miss levels (up-only). If none qualifies, use 15 min and raise repetitions (A2). Count down flow only if the up+down protocol at the chosen window meets the same bound. The 2-day results are reported for the pilot.
- **A2:** schedule simultaneous, one-pass or rotation × 2, 4 or 6 days × boundary set B2, B3 or B6 (§3) × miss lo or hi; 15-minute up-only windows (54 protocols: 3 schedules × 3 sets × 3 day counts × 2 miss levels). `k` = windows per boundary per block over all days. With 15-minute windows a rotation pass fits 3 times in a 120-minute block for B2 (k = 6, 12, 18 over 2, 4, 6 days), 2 times for B3 (k = 4, 8, 12) and once for B6 (k = 2, 4, 6). For each boundary set, the minimum `k` is the smallest rotation `k` with worst |`AUFR` bias| ≤ 0.05, worst `AUFR` RMSE ≤ 0.15 and no `AUFR` target failing the coverage rule of §2 at every point and both miss levels. If no tested `k` qualifies, the result is "not achievable within the tested grid" and the closest protocol is reported. Simultaneous and one-pass results are reported as comparators (D013).
- **A3:** generator only, 2 days; elevator impedance in {disabled, 6, 4, 3, 2.5, 2, 1.5, 1.2} × elevator per-floor cost τ in {0, −0.3}. Primary construct `observable_escalator_stair_upward_flow` (excludes only the elevator); escalator-only reported. A cell is material when the replicate mean of the worst-target |AUFR_construct − AUFR_total| / AUFR_total exceeds 0.10, or the replicate mean of the lowest block Spearman correlation between the two true profiles is below 0.90. The elevator share of a replicate is the true share of upward boundary crossings made by elevator over the simulated days. The materiality threshold is the lowest mean elevator share among material cells over the points in scope (§3) and all τ values.
- **A4:** γ = θ₂ = 0 and equal size basis (zero program effect); an upper-floor entry at 5F with share in {0, 0.05, 0.10, 0.20, 0.30} × a basement share at B2 in {0.10, 0.30}, with the street share taking the rest; protocols: rotation and simultaneous, each at miss lo and miss hi (four observers per run), B6, 15 min, 4 days. The spurious rate per target is the share of replicates whose lower 95 % `AUFR` bound exceeds 1. The threshold per boundary is the smallest upper-entry share with a spurious rate above 0.05 at any point in scope (§3) and either miss level. A boundary whose spurious rate already exceeds 0.05 at share 0 is reported as a structural (street-entry) effect and gets threshold 0. Consequence (spec §5): at a boundary, at or above its threshold share, `AUFR` > 1 is not interpreted as program-associated.
- **A5:** synthetic facilities with 7, 9 or 11 floors; `x_j` ~ U(0, 0.5) drawn per replicate; one street entry at the ground floor. Effects run through γ with θ₂ = 0. γ is calibrated so that the truth-level rate ratio per 0.1 `delta_fnb` (quasi-Poisson GLM on true block totals, 50 replicates as sites) is 1.10, 1.25 or 1.50; the grid is extended to γ = 6, 8, 10 if a target is not reached. Designs: 8, 12, 16, 20, 24 and 30 boundaries over 1–3 sites. Protocol: 10-minute rotation, one pass per block per day, 4 days, miss hi (the conservative case for power, §3). Model: `up_count ~ delta_fnb + boundary_order + block + site + (1 | boundary) + offset(log(window_minutes))`, negative binomial, with site omitted for one site. Power is the share of 200 replicates with p < 0.05; a non-converged fit counts as not significant. Pooled modelling is feasible for a design if power ≥ 0.80 at rate ratio 1.25 at every point. Type-I error at γ = 0 is reported.
- **Morris:** r = 10, 6 levels, grid jump 3, 11 factors (the 10 generator ranges plus `miss_base` ∈ [0.074, 0.2381], the calibrated lo and hi values; `miss_flow` is held at the hi level, 0.0010); design seed 20261027; protocol: rotation, B6, 15 min, 4 days. Outcomes: worst `AUFR` RMSE, worst quiet-rate RMSE, and pooled `AUFR` coverage (a screening outcome; the per-target rule of §2 is not applied to Morris). A factor is a driver if μ* ≥ 0.10 × the largest μ* for any outcome; drivers become pilot measurement priorities.

## 6. Compute tiers

The A0 projection of the first-pass total is about 11 h on 16 cores (Tier 1). The measured time of the first A1/A2 chunk and the A0 projection decide the tier before the remaining runs start:

- Tier 1 (projected ≤ 60 h): as specified.
- Tier 2 (60–120 h): Morris uses 30 replicates per point; A5 runs the centre point first and the corners afterwards.
- Tier 3 (> 120 h): additionally, A3 and A4 use the centre point only. This is a declared scope reduction (§3): the report states the tier, and every affected result carries the reduction as a deviation.

Measured in A0: median 3.9 s per simulated day with two observers on 16 cores. Run cost grows with the number of observers, and A1/A2 run 86 observers per run (32 in A1 and 54 in A2); the A1/A2 cost is measured on the first chunk, and the measured time per run and the resulting tier are written to `analysis/outputs/sim/first/compute_tier.md` before the remaining runs start.

## 7. Implementation clarifications of spec r1

1. **CI method:** Monte Carlo draws from the fitted fixed-effect distribution. The A0 diagnostic against the refit bootstrap (30 replicates, `A0_perfect_d2`: rate coverage 0.969 Monte Carlo versus 0.941 refit; `AUFR` coverage 0.956 versus 0.960) supports its use for the 2-day model, and the field analysis uses the same method; for 5 or more days the rate CIs use the joint draws of item 8, which the diagnostic did not cover.
2. **Designs:** LHS and Morris designs are generated in R (`lhs`, `sensitivity`) and executed by GAMA headless, because GAMA's built-in methods cannot compute GLMM-based outcomes.
3. **Observer error:** miss level and down-count load are observer design factors, not generator ranges.
4. **Aggregation:** the target aggregation in §2.
5. **A5:** effect channel γ with θ₂ = 0, truth-level calibration, and 10-minute windows (ten boundaries do not fit in a 120-minute block with 15-minute windows).
6. **A0:** "within Monte Carlo error" is operationalized as |z| < 4.

Implementation amendments made while building the generator, observer and estimators, none of which changes a threshold:

7. **Counterbalancing:** rotation direction alternates with pass, block and day via (day − 1) + pass + block parity (`analysis/R/schedule.R`); a pass index that ignored the day would repeat the same order every day whenever the number of passes per block is even.
8. **Random-day CIs:** random-day (≥ 5 days) rate CIs use joint draws of fixed effects and day random effects from the TMB joint precision, so the estimand is the rate over the observed days (`analysis/R/estimators.R`); the refit bootstrap is restricted to fixed/no-day models.
9. **Zero and unobserved cells:** zero-total boundary-block cells have point 0 with uncertainty from the Jeffreys posterior Gamma(shape = 0.5, rate = exposure minutes); `AUFR` with a zero numerator is 0 with reason `zero_numerator`; `AUFR`/RUI rows are built over the declared boundary set and unobserved ones get reason `rate_unavailable` (`analysis/R/estimators.R`; `data/data_dictionary.md` §5).
10. **Dispersion by REML:** the negative-binomial dispersion is estimated by REML (fallback ML, then Poisson); under ML the 2-day perfect-observer pooled coverage was 0.878 (< 0.90), under REML 0.946 (A0 report). This also applies to the field analysis; `ESTIMATOR_VERSION` = `est-v2` (`analysis/R/estimators.R`).
11. **A0a-2 sparse cells:** A0a-2 (mode-choice |z| < 4) can fail spuriously on cells with expected counts < 1 (about 13–15 % per fresh seed); the A0 PASS stands; a future A0 re-run may need exact tail probabilities for sparse cells — user decision (`analysis/R/experiments/a0_verify.R`).
12. **Design effect found in A0:** with six boundaries, 15-minute windows and 2-minute walks, one rotation pass covers only the first ~100 of 120 block minutes, giving perfect-observer boundary-rate relative bias up to 0.065 (2 days) / 0.085 (6 days); A1/A2 evaluate this against full-block truth as intended. With 10-minute windows and six boundaries only one pass fits and covers minutes 0–70 of the 120-minute block (0–100 for 15-minute windows), so the A1 window comparison is confounded with block coverage; A1 results are reported with this caveat (`analysis/R/schedule.R`; A0 report).
13. **Coverage rule:** per-target coverage with a two-Monte-Carlo-standard-error floor (§2) replaces pooled coverage ≥ 0.90 as the decision statistic in A0b and A2. It was adopted at the user gate after A0, before any A1–A5 run; the A0 recovery was re-judged under it with the same simulation outputs (`analysis/R/experiments/a0_verify.R`, A0 report). A0b passes at 2 and 6 days: none of the 18 rate targets fails (floor 0.858), the worst-target coverage is 0.885 (2 days) and 0.900 (6 days), and the pooled coverage is 0.946 and 0.954.
14. **Boundary set B2:** B2 (2F-3F, 3F-4F) was added to A1 and A2 at the user gate. A0 showed that the A1 and A2 bounds are not reachable within 6 days with six boundaries even for a perfect observer (centre point, worst quiet-rate relative RMSE 0.53 at 2 days and 0.29 at 6 days against 0.15; worst `AUFR` relative RMSE 1.06 and 0.38 against 0.15; `analysis/outputs/sim/a0/a0_recovery_summary.csv`). The decision rests on the A0 results, not on any A1–A5 result.
15. **Degenerate fixed-day fits (`est-v3`):** a fixed- or no-day fit whose fixed-effect covariance is not finite (for example when every count of a boundary falls on one of two days, so the day coefficient diverges) is treated as a failed fit: its fitted cells are non-finite and count toward the non-finite share (§2), and its zero cells keep their Jeffreys draws. The case was found in the 2-replicate A1/A2 timing chunk (Task 12), which measures compute time only and is not a result run; under `est-v2` such a fit stopped the whole cell. Fits that completed under `est-v2` are unchanged, so the A0 results stand (A0 completed under `est-v2`, which would have stopped on such a fit). `ESTIMATOR_VERSION` = `est-v3`. This also applies to the field analysis. Added by the controller before the first A1–A5 result run; user confirmation is pending at the next merge gate.
16. **Non-finite share per estimand; points without evaluable targets:** the non-finite rule of §2 is applied to the estimand that a decision judges: A1 (boundary rates) uses `rate_nonfinite_share`, and A2 (`AUFR`) uses `aufr_nonfinite_share`; both shares are reported for every protocol. A design point × miss level at which a protocol has no evaluable target (every target excluded) fails that protocol, in A1 and in A2. Added by the controller before the first A1–A5 result run; user confirmation is pending at the next merge gate.

## 8. Change control

After the first A1–A5 run, any change is a new dated version of this document and is reported as a deviation in every result that it affects.

Versions:

- **1.1 (2026-10-20, user decision D023).** Made during the A1/A2 run, before any A1–A5 result was seen. The user limited the simulations to 8 threads and a 10 GB Java heap while the PC is in use, with 16 threads only while it is idle. The user then adopted the Tier 3 scope of §6 by decision rather than by projection: A3 and A4 use the centre point only, Morris uses 30 replicates per point, and A5 runs the centre point first. The A5 corners are deferred until after the midterm and are not dropped. Every affected result carries this as a declared deviation (§3). Replicates per acceptance cell (200), all thresholds and the A1/A2 scope are unchanged. Items 15 and 16 of §7 remain pending user confirmation at the next merge gate. Details: `analysis/outputs/sim/first/compute_tier.md`.
- **1.2 (2026-10-26, user decision D025).** Made after the first-pass A1/A2 and Morris results were seen. A second pass, `audit1`, reruns A1/A2, Morris and A3 (centre point) with the facility configuration `facilities/doota_audit1`, built from the remote audit of D024. In that configuration:
  - floor sizes come from registered retail area;
  - F&B shares come from the official directory, which is inert where `gamma` = 0;
  - the transit entry moves from B2 to 1F;
  - the hourly profile follows Kakao Map.

  Everything else matches the first pass: rules, thresholds, scenario ranges (`ranges_audit1.csv` is a copy of `ranges_first.csv`), design points, seeds and the Tier 3 scope. A4 is not rerun, because its design fixes equal floor sizes and its own entries; A5 is not rerun, because it uses synthetic facilities. The first-pass results stand. The `audit1` results are reported beside them as the same experiments under the audited facility configuration, and the configuration change is a declared deviation in every `audit1` result. Vertical routes stay `ASSUMED_PRE_AUDIT`. Details: `analysis/outputs/sim/audit1/compute_tier.md` and `simulation/gama/VerticalFlow/includes/facilities/doota_audit1/SOURCES.md`.

## 9. Candidate references — pending review

Under `RESEARCH_RULES.md` this entry is not curated literature; it must pass the normal review and approval flow before entering `literature/`. Unverified fields are marked `UNKNOWN`.

| Use | Reference | Identifier |
|---|---|---|
| Monte Carlo standard error of coverage; per-estimand performance measures (§2) | Morris TP, White IR, Crowther MJ (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine*. Volume and pages `UNKNOWN`. | DOI 10.1002/sim.8086 |
