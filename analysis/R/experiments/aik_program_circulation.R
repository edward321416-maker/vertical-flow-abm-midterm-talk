# Simulation C: AIK paper experiments E1 (random program draws) and E2 (fixed arrangements), see
# docs/simulation/aik_experiment_plan.md (frozen before the first run). Truth logs only; observers are off.
# Usage: D:\vcpf\bin\Rscript.cmd analysis/R/experiments/aik_program_circulation.R <cores> [n_rep=200] [stage=all] [cell_regex]
#   stage = e1, e2 or all. cores is at most 8 (user limit). n_rep < 200 is a pilot or smoke check, not a result: it writes to
#   analysis/outputs/sim/aik_pilot/ under cell ids prefixed aikp_. cell_regex keeps only the cells whose id matches.
# Outputs under analysis/outputs/sim/<aik|aik_pilot>/: aik_cells.csv, aik_boundary_rep.csv (one row per cell, replicate and
# boundary), aik_timing.csv, aik_checks.csv. Runs resume from finished replicates (run keys).
Sys.setenv(VCPF_ROOT = normalizePath("."))
source(file.path("analysis", "R", "io.R"))
source_pipeline(Sys.getenv("VCPF_ROOT"))

usage <- "usage: aik_program_circulation.R <cores> [n_rep=200] [stage=all] [cell_regex]"
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1L) stop(usage)
cores <- suppressWarnings(as.integer(args[[1L]]))
if (is.na(cores) || cores < 1L || cores > 8L) stop("cores must be 1..8 (user limit); ", usage)
n_rep <- if (length(args) >= 2L) suppressWarnings(as.integer(args[[2L]])) else 200L
if (is.na(n_rep) || n_rep < 1L || n_rep >= SEED_REP_LIMIT) stop("n_rep must be a positive integer below ", SEED_REP_LIMIT, "; ", usage)
stage <- if (length(args) >= 3L) args[[3L]] else "all"
if (!stage %in% c("e1", "e2", "all")) stop("stage must be e1, e2 or all; ", usage)
cell_regex <- if (length(args) >= 4L) args[[4L]] else NULL
full <- n_rep == 200L
tag <- if (full) "aik" else "aikp"
if (!full) message(sprintf("n_rep = %d (plan: 200): pilot or smoke check, not a result", n_rep))

lp <- local_paths()
out_dir <- file.path("analysis", "outputs", "sim", if (full) "aik" else "aik_pilot")
cells_dir <- file.path(lp$runs_root, "_cells", tag)
fac_root <- file.path(lp$runs_root, "_facilities")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# ---- facilities: the plain 9-floor stack (E1) and the four fixed arrangements (E2) -------------------------------------
N_FLOORS <- 9L
base_fac <- make_synthetic_facility(N_FLOORS, file.path(fac_root, "aik_S09"), template = DOOTA_DIR)
PATTERN_X <- list(
  UNIFORM = c(0.05, rep(0.20, 8)),
  TOP1    = c(0.05, rep(0.107143, 7), 0.85),
  STEP3   = replace(rep(0.05, N_FLOORS), c(2, 5, 8) + 1L, 0.45),
  LOW3    = replace(rep(0.05, N_FLOORS), c(1, 2, 3) + 1L, 0.45))
pattern_fac <- function(name) {
  d <- file.path(fac_root, paste0("aik_S09_", tolower(name)))
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  for (f in c("boundaries.csv", "entries.csv", "blocks.csv", "day_profile.csv", "facility.csv")) {
    if (!file.copy(file.path(base_fac$dir, f), file.path(d, f), overwrite = TRUE)) stop("cannot copy ", f)
  }
  fl <- copy(base_fac$floors)
  fl[, `:=`(x_fnb = PATTERN_X[[name]], program_source = paste0("aik_pattern_", name))]
  fwrite(fl, file.path(d, "floors.csv"))
  read_facility(d)
}
pat_fac <- setNames(lapply(names(PATTERN_X), pattern_fac), names(PATTERN_X))

# ---- design ---------------------------------------------------------------------------------------------------------------
CIRC <- list(cont = list(imp_escalator = 1.0, esc_s = 25), frag = list(imp_escalator = 2.45, esc_s = 55))
gfmt <- function(g) format(g, trim = TRUE)
design <- rbindlist(list(
  if (stage %in% c("e1", "all")) CJ(exp = "e1", pattern = NA_character_, gamma = c(0, 2, 4, 8), circ = names(CIRC), sorted = FALSE)[
    , cell_id := sprintf("%s_e1_g%s_%s", tag, gfmt(gamma), circ)],
  if (stage %in% c("e2", "all")) rbind(
    CJ(exp = "e2", pattern = names(PATTERN_X), gamma = 4, circ = names(CIRC), sorted = FALSE),
    data.table(exp = "e2", pattern = c("UNIFORM", "TOP1"), gamma = 0, circ = "cont"))[
    , cell_id := sprintf("%s_e2_%s_g%s_%s", tag, tolower(pattern), gfmt(gamma), circ)]), use.names = TRUE)
if (!is.null(cell_regex)) design <- design[grepl(cell_regex, cell_id)]
if (nrow(design) == 0L) stop("no cell selected")
stopifnot(!anyDuplicated(design$cell_id))
# Plan revision r1 (before the first full run): E2 uses 100 replicates, E1 200 (pilot: about 10 s per simulated day at gamma 8).
n_e2 <- if (full) 100L else n_rep
design[, n := ifelse(exp == "e2", n_e2, n_rep)]
message(sprintf("%d cells, %d runs, %d cores", nrow(design), sum(design$n), cores))

