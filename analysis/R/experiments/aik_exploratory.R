# EXPLORATORY, not pre-registered (docs/simulation/aik_experiment_plan.md has no such analysis): do the upper-floor and
# lower-floor programs enter log AUFR with equal and opposite weights, as an "adjacent contrast" would imply?
# Usage: D:\vcpf\bin\Rscript.cmd analysis/R/experiments/aik_exploratory.R
suppressPackageStartupMessages({library(data.table); library(sandwich)})
d <- fread(file.path("analysis", "outputs", "sim", "aik", "aik_boundary_rep.csv"))[exp == "e1" & gamma > 0 & is.finite(AUFR) & AUFR > 0]
d[, `:=`(logAUFR = log(AUFR), xu10 = 10 * x_upper, xl10 = 10 * x_lower)]
res <- rbindlist(lapply(unique(d$cell_id), function(cid) {
  x <- d[cell_id == cid]
  f <- lm(logAUFR ~ factor(boundary_order) + xu10 + xl10, x)
  V <- vcovCL(f, cluster = x$rep_id, type = "HC1")
  tq <- qt(0.975, uniqueN(x$rep_id) - 1L)
  b <- coef(f)[c("xu10", "xl10")]; se <- sqrt(diag(V)[c("xu10", "xl10")])
  data.table(cell_id = cid, gamma = x$gamma[1], circ = x$circ[1], term = c("upper floor", "lower floor"),
             log_coef = unname(b), lo = unname(b - tq * se), hi = unname(b + tq * se), rate_ratio = exp(unname(b)))
}))
fwrite(res, file.path("analysis", "outputs", "sim", "aik", "aik_exploratory_upper_lower.csv"))
options(width = 160, digits = 4); print(res)
