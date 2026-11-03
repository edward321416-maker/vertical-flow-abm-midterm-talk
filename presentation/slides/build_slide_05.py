"""슬라이드 5 (4.1 프로그램 중립 기준선) HTML 생성. 숫자는 모두 CSV에서 읽는다(직접 입력 금지).

자료: aik_a1_profile.csv (경계별 평균 인원, 1층 대비 비율, 직전 경계 대비 비율 AUFR)
      aik_boundary_rep.csv (200회 반복별 경계 인원 -> 2.5~97.5 백분위수)
"""
import csv
import os

AIK = r"D:\vcpf\repo\analysis\outputs\sim\aik"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "slide_05.html")

INK, MUT, RULE = "#0f1a24", "#5f6d79", "#e3e7ea"
CONT, FRAG, ACC, ACC_SOFT = "#1d4e80", "#b0602e", "#c0392b", "#fbefed"

prof = list(csv.DictReader(open(os.path.join(AIK, "aik_a1_profile.csv"), encoding="utf-8-sig")))
def pick(circ, key):
    return {int(r["boundary_order"]): (float(r[key]) if r[key] else None) for r in prof if r["circ"] == circ}
U = {c: pick(c, "U_mean") for c in ("cont", "frag")}
RUI = {c: pick(c, "RUI_mean") for c in ("cont", "frag")}
AUFR = {c: pick(c, "AUFR_mean") for c in ("cont", "frag")}

reps = {}
for r in csv.DictReader(open(os.path.join(AIK, "aik_boundary_rep.csv"), encoding="utf-8-sig")):
    if r["cell_id"] in ("aik_e1_g0_cont", "aik_e1_g0_frag"):
        reps.setdefault((r["circ"], int(r["boundary_order"])), []).append(float(r["U"]))
def q(vals, p):
    v = sorted(vals)
    k = (len(v) - 1) * p
    f = int(k)
    return v[f] + (v[min(f + 1, len(v) - 1)] - v[f]) * (k - f)
Q = {k: (q(v, 0.025), q(v, 0.975), len(v)) for k, v in reps.items()}
n_rep = Q[("cont", 1)][2]

B = list(range(1, 9))
drop = 1 - U["frag"][1] / U["cont"][1]

# ---- 기하(슬라이드 좌표, 1920x1080) ----
CX, CW = 960, 200
XL, XR = CX - CW / 2, CX + CW / 2          # 중앙열 좌우 경계
Y0, RH, BH = 346, 70, 36
SC = 540 / max(v[1] for v in Q.values())   # 가장 긴 가는 선 끝이 라벨 포함해 왼쪽 여백 안에 들어오도록


def pct(v):
    p = v * 100
    return f"{p:.0f}%" if p > 99.5 else f"{p:.1f}%"


svg = []
# 헤더
svg.append(f'<text x="{XL-8}" y="318" text-anchor="end" class="hd" fill="{CONT}">연속형 동선</text>')
svg.append(f'<text x="{XR+8}" y="318" text-anchor="start" class="hd" fill="{FRAG}">분절형 동선</text>')
svg.append(f'<text x="{CX}" y="318" text-anchor="middle" class="hs" fill="{MUT}">경계 · 직전 대비 감소</text>')
# 맨 위 경계 강조 띠
top_y = Y0
svg.append(f'<rect x="560" y="{top_y}" width="840" height="{RH}" fill="{ACC_SOFT}" rx="4"/>')
# 중앙열 세로선
svg.append(f'<line x1="{XL}" x2="{XL}" y1="{Y0-6}" y2="{Y0+8*RH+6}" stroke="{RULE}" stroke-width="2"/>')
svg.append(f'<line x1="{XR}" x2="{XR}" y1="{Y0-6}" y2="{Y0+8*RH+6}" stroke="{RULE}" stroke-width="2"/>')

