# AIK paper experiments (Simulation C) — plan, frozen before the first run

Date: 2026-11-01
Status: FROZEN before the first full run. Any later change is a dated deviation and is reported in every result it touches.
Direction: the user chose "keep the topic, rewrite with the current model" on 2026-11-01, after an audit showed that the manuscript's Track 1/Track 2 numbers were typed constants, not simulation output (memory note `paper-numbers-not-simulated`).
Model: `simulation/gama/VerticalFlow/models/vertical_flow.gaml`, unchanged since commit `16381bc` (md5 `76a3e67ca6dbfdc09c46cd024f5b7685`). The model is not edited for this study.

## 1. What the model can and cannot say

- The model is a non-spatial nested logit over floors. A floor's program enters only as destination attractiveness `gamma * x_j` (`theta2 = 0`, so the program of the current floor does not affect exit). There is no origin-to-destination spillover term, so an "adjacent-floor interaction" is not built in.
- `gamma` is therefore an assumption, not an estimate. It is a sensitivity axis. Every result is conditional on the model structure and on assumed parameters, and is worded as "what the stated mechanism implies", never as an observed effect in real malls.
- Existing evidence: A5 (first pass, centre point, 11 floors) found a truth-level rate ratio of at most 1.05 per 0.1 of adjacent program contrast even at `gamma` = 6, and 1.03 at `gamma` = 4. The adjacent-contrast construct may be weak in this model. This study tests that, and tests an alternative construct, rather than assuming the contrast matters.

## 2. Research questions (restated for the model)

- RQ1: How does boundary upward flow and `AUFR` attenuate with height when program is held neutral (`gamma` = 0)? Is the profile smooth or stepped?
- RQ2: Does the adjacent program contrast `Delta x` change `AUFR` at a boundary, and is it a better predictor than the cumulative program above the boundary?
- RQ3: Does circulation friction change the size of the program effect? The answer is reported on both a multiplicative and an additive scale, because an additive interaction can appear in a purely multiplicative model.
- RQ4 (design implication): at an equal total program budget, does the vertical arrangement of F&B (uniform, single top anchor, stepping, base-loaded) change how far visitors reach?

## 3. Facility and fixed settings

- Facility: synthetic 9-floor stack from `make_synthetic_facility(9, ..., template = DOOTA_DIR)`: floors S00–S08, one street entry at S00, escalators (both ways), stairs and an elevator at every boundary, `size_basis` 1 on every floor. Opening hours, blocks (midday, afternoon, evening) and the weekday/weekend profile are copied from the Doota template. Boundary `b` = S(b-1)–S(b), `b` = 1..8.
- Parameter point: `center_point(read_ranges("first"))`: base_rate_gpm 7, group_extra_mean 0.75, day_sd 0.25, dwell_meanlog 2.851891, dwell_sdlog 0.75, alpha 1.75, beta 1.0, theta0 −0.25, theta1 0.02, delta_down 0, plus `FIXED_GEN` (theta2 0, imp_stairs 3.0, imp_elevator 2.5, tau 0.2/0.7/−0.1, mode_mu 2, elevator enabled, stair_s 60, elev_wait_mean_s 60, elev_s_per_floor 6).
- Circulation levels (assumed, not estimated; the 2.45 value and the 35 m detour come from the manuscript draft): `C_cont`: `imp_escalator` 1.0, `esc_s` 25 s per boundary. `C_frag`: `imp_escalator` 2.45, `esc_s` 55 s per boundary (25 s plus a 35 m detour at 1.2 m/s). `beta` stays at 1.0 in both.
- Runs: 4 simulated days (WE, WE, WD, WD), observers off, seed `seed_for(cell_id, rep_id)`. Replicates per cell: 200 in E1, 100 in E2 (revision r1, below).
- Resources: at most 8 cores, Java heap 10 GB (`Gama.ini`), no second GAMA JVM. A watchdog stops the run if free memory falls below 1.5 GB; runs resume from finished replicates (run keys).

## 3b. Revision r1 (2026-11-01, before the first full run, no result seen)

A 32-run pilot (cells `gamma` = 8, 8 cores, 16 replicates each) took 2.8 min, about 10 s per simulated day, with a Java peak of 2.3 GB and a system free-memory minimum of 3.9 GB. At 200 replicates in every cell the plan would take about 3 h. E2 therefore uses 100 replicates per cell: its arrangements are fixed, so replicate-to-replicate variation comes only from arrivals, and `RUI` is a ratio in which the day multiplier cancels. E1 keeps 200. Planned total: 2,600 runs, about 2.2 h. Nothing else in this plan changes. The pilot data (`analysis/outputs/sim/aik_pilot/`) is used only to test the scripts and is not reported.

## 4. Designs

E1 (RQ2, RQ3): program drawn per replicate, `x_j ~ U(0, 0.5)` independently on every floor (`x_fnb_random`). Cells: `gamma` in {0, 2, 4, 8} × circulation in {`C_cont`, `C_frag`} = 8 cells. `gamma` = 0 is the null control; `gamma` = 8 is beyond the A5 plateau.

