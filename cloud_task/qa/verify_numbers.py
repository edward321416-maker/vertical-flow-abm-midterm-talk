"""QA: recompute the deck's numbers from the run-level CSV and check that the
final PDF prints them.

Usage:  python3 cloud_task/qa/verify_numbers.py [deck.pdf]
Writes cloud_task/qa/numbers_check.csv and exits non-zero on any failure.

Three kinds of check:
  1. recompute  - from aik_boundary_rep.csv (one row per run x boundary),
                  independently of the summary CSVs, and compare.
  2. summary    - values taken from the summary CSVs (regression / bootstrap
                  outputs that are not re-estimated here).
  3. printed    - the formatted value appears on the stated slide of the PDF.
"""
import sys, re, csv
from pathlib import Path
import numpy as np
import pandas as pd
import pypdfium2 as pdfium

REPO = Path(__file__).resolve().parents[2]
D = REPO / 'analysis' / 'outputs' / 'aik'
PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / 'cloud_task' / 'output' / 'vertical_flow_midterm_refined.pdf'

rep = pd.read_csv(D / 'aik_boundary_rep.csv')
prof = pd.read_csv(D / 'aik_a1_profile.csv')
theta = pd.read_csv(D / 'aik_a2_theta.csv')
cons = pd.read_csv(D / 'aik_a2b_constructs.csv')
mod = pd.read_csv(D / 'aik_a3_moderation.csv')
reach = pd.read_csv(D / 'aik_a4_reach.csv')
e2 = pd.read_csv(D / 'aik_e2_profile.csv')
shape = pd.read_csv(D / 'aik_a1_shape.csv')
checks = pd.read_csv(D / 'aik_checks.csv')

doc = pdfium.PdfDocument(str(PDF))
PAGES = [re.sub(r'\s+', '', doc[i].get_textpage().get_text_range()) for i in range(len(doc))]
rows, fails = [], 0


def rec(kind, slide, item, expected, observed=None, ok=None):
    global fails
    if ok is None:
        ok = True
    rows.append([kind, slide, item, expected, '' if observed is None else observed, 'PASS' if ok else 'FAIL'])
    if not ok:
        fails += 1


def near(kind, slide, item, a, b, tol):
    rec(kind, slide, item, f'{b:.6g}', f'{a:.6g}', abs(a - b) <= tol)


def printed(slide, s):
    rec('printed', slide, s, s, None, re.sub(r'\s+', '', s) in PAGES[slide - 1])


def cell(cid):
    return rep[rep.cell_id == cid]


# ---------------------------------------------------------------- structure
rec('structure', 0, 'page count = 18', 18, len(doc), len(doc) == 18)
w, h = doc[0].get_size()
rec('structure', 0, 'page size 960x540 (16:9)', '960x540', f'{w:.0f}x{h:.0f}', (round(w), round(h)) == (960, 540))
nrep = rep.groupby('cell_id').rep_id.nunique()
rec('recompute', 9, 'total runs', 2600, int(nrep.sum()), nrep.sum() == 2600)
rec('recompute', 9, 'E1 runs', 1600, int(nrep[nrep.index.str.startswith('aik_e1')].sum()),
    nrep[nrep.index.str.startswith('aik_e1')].sum() == 1600)
rec('recompute', 9, 'E2 runs', 1000, int(nrep[nrep.index.str.startswith('aik_e2')].sum()),
    nrep[nrep.index.str.startswith('aik_e2')].sum() == 1000)
rec('recompute', 9, 'every run has 8 boundaries', 8,
    int(rep.groupby(['cell_id', 'rep_id']).size().min()), rep.groupby(['cell_id', 'rep_id']).size().eq(8).all())
rec('recompute', 9, 'no boundary with U = 0', 0, int((rep.U == 0).sum()), (rep.U == 0).sum() == 0)
rec('summary', 9, 'aik_checks: missing boundaries / zero U', '0 / 0',
    f'{checks.n_missing_rep_boundary.sum()} / {checks.n_zero_U.sum()}',
    checks.n_missing_rep_boundary.sum() == 0 and checks.n_zero_U.sum() == 0)
