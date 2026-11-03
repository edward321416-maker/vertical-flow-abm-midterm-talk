# Glue between R experiment drivers and GAMA headless (spec §4, §8).
suppressPackageStartupMessages(library(data.table))

MODEL_REL <- file.path("simulation", "gama", "VerticalFlow", "models", "vertical_flow.gaml")
RUN_DEFAULTS <- list(log_crossings = 0L, log_decisions = 0L, observers_enabled = 1L,
                     x_fnb_random = 0L, x_fnb_low = 0, x_fnb_high = 0.5)
GAMA_REQUIRED_KEYS <- c(
  "cell_id", "out_root", "protocols_file", "schedule_file", "floors_file", "boundaries_file",
  "entries_file", "blocks_file", "day_profile_file", "facility_file", "n_days", "day_types",
  "sim_end_min", "alpha", "beta", "gamma", "delta_down", "theta0", "theta1", "theta2",
  "imp_escalator", "imp_stairs", "imp_elevator", "tau_escalator", "tau_stairs", "tau_elevator",
  "mode_mu", "elevator_enabled", "base_rate_gpm", "group_extra_mean", "day_sd", "dwell_meanlog",
  "dwell_sdlog", "esc_s", "stair_s", "elev_wait_mean_s", "elev_s_per_floor", "log_crossings",
  "log_decisions", "observers_enabled", "x_fnb_random", "x_fnb_low", "x_fnb_high")

local_paths <- function(root = Sys.getenv("VCPF_ROOT", ".")) {
  f <- file.path(root, "simulation", "local_paths.csv")
  if (!file.exists(f)) stop("missing ", f, "; copy simulation/local_paths.example.csv and edit it")
  kv <- fread(f, colClasses = "character")
  setNames(as.list(kv$value), kv$key)
}

fwd <- function(path) normalizePath(path, winslash = "/", mustWork = FALSE)

# 31-bit polynomial string hash (base 131, modulus 2^31 - 1, exact in doubles), then one step of
# 10007 per cell so that replicates 0..10006 of a cell always get distinct seeds. Seeds lie in 1..2^31 - 2.
SEED_MODULUS <- 2147483647
SEED_REP_LIMIT <- 10007

seed_for <- function(cell_id, rep_id) {
  if (!is.character(cell_id) || length(cell_id) != 1L || is.na(cell_id)) stop("cell_id must be a single string")
  if (length(rep_id) != 1L || is.na(rep_id) || rep_id < 0 || rep_id >= SEED_REP_LIMIT) {
    stop("rep_id must lie in 0..", SEED_REP_LIMIT - 1, " so that replicate seeds stay distinct")
  }
  h <- 0
  for (cp in utf8ToInt(cell_id)) h <- (h * 131 + cp) %% SEED_MODULUS
  seed <- (h * SEED_REP_LIMIT + rep_id) %% SEED_MODULUS
  as.integer(if (seed == 0) 1 else seed)
}

final_step_for <- function(params, fac) {
  open_min <- as.numeric(facility_value(fac, "open_min"))
  as.integer(params$n_days * (params$sim_end_min - open_min) * 60 / STEP_S + 5)
}

format_value <- function(v) {
  if (is.numeric(v)) format(v, scientific = FALSE, digits = 15, trim = TRUE) else as.character(v)
}

