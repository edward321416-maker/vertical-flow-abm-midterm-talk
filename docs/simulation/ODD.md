# ODD — VerticalFlow (Simulation A generator and virtual observer)

Structure: ODD protocol, second update (Grimm et al. 2020; candidate reference pending review, spec §10).
Implementation: `simulation/gama/VerticalFlow/models/vertical_flow.gaml` (GAMA 2025.06.4).
Inputs: cell files written by `analysis/R/gama_runner.R`; scenario ranges and rules in `docs/simulation/simulation_a_rules.md`; the range tables themselves in `simulation/gama/VerticalFlow/includes/scenarios/`, and the fixed generator values and observer protocols in `analysis/R/design.R`.
Status: describes the model version used for the A0–A5 first pass (model file as of commit `16381bc`; the A0 verification record in the Appendix post-dates it). Simulated outputs are never field observations.
Scope: the simulation model only. How the simulated tables are analysed (estimators, evaluation) is specified in the spec (§4.4) and `analysis/R/`, not here.

## 1. Purpose and patterns

The model generates anonymous vertical movement in a multi-level commercial facility with fully known boundary crossings, and observes that movement with a virtual one-person counting protocol. Estimates from the virtual observations are then compared with the truth (virtual-observer approach, Zurell et al. 2010; candidate reference pending review, spec §10). The model validates measurement designs. It is not a model of any real facility's behaviour.

Patterns the model must reproduce to be fit for this purpose: (P1) overdispersed window counts with between-day variation; (P2) upward flow that changes along the floor stack; (P3) multi-floor trips that cross every intermediate boundary; (P4) elevator trips that cross boundaries without passing the counted escalator route (D018).

## 2. Entities, state variables and scales

| Entity | State variables |
|---|---|
| Facility (world) | floors in vertical order with size basis `A_j`, program term `x_j`, dwell offset, elevator service; boundaries with escalator up/down and stair availability; entries with floor and share (the entry type in `entries.csv` is documentation only; the model does not read it); blocks; hourly arrival profile by day type; day multiplier; ground-truth accumulator per block × boundary × direction × mode |
| Visitor group | group id, persons, entry floor, current floor, entry time, next event time, moving flag, leaving flag, destination, mode, direction, pending boundary crossings with times, arrival time of the current trip, trip number |
| Field observer | protocol id, construct label, counted modes, down-counting flag, miss parameters (`miss_base`, `miss_edge`, `miss_edge_s`, `miss_flow`, `down_load`), scheduled windows (day, block, boundary, start, end, order) with true and observed counts |

Time step 10 s. A simulated day runs from opening (`open_min` in `facility.csv`) to `sim_end_min` in the cell file. The experiment drivers set `sim_end_min` to 30 minutes after the end of the last block (`run_settings()` in `analysis/R/design.R`), so a day runs from opening to 30 minutes after the last block. Several days are simulated in one run (`n_days`, with one day type per day). Space is not represented: floors are ordered indices, and floor separation is `d_ij = |j − i|`.

## 3. Process overview and scheduling

The world agent's reflexes run first in each step, in declaration order, and the group agents' reflex runs after them. Observers have no reflex of their own; they act only when a crossing is passed to them. In every step, in this order:

1. The facility checks for the end of the day (`time − day_start ≥ day length`). If the day has ended, it counts the persons of the groups still present as forced exits and removes those groups, writes the day's outputs (truth, conservation, observer windows, optional logs, timing), and starts the next day with a new day multiplier and zeroed accumulators. After the last day, no further arrivals or outputs are produced.
2. The facility generates arrivals (submodel 7.1). New groups are created with their first dwell already drawn, so they do not act in the step they arrive.
3. Each group whose next event time has passed acts. A moving group processes its due boundary crossings in order (truth accumulator, optional crossing log, observers); when none is pending and its arrival time has passed, it arrives (submodel 7.2, 7.5). A dwelling group makes its next choice (submodels 7.3 and 7.4). The model does not rely on the order in which groups are processed within a step.

Events are processed at the first step at or after their scheduled time, so a crossing, an arrival or the end of a dwell is handled less than one step (10 s) late. Crossings are always stamped with their scheduled time, not the time of processing.

## 4. Design concepts