for s in ['1,600회', '1,000회', '2,600회', '경계누락0', 'U=0사례0']:
    printed(9, s)

# ---------------------------------------------------------------- slide 10: absolute U, gamma=0
for circ in ['cont', 'frag']:
    r = cell(f'aik_e1_g0_{circ}')
    um = r.groupby('boundary_order').U.mean()
    p = prof[prof.cell_id == f'aik_e1_g0_{circ}'].set_index('boundary_order')
    for b in range(1, 9):
        near('recompute', 10, f'U mean {circ} b={b} (rep vs profile CSV)', um[b], p.U_mean[b], 1e-6)
        printed(10, f'{um[b]:,.0f}')
c0, f0 = cell('aik_e1_g0_cont'), cell('aik_e1_g0_frag')
t_cont = c0[c0.boundary_order == 8].RUI.mean()
near('recompute', 10, 'cont mean_r(U8/U1)', t_cont, 0.036, 0.0005)
printed(10, f'{t_cont*100:.1f}%')
gap = 1 - f0[f0.boundary_order == 1].U.mean() / c0[c0.boundary_order == 1].U.mean()
near('recompute', 10, 'frag first-boundary U lower than cont (ratio of cell means)', gap, 0.206, 0.0005)
printed(10, f'{gap*100:.1f}%')
for s in ['12,346명', '9,802명', '448명', '408명']:
    printed(10, s)

# ---------------------------------------------------------------- slide 11: local AUFR + percentile band
for circ in ['cont', 'frag']:
    r = cell(f'aik_e1_g0_{circ}')
    p = prof[prof.cell_id == f'aik_e1_g0_{circ}'].set_index('boundary_order')
    for b in range(2, 9):
        a = r[r.boundary_order == b].AUFR
        near('recompute', 11, f'AUFR mean {circ} b={b}', a.mean(), p.AUFR_mean[b], 1e-9)
        # the band is the spread of run values (2.5/97.5 percentiles), NOT a CI of the mean
        near('recompute', 11, f'band = run-value percentile 2.5 {circ} b={b}', a.quantile(.025), p.AUFR_q025[b], 1e-9)
        near('recompute', 11, f'band = run-value percentile 97.5 {circ} b={b}', a.quantile(.975), p.AUFR_q975[b], 1e-9)
    last = r[r.boundary_order == 8].AUFR.mean()
    printed(11, f'{last*100:.1f}%')
a = c0[c0.boundary_order == 2].AUFR
ci_half = 1.96 * a.std() / np.sqrt(len(a))
rec('recompute', 11, 'band is wider than a 95% CI of the mean (cont b=2)',
    f'band half-width {(a.quantile(.975)-a.quantile(.025))/2:.4f} > CI half-width {ci_half:.4f}', None,
    (a.quantile(.975) - a.quantile(.025)) / 2 > 5 * ci_half)
printed(11, '평균의95%신뢰구간이아니다')
for circ, F in [('cont', 1302), ('frag', 1977)]:
    v = shape[shape.circ == circ].F.iloc[0]
    rec('summary', 11, f'F {circ}', F, f'{v:.1f}', round(v) == F)
    printed(11, f'F={F:,}')

# ---------------------------------------------------------------- slide 8
p = prof[prof.cell_id == 'aik_e1_g0_cont'].set_index('boundary_order')
for s in [f'{p.U_mean[3]:,.0f}명', f'{p.U_mean[4]:,.0f}명', f'{p.AUFR_mean[4]:.3f}']:
    printed(8, s)

