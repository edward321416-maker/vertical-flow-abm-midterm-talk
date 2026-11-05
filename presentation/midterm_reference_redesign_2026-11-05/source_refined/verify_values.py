#!/usr/bin/env python3
"""Recompute every number shown in the refined deck from the tracked analysis outputs.

Read-only inputs (repository root):
  analysis/outputs/aik/aik_boundary_rep.csv   one row per (cell, repetition, boundary), 20,800 rows
  analysis/outputs/aik/aik_*.csv               summary tables written by analysis/R/experiments/aik_analysis.R
  analysis/R/experiments/aik_program_circulation.R   PATTERN_X (E2 anchor proportions)

Independent re-estimation (numpy only, mirrors aik_analysis.R):
  A1  profile means, per-repetition AUFR quantiles, U8/U1
  A2  log AUFR ~ factor(boundary) + delta10, cluster-robust (HC1, by repetition) 95% CI, t(199)
  A2b quasi-Poisson U ~ factor(boundary) + factor(rep) [+ predictor]: residual-deviance reduction
  A3  additive AUFR slope ratio frag/cont and erosion; repetition-cluster bootstrap CI (check only)
  A4  per-repetition T = U8/U1 means and U8 means for the four placements

Outputs (task folder):
  source_refined/verified_values.json   the only numeric source read by build_deck.mjs
  qa/value_checks.csv                   displayed value vs CSV value vs independent recomputation
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

TASK = Path(__file__).resolve().parent.parent
REPO = TASK.parent.parent
AIK = REPO / "analysis" / "outputs" / "aik"
RCODE = REPO / "analysis" / "R" / "experiments" / "aik_program_circulation.R"
OUT_JSON = TASK / "source_refined" / "verified_values.json"
OUT_CSV = TASK / "qa" / "value_checks.csv"

rng = np.random.default_rng(20261104)
checks: list[dict] = []


def check(cid: str, pages: str, description: str, displayed: str, csv_value, recomputed, tol: float, source: str):
    ok = True
    if csv_value is not None and recomputed is not None:
        ok = abs(float(csv_value) - float(recomputed)) <= tol
    checks.append({
        "check_id": cid, "pages": pages, "description": description, "displayed_value": displayed,
        "csv_value": "" if csv_value is None else f"{float(csv_value):.6g}",
        "independent_recomputation": "" if recomputed is None else f"{float(recomputed):.6g}",
        "tolerance": tol, "source": source, "status": "PASS" if ok else "FAIL",
    })
    return ok


def fmt_display_ok(cid: str, pages: str, description: str, displayed: str, value: float, decimals: int, scale: float = 1.0,
                   source: str = ""):
    """Confirm that the rounded displayed string equals the verified value rounded the same way."""
    s = f"{value * scale:,.{decimals}f}"
    ok = displayed.replace("+", "").replace("%", "").replace("명", "").replace("회", "").strip() == s
    checks.append({
        "check_id": cid + "_display", "pages": pages, "description": description + " (display rounding)",
        "displayed_value": displayed, "csv_value": s, "independent_recomputation": "", "tolerance": 0,
        "source": source, "status": "PASS" if ok else "FAIL",
    })
    return ok


# ---------------------------------------------------------------------------------------------- load
d = pd.read_csv(AIK / "aik_boundary_rep.csv")
a1p = pd.read_csv(AIK / "aik_a1_profile.csv")
a1s = pd.read_csv(AIK / "aik_a1_shape.csv")
a2 = pd.read_csv(AIK / "aik_a2_theta.csv")
a2b = pd.read_csv(AIK / "aik_a2b_constructs.csv")
a3 = pd.read_csv(AIK / "aik_a3_moderation.csv")
a4 = pd.read_csv(AIK / "aik_a4_reach.csv")
a4c = pd.read_csv(AIK / "aik_a4_contrasts.csv")
e2p = pd.read_csv(AIK / "aik_e2_profile.csv")
chk = pd.read_csv(AIK / "aik_checks.csv")
cells = pd.read_csv(AIK / "aik_cells.csv")

# ---------------------------------------------------------------------------------------------- run counts
runs = d.groupby(["exp", "cell_id"]).rep_id.nunique().reset_index()
e1_runs = int(runs[runs.exp == "e1"].rep_id.sum())
e2_runs = int(runs[runs.exp == "e2"].rep_id.sum())
check("runs_e1", "9", "E1 runs (8 cells x 200)", "1,600", int(chk[chk.cell_id.str.contains("_e1_")].n_rep.sum()), e1_runs, 0, "aik_checks.csv n_rep; aik_boundary_rep.csv")
check("runs_e2", "9", "E2 runs (8 cells x 100 + 2 gamma=0 controls x 100)", "1,000", int(chk[chk.cell_id.str.contains("_e2_")].n_rep.sum()), e2_runs, 0, "aik_checks.csv; aik_boundary_rep.csv")
check("runs_total", "9", "Total runs", "2,600", 2600, e1_runs + e2_runs, 0, "sum")
check("rows_total", "9", "Boundary rows = runs x 8", "20,800", 20800, len(d), 0, "aik_boundary_rep.csv")
check("missing_boundaries", "9", "Missing repetition-boundaries", "0", int(chk.n_missing_rep_boundary.sum()), 0, 0, "aik_checks.csv")
check("zero_U", "9", "Boundaries with U = 0", "0", int(chk.n_zero_U.sum()), int((d.U == 0).sum()), 0, "aik_checks.csv; boundary_rep")
check("n_days", "10", "Simulated days per repetition", "4", int(cells.n_days.unique()[0]), 4, 0, "aik_cells.csv n_days")
e1_grid = runs[runs.exp == "e1"].set_index("cell_id").rep_id.to_dict()
e2_grid = runs[runs.exp == "e2"].set_index("cell_id").rep_id.to_dict()

# ---------------------------------------------------------------------------------------------- A1 profile
g0 = d[(d.exp == "e1") & (d.gamma == 0)]
prof = {}
for circ in ("cont", "frag"):
    x = g0[g0.circ == circ]
    rows = []
    for b in range(1, 9):
        xb = x[x.boundary_order == b]
        au = xb.AUFR.dropna()
        rows.append({
            "b": b, "U_mean": xb.U.mean(),
            "AUFR_mean": None if au.empty else au.mean(),
            "AUFR_q025": None if au.empty else float(np.quantile(au, 0.025)),
            "AUFR_q975": None if au.empty else float(np.quantile(au, 0.975)),
            "RUI_mean": xb.RUI.mean(),
            "U_q025": float(np.quantile(xb.U, 0.025)), "U_q975": float(np.quantile(xb.U, 0.975)),
        })
    prof[circ] = rows
    ref = a1p[a1p.circ == circ].sort_values("boundary_order")
    for r, (_, rr) in zip(rows, ref.iterrows()):
        check(f"a1_U_{circ}_b{r['b']}", "10", f"gamma=0 {circ} mean U boundary {r['b']}", "", rr.U_mean, r["U_mean"], 1e-6, "aik_a1_profile.csv U_mean")
        if r["AUFR_mean"] is not None:
            check(f"a1_AUFR_{circ}_b{r['b']}", "11", f"gamma=0 {circ} mean AUFR boundary {r['b']}", "", rr.AUFR_mean, r["AUFR_mean"], 1e-9, "aik_a1_profile.csv AUFR_mean")
            check(f"a1_AUFRq_{circ}_b{r['b']}", "11", f"gamma=0 {circ} AUFR 2.5-97.5% band boundary {r['b']}", "", rr.AUFR_q025 + rr.AUFR_q975, r["AUFR_q025"] + r["AUFR_q975"], 1e-9, "aik_a1_profile.csv quantiles (R type 7 = numpy linear)")

c = prof["cont"]
u1, u8 = c[0]["U_mean"], c[7]["U_mean"]
ratio_of_means = u8 / u1
mean_rep_ratio = c[7]["RUI_mean"]
frag_gap = prof["frag"][0]["U_mean"] / u1 - 1
check("u1_cont", "10,18", "Continuous U1 (gamma=0)", "12,346", 12346.405, u1, 1e-6, "aik_a1_profile.csv")
fmt_display_ok("u1_cont", "10", "Continuous U1", "12,346", u1, 0)
check("u8_cont", "10,18", "Continuous U8 (gamma=0)", "448", 447.76, u8, 1e-6, "aik_a1_profile.csv")
fmt_display_ok("u8_cont", "10", "Continuous U8", "448", u8, 0)
check("u8u1_cont", "10,11,18", "U8/U1 continuous: mean of per-repetition ratios (RUI_8)", "3.6%", 0.0363039287507832, mean_rep_ratio, 1e-12, "aik_a1_profile.csv RUI_mean b=8")
fmt_display_ok("u8u1_cont", "10", "U8/U1 per-repetition mean", "3.6%", mean_rep_ratio, 1, 100)
fmt_display_ok("u8u1_ratio_of_means", "10", "U8/U1 ratio of means (same rounding)", "3.6%", ratio_of_means, 1, 100)
check("last_local_aufr", "11,18", "Last local AUFR U8/U7, continuous gamma=0", "51.7%", 0.516841613659622, c[7]["AUFR_mean"], 1e-12, "aik_a1_profile.csv AUFR_mean b=8")
fmt_display_ok("last_local_aufr", "11", "Last local AUFR", "51.7%", c[7]["AUFR_mean"], 1, 100)
check("frag_gap", "10", "Segmented first-boundary U vs continuous", "−20.6%", -0.20607618169013577, frag_gap, 1e-12, "aik_a1_profile.csv U_mean b=1")
fmt_display_ok("frag_gap", "10", "Segmented first-boundary gap", "-20.6%", frag_gap, 1, 100)
geo_ratio = ratio_of_means ** (1 / 7)
check("geo_ratio", "11", "Constant-ratio reference (U8/U1)^(1/7)", "≈ 62%", None, geo_ratio, 0, "derived from aik_a1_profile.csv")
aufr4 = c[3]["AUFR_mean"]
check("aufr4_cont", "8", "Worked example AUFR4 = mean per-rep U4/U3, continuous gamma=0", "0.659", 0.65931678773585, aufr4, 1e-12, "aik_a1_profile.csv AUFR_mean b=4")
fmt_display_ok("aufr4_cont", "8", "AUFR4 worked example", "0.659", aufr4, 3)
shape = {r.circ: {"max_dev_log": r.max_dev_log, "F": r.F, "p": r.p} for r in a1s.itertuples()}

# re-run the A1 shape test (log U ~ rep FE + b  vs  log U ~ rep FE + factor(b))
def lm_rss(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    return float(r @ r), X.shape[1]

for circ in ("cont", "frag"):
    x = g0[(g0.circ == circ) & (g0.U > 0)].copy()
    reps = pd.get_dummies(x.rep_id.astype(int), drop_first=True).to_numpy(float)
    bf = pd.get_dummies(x.boundary_order.astype(int), drop_first=True).to_numpy(float)
    one = np.ones((len(x), 1))
    y = np.log(x.U.to_numpy(float))
    rss1, k1 = lm_rss(np.hstack([one, reps, x[["boundary_order"]].to_numpy(float)]), y)
    rss2, k2 = lm_rss(np.hstack([one, reps, bf]), y)
    n = len(y)
    F = ((rss1 - rss2) / (k2 - k1)) / (rss2 / (n - k2))
    check(f"a1_shape_F_{circ}", "11", f"Log-linear vs boundary-factor F ({circ})", "1,302" if circ == "cont" else "1,977", shape[circ]["F"], F, 1e-3, "aik_a1_shape.csv F")

# ---------------------------------------------------------------------------------------------- A2 AUFR multipliers
e1 = d[d.exp == "e1"].copy()
e1["delta10"] = 10 * e1.delta


def cluster_ols(x: pd.DataFrame, yvar: str):
    x = x.sort_values(["rep_id", "boundary_order"])
    bf = pd.get_dummies(x.boundary_order.astype(int), drop_first=True).to_numpy(float)
    X = np.hstack([np.ones((len(x), 1)), bf, x[["delta10"]].to_numpy(float)])
    y = x[yvar].to_numpy(float)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    meat = np.zeros((X.shape[1], X.shape[1]))
    groups = x.rep_id.to_numpy()
    for g in np.unique(groups):
        idx = groups == g
        s = X[idx].T @ u[idx]
        meat += np.outer(s, s)
    n, k = X.shape
    G = len(np.unique(groups))
    V = XtX_inv @ meat @ XtX_inv * (G / (G - 1)) * ((n - 1) / (n - k))
    se = float(np.sqrt(V[-1, -1]))
    return float(beta[-1]), se, G


T_975_199 = 1.9719565442  # qt(0.975, 199)
mult = {}
for circ in ("cont", "frag"):
    for g in (0, 2, 4, 8):
        x = e1[(e1.circ == circ) & (e1.gamma == g) & e1.AUFR.notna() & (e1.AUFR > 0)].copy()
        x["logAUFR"] = np.log(x.AUFR)
        est, se, G = cluster_ols(x, "logAUFR")
        lo, hi = est - T_975_199 * se, est + T_975_199 * se
        ref = a2[(a2.circ == circ) & (a2.gamma == g)].iloc[0]
        check(f"a2_rr_{circ}_g{g}", "12", f"AUFR multiplier per +0.1 contrast, {circ} gamma={g}", "", ref.rate_ratio, np.exp(est), 1e-9, "aik_a2_theta.csv rate_ratio")
        check(f"a2_lo_{circ}_g{g}", "12", f"multiplier 95% CI low, {circ} gamma={g}", "", ref.rr_lo, np.exp(lo), 1e-6, "aik_a2_theta.csv rr_lo")
        check(f"a2_hi_{circ}_g{g}", "12", f"multiplier 95% CI high, {circ} gamma={g}", "", ref.rr_hi, np.exp(hi), 1e-6, "aik_a2_theta.csv rr_hi")
        mult[(circ, g)] = {"rr": float(ref.rate_ratio), "lo": float(ref.rr_lo), "hi": float(ref.rr_hi)}
for g, shown in ((2, "+6.0%"), (4, "+10.9%"), (8, "+18.4%")):
    fmt_display_ok(f"a2_pct_g{g}", "12,18", f"AUFR relative change per +0.1 contrast, cont gamma={g}", shown, mult[("cont", g)]["rr"] - 1, 1, 100, "aik_a2_theta.csv")

# ---------------------------------------------------------------------------------------------- A2b deviance reduction
def poisson_deviance(X, y, iters=60):
    mu = y + 0.5
    eta = np.log(mu)
    for _ in range(iters):
        z = eta + (y - mu) / mu
        w = mu
        WX = X * w[:, None]
        beta = np.linalg.solve(X.T @ WX, WX.T @ z)
        eta_new = X @ beta
        if np.max(np.abs(eta_new - eta)) < 1e-11:
            eta = eta_new
            break
        eta = eta_new
        mu = np.exp(eta)
    mu = np.exp(eta)
    return float(2 * np.sum(y * np.log(y / mu) - (y - mu)))


dev = {}
for circ in ("cont", "frag"):
    for g in (2, 4, 8):
        x = e1[(e1.circ == circ) & (e1.gamma == g) & (e1.U > 0)].copy()
        y = x.U.to_numpy(float)
        base = np.hstack([np.ones((len(x), 1)),
                          pd.get_dummies(x.boundary_order.astype(int), drop_first=True).to_numpy(float),
                          pd.get_dummies(x.rep_id.astype(int), drop_first=True).to_numpy(float)])
        d0 = poisson_deviance(base, y)
        for col, name in (("delta", "adjacent contrast (Delta)"), ("x_upper", "upper-floor program"), ("M_above", "mean program above boundary")):
            d1 = poisson_deviance(np.hstack([base, 10 * x[[col]].to_numpy(float)]), y)
            red = (d0 - d1) / d0
            ref = a2b[(a2b.circ == circ) & (a2b.gamma == g) & (a2b.predictor == name)].iloc[0]
            check(f"a2b_{circ}_g{g}_{col}", "13", f"U residual-deviance reduction, {circ} gamma={g}, {col}", "", ref.dev_explained, red, 1e-6, "aik_a2b_constructs.csv dev_explained")
            dev[(circ, g, col)] = float(ref.dev_explained)
for col, shown in (("delta", "10.2%"), ("x_upper", "60.1%"), ("M_above", "39.7%")):
    fmt_display_ok(f"a2b_display_{col}", "13", f"U deviance reduction gamma=4 cont {col}", shown, dev[("cont", 4, col)], 1, 100, "aik_a2b_constructs.csv")

# ---------------------------------------------------------------------------------------------- A3 erosion
def slope_fast(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta[-1]


def design_abs(x):
    x = x.sort_values(["rep_id", "boundary_order"])
    bf = pd.get_dummies(x.boundary_order.astype(int), drop_first=True).to_numpy(float)
    X = np.hstack([np.ones((len(x), 1)), bf, x[["delta10"]].to_numpy(float)])
    return X, x.AUFR.to_numpy(float), x.rep_id.to_numpy()


eros = {}
for g in (2, 4, 8):
    xc = e1[(e1.gamma == g) & (e1.circ == "cont") & e1.AUFR.notna()].copy()
    xf = e1[(e1.gamma == g) & (e1.circ == "frag") & e1.AUFR.notna()].copy()
    Xc, yc, gc = design_abs(xc)
    Xf, yf, gf = design_abs(xf)
    sc, sf = slope_fast(Xc, yc), slope_fast(Xf, yf)
    erosion = 1 - sf / sc
    ref = a3[a3.gamma == g].iloc[0]
    check(f"a3_erosion_g{g}", "14", f"Additive AUFR slope erosion gamma={g}", "", ref.erosion, erosion, 1e-9, "aik_a3_moderation.csv erosion")
    # bootstrap check (B=600, different RNG from R; reported CI comes from the CSV, B=2000)
    ic = [np.where(gc == k)[0] for k in np.unique(gc)]
    jf = [np.where(gf == k)[0] for k in np.unique(gf)]
    ratios = []
    for _ in range(600):
        a = np.concatenate([ic[i] for i in rng.integers(0, len(ic), len(ic))])
        b = np.concatenate([jf[i] for i in rng.integers(0, len(jf), len(jf))])
        ratios.append(slope_fast(Xf[b], yf[b]) / slope_fast(Xc[a], yc[a]))
    q = np.quantile(ratios, [0.025, 0.975])
    boot_lo, boot_hi = 1 - q[1], 1 - q[0]
    check(f"a3_ci_lo_g{g}", "14", f"Erosion 95% CI low gamma={g} (independent bootstrap B=600, tolerance 1.5 pp)", "", ref.erosion_lo, boot_lo, 0.015, "aik_a3_moderation.csv erosion_lo (R B=2000)")
    check(f"a3_ci_hi_g{g}", "14", f"Erosion 95% CI high gamma={g} (independent bootstrap B=600, tolerance 1.5 pp)", "", ref.erosion_hi, boot_hi, 0.015, "aik_a3_moderation.csv erosion_hi (R B=2000)")
    eros[g] = {"est": float(ref.erosion), "lo": float(ref.erosion_lo), "hi": float(ref.erosion_hi),
               "includes_zero": bool(ref.erosion_lo <= 0 <= ref.erosion_hi)}
for g, (shown, slo, shi) in {2: ("6.7%", "2.7", "10.5"), 4: ("0.8%", "-4.1", "5.2"), 8: ("1.7%", "-6.4", "8.6")}.items():
    fmt_display_ok(f"a3_display_g{g}", "14", f"Erosion estimate gamma={g}", shown, eros[g]["est"], 1, 100)
    fmt_display_ok(f"a3_display_lo_g{g}", "14", f"Erosion CI low gamma={g}", slo, eros[g]["lo"], 1, 100)
    fmt_display_ok(f"a3_display_hi_g{g}", "14", f"Erosion CI high gamma={g}", shi, eros[g]["hi"], 1, 100)

# level gap of first-boundary U, segmented vs continuous, by gamma
u1gap = {}
for g in (0, 2, 4, 8):
    m = e1[(e1.gamma == g) & (e1.boundary_order == 1)].groupby("circ").U.mean()
    u1gap[g] = float(m["frag"] / m["cont"] - 1)
for g, shown in ((0, "-20.6"), (2, "-18.5"), (4, "-14.8"), (8, "-9.2")):
    fmt_display_ok(f"u1gap_g{g}", "14", f"Segmented first-boundary U gap gamma={g}", shown, u1gap[g], 1, 100, "aik_boundary_rep.csv")

# ---------------------------------------------------------------------------------------------- A4 placements
e2 = d[d.exp == "e2"]
pattern_txt = RCODE.read_text(encoding="utf-8")
assert "TOP1    = c(0.05, rep(0.107143, 7), 0.85)" in pattern_txt
weights = {
    "TOP1": [0.05] + [0.107143] * 7 + [0.85],
    "STEP3": [0.05, 0.05, 0.45, 0.05, 0.05, 0.45, 0.05, 0.05, 0.45],
    "UNIFORM": [0.05] + [0.20] * 8,
    "LOW3": [0.05, 0.45, 0.45, 0.45, 0.05, 0.05, 0.05, 0.05, 0.05],
}
# confirm the weights against the realised per-boundary inputs in the tidy table
for pat, w in weights.items():
    sub = e2[(e2.pattern == pat) & (e2.gamma == 4) & (e2.circ == "cont")]
    realised = [float(sub[sub.boundary_order == 1].x_lower.iloc[0])] + [float(sub[sub.boundary_order == b].x_upper.iloc[0]) for b in range(1, 9)]
    check(f"weights_{pat}", "15", f"{pat} floor proportions 1F-9F vs realised x_lower/x_upper", "", sum(w), sum(realised), 1e-9, "aik_program_circulation.R PATTERN_X; boundary_rep x_upper")
    s29 = sum(w[1:])
    check(f"budget_{pat}", "15", f"{pat} sum 2F-9F", "1.60", float(chk[chk.cell_id == f"aik_e2_{pat.lower()}_g4_cont"].budget_S01_S08.iloc[0]), s29, 1e-6, "aik_checks.csv budget_S01_S08")
    fmt_display_ok(f"budget_{pat}", "15", f"{pat} sum 2F-9F", "1.60", s29, 2)

place = {}
for pat in ("TOP1", "STEP3", "UNIFORM", "LOW3"):
    sub = e2[(e2.pattern == pat) & (e2.gamma == 4) & (e2.circ == "cont")]
    T = sub[sub.boundary_order == 8].set_index("rep_id").RUI
    u8m = sub[sub.boundary_order == 8].U.mean()
    ref = a4[(a4.pattern == pat) & (a4.gamma == 4) & (a4.circ == "cont")].iloc[0]
    check(f"a4_T_{pat}", "16,18", f"{pat} mean per-repetition T = U8/U1 (gamma=4 cont)", "", ref.T_mean, T.mean(), 1e-12, "aik_a4_reach.csv T_mean")
    refu = e2p[(e2p.pattern == pat) & (e2p.gamma == 4) & (e2p.circ == "cont") & (e2p.boundary_order == 8)].iloc[0]
    check(f"a4_U8_{pat}", "16,18", f"{pat} mean U8 (gamma=4 cont)", "", refu.U_mean, u8m, 1e-6, "aik_e2_profile.csv U_mean b=8")
    traj = []
    for b in range(1, 9):
        sb = sub[sub.boundary_order == b]
        traj.append({"b": b, "RUI_mean": float(sb.RUI.mean()), "U_mean": float(sb.U.mean()),
                     "AUFR_mean": None if b == 1 else float(sb.AUFR.mean())})
        refb = e2p[(e2p.pattern == pat) & (e2p.gamma == 4) & (e2p.circ == "cont") & (e2p.boundary_order == b)].iloc[0]
        check(f"a4_RUI_{pat}_b{b}", "16", f"{pat} mean RUI boundary {b}", "", refb.RUI_mean, sb.RUI.mean(), 1e-12, "aik_e2_profile.csv RUI_mean")
    place[pat] = {"T": float(ref.T_mean), "T_lo": float(ref.T_lo), "T_hi": float(ref.T_hi), "U8": float(refu.U_mean),
                  "U1": float(traj[0]["U_mean"]), "traj": traj, "weights": weights[pat]}
for pat, shown in (("TOP1", "58.7%"), ("STEP3", "14.0%"), ("UNIFORM", "5.9%"), ("LOW3", "1.5%")):
    fmt_display_ok(f"a4_T_{pat}", "16,18", f"{pat} T display", shown, place[pat]["T"], 1, 100)
for pat, shown in (("TOP1", "9,112"), ("STEP3", "2,197"), ("UNIFORM", "975"), ("LOW3", "286")):
    fmt_display_ok(f"a4_U8_{pat}", "16,18", f"{pat} U8 display", shown, place[pat]["U8"], 0)
top_u = {b["b"]: b["U_mean"] for b in place["TOP1"]["traj"]}
for b, shown in ((6, "7,077"), (7, "7,209"), (8, "9,112")):
    fmt_display_ok(f"top1_rebound_b{b}", "16", f"TOP1 mean U boundary {b} (upper rebound)", shown, top_u[b], 0, 1, "aik_e2_profile.csv")
holm = a4c[(a4c.circ == "cont") & (a4c.outcome == "T") & (a4c.primary)]
check("a4_holm", "16", "Primary T contrasts (cont) Holm p < 0.001", "p < 0.001", 1, float((holm.p_holm < 0.001).all()), 0, "aik_a4_contrasts.csv p_holm")

# ---------------------------------------------------------------------------------------------- write
values = {
    "_provenance": "Generated by source_refined/verify_values.py from analysis/outputs/aik/*.csv; do not edit by hand.",
    "runs": {"e1": e1_runs, "e2": e2_runs, "total": e1_runs + e2_runs, "rows": int(len(d)),
             "e1_cells": e1_grid, "e2_cells": e2_grid, "days_per_rep": 4},
    "rq1": {"profile": prof, "u1": u1, "u8": u8, "u8u1_mean_rep": mean_rep_ratio, "u8u1_ratio_of_means": ratio_of_means,
             "last_local_aufr": c[7]["AUFR_mean"], "frag_first_gap": frag_gap, "geo_ratio": geo_ratio,
             "aufr4": aufr4, "shape": shape},
    "rq2": {"multipliers": {f"{k[0]}_g{k[1]}": v for k, v in mult.items()},
             "deviance": {f"{k[0]}_g{k[1]}_{k[2]}": v for k, v in dev.items()}},
    "rq3": {"erosion": {f"g{k}": v for k, v in eros.items()}, "u1_gap": {f"g{k}": v for k, v in u1gap.items()}},
    "rq4": {"placements": place},
}
OUT_JSON.write_text(json.dumps(values, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(checks[0].keys()))
    w.writeheader()
    w.writerows(checks)
fails = [c for c in checks if c["status"] != "PASS"]
print(f"[{'PASS' if not fails else 'FAIL'}] {len(checks)} value checks, {len(fails)} failed -> {OUT_CSV}")
for f in fails:
    print("  FAIL", f)
print(f"wrote {OUT_JSON}")