for b in B:
    y = Y0 + (8 - b) * RH
    yc = y + RH / 2
    by = yc - BH / 2
    top = b == 8
    for side, circ, col, x_edge, sign in (("L", "cont", CONT, XL, -1), ("R", "frag", FRAG, XR, 1)):
        u = U[circ][b]
        lo, hi, _ = Q[(circ, b)]
        ln = u * SC
        x = x_edge - ln if sign < 0 else x_edge
        svg.append(f'<rect x="{x:.1f}" y="{by:.1f}" width="{ln:.1f}" height="{BH}" fill="{col}" rx="2"/>')
        # 200회 반복의 2.5~97.5 백분위수
        xa, xb = x_edge + sign * lo * SC, x_edge + sign * hi * SC
        svg.append(f'<line x1="{xa:.1f}" x2="{xb:.1f}" y1="{yc:.1f}" y2="{yc:.1f}" stroke="{INK}" stroke-opacity=".55" stroke-width="2"/>')
        for xx in (xa, xb):
            svg.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{yc-8:.1f}" y2="{yc+8:.1f}" stroke="{INK}" stroke-opacity=".55" stroke-width="2"/>')
        lx = x_edge + sign * hi * SC + sign * 16
        anchor = "end" if sign < 0 else "start"
        svg.append(f'<text x="{lx:.1f}" y="{yc+8:.1f}" text-anchor="{anchor}" class="vv" fill="{col}">{u:,.0f}<tspan class="vp" fill="{MUT}"> · {pct(RUI[circ][b])}</tspan></text>')
    # 중앙: 경계 이름 + 직전 대비 감소
    svg.append(f'<text x="{CX}" y="{yc-3:.1f}" text-anchor="middle" class="fl">{b}→{b+1}층</text>')
    if b == 1:
        svg.append(f'<text x="{CX}" y="{yc+22:.1f}" text-anchor="middle" class="ls" fill="{MUT}">첫 경계</text>')
    else:
        lc = (1 - AUFR["cont"][b]) * 100
        lf = (1 - AUFR["frag"][b]) * 100
        c1, c2 = (ACC, ACC) if top else (CONT, FRAG)
        wgt = "800" if top else "600"
        svg.append(f'<text x="{CX}" y="{yc+22:.1f}" text-anchor="middle" class="ls" style="font-weight:{wgt}">'
                   f'<tspan fill="{c1}">−{lc:.0f}%</tspan><tspan fill="{MUT}" style="font-weight:400">  ·  </tspan><tspan fill="{c2}">−{lf:.0f}%</tspan></text>')

# 큰 숫자 콜아웃(막대가 짧은 위쪽 빈 공간)
svg.append(f'<text x="110" y="376" class="cap">1층에서 올라간 100명 중</text>')
svg.append(f'<text x="110" y="410" class="cap">맨 위 층까지 가는 사람</text>')
svg.append(f'<text x="104" y="528" class="big" fill="{ACC}">{RUI["cont"][8]*100:.1f}<tspan class="unit">명</tspan></text>')
svg.append(f'<text x="110" y="578" class="cap2" fill="{FRAG}">분절형 동선에서는 {RUI["frag"][8]*100:.1f}명</text>')
svg.append(f'<text x="1440" y="376" class="cap">분절형 동선은 첫 경계부터</text>')
svg.append(f'<text x="1432" y="528" class="big" fill="{INK}" style="font-size:116px">−{drop*100:.1f}<tspan class="unit" style="font-size:52px">%</tspan></text>')
svg.append(f'<text x="1440" y="578" class="cap2" fill="{MUT}">{U["cont"][1]:,.0f}명 → {U["frag"][1]:,.0f}명</text>')

# RQ1 검정: 로그 직선 가설 기각 (aik_a1_shape.csv)
shape = {r["circ"]: r for r in csv.DictReader(open(os.path.join(AIK, "aik_a1_shape.csv"), encoding="utf-8-sig"))}
dc, df = float(shape["cont"]["max_dev_log"]), float(shape["frag"]["max_dev_log"])
fc, ff = float(shape["cont"]["F"]), float(shape["frag"]["F"])
nx, ny = 1528, 664
svg.append(f'<line x1="{nx}" x2="{nx+300}" y1="{ny-30}" y2="{ny-30}" stroke="{RULE}" stroke-width="2"/>')
svg.append(f'<text x="{nx}" y="{ny}" class="nh">층마다 같은 비율로</text>')
svg.append(f'<text x="{nx}" y="{ny+30}" class="nh">줄지 않습니다</text>')
svg.append(f'<text x="{nx}" y="{ny+68}" class="nb">로그 직선 이탈 폭</text>')
svg.append(f'<text x="{nx}" y="{ny+96}" class="nb"><tspan fill="{CONT}" font-weight="700">{dc:.3f}</tspan> · <tspan fill="{FRAG}" font-weight="700">{df:.3f}</tspan>  (기준 0.10)</text>')
svg.append(f'<text x="{nx}" y="{ny+124}" class="nb">F = {fc:,.0f} · {ff:,.0f}, p &lt; 0.001</text>')

