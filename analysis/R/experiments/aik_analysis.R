# Analysis of Simulation C (docs/simulation/aik_experiment_plan.md, section 6). Reads the tidy table written by
# aik_program_circulation.R and writes one CSV per analysis next to it. No simulation is run here.
# Usage: D:\vcpf\bin\Rscript.cmd analysis/R/experiments/aik_analysis.R [aik|aik_pilot]
suppressPackageStartupMessages({
  library(data.table)
  library(sandwich)
})
args <- commandArgs(trailingOnly = TRUE)
pass <- if (length(args) >= 1L) args[[1L]] else "aik"
if (!pass %in% c("aik", "aik_pilot")) stop("pass must be aik or aik_pilot")
dir <- file.path("analysis", "outputs", "sim", pass)
set.seed(20261101L)
B_BOOT <- if (pass == "aik") 2000L else 200L
d <- fread(file.path(dir, "aik_boundary_rep.csv"))
d[, delta10 := 10 * delta]
d[, logAUFR := ifelse(is.finite(AUFR) & AUFR > 0, log(AUFR), NA_real_)]
out <- function(x, name) { fwrite(x, file.path(dir, name)); invisible(x) }
cell_key <- function(x) x[, .(cell_id, exp, pattern, gamma, circ)][1L]

# ---- A1: structural profile (gamma = 0 cells of E1) ---------------------------------------------------------------------
a1_cells <- unique(d[exp == "e1" & gamma == 0, cell_id])
a1_profile <- d[cell_id %in% a1_cells, .(
  AUFR_mean = mean(AUFR, na.rm = TRUE), AUFR_q025 = quantile(AUFR, 0.025, na.rm = TRUE), AUFR_q975 = quantile(AUFR, 0.975, na.rm = TRUE),
  RUI_mean = mean(RUI, na.rm = TRUE), RUI_q025 = quantile(RUI, 0.025, na.rm = TRUE), RUI_q975 = quantile(RUI, 0.975, na.rm = TRUE),
  U_mean = mean(U), n = .N), by = .(cell_id, circ, boundary_order)]
a1_shape <- rbindlist(lapply(a1_cells, function(cid) {
  x <- d[cell_id == cid & U > 0][, `:=`(logU = log(U), b = boundary_order)]
  m1 <- lm(logU ~ factor(rep_id) + b, x)
  m2 <- lm(logU ~ factor(rep_id) + factor(b), x)
  a <- anova(m1, m2)
  prof <- x[, .(m = mean(logU)), by = b]
  dev <- max(abs(resid(lm(m ~ b, prof))))
  data.table(cell_id = cid, circ = x$circ[1L], max_dev_log = dev, F = a$F[2L], p = a$`Pr(>F)`[2L],
             stepped = dev > 0.10 & a$`Pr(>F)`[2L] < 0.01)
}))
out(a1_profile, "aik_a1_profile.csv")
out(a1_shape, "aik_a1_shape.csv")

# ---- A2: program contrast -> AUFR, cluster-robust by replicate ---------------------------------------------------------
cr_slope <- function(x, yvar) {
  f <- lm(reformulate(c("factor(boundary_order)", "delta10"), response = yvar), data = x)
  V <- vcovCL(f, cluster = x$rep_id, type = "HC1")
  b <- coef(f)[["delta10"]]
  se <- sqrt(V["delta10", "delta10"])
  tq <- qt(0.975, uniqueN(x$rep_id) - 1L)
  data.table(est = b, se = se, lo = b - tq * se, hi = b + tq * se, n_rows = nrow(x), n_clusters = uniqueN(x$rep_id))
}
e1 <- d[exp == "e1"]
a2 <- rbindlist(lapply(unique(e1$cell_id), function(cid) {
  x <- e1[cell_id == cid & !is.na(logAUFR)]
  k <- cell_key(x)
  th <- cr_slope(x, "logAUFR")
  th[, `:=`(rate_ratio = exp(est), rr_lo = exp(lo), rr_hi = exp(hi), n_dropped = nrow(e1[cell_id == cid & boundary_order >= 2L]) - nrow(x))]
  cbind(k, th)
}))
a2[, null_ok := ifelse(gamma == 0, rr_lo <= 1 & rr_hi >= 1, NA)]
out(a2, "aik_a2_theta.csv")