write_cell <- function(cell_id, params, fac, protocols, cells_dir, runs_root, overrides = list()) {
  for (pr in protocols) {
    if (pr$n_days > params$n_days) {
      stop("cell ", cell_id, ": protocol ", pr$protocol_id, " spans ", pr$n_days,
           " days but the run has n_days = ", params$n_days,
           "; the extra schedule days and truth would be missing")
    }
  }
  dir.create(cells_dir, recursive = TRUE, showWarnings = FALSE)
  prot_path <- file.path(cells_dir, paste0(cell_id, "_protocols.csv"))
  sched_path <- file.path(cells_dir, paste0(cell_id, "_schedule.csv"))
  if (length(protocols) > 0) {
    pt <- protocol_tables(protocols, fac)
    fwrite(pt$protocols, prot_path)
    fwrite(pt$schedule, sched_path)
  }
  files <- list(floors_file = file.path(fac$dir, "floors.csv"), boundaries_file = file.path(fac$dir, "boundaries.csv"),
                entries_file = file.path(fac$dir, "entries.csv"), blocks_file = file.path(fac$dir, "blocks.csv"),
                day_profile_file = file.path(fac$dir, "day_profile.csv"), facility_file = file.path(fac$dir, "facility.csv"))
  files[names(overrides)] <- overrides
  run <- modifyList(RUN_DEFAULTS, params)
  run$observers_enabled <- if (length(protocols) > 0) 1L else 0L
  kv <- c(list(cell_id = cell_id, out_root = fwd(file.path(runs_root, cell_id)),
               protocols_file = fwd(prot_path), schedule_file = fwd(sched_path)),
          lapply(files, fwd), run)
  missing <- setdiff(GAMA_REQUIRED_KEYS, names(kv))
  if (length(missing) > 0) stop("cell ", cell_id, " lacks keys: ", paste(missing, collapse = ", "))
  path <- file.path(cells_dir, paste0(cell_id, ".csv"))
  # data.table(key = ...) would set the table key, so build the key/value columns by position.
  fwrite(setnames(data.table(names(kv), vapply(kv, format_value, "")), c("key", "value")), path)
  data.table(cell_id = cell_id, cell_file = fwd(path), final_step = final_step_for(run, fac), n_days = run$n_days)
}

write_headless_plan <- function(runs, model_path, plan_path) {
  sims <- vapply(seq_len(nrow(runs)), function(k) paste0(
    sprintf('  <Simulation id="%d" sourcePath="%s" finalStep="%d" experiment="headless_run" seed="%d">\n',
            k, model_path, runs$final_step[k], runs$seed[k]),
    '    <Parameters>\n',
    sprintf('      <Parameter name="cell_file" var="cell_file" type="STRING" value="%s"/>\n', runs$cell_file[k]),
    sprintf('      <Parameter name="rep_id" var="rep_id" type="INT" value="%d"/>\n', runs$rep_id[k]),
    '    </Parameters>\n    <Outputs/>\n  </Simulation>'), "")
  writeLines(c('<?xml version="1.0" encoding="UTF-8"?>', "<Experiment_plan>", sims, "</Experiment_plan>"), plan_path)
  invisible(plan_path)
}

# A replicate counts as finished only if its timing file has one row per day AND its run_key.txt equals
# the key of the current cell file, model, input files and seed, so outputs of an older cell or model
# are never accepted as current.
run_done <- function(out_dir, n_days, key) {
  f <- file.path(out_dir, "timing.csv")
  kf <- file.path(out_dir, "run_key.txt")
  if (!file.exists(f) || !file.exists(kf)) return(FALSE)
  if (!identical(readLines(kf, warn = FALSE)[1], key)) return(FALSE)
  tryCatch(nrow(fread(f)) >= n_days, error = function(e) FALSE)
}

file_md5 <- function(paths) unname(as.character(tools::md5sum(paths)))

# md5 of the cell file, the model and every input file the cell file names (facility, protocols,
# schedule, ...; entries that do not exist, such as the schedule of an observer-free cell, are skipped).
cell_key <- function(cell_file, model_path) {
  stopifnot(file.exists(cell_file), file.exists(model_path))
  kv <- fread(cell_file, colClasses = "character")
  refs <- kv[grepl("_file$", key) & file.exists(value)]
  refs <- refs[order(key)]
  parts <- c(cell = file_md5(cell_file), model = file_md5(model_path), setNames(file_md5(refs$value), refs$key))
  paste0(names(parts), "=", parts, collapse = ";")
}

run_key <- function(cell_key, seed) paste0(cell_key, ";seed=", seed)

# Remove everything a previous run left in the replicate folder, then record the key of the new run.
prepare_rep_dir <- function(out_dir, key) {
  unlink(out_dir, recursive = TRUE)
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  writeLines(key, file.path(out_dir, "run_key.txt"))
  invisible(out_dir)
}