pt <- center_point(read_ranges("first"))
cell_params <- function(fac, gamma, circ, random_x) {
  modifyList(pt, c(run_settings(fac, 4L), list(x_fnb_random = as.integer(random_x), x_fnb_low = 0, x_fnb_high = 0.5, theta2 = 0,
                                               gamma = gamma), CIRC[[circ]]))
}
fac_of <- function(d) if (d$exp == "e1") base_fac else pat_fac[[d$pattern]]
cells <- rbindlist(lapply(seq_len(nrow(design)), function(k) {
  d <- design[k]
  write_cell(d$cell_id, cell_params(fac_of(d), d$gamma, d$circ, d$exp == "e1"), fac_of(d), list(), cells_dir, lp$runs_root)
}))
fwrite(merge(design, cells, by = "cell_id", sort = FALSE), file.path(out_dir, "aik_cells.csv"))

# ---- run ------------------------------------------------------------------------------------------------------------------
t0 <- Sys.time()
n_new <- 0L
for (e in unique(design$exp)) {
  ce <- cells[cell_id %in% design[exp == e, cell_id]]
  n_new <- n_new + run_cells(ce, reps = seq_len(design[exp == e, n[1L]]), cores = cores)
}
message(sprintf("simulation finished: %d new runs in %.1f min", n_new, as.numeric(difftime(Sys.time(), t0, units = "mins"))))

# ---- collect, check, tidy -------------------------------------------------------------------------------------------------
tidy_cell <- function(d) {
  cid <- d$cell_id
  fac <- fac_of(d)
  n <- d$n
  assert_cell_conservation(cid, n)
  tru <- collect_runs(cid, "truth", reps = seq_len(n))
  up <- tru[direction == "up", .(U = sum(persons), U_esc = sum(persons[mode == "escalator"]),
                                 U_stairs = sum(persons[mode == "stairs"]), U_elev = sum(persons[mode == "elevator"])),
            by = .(rep_id, boundary_id)]
  bd <- fac$boundaries[, .(boundary_id, boundary_order, lower_floor_index, upper_floor_index)]
  up <- merge(up, bd, by = "boundary_id")
  xr <- if (d$exp == "e1") {
    collect_runs(cid, "floors_realized", reps = seq_len(n))[, .(rep_id, floor_index = as.integer(floor_index), x_fnb)]
  } else {
    merge(CJ(rep_id = seq_len(n), floor_index = fac$floors$floor_index), fac$floors[, .(floor_index, x_fnb)], by = "floor_index")
  }
  chk <- data.table(cell_id = cid, n_rep = n,
                    floors_per_rep_ok = all(xr[, .N, by = rep_id]$N == N_FLOORS),
                    x_min = min(xr$x_fnb), x_max = max(xr$x_fnb), x_mean = mean(xr$x_fnb),
                    budget_S01_S08 = xr[floor_index >= 1L, sum(x_fnb) / uniqueN(rep_id)],
                    n_missing_rep_boundary = n * (N_FLOORS - 1L) - nrow(up),
                    n_zero_U = sum(up$U == 0))
  up <- merge(up, xr[, .(rep_id, lower_floor_index = floor_index, x_lower = x_fnb)], by = c("rep_id", "lower_floor_index"))
  up <- merge(up, xr[, .(rep_id, upper_floor_index = floor_index, x_upper = x_fnb)], by = c("rep_id", "upper_floor_index"))
  setkey(xr, rep_id, floor_index)
  up[, M_above := mapply(function(r, u) xr[rep_id == r & floor_index >= u, mean(x_fnb)], rep_id, upper_floor_index)]
  setorder(up, rep_id, boundary_order)
  up[, `:=`(U_prev = shift(U), U_first = rep(U[1L], .N)), by = rep_id]
  up[, `:=`(AUFR = ifelse(U_prev > 0, U / U_prev, NA_real_), RUI = ifelse(U_first > 0, U / U_first, NA_real_),
            AUFR_esc = NA_real_, delta = x_upper - x_lower)]
  up[, AUFR_esc := {p <- shift(U_esc); ifelse(p > 0, U_esc / p, NA_real_)}, by = rep_id]
  up[, `:=`(cell_id = cid, exp = d$exp, pattern = d$pattern, gamma = d$gamma, circ = d$circ)]
  list(rows = up, check = chk)
}
res <- lapply(seq_len(nrow(design)), function(k) tidy_cell(design[k]))
rows <- rbindlist(lapply(res, `[[`, "rows"))
checks <- rbindlist(lapply(res, `[[`, "check"))
tim <- rbindlist(lapply(seq_len(nrow(design)), function(k) sim_day_seconds(design$cell_id[k], design$n[k])))
timing <- tim[, .(n_runs = uniqueN(rep_id), sec_day_median = median(day_s), sec_day_mean = mean(day_s), sec_day_max = max(day_s)),
              by = cell_id]
fwrite(rows, file.path(out_dir, "aik_boundary_rep.csv"))
fwrite(checks, file.path(out_dir, "aik_checks.csv"))
fwrite(timing, file.path(out_dir, "aik_timing.csv"))
message("wrote ", normalizePath(out_dir, winslash = "\\"))
print(checks)
print(timing)