E2 (RQ4): fixed arrangements with the same total program budget on S01–S08 (sum 1.60, mean 0.20) and S00 fixed at 0.05:

| Pattern | Program `x_j` |
|---|---|
| UNIFORM | 0.20 on S01–S08 |
| TOP1 | 0.85 on S08; 0.107143 on S01–S07 |
| STEP3 | 0.45 on S02, S05, S08; 0.05 on the other five |
| LOW3 | 0.45 on S01, S02, S03; 0.05 on the other five |

Cells: 4 patterns × 2 circulation states at `gamma` = 4 (8 cells), plus UNIFORM and TOP1 at `gamma` = 0 under `C_cont` as a null check (2 cells).

RQ1: from E1 cells with `gamma` = 0. As a real-building reference, the existing audited Doota runs (`audit1`, `gamma` = 0, 18 parameter points) are summarised without new runs; their entry floor is 1F, so only boundaries above 2F–3F have a defined `AUFR`.

## 5. Outcomes

For replicate `r` and boundary `b`: `U_rb` = persons crossing the boundary upward, all modes, summed over all days and blocks (truth log). Sensitivity construct: escalator only (`U_esc_rb`, the construct of A5).
- `AUFR_rb = U_rb / U_r,b-1` for b = 2..8 (7 values; b = 1 has no lower boundary).
- `RUI_rb = U_rb / U_r1`. Top reach `T_r = RUI_r8`. Mean reach `R_r = mean(RUI_rb, b = 2..8)`.
- Program contrast of boundary b: `Delta_rb = x(S_b) − x(S_b-1)`. Cumulative program above: `M_rb = mean of x(S_j), j >= b`.

## 6. Analyses

A1 (RQ1): per cell with `gamma` = 0, mean and 2.5/97.5 percentiles over replicates of `AUFR_b` and `RUI_b`. Shape: fit `log U_b` on `b` linearly and with boundary as a factor; report the maximum departure of the cell-mean profile from the line and the F test over replicate means. "Stepped" is reported only if both the departure exceeds 0.10 log units and p < 0.01.

A2 (RQ2): for each E1 cell, OLS `log AUFR_rb ~ factor(b) + 10 * Delta_rb`, standard errors clustered by replicate (CR1 sandwich). Report `exp(theta)` with 95% CI: the multiplicative change in `AUFR` per +0.1 of contrast. Validity check: at `gamma` = 0 the CI must include 1; otherwise the estimator is flagged and no `gamma` > 0 result is interpreted.

A2b (construct comparison): for each E1 cell with `gamma` > 0, quasi-Poisson GLM `U_rb ~ factor(b) + factor(r) + predictor`, with the predictor one of: `Delta` (adjacent contrast), `x(S_b)` (upper-floor program), `M` (cumulative program above). Compare by deviance explained relative to the model without the predictor. Expectation, from the model's mechanism (multi-floor trips cross every boundary below their destination): `M` explains more than `Delta`. The result is reported whichever way it goes.

A3 (RQ3): at each `gamma` > 0, difference of `theta` between `C_frag` and `C_cont` (cells are independent, SE = sqrt(se1² + se2²)), on the log scale. Additive scale: the same regression with `AUFR` (not logged) as outcome; report the slope per +0.1 in each state, the ratio `slope_frag / slope_cont` and 1 − that ratio (the draft's "erosion"), with a cluster bootstrap (2,000 resamples of replicates) 95% CI. Both scales are reported together.

A4 (RQ4): per circulation state, mean `T` and `R` per pattern with 95% CI. Primary contrasts: STEP3 − TOP1 and STEP3 − UNIFORM, Holm-adjusted within each outcome and circulation state. All other pairs are secondary. Null check: UNIFORM vs TOP1 at `gamma` = 0 must be indistinguishable (CI includes 0).

## 7. Checks before any interpretation

- `assert_cell_conservation` passes in every cell (entered = exited + forced exit).
- `floors_realized.csv` of E1 has `x` within [0, 0.5], mean near 0.25, and 9 floors per replicate; E2 fixed `x` match the table in section 4, with sums equal to 1.60 (±1e-5).
- Seeds are unique across all runs; no replicate is missing; every zero denominator is counted and reported.
- Number of replicates with `U_rb = 0` for any b is reported per cell.

## 8. Reporting rules

- Every cell is reported. No cell, replicate or construct is dropped after the fact.
- Figures use only these tables (no padded or resampled points, no typed constants). Tables are generated by script into `analysis/outputs/sim/aik/`.
- Wording: results are model-conditional implications. No claim about observed mall behaviour, no "demonstrated in practice". Design guidelines are stated as hypotheses the model supports under the stated assumptions.
- The old manuscript numbers (Track 1 24 boundaries, Track 2 4×2, ANOVA F values, 34% erosion, S0–S4 profiles) are not used anywhere.