# gama-headless.bat resolves ..\plugins and ..\GAMA.ini against the working directory, so it must
# run from its own folder. The GAMA workspace goes to <out_dir>/ws (unique to this call) instead of
# the install folder.
run_headless <- function(plan_path, cores, out_dir) {
  lp <- local_paths()
  plan_abs <- fwd(plan_path)
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  out_abs <- fwd(out_dir)
  launcher <- normalizePath(lp$gama_headless, winslash = "\\", mustWork = TRUE)
  old <- setwd(dirname(launcher))
  on.exit(setwd(old), add = TRUE)
  args <- c("-ws", shQuote(file.path(out_abs, "ws")), "-hpc", as.character(cores),
            shQuote(plan_abs), shQuote(out_abs))
  status <- system2(launcher, args,
                    stdout = file.path(out_abs, "headless_stdout.txt"),
                    stderr = file.path(out_abs, "headless_stderr.txt"))
  if (!identical(as.integer(status), 0L)) stop("gama-headless exited with status ", status, "; see ", out_abs)
  invisible(status)
}

run_cells <- function(cells, reps, cores, chunk_size = 400L, seed_fun = seed_for) {
  root <- normalizePath(Sys.getenv("VCPF_ROOT", "."), winslash = "/")
  lp <- local_paths(root)
  model <- fwd(file.path(root, MODEL_REL))
  if (!file.exists(model)) stop("missing model file ", model)
  cells <- copy(as.data.table(cells))
  cells[, base_key := vapply(cell_file, cell_key, "", model_path = model, USE.NAMES = FALSE)]
  runs <- cells[, .(rep_id = as.integer(reps)), by = .(cell_id, cell_file, final_step, n_days, base_key)]
  runs[, seed := as.integer(mapply(seed_fun, cell_id, rep_id))]
  runs[, key := run_key(base_key, seed)]
  runs[, out_dir := file.path(lp$runs_root, cell_id, paste0("rep_", rep_id))]
  runs <- runs[!mapply(run_done, out_dir, n_days, key)]
  if (nrow(runs) == 0) return(invisible(0L))
  for (k in seq_len(nrow(runs))) prepare_rep_dir(runs$out_dir[k], runs$key[k])
  plans_dir <- file.path(lp$runs_root, "_plans")
  dir.create(plans_dir, recursive = TRUE, showWarnings = FALSE)
  chunks <- split(seq_len(nrow(runs)), ceiling(seq_len(nrow(runs)) / chunk_size))
  for (ci in seq_along(chunks)) {
    stamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
    plan <- file.path(plans_dir, sprintf("plan_%s_%03d.xml", stamp, ci))
    write_headless_plan(runs[chunks[[ci]]], model, plan)
    t0 <- Sys.time()
    run_headless(plan, cores, file.path(plans_dir, sprintf("out_%s_%03d", stamp, ci)))
    message(sprintf("chunk %d/%d: %d runs in %.1f min", ci, length(chunks), length(chunks[[ci]]),
                    as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  }
  bad <- runs[!mapply(run_done, out_dir, n_days, key)]
  if (nrow(bad) > 0) stop(nrow(bad), " runs did not finish; first: ", bad$out_dir[1])
  invisible(nrow(runs))
}

# reps = NULL reads every rep_<n> folder under the cell; a vector of replicate numbers reads only those
# (and fails if one is missing), so leftover folders of an earlier, larger campaign are ignored.
collect_runs <- function(cell_id, what, reps = NULL, runs_root = local_paths()$runs_root) {
  cell_dir <- file.path(runs_root, cell_id)
  files <- if (is.null(reps)) {
    list.files(cell_dir, pattern = paste0("^", what, "\\.csv$"), recursive = TRUE, full.names = TRUE)
  } else {
    f <- file.path(cell_dir, paste0("rep_", reps), paste0(what, ".csv"))
    gone <- !file.exists(f)
    if (any(gone)) stop("no ", what, " output for cell ", cell_id, " rep ", paste(reps[gone], collapse = ", "))
    f
  }
  if (length(files) == 0) stop("no ", what, " outputs for cell ", cell_id)
  cols <- switch(what, observed = OBSERVED_COLS, truth = TRUTH_COLS, conservation = CONSERVATION_COLS,
                 decisions = DECISION_COLS, crossings = CROSSING_COLS, timing = TIMING_COLS,
                 floors_realized = FLOORS_REALIZED_COLS, stop("unknown output ", what))
  out <- rbindlist(lapply(files, read_contract, cols = cols))
  if (what == "observed") out[down_count < 0, down_count := NA]
  out[]
}