- **Basic principles:** gravity-type destination utility inside a nested logit. Exponentiating the upward utilities gives the first-semester choice rule at floor level, without its jitter term (spec §4.2).
- **Emergence:** boundary flows, `AUFR` profiles, and window-count dispersion emerge from arrivals, dwell, choice and exit.
- **Adaptation and objectives:** groups choose among the alternatives with multinomial-logit probabilities, which is equivalent to choosing the alternative with the highest random utility under independent Gumbel errors; the model draws from the probabilities directly. There is no learning and no prediction.
- **Sensing:** groups know floor attributes, the available modes and the time since they entered; there is no congestion sensing.
- **Interaction:** none between groups (no capacity limits); observers do not affect groups.
- **Stochasticity:** Poisson group arrivals; group size `1 + Poisson`; log-normal day multiplier; log-normal dwell; logit choices; truncated exponential elevator wait; binomial observer misses; optional uniform program draws (A5).
- **Collectives:** visitor groups move as one unit.
- **Observation:** per replicate folder (`<runs_root>/<cell_id>/rep_<n>/`), CSV files whose column contracts are defined in `analysis/R/io.R`:
  - `truth.csv`: persons per day, block, boundary, direction and mode (zero-filled for every combination);
  - `observed.csv` (when observers are enabled): one row per scheduled window of every protocol, with true and observed up and down counts; `down_count` is `−1` when down flow is not counted (read as missing in R) and `valid_window` is always true;
  - `conservation.csv`: groups entered, persons entered, persons exited and persons forced out at the end of each day;
  - `timing.csv`: cumulative wall-clock milliseconds since initialization, after each day;
  - optional `crossings.csv` (every crossing, also outside blocks, with the time of day in seconds), `decisions.csv` (every choice) and, for A5, `floors_realized.csv` (the drawn `x_j`).

## 5. Initialization

The cell file and facility CSVs are read; for A5, `x_j` is optionally drawn per replicate; the nested-logit structure is precomputed; observers load their schedules; day 1 starts with a new day multiplier. Output files are created with headers first. The facility is empty at the start of every day. The random seed of each run is set by `seed_for(cell_id, rep_id)` in `analysis/R/gama_runner.R` and passed to GAMA through the `seed` attribute of the headless XML; every random draw of a run comes from that one seed, and identical seeds give identical output tables.

## 6. Input data

Facility CSVs (`floors`, `boundaries`, `entries`, `blocks`, `day_profile`, `facility`), the observer protocol and schedule CSVs (read only when observers are enabled), and the cell file. No time series drive the model. Of `facility.csv` the model reads only `open_min`. The R side validates the facility before a run (`validate_facility()` in `analysis/R/facility.R`), including that an escalator or stair route leads from every floor back to every entry floor; the model itself checks only basic shapes (at least two floors, floors sorted by index, one boundary per consecutive floor pair, one day type per day, a positive day length, and the presence of every numeric cell-file key it reads). Identifiers are written to CSV unquoted, so they must not contain commas, quotes or newlines. The first-pass facility is the Doota Mall scenario configuration in `simulation/gama/VerticalFlow/includes/facilities/doota/` (floors B2–5F; values marked `ASSUMED_PRE_AUDIT` there are scenario inputs, not observations).

Cell-file keys used below: `alpha` (α), `beta` (β), `gamma` (γ), `delta_down` (δ_down), `theta0`, `theta1`, `theta2` (θ0, θ1, θ2), `imp_escalator`, `imp_stairs`, `imp_elevator` (`I_m`), `tau_escalator`, `tau_stairs`, `tau_elevator` (`τ_m`), `mode_mu` (μ), `elevator_enabled`, `base_rate_gpm`, `group_extra_mean`, `day_sd` (σ), `dwell_meanlog`, `dwell_sdlog`, `esc_s`, `stair_s`, `elev_wait_mean_s`, `elev_s_per_floor`, `n_days`, `day_types`, `sim_end_min`, `x_fnb_random`, `x_fnb_low`, `x_fnb_high`, and the flags `log_crossings`, `log_decisions`, `observers_enabled`.

## 7. Submodels

**7.1 Arrivals.** Groups per minute at entry `e`: `λ_e(t) = base_rate_gpm · share_e · profile(hour, day type) · M_day`, with `M_day = exp(N(−σ²/2, σ))` and `σ = day_sd`. The number of groups in a step is Poisson(`λ_e · Δt`), with `Δt = 10/60` minutes. `M_day` is drawn once per day, independently across days, and has mean 1. `hour` is the hour of the time of day (opening time plus time since day start; at most 23) and the profile column is `WE` for a weekend day and `WD` for any other day type; an hour missing from `day_profile.csv` has intensity 0. Each new group has `persons = 1 + Poisson(group_extra_mean)`, appears on the entry floor of its entry, and begins with a dwell there (7.2).

**7.2 Dwell.** Minutes per floor visit: `exp(N(dwell_meanlog + offset_j, dwell_sdlog))`, where `offset_j` is the dwell offset of the floor being visited. A dwell is drawn on arrival at a floor, except that a group that is leaving does not dwell on its entry floor (7.5).

**7.3 Exit or destination (upper level).** At the end of each dwell, with `elapsed` the minutes since the group entered: `V_exit,i = θ0 + θ1·elapsed + θ2·x_i`; `V_ij = ln A_j + γ·x_j − α·ln d_ij − β·ln Ī_ij + δ_down·[j < i]`; multinomial logit over the exit and every reachable floor `j ≠ i`. A floor is reachable from `i` when at least one mode is available for `i → j` (7.4). Exit is always available.

