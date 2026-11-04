"""Check the numbers in paper/final_paper_text.txt against analysis/outputs/aik/*.csv.

Standard library only (R is not needed). Run from the repository root:

    python3 analysis/python/audit_paper_numbers.py

Each check rounds the CSV value to the precision the paper prints and compares.
Exit code is 1 if any check fails, so the script can be used as a guard.
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "outputs" / "aik"


def rows(name):
    with open(OUT / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pick(table, **kw):
    hit = [r for r in table if all(str(r[k]) == str(v) for k, v in kw.items())]
    if len(hit) != 1:
        raise LookupError(f"{kw}: {len(hit)} rows")
    return hit[0]


a1 = rows("aik_a1_profile.csv")
shape = rows("aik_a1_shape.csv")
theta = rows("aik_a2_theta.csv")
a2b = rows("aik_a2b_constructs.csv")
explo = rows("aik_exploratory_upper_lower.csv")
a3 = rows("aik_a3_moderation.csv")
reach = rows("aik_a4_reach.csv")
contr = rows("aik_a4_contrasts.csv")
e2p = rows("aik_e2_profile.csv")
doota = rows("aik_doota_reference.csv")
cells = rows("aik_cells.csv")

# First-boundary mean U per E1 cell, from the replicate-level file.
first_U = defaultdict(list)
for r in rows("aik_boundary_rep.csv"):
    if r["exp"] == "e1" and r["boundary_order"] == "1":
        first_U[(int(r["gamma"]), r["circ"])].append(float(r["U"]))
first_U = {k: sum(v) / len(v) for k, v in first_U.items()}


def a1v(circ, b, col):
    return float(pick(a1, circ=circ, boundary_order=b)[col])


def dev(g, circ, pred):
    return float(pick(a2b, gamma=g, circ=circ, predictor=pred)["dev_explained"])


def a3v(g, col):
    return float(pick(a3, gamma=g)[col])


def rch(pattern, circ, col, g=4):
    return float(pick(reach, pattern=pattern, circ=circ, gamma=g)[col])


def ct(name, circ, outcome, col="diff"):
    return float(pick(contr, contrast=name, circ=circ, outcome=outcome)[col])


def e2u(pattern, circ, b=8, g=4):
    return float(pick(e2p, pattern=pattern, circ=circ, gamma=g, boundary_order=b)["U_mean"])


def level_drop(g):
    return 1 - first_U[(g, "frag")] / first_U[(g, "cont")]


PRED = {"d": "adjacent contrast (Delta)", "u": "upper-floor program", "m": "mean program above boundary"}


def dev_range(key):
    v = [dev(g, c, PRED[key]) for g in (2, 4, 8) for c in ("cont", "frag")]
    return min(v), max(v)


n_e1 = sum(int(c["n"]) for c in cells if c["exp"] == "e1")
n_e2_g4 = sum(int(c["n"]) for c in cells if c["exp"] == "e2" and c["gamma"] == "4")
n_e2_all = sum(int(c["n"]) for c in cells if c["exp"] == "e2")
doota_runs = int(doota[0]["n_points"]) * int(doota[0]["n_rep_min"])

# (paper line, label, paper value, computed value, decimals the paper prints)
CHECKS = [
    # 3.2 design
    (54, "E1 runs", 1600, n_e1, 0),
    (63, "E2 runs at gamma=4 (8 cells)", 800, n_e2_g4, 0),
    # '3,600회' is not the gamma=0 runs in this repo (600). It matches the Doota
    # calibration grid (18 points x 200 reps); those runs are not in the repo.
    (45, "Doota grid n_points*n_rep ('3,600회')", 3600, doota_runs, 0),
    # 4.1 RQ1
    (79, "cont U_1", 12346, a1v("cont", 1, "U_mean"), 0),
    (79, "cont U_8", 448, a1v("cont", 8, "U_mean"), 0),
    (79, "cont RUI_8", 0.036, a1v("cont", 8, "RUI_mean"), 3),
    (79, "frag U_1", 9802, a1v("frag", 1, "U_mean"), 0),
    (79, "frag first-boundary drop %", 20.6, 100 * level_drop(0), 1),
    (79, "frag RUI_8", 0.042, a1v("frag", 8, "RUI_mean"), 3),
    (79, "frag U_8", 408, a1v("frag", 8, "U_mean"), 0),
    (84, "cont AUFR b2-7 min", 0.60, min(a1v("cont", b, "AUFR_mean") for b in range(2, 8)), 2),
    (84, "cont AUFR b2-7 max", 0.67, max(a1v("cont", b, "AUFR_mean") for b in range(2, 8)), 2),
    (84, "frag AUFR b2-7 min", 0.58, min(a1v("frag", b, "AUFR_mean") for b in range(2, 8)), 2),
    (84, "frag AUFR b2-7 max", 0.71, max(a1v("frag", b, "AUFR_mean") for b in range(2, 8)), 2),
    (84, "cont AUFR b8", 0.52, a1v("cont", 8, "AUFR_mean"), 2),
    (84, "frag AUFR b8", 0.51, a1v("frag", 8, "AUFR_mean"), 2),
    (84, "cont max log deviation", 0.131, float(pick(shape, circ="cont")["max_dev_log"]), 3),
    (84, "frag max log deviation", 0.152, float(pick(shape, circ="frag")["max_dev_log"]), 3),
    (84, "cont F", 1302, float(pick(shape, circ="cont")["F"]), 0),
    (84, "frag F", 1977, float(pick(shape, circ="frag")["F"]), 0),
    (85, "Doota AUFR 2F-3F", 0.51, float(pick(doota, b="2F-3F")["AUFR_mean"]), 2),
    (85, "Doota AUFR 3F-4F", 0.51, float(pick(doota, b="3F-4F")["AUFR_mean"]), 2),
    (85, "Doota AUFR 4F-5F", 0.43, float(pick(doota, b="4F-5F")["AUFR_mean"]), 2),
    # 4.2 RQ2
    (91, "cont rate ratio per 0.1 Delta, g2", 1.060, float(pick(theta, gamma=2, circ="cont")["rate_ratio"]), 3),
    (91, "cont rate ratio per 0.1 Delta, g4", 1.109, float(pick(theta, gamma=4, circ="cont")["rate_ratio"]), 3),
    (91, "cont rate ratio per 0.1 Delta, g8", 1.184, float(pick(theta, gamma=8, circ="cont")["rate_ratio"]), 3),
    (91, "frag % per 0.1 Delta, g2", 5.6, 100 * (float(pick(theta, gamma=2, circ="frag")["rate_ratio"]) - 1), 1),
    (91, "frag % per 0.1 Delta, g4", 10.9, 100 * (float(pick(theta, gamma=4, circ="frag")["rate_ratio"]) - 1), 1),
    (91, "frag % per 0.1 Delta, g8", 17.4, 100 * (float(pick(theta, gamma=8, circ="frag")["rate_ratio"]) - 1), 1),
    (95, "dev explained Delta min %", 4, 100 * dev_range("d")[0], 0),
    (95, "dev explained Delta max %", 22, 100 * dev_range("d")[1], 0),
    (96, "dev explained M_b min %", 29, 100 * dev_range("m")[0], 0),
    (96, "dev explained M_b max %", 57, 100 * dev_range("m")[1], 0),
    (97, "dev explained x_upper min %", 46, 100 * dev_range("u")[0], 0),
    (97, "dev explained x_upper max %", 71, 100 * dev_range("u")[1], 0),
    (98, "upper-floor log coef (g4 cont)", 0.130, float(pick(explo, gamma=4, circ="cont", term="upper floor")["log_coef"]), 3),
    (98, "lower-floor log coef (g4 cont)", -0.077, float(pick(explo, gamma=4, circ="cont", term="lower floor")["log_coef"]), 3),
    # 4.3 RQ3
    (105, "first-boundary drop % g2", 18.5, 100 * level_drop(2), 1),
    (105, "first-boundary drop % g4", 14.8, 100 * level_drop(4), 1),
    (105, "first-boundary drop % g8", 9.2, 100 * level_drop(8), 1),
    (106, "log diff g2", -0.0042, a3v(2, "log_diff"), 4),
    (106, "log diff g4", -0.0007, a3v(4, "log_diff"), 4),
    (106, "log diff g8", -0.0085, a3v(8, "log_diff"), 4),
    (107, "erosion % g2", 6.7, 100 * a3v(2, "erosion"), 1),
    (107, "erosion lo % g2", 2.7, 100 * a3v(2, "erosion_lo"), 1),
    (107, "erosion hi % g2", 10.5, 100 * a3v(2, "erosion_hi"), 1),
    (107, "erosion % g4", 0.8, 100 * a3v(4, "erosion"), 1),
    (107, "erosion lo % g4", -4.1, 100 * a3v(4, "erosion_lo"), 1),
    (107, "erosion hi % g4", 5.2, 100 * a3v(4, "erosion_hi"), 1),
    (107, "erosion % g8", 1.7, 100 * a3v(8, "erosion"), 1),
    (107, "erosion lo % g8", -6.4, 100 * a3v(8, "erosion_lo"), 1),
    (107, "erosion hi % g8", 8.6, 100 * a3v(8, "erosion_hi"), 1),
    (107, "bootstrap B", 2000, a3v(2, "B"), 0),
    # 4.4 RQ4
    (112, "T TOP1 cont", 0.587, rch("TOP1", "cont", "T_mean"), 3),
    (112, "T STEP3 cont", 0.140, rch("STEP3", "cont", "T_mean"), 3),
    (112, "T UNIFORM cont", 0.059, rch("UNIFORM", "cont", "T_mean"), 3),
    (112, "T LOW3 cont", 0.015, rch("LOW3", "cont", "T_mean"), 3),
    (112, "R TOP1 cont", 0.554, rch("TOP1", "cont", "R_mean"), 3),
    (112, "R STEP3 cont", 0.409, rch("STEP3", "cont", "R_mean"), 3),
    (112, "R UNIFORM cont", 0.311, rch("UNIFORM", "cont", "R_mean"), 3),
    (112, "R LOW3 cont", 0.284, rch("LOW3", "cont", "R_mean"), 3),
    (114, "U_8 TOP1 cont", 9112, e2u("TOP1", "cont"), 0),
    (115, "U_8 STEP3 cont", 2197, e2u("STEP3", "cont"), 0),
    (116, "U_8 UNIFORM cont", 975, e2u("UNIFORM", "cont"), 0),
    (117, "U_8 LOW3 cont", 286, e2u("LOW3", "cont"), 0),
    (117, "TOP1 / LOW3 ratio ('32배')", 32, e2u("TOP1", "cont") / e2u("LOW3", "cont"), 0),
    (118, "TOP1 - STEP3, T", 0.447, -ct("STEP3-TOP1", "cont", "T"), 3),
    (118, "TOP1 - STEP3, T, CI lo", 0.445, -ct("STEP3-TOP1", "cont", "T", "hi"), 3),
    (118, "TOP1 - STEP3, T, CI hi", 0.449, -ct("STEP3-TOP1", "cont", "T", "lo"), 3),
    (118, "TOP1 - STEP3, R", 0.146, -ct("STEP3-TOP1", "cont", "R"), 3),
    (118, "TOP1 - STEP3, R, CI lo", 0.144, -ct("STEP3-TOP1", "cont", "R", "hi"), 3),
    (118, "TOP1 - STEP3, R, CI hi", 0.147, -ct("STEP3-TOP1", "cont", "R", "lo"), 3),
    (118, "STEP3 - UNIFORM, T", 0.082, ct("STEP3-UNIFORM", "cont", "T"), 3),
    (118, "STEP3 - UNIFORM, R", 0.097, ct("STEP3-UNIFORM", "cont", "R"), 3),
]

# Holm-adjusted p of every primary contrast must be < 0.001 (line 118).
holm_ok = all(float(r["p_holm"]) < 0.001 for r in contr if r["primary"] == "TRUE")
# Rank order TOP1 > STEP3 > UNIFORM > LOW3 holds in frag for T and R (line 112).
order = ["TOP1", "STEP3", "UNIFORM", "LOW3"]
frag_rank_ok = all(
    [rch(p, "frag", col) for p in order] == sorted([rch(p, "frag", col) for p in order], reverse=True)
    for col in ("T_mean", "R_mean")
)


def rounded(x, d):
    # Round half away from zero, as a reader would.
    q = 10 ** d
    return math.copysign(math.floor(abs(x) * q + 0.5) / q, x)


def main():
    fails = 0
    print(f"{'line':>4}  {'check':<42} {'paper':>10} {'csv':>14}  result")
    for line, label, paper, value, d in CHECKS:
        ok = rounded(value, d) == paper
        fails += not ok
        print(f"{line:>4}  {label:<42} {paper:>10} {value:>14.6g}  {'OK' if ok else 'MISMATCH'}")
    for line, label, ok in [(118, "primary contrasts Holm p < 0.001", holm_ok),
                            (112, "frag rank order unchanged (T, R)", frag_rank_ok)]:
        fails += not ok
        print(f"{line:>4}  {label:<42} {'':>10} {'':>14}  {'OK' if ok else 'MISMATCH'}")
    print(f"\nE2 runs incl. gamma=0 null cells: {n_e2_all}; all runs: {n_e1 + n_e2_all}")
    print(f"{fails} mismatch(es) of {len(CHECKS) + 2} checks")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