# 하단 읽는 법
svg.append(f'<line x1="110" x2="1810" y1="968" y2="968" stroke="{RULE}" stroke-width="2"/>')
svg.append(f'<text x="110" y="1004" class="src">막대 = 4일 모의 평균 상향 이동 인원(선형 눈금), 가는 선 = {n_rep}회 반복의 2.5~97.5 백분위수 · % = 각 동선의 1층 진입량 대비</text>')
svg.append(f'<text x="110" y="1034" class="src">매장 효과 없음(γ=0) · 중앙 숫자 = 직전 경계 대비 감소(1 − AUFR), 남색 연속형 · 갈색 분절형 · 자료: aik_a1_profile.csv, aik_boundary_rep.csv</text>')

title = "구조만의 몫을 알아보려고, 매장 효과를 끈 상태를 먼저 봤습니다"
answer = (f'구조만으로 최상층에는 1층의 <b>{RUI["cont"][8]*100:.1f}%</b>만 도착하고, '
          f'동선을 꼬면 들어오는 사람이 처음부터 <b>{drop*100:.1f}%</b> 줄어듭니다')

html = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>슬라이드 5</title>
<style>
html,body{{margin:0;padding:0;background:#fff}}
.slide{{position:relative;width:1920px;height:1080px;overflow:hidden;background:#fff;font-family:"Pretendard","Malgun Gothic",sans-serif;color:{INK};font-feature-settings:"tnum"}}
.tag{{position:absolute;left:110px;top:52px;font-size:22px;font-weight:600;letter-spacing:.08em;color:{MUT}}}
.title{{position:absolute;left:110px;top:92px;width:1700px;font-size:48px;font-weight:700;line-height:1.25;letter-spacing:-.01em}}
.answer{{position:absolute;left:110px;top:168px;width:1700px;font-size:28px;font-weight:500;line-height:1.4;color:#2b3a47}}
.answer b{{color:{ACC};font-weight:800}}
.num{{position:absolute;right:110px;top:56px;font-size:22px;font-weight:600;color:{MUT}}}
svg{{position:absolute;left:0;top:0}}
svg text{{font-family:"Pretendard","Malgun Gothic",sans-serif}}
.hd{{font-size:28px;font-weight:700}}
.hs{{font-size:20px;font-weight:500}}
.fl{{font-size:26px;font-weight:700;fill:{INK}}}
.ls{{font-size:20px}}
.vv{{font-size:25px;font-weight:700}}
.vp{{font-size:22px;font-weight:400}}
.cap{{font-size:28px;font-weight:500;fill:{MUT}}}
.cap2{{font-size:28px;font-weight:600}}
.big{{font-size:150px;font-weight:800;letter-spacing:-.03em}}
.unit{{font-size:64px;font-weight:700;letter-spacing:0}}
.src{{font-size:19px;fill:{MUT}}}
.nh{{font-size:24px;font-weight:700;fill:{INK}}}
.nb{{font-size:20px;font-weight:500;fill:{MUT}}}
</style></head><body>
<div class="slide">
<div class="tag">4.1  프로그램 중립 기준선 (RQ1)</div>
<div class="num">5 / 9</div>
<div class="title">{title}</div>
<div class="answer">{answer}</div>
<svg width="1920" height="1080" viewBox="0 0 1920 1080">{"".join(svg)}</svg>
</div>
</body></html>
'''
open(OUT, "w", encoding="utf-8").write(html)
print("saved:", os.path.abspath(OUT))
print("RUI8", round(RUI["cont"][8] * 100, 2), RUI["frag"][8] and round(RUI["frag"][8] * 100, 2), "drop", round(drop * 100, 2), "n_rep", n_rep)
print("q b=1 cont", [round(x) for x in Q[("cont", 1)][:2]], "b=8 cont", [round(x) for x in Q[("cont", 8)][:2]])