**7.4 Mode choice and movement (lower level).** Mode cost `c_ijm = ln I_m + τ_m·(d_ij − 1)`; `P(m | i, j) ∝ exp(−μ·c_ijm)` over available modes; composite `ln Ī_ij = −(1/μ)·ln Σ_m exp(−μ·c_ijm)`, which equals `ln I_m` for a single mode on an adjacent trip. A mode is available for `i → j` as follows. Elevator: the elevator is enabled and both floors are elevator-served. Escalator: every boundary between the floors has an escalator in the direction of travel (`esc_up` for an upward trip, `esc_down` for a downward trip). Stairs: every boundary between the floors has stairs. Escalator and stair trips cross boundary `k` (counting from the origin floor, `k = 1..d_ij`) at `t0 + (k − 0.5)·per_boundary_time` and arrive at `t0 + d_ij·per_boundary_time`, where `t0` is the decision time and `per_boundary_time` is `esc_s` for the escalator and `stair_s` for stairs. Elevator trips wait, then cross boundary `k` at `t0 + wait + k·s_per_floor` and arrive at `t0 + wait + d_ij·s_per_floor`, with `s_per_floor = elev_s_per_floor`. The wait is `−elev_wait_mean_s · ln(1 − U)` with `U` uniform on [0, 0.999], an exponential wait truncated at about 6.9 times its mean, so the realized mean wait is about 99.3 % of `elev_wait_mean_s`. A multi-floor trip crosses every boundary between origin and destination, in order, and an elevator trip is recorded as a crossing of each boundary it spans, with mode `elevator`, which an observer counting only the escalator route does not see (D018). The two levels are consistent with random utility maximization when the logsum coefficient `β/μ` lies in [0, 1], which the first-pass ranges respect (β ≤ 2, μ = 2); the code does not enforce this.

**7.5 Exit.** A group that chooses to exit returns to its entry floor using the same mode logit, then leaves. A group that chooses to exit while already on its entry floor leaves at once. Its persons then count as exited. (The model uses the entry floor as the exit floor.)

**7.6 Ground truth.** Every crossing inside a block (time of day `t` with block start ≤ `t` < block end) adds the group's persons to the accumulator cell (block, boundary, direction, mode). Crossings outside every block are not accumulated. The optional crossing log records each crossing individually, including those outside blocks.

**7.7 Virtual observer.** Each protocol's windows are fixed by `analysis/R/schedule.R`. Every protocol has one observer; each crossing is passed to all observers, and each observer draws its misses independently. A crossing of a counted mode at boundary `b`, time `t` belongs to the window on `b` with `start ≤ t < end` (half-open); a crossing that belongs to no window is ignored. The observer has no position: walking and reset times appear only as gaps between scheduled windows. Because crossings reach the observer at most one step out of time order, a window is passed over only once it ended more than one step before the crossing being processed. On a hit, the group's persons are first added to the window's true count (up or down; the true down count is recorded even when down flow is not counted). Each person in the group is then missed with probability `p = clamp(f·(miss_base + miss_edge·[edge] + miss_flow·load), 0, 0.95)`, with `f = down_load` when down flow is counted and `f = 1` otherwise. Here `edge` means the crossing lies within `miss_edge_s` of the window start or of the window end, and `load` is the persons per minute so far in the window, namely the window's true up count (plus true down count when down flow is counted) including the current group, divided by the minutes since the window start (at least 1). The number of persons observed is Binomial(`n`, `1 − p`); when `p = 0` the detection probability is 1 and all `n` persons are observed without a binomial draw. Down crossings are observed only when down flow is counted. The observer records the true and observed counts of every window; windows with no crossing are written with zero counts (down count `−1` when down flow is not counted).

## References (candidate references pending review, spec §10)

- Grimm et al. 2020
- Zurell et al. 2010

## Appendix. Implementation notes and verification record

- **Seeds and reproducibility.** See §5. A0 check A0a-7 confirms identical truth and observed tables for identical seeds, and A0a-8 that a different seed gives different output.
- **Verification record.** A0 passed 10 of 10 checks on 2026-10-20: `analysis/outputs/sim/a0/a0_report.md` (check tables beside it). It covers the exit/destination and mode choice frequencies against the specified logit, conservation (entered = exited + forced exit), the crossing sequence of every trip (P3, P4), observer window truth against a recount from the crossing log, the perfect observer, seed reproducibility, and, for two perfect-observer scenarios, the coverage of the boundary-rate confidence intervals in the estimator pipeline.
- **Not covered by A0.** The patterns P1 (overdispersion with between-day variation) and P2 (changing upward flow along the stack) are properties of the scenario ranges and are not tested by A0; the comparison of simulated and observed repeated-window variability is the pilot-informed pass (spec §5, parameter policy).
- **Platform idioms.** Binomial draws use `(p >= 1.0) ? n : binomial(n, p)` because `binomial(n, 1.0)` does not terminate in GAMA 2025.06.4; GAML range loops that can be empty are guarded. Details are in `simulation/README.md`.