# ---- A2b: which program construct explains boundary flow ---------------------------------------------------------------
a2b <- rbindlist(lapply(unique(e1[gamma > 0, cell_id]), function(cid) {
  x <- e1[cell_id == cid & U > 0]
  x[, `:=`(p_delta = 10 * delta, p_upper = 10 * x_upper, p_above = 10 * M_above)]
  base <- glm(U ~ factor(boundary_order) + factor(rep_id), family = quasipoisson(), data = x)
  rbindlist(lapply(c(delta = "p_delta", upper_floor = "p_upper", above_mean = "p_above"), function(p) {
    f <- glm(reformulate(c("factor(boundary_order)", "factor(rep_id)", p), response = "U"), family = quasipoisson(), data = x)
    cbind(cell_key(x), data.table(predictor = p, rate_ratio_per_0.1 = exp(coef(f)[[p]]),
                                  dev_explained = (deviance(base) - deviance(f)) / deviance(base)))
  }))
}))
a2b[, predictor := fcase(predictor == "p_delta", "adjacent contrast (Delta)", predictor == "p_upper", "upper-floor program",
                         predictor == "p_above", "mean program above boundary")]
out(a2b, "aik_a2b_constructs.csv")

# ---- A3: circulation moderation, log and additive scale ---------------------------------------------------------------
slope_fast <- function(x, yvar, idx = NULL) {
  X <- model.matrix(~ factor(boundary_order) + delta10, x)
  y <- x[[yvar]]
  if (!is.null(idx)) { X <- X[idx, , drop = FALSE]; y <- y[idx] }
  unname(lm.fit(X, y)$coefficients[ncol(X)])
}
boot_ratio <- function(xc, xf, yvar, B) {
  ic <- split(seq_len(nrow(xc)), xc$rep_id)
  if_ <- split(seq_len(nrow(xf)), xf$rep_id)
  r <- numeric(B)
  for (i in seq_len(B)) {
    sc <- slope_fast(xc, yvar, unlist(ic[sample.int(length(ic), replace = TRUE)], use.names = FALSE))
    sf <- slope_fast(xf, yvar, unlist(if_[sample.int(length(if_), replace = TRUE)], use.names = FALSE))
    r[i] <- sf / sc
  }
  quantile(r, c(0.025, 0.975), na.rm = TRUE)
}
a3 <- rbindlist(lapply(sort(unique(e1[gamma > 0, gamma])), function(g) {
  xc <- e1[gamma == g & circ == "cont" & !is.na(logAUFR)]
  xf <- e1[gamma == g & circ == "frag" & !is.na(logAUFR)]
  tc <- cr_slope(xc, "logAUFR")
  tf <- cr_slope(xf, "logAUFR")
  diff_log <- tf$est - tc$est
  se_diff <- sqrt(tf$se^2 + tc$se^2)
  ac <- cr_slope(xc, "AUFR")
  af <- cr_slope(xf, "AUFR")
  ratio <- af$est / ac$est
  ci <- boot_ratio(xc, xf, "AUFR", B_BOOT)
  data.table(gamma = g,
             log_theta_cont = tc$est, log_theta_frag = tf$est, log_diff = diff_log, log_diff_lo = diff_log - 1.96 * se_diff,
             log_diff_hi = diff_log + 1.96 * se_diff,
             abs_slope_cont = ac$est, abs_slope_frag = af$est, abs_ratio_frag_over_cont = ratio, abs_ratio_lo = ci[[1]],
             abs_ratio_hi = ci[[2]], erosion = 1 - ratio, erosion_lo = 1 - ci[[2]], erosion_hi = 1 - ci[[1]], B = B_BOOT)
}))
out(a3, "aik_a3_moderation.csv")