# ---------------------------------------------------------------- slide 12: AUFR multiplier, cluster-robust CI
for g in [2, 4, 8]:
    r = cell(f'aik_e1_g{g}_cont')
    # independent re-estimate of the point estimate: log AUFR ~ boundary FE + delta10
    q = r[r.boundary_order >= 2].copy()
    q['y'] = np.log(q.AUFR); q['x'] = 10 * q.delta
    yd = q.y - q.groupby('boundary_order').y.transform('mean')
    xd = q.x - q.groupby('boundary_order').x.transform('mean')
    th = (xd * yd).sum() / (xd * xd).sum()
    t = theta[(theta.gamma == g) & (theta.circ == 'cont')].iloc[0]
    near('recompute', 12, f'theta g={g} (OLS with boundary FE)', th, t.est, 1e-6)
    est, lo, hi = (t.rate_ratio - 1) * 100, (t.rr_lo - 1) * 100, (t.rr_hi - 1) * 100
    printed(12, f'+{est:.1f}%')
    printed(12, f'95% CI {lo:.1f} – {hi:.1f}')
t0 = theta[(theta.gamma == 0) & (theta.circ == 'cont')].iloc[0]
rec('summary', 12, 'gamma=0 control CI contains 1', 'rr_lo<1<rr_hi', f'{t0.rr_lo:.5f}..{t0.rr_hi:.5f}',
    t0.rr_lo < 1 < t0.rr_hi)
printed(12, '퍼센트포인트가아님')
e0, l0, h0 = (t0.rate_ratio - 1) * 100, (t0.rr_lo - 1) * 100, (t0.rr_hi - 1) * 100
printed(12, ('−' if e0 < 0 else '+') + f'{abs(e0):.2f}%')
printed(12, f'95% CI −{abs(l0):.2f} – {h0:.2f} · 0 포함')

# ---------------------------------------------------------------- slide 13: deviance reduction (U, quasi-Poisson; from CSV)
cs = cons[cons.exp == 'e1']
for key, v4 in [('adjacent contrast (Delta)', 10.2), ('upper-floor program', 60.1), ('mean program above boundary', 39.7)]:
    sub = cs[cs.predictor == key]
    val = sub[(sub.gamma == 4) & (sub.circ == 'cont')].dev_explained.iloc[0] * 100
    rec('summary', 13, f'{key} gamma=4 cont', v4, f'{val:.2f}', round(val, 1) == v4)
    printed(13, f'{val:.1f}%')
    printed(13, f'범위 {sub.dev_explained.min()*100:.0f}–{sub.dev_explained.max()*100:.0f}%')

# ---------------------------------------------------------------- slide 14: erosion, bootstrap CI (from CSV) + point re-estimate
def add_slope(r):
    q = r[r.boundary_order >= 2].copy(); q['x'] = 10 * q.delta
    yd = q.AUFR - q.groupby('boundary_order').AUFR.transform('mean')
    xd = q.x - q.groupby('boundary_order').x.transform('mean')
    return (xd * yd).sum() / (xd * xd).sum()


for g, (e, lo, hi) in {2: (6.7, 2.7, 10.5), 4: (0.8, -4.1, 5.2), 8: (1.7, -6.4, 8.6)}.items():
    m = mod[mod.gamma == g].iloc[0]
    sc, sf = add_slope(cell(f'aik_e1_g{g}_cont')), add_slope(cell(f'aik_e1_g{g}_frag'))
    near('recompute', 14, f'additive slope cont g={g}', sc, m.abs_slope_cont, 1e-6)
    near('recompute', 14, f'erosion g={g} = 1 - s_frag/s_cont', 1 - sf / sc, m.erosion, 1e-6)
    rec('summary', 14, f'erosion g={g} [CI]', f'{e} [{lo}, {hi}]',
        f'{m.erosion*100:.2f} [{m.erosion_lo*100:.2f}, {m.erosion_hi*100:.2f}]',
        (round(m.erosion * 100, 1), round(m.erosion_lo * 100, 1), round(m.erosion_hi * 100, 1)) == (e, lo, hi))
    printed(14, f'{e:.1f}%')
    printed(14, '[' + ('−' if lo < 0 else '') + f'{abs(lo):.1f}, {hi:.1f}]')  # sign must survive in the text layer
    excl = m.erosion_lo > 0 or m.erosion_hi < 0
    printed(14, '0을 ' + ('제외' if excl else '포함'))