# ---- A4: arrangement and reach (E2) -----------------------------------------------------------------------------------
e2 <- d[exp == "e2"]
a4_reach <- data.table()
if (nrow(e2) > 0L) {
rep_reach <- e2[, .(T = RUI[boundary_order == max(boundary_order)], R = mean(RUI[boundary_order >= 2L], na.rm = TRUE)),
                by = .(cell_id, pattern, gamma, circ, rep_id)]
a4_reach <- rep_reach[, {
  tq <- qt(0.975, .N - 1L)
  .(n = .N, T_mean = mean(T), T_lo = mean(T) - tq * sd(T) / sqrt(.N), T_hi = mean(T) + tq * sd(T) / sqrt(.N),
    R_mean = mean(R), R_lo = mean(R) - tq * sd(R) / sqrt(.N), R_hi = mean(R) + tq * sd(R) / sqrt(.N))
}, by = .(cell_id, pattern, gamma, circ)]
out(a4_reach, "aik_a4_reach.csv")
out(e2[, .(AUFR_mean = mean(AUFR, na.rm = TRUE), RUI_mean = mean(RUI, na.rm = TRUE), U_mean = mean(U)),
       by = .(cell_id, pattern, gamma, circ, boundary_order)], "aik_e2_profile.csv")
welch <- function(a, b) { t <- t.test(a, b); c(diff = unname(t$estimate[1] - t$estimate[2]), lo = t$conf.int[1], hi = t$conf.int[2], p = t$p.value) }
PAIRS <- list(c("STEP3", "TOP1"), c("STEP3", "UNIFORM"), c("STEP3", "LOW3"), c("TOP1", "UNIFORM"), c("TOP1", "LOW3"), c("UNIFORM", "LOW3"))
PRIMARY <- c("STEP3-TOP1", "STEP3-UNIFORM")
a4_contrasts <- rbindlist(lapply(c("cont", "frag"), function(cc) {
  rbindlist(lapply(c("T", "R"), function(oc) {
    sub <- rep_reach[gamma == 4 & circ == cc]
    if (nrow(sub) == 0L) return(NULL)
    r <- rbindlist(lapply(PAIRS, function(pr) {
      a <- sub[pattern == pr[1L], get(oc)]; b <- sub[pattern == pr[2L], get(oc)]
      if (length(a) < 2L || length(b) < 2L) return(NULL)
      w <- welch(a, b)
      data.table(contrast = paste(pr, collapse = "-"), diff = w[["diff"]], lo = w[["lo"]], hi = w[["hi"]], p = w[["p"]])
    }))
    r[, `:=`(circ = cc, outcome = oc, primary = contrast %in% PRIMARY)]
    r[primary == TRUE, p_holm := p.adjust(p, "holm")]
    r
  }))
}))
null_sub <- rep_reach[gamma == 0 & circ == "cont"]
a4_null <- rbindlist(lapply(c("T", "R"), function(oc) {
  a <- null_sub[pattern == "UNIFORM", get(oc)]; b <- null_sub[pattern == "TOP1", get(oc)]
  if (length(a) < 2L || length(b) < 2L) return(NULL)
  w <- welch(a, b)
  data.table(outcome = oc, contrast = "UNIFORM-TOP1 at gamma=0", diff = w[["diff"]], lo = w[["lo"]], hi = w[["hi"]], p = w[["p"]],
             ci_includes_0 = w[["lo"]] <= 0 & w[["hi"]] >= 0)
}))
out(a4_contrasts, "aik_a4_contrasts.csv")
out(a4_null, "aik_a4_null_check.csv")
}

# ---- reference: audited Doota runs (audit1, gamma = 0), no new simulation -----------------------------------------------
root <- tryCatch(Sys.getenv("VCPF_ROOT", "."), error = function(e) ".")
runs_root <- tryCatch(fread(file.path(root, "simulation", "local_paths.csv"))[key == "runs_root", value], error = function(e) NA_character_)
if (!is.na(runs_root) && length(Sys.glob(file.path(runs_root, "audit1_a12_*"))) > 0L) {
  ORDER <- c("B2-B1", "B1-1F", "1F-2F", "2F-3F", "3F-4F", "4F-5F")
  cells <- basename(Sys.glob(file.path(runs_root, "audit1_a12_*")))
  ref <- rbindlist(lapply(cells, function(cid) {
    fs <- Sys.glob(file.path(runs_root, cid, "rep_*", "truth.csv"))
    rbindlist(lapply(fs, function(f) {
      t <- fread(f)[direction == "up", .(U = sum(persons)), by = boundary_id]
      u <- setNames(t$U, t$boundary_id)[ORDER]
      data.table(cell_id = cid, rep = as.integer(sub(".*rep_([0-9]+).*", "\\1", f)),
                 b = ORDER[4:6], AUFR = u[4:6] / u[3:5], RUI = u[4:6] / u[3])
    }))
  }))
  ref_cell <- ref[, .(AUFR = mean(AUFR, na.rm = TRUE), RUI = mean(RUI, na.rm = TRUE), n_rep = .N), by = .(cell_id, b)]
  out(ref_cell[, .(AUFR_min = min(AUFR), AUFR_mean = mean(AUFR), AUFR_max = max(AUFR), RUI_min = min(RUI), RUI_mean = mean(RUI),
                   RUI_max = max(RUI), n_points = .N, n_rep_min = min(n_rep)), by = b][match(ORDER[4:6], b)], "aik_doota_reference.csv")
}

# ---- console summary ---------------------------------------------------------------------------------------------------
options(width = 200, digits = 4)
cat("\n== A1 shape (gamma = 0)\n"); print(a1_shape)
cat("\n== A2 theta: AUFR rate ratio per +0.1 contrast\n"); print(a2[, .(cell_id, gamma, circ, rate_ratio, rr_lo, rr_hi, null_ok)])
cat("\n== A2b constructs\n"); print(a2b[, .(cell_id, predictor, rate_ratio_per_0.1, dev_explained)])
cat("\n== A3 moderation\n"); print(a3)
if (nrow(a4_reach) > 0L) { cat("\n== A4 reach\n"); print(a4_reach); cat("\n== A4 contrasts\n"); print(a4_contrasts); print(a4_null) }
cat("\nwrote CSVs to ", normalizePath(dir, winslash = "\\"), "\n")