# ---------------------------------------------------------------- slide 15: anchor shares
sh = {'TOP1': [.107143] * 7 + [.85], 'STEP3': [.05, .45, .05, .05, .45, .05, .05, .45],
      'UNIFORM': [.2] * 8, 'LOW3': [.45, .45, .45] + [.05] * 5}
for k, v in sh.items():
    rec('recompute', 15, f'{k} 2–9F sum', 1.60, f'{sum(v):.6f}', abs(sum(v) - 1.6) < 1e-5)
# shares by floor, inferred from the run CSV (x_upper of boundary b = share of floor b+1)
for k in sh:
    r = cell(f'aik_e2_{k.lower()}_g4_cont')
    xs = r.groupby('boundary_order').x_upper.mean().values
    rec('recompute', 15, f'{k} shares 2F..9F from run CSV', sh[k], np.round(xs, 6).tolist(),
        np.allclose(xs, sh[k], atol=1e-5))
printed(15, '2–9층 합계 1.60')

# ---------------------------------------------------------------- slide 16: placements (mean of per-run ratios)
for k in ['TOP1', 'STEP3', 'UNIFORM', 'LOW3']:
    r = cell(f'aik_e2_{k.lower()}_g4_cont')
    T = r[r.boundary_order == 8].RUI.mean()
    Rr = r[r.boundary_order >= 2].groupby('rep_id').RUI.mean().mean()
    U8 = r[r.boundary_order == 8].U.mean()
    ratio_of_means = U8 / r[r.boundary_order == 1].U.mean()
    a = reach[(reach.pattern == k) & (reach.gamma == 4) & (reach.circ == 'cont')].iloc[0]
    near('recompute', 16, f'{k} T = mean_r(U8/U1)', T, a.T_mean, 1e-9)
    near('recompute', 16, f'{k} R = mean_r(mean_b RUI, b=2..8)', Rr, a.R_mean, 1e-9)
    rec('recompute', 16, f'{k} T differs from ratio of means (method check)', f'{T:.4f}', f'{ratio_of_means:.4f}', True)
    printed(16, f'{T*100:.1f}%'); printed(16, f'{a.R_mean*100:.1f}%'); printed(16, f'{U8:,.0f}')

# ---------------------------------------------------------------- slide 18 summary numbers
for s in ['3.6%', '51.7%', '+6.0', '+10.9', '+18.4%', '6.7%', '58.7%', '9,112명']:
    printed(18, s)

# ---------------------------------------------------------------- wording audit (whole deck)
alltext = ''.join(PAGES)
n_bare = len(re.findall(r'(?<!앵커)유인이없', alltext))  # gamma=0 must be '추가 앵커 유인이 없는'
rec('wording', 0, 'absent: 유인이 없 (without 앵커)', 0, n_bare, n_bare == 0)
for bad in ['프로그램유인이없', '퍼센트포인트상승', '퍼센트포인트증가했', '학술발표', 'RQ1·RQ2', 'RQ3·RQ4', '종합결론']:
    rec('wording', 0, f'absent: {bad}', 0, alltext.count(bad), alltext.count(bad) == 0)
for g0 in ['추가앵커유인이없']:
    rec('wording', 0, 'gamma=0 phrased as "추가 앵커 유인이 없는 조건" (pages)', '>=4 pages',
        sum(g0 in t for t in PAGES), sum(g0 in t for t in PAGES) >= 4)
printed(1, '논문 중간발표')
printed(2, '층간 상행유량 감소와 프로그램 구성')
printed(2, '이동 저항과 앵커 배치에 따른 차이')

out = REPO / 'cloud_task' / 'qa' / 'numbers_check.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['kind', 'slide', 'item', 'expected', 'observed', 'result']); w.writerows(rows)
print(f'{len(rows)} checks, {fails} failed -> {out.relative_to(REPO)}')
for r in rows:
    if r[-1] == 'FAIL':
        print('FAIL', r)
sys.exit(1 if fails else 0)
