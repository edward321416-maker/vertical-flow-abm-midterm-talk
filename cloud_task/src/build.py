"""Build the midterm deck PDF from the repository's analysis CSVs.

Usage (from any working directory):
    python3 cloud_task/src/build.py [output.pdf]
Default output: cloud_task/output/vertical_flow_midterm_refined.pdf
A title/label inventory CSV is written next to the PDF as title_inventory.csv.
"""
import sys, math, csv
from pathlib import Path
import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
REPO = SRC_DIR.parents[1]
sys.path.insert(0, str(SRC_DIR))
from lib import *

D = str(REPO / 'analysis' / 'outputs' / 'aik') + '/'
prof = pd.read_csv(D + 'aik_a1_profile.csv')
theta = pd.read_csv(D + 'aik_a2_theta.csv')
cons = pd.read_csv(D + 'aik_a2b_constructs.csv')
mod = pd.read_csv(D + 'aik_a3_moderation.csv')
reach = pd.read_csv(D + 'aik_a4_reach.csv')
e2 = pd.read_csv(D + 'aik_e2_profile.csv')
shape = pd.read_csv(D + 'aik_a1_shape.csv')

OUT = str(Path(sys.argv[1]).resolve()) if len(sys.argv) > 1 else \
    str(REPO / 'cloud_task' / 'output' / 'vertical_flow_midterm_refined.pdf')
Path(OUT).parent.mkdir(parents=True, exist_ok=True)
d = Deck(OUT)
SRC = '출처: 수정 논문 8쪽 · 분석 CSV(analysis/outputs/aik)'


class Ax:
    def __init__(s, x0, y0, x1, y1, xr, yr, ylog=False):
        s.x0, s.y0, s.x1, s.y1, s.xr, s.yr, s.ylog = x0, y0, x1, y1, xr, yr, ylog

    def X(s, v):
        return s.x0 + (v - s.xr[0]) / (s.xr[1] - s.xr[0]) * (s.x1 - s.x0)

    def Yv(s, v):
        if s.ylog:
            f = (math.log10(v) - math.log10(s.yr[0])) / (math.log10(s.yr[1]) - math.log10(s.yr[0]))
        else:
            f = (v - s.yr[0]) / (s.yr[1] - s.yr[0])
        return s.y1 - f * (s.y1 - s.y0)


def fmt_int(v):
    return f'{v:,.0f}'


# ---------------------------------------------------------------- 01 cover
c = d.slide('논문 중간발표', '', '')
d.inventory.clear(); d.inventory.append((1, 'title', '다층 상업시설의 프로그램 배치와 수직동선 마찰이 층간 상행유량에 미치는 영향'))
text(c, ML, 150, '논문 중간발표', 13, 'B', K75)
line(c, ML, 164, ML + 28, 164, K100, 1.2)
y = 214
for t in ['다층 상업시설의 프로그램 배치와', '수직동선 마찰이 층간 상행유량에', '미치는 영향']:
    text(c, ML, y, t, 28, 'B'); y += 44
text(c, ML, y + 14, '에이전트 기반 시뮬레이션 민감도 분석', 15, 'R', K55)
text(c, ML, 448, '봉성현', 14, 'B')
text(c, ML, 470, '성균관대학교 건축학과', 12, 'R', K55)
text(c, W - ML, 470, '현재까지의 모형 실험과 분석 결과, 해석 범위, 향후 검증', 11, 'R', K55, 'r')
d.note('cover', '논문 중간발표 · 봉성현 · 성균관대학교 건축학과')

# ---------------------------------------------------------------- 02 contents
c = d.slide('발표 구성', '발표 구성', '현재까지 수행한 모형 실험과 분석 결과, 해석 범위, 향후 검증 순서로 진행한다', None)
items = [
    ('연구 배경과 분석 단위', '왜 절대 유량뿐 아니라 비율을 보는가', '3–4'),
    ('선행연구와 핵심 질문', 'Chang & Penn(1998)과의 관계, 네 가지 질문', '5–6'),
    ('시뮬레이션 조건과 실험 설계', '합성 9층 모형, 이동 저항과 앵커 배치 실험', '7–9'),
    ('층간 상행유량 감소와 프로그램 구성', '높이에 따른 감소, 인접층 프로그램 차이와의 관계', '10–13'),
    ('이동 저항과 앵커 배치에 따른 차이', '이동 저항의 조절 효과, 같은 총량의 네 가지 배치', '14–16'),
    ('현재까지의 분석 결과와 향후 검증', '해석의 한계와 후속 과제', '17–18'),
]
d.note('toc', ' | '.join(i[0] for i in items))
colx = [ML, ML + 440]
for i, (t, s, p) in enumerate(items):
    col, row = divmod(i, 3)
    x, y0 = colx[i // 3], 168 + row * 108
    text(c, x, y0 + 30, f'{i+1:02d}', 30, 'R', K30)
    text(c, x + 64, y0 + 14, t, 16, 'B')
    wrap(c, x + 64, y0 + 38, s, 330, 12, 'R', K55)
    text(c, x + 64, y0 + 76, f'슬라이드 {p}', 10.5, 'R', K55)
    line(c, x, y0 + 92, x + 408, y0 + 92, K12, .75)
d.note('toc-detail', ' | '.join(i[1] for i in items))

# ---------------------------------------------------------------- 03 background
c = d.slide('01 연구 배경과 분석 단위', '절대 감소량이 같아도 층간 유지 정도는 다르다',
            '경계를 지나는 사람 수의 크기와, 직전 경계 대비 비율을 구분해 살펴본다', '주: 개념 설명용 가상 예시이며 실제 시뮬레이션 수치가 아니다')
# virtual-example tag
rect(c, W - ML - 150, 124, 150, 22, stroke=K55, sw=.75)
text(c, W - ML - 75, 139, '가상 예시 (연구 수치 아님)', 10, 'R', K75, 'c')
# left panel
text(c, ML, 166, '① 절대 통과 유량 (명)', 13, 'B')
text(c, ML, 184, '두 사례 모두 50명이 줄었다', 11.5, 'R', K55)
ax = Ax(ML + 70, 200, ML + 400, 420, (0, 1000), (0, 1))
for v in (0, 500, 1000):
    line(c, ax.X(v), 214, ax.X(v), 424, K12, .75)
    text(c, ax.X(v), 440, f'{v:,}', 10.5, 'R', K55, 'c')
cases = [('사례 A', 100, 50, 232), ('사례 B', 1000, 950, 340)]
for nm, a, b, yy in cases:
    text(c, ML, yy + 18, nm, 12, 'B')
    rect(c, ax.X(0), yy, ax.X(a) - ax.X(0), 18, fill=K30)
    text(c, ax.X(a) + 8, yy + 14, f'직전 경계 {a:,}명', 11, 'R', K75) if a < 900 else text(c, ax.X(a) - 8, yy + 14, f'직전 경계 {a:,}명', 11, 'R', K100, 'r')
    rect(c, ax.X(0), yy + 26, ax.X(b) - ax.X(0), 18, fill=K100)
    text(c, ax.X(b) + 8, yy + 40, f'현재 경계 {b:,}명', 11, 'R', K75) if b < 900 else text(c, ax.X(b) - 8, yy + 40, f'현재 경계 {b:,}명', 11, 'R', HexColor('#FFFFFF'), 'r')
    if nm == '사례 B':
        pass
line(c, W / 2, 160, W / 2, 452, K12, .75)
# right panel
rx0 = W / 2 + 40
text(c, rx0, 166, '② 직전 경계를 100%로 놓은 비율 (AUFR)', 13, 'B')
text(c, rx0, 184, '유지된 정도는 50%와 95%로 크게 다르다', 11.5, 'R', K55)
bw = 312
for nm, a, b, yy in cases:
    text(c, rx0, yy + 18, nm, 12, 'B')
    rect(c, rx0 + 62, yy, bw * .8, 18, fill=K30)
    text(c, rx0 + 62 + bw * .8 + 8, yy + 14, '직전 100%', 11, 'R', K75)
    rect(c, rx0 + 62, yy + 26, bw * .8 * b / a if a == 100 else bw * .8 * .95, 18, fill=CONT)
    pct = 50 if a == 100 else 95
    text(c, rx0 + 62 + bw * .8 * pct / 100 - 8 if pct > 90 else rx0 + 62 + bw * .8 * pct / 100 + 8, yy + 41,
         f'{pct}%', 14, 'B', HexColor('#FFFFFF') if pct > 90 else CONT, 'r' if pct > 90 else 'l')
line(c, rx0 + 62 + bw * .8, 222, rx0 + 62 + bw * .8, 400, K55, .75, [3, 3])
text(c, rx0 + 62, 440, 'AUFR = 현재 경계 ÷ 직전 경계', 11.5, 'R', K75)
text(c, ML, 478, '절대 감소량이 같아도 상대 유량은 다르다. 따라서 U(크기)와 AUFR(비율)을 구분해 분석한다.', 12.5, 'B')
d.note('chart', '사례 A 100→50 (50%), 사례 B 1,000→950 (95%), 가상 예시')

# ---------------------------------------------------------------- 04 metrics
c = d.slide('01 연구 배경과 분석 단위', '유량의 크기와 비율은 서로 다른 질문에 답한다',
            '같은 반복 r의 경계 통과량 U에서 세 지표를 계산하며, 각각 묻는 것이 다르다', SRC)
cols = [
    ('01  경계 상행유량', '얼마나 통과했는가?', 'U_{r,b}', None,
     ['반복 r에서 경계 b를 위로 통과한 연인원', 'U_{1} = 1F→2F,  U_{8} = 8F→9F'], '건물 입장객 수가 아님'),
    ('02  국소 상행유량비 (AUFR)', '직전 경계 대비 얼마나 유지됐는가?', 'AUFR_{r,b}', ('U_{r,b}', 'U_{r,b−1}'),
     ['같은 반복 r의 인접한 두 경계 통과량의 비', 'b = 2, …, 8  (b = 1은 분모가 없음)'], '개별 방문객의 생존율이 아님'),
    ('03  최상단 상대 유량', '첫 경계 대비 마지막 경계는?', 'T_{r}', ('U_{r,8}', 'U_{r,1}'),
     ['T_{r} = AUFR_{r,2} × … × AUFR_{r,8}', '반복별로 먼저 계산한 뒤 평균'], '최상층 방문 확률이 아님'),
]
cw = CW / 3
for i, (lab, q, sym, fr, defs, warn) in enumerate(cols):
    x = ML + i * cw + (0 if i == 0 else 20)
    if i:
        line(c, ML + i * cw, 140, ML + i * cw, 480, K12, .75)
    text(c, x, 156, lab, 11, 'R', K55)
    wrap(c, x, 188, q, cw - 40, 16, 'B', K100, 1.3)
    # formula zone y 236..330
    if fr is None:
        text(c, x, 296, sym, 30, 'R')
    else:
        sw_ = text(c, x, 296, sym + ' =', 22, 'R')
        frac(c, x + sw_ + 12 + max(tw(fr[0], 22), tw(fr[1], 22)) / 2, 288, fr[0], fr[1], 22)
    yy = 358
    for dline in defs:
        yy = wrap(c, x, yy, dline, cw - 40, 12, 'R', K75, 1.45) + 4
    text(c, x, 450, warn, 12, 'B', K100)
    d.note('metric', f'{lab} | {q} | {sym}')

# ---------------------------------------------------------------- 05 prior research
c = d.slide('02 선행연구와 핵심 질문', '실제 다층 공간 연구에서 합성 층 모형으로 범위를 좁혔다',
            'Chang & Penn(1998)은 관측·모형화 연구이며, 본 연구는 그 결과를 재현하거나 검증하지 않는다',
            '출처: Chang & Penn (1998), Environment and Planning B 25(4), 507–538 · 수정 논문 2장')
cx0, cx1 = 404, 556
text(c, cx0 - 24, 148, 'Chang & Penn (1998)', 15, 'B', K100, 'r')
text(c, cx0 - 24, 167, '실제 다층 복합공간의 관찰·모형화', 11, 'R', K55, 'r')
text(c, cx1 + 24, 148, '본 연구', 15, 'B', K100)
text(c, cx1 + 24, 167, '합성 9층의 층 단위 선택 모형', 11, 'R', K55)
rows = [
    ('대상 공간', '런던 Barbican과 South Bank의 실제 다층 보행 공간', '실제 평면을 복제하지 않은 합성 9층'),
    ('접근', '게이트 관측 보행량과 IMCM(통합 다층 동선 모형) 비교', '에이전트 선택 규칙의 민감도 분석'),
    ('중심 변수', '수평 방향 전환 깊이 · 층 분리 · 발생·유인 지점', '프로그램 비중·배치 · 유인 강도 γ · 이동 저항'),
    ('분석 단위', '공간 구성과 관측된 보행 분포', '8개 상행 경계의 U와 AUFR'),
    ('해석 범위', '실제 복합지역의 이동 분포 설명', '명시한 모형과 네 배치 안의 조건부 결과'),
]
for i, (lab, l, r) in enumerate(rows):
    y0 = 188 + i * 52
    line(c, ML, y0, W - ML, y0, K12, .75)
    text(c, (cx0 + cx1) / 2, y0 + 31, lab, 11.5, 'B', K55, 'c')
    for s_, x_, al in ((l, cx0 - 24, 'r'), (r, cx1 + 24, 'l')):
        assert tw(s_, 12.5) <= cx0 - 24 - ML, s_  # one line per cell, no orphan wraps
        text(c, x_, y0 + 31, s_, 12.5, 'R', K100, al)
line(c, cx0 + 6, 180, cx0 + 6, 448, K12, .75); line(c, cx1 - 6, 180, cx1 - 6, 448, K12, .75)
line(c, ML, 448, W - ML, 448, K12, .75)
text(c, ML, 478, '두 연구는 복제·검증 관계가 아니라 연구 문제의 계보로 이어진다.', 12.5, 'B')
d.note('compare', 'Chang & Penn vs 본 연구 5행')

# ---------------------------------------------------------------- 06 questions
c = d.slide('02 선행연구와 핵심 질문', '이 발표가 확인하려는 네 가지 질문',
            '질문마다 사용하는 지표와 실험 조건이 다르다', SRC)
qs = [
    ('RQ1', '추가 앵커 유인이 없을 때, 위층으로 갈수록 상행유량은 어떻게 줄어드는가?', 'γ = 0 (앵커 비중 효용항이 0) · U와 국소 AUFR'),
    ('RQ2', '인접한 두 층의 프로그램 차이는 상행유량비와 어떤 관계가 있는가?', 'Δx 0.1 증가당 AUFR 상대 변화 · U 보조 분석'),
    ('RQ3', '이동 저항이 커지면 이 관계는 약해지는가?', '연속형 대 분절형 · 기울기 잠식률과 95% 신뢰구간'),
    ('RQ4', '프로그램 총량이 같을 때, 배치만 바꾸면 최상단 유량이 달라지는가?', 'TOP1 · STEP3 · UNIFORM · LOW3 · 상대 유량 T'),
]
for i, (rq, q, m) in enumerate(qs):
    y0 = 142 + i * 88
    line(c, ML, y0, W - ML, y0, K12, .75)
    text(c, ML, y0 + 30, f'{i+1}', 28, 'R', K30)
    text(c, ML + 4, y0 + 52, rq, 9.5, 'R', K55)
    wrap(c, ML + 70, y0 + 31, q, 600, 17, 'B', K100, 1.3)
    text(c, ML + 70, y0 + 66, m, 12, 'R', K55)
    d.note('question', f'{rq} {q}')
line(c, ML, 142 + 4 * 88, W - ML, 142 + 4 * 88, K12, .75)

# ---------------------------------------------------------------- 07 model
c = d.slide('03 시뮬레이션 조건과 실험 설계', '방문 그룹의 선택 규칙과 경계 기록 위치를 분리했다',
            '비공간적 합성 9층 모형: 실제 평면·에스컬레이터 기하는 재현하지 않았다', '출처: 수정 논문 3.1–3.2절 · 식 (1)–(3)')
text(c, ML, 142, '측정 위치: 층 9개, 상행 경계 8개', 13, 'B')
fy0, fh = 156, 33
for i in range(9):  # 9F top
    fl = 9 - i
    yy = fy0 + i * fh
    rect(c, ML + 40, yy + 4, 190, fh - 8, stroke=K55, sw=.75)
    text(c, ML + 28, yy + 21, f'{fl}F', 11.5, 'R', K75, 'r')
for b in range(1, 9):  # boundary b between floor b and b+1
    yy = fy0 + (9 - b) * fh   # line between floor b+1 (above) and b
    line(c, ML + 40, yy, ML + 252, yy, K100, .75)
    c.setFillColor(K100)
    text(c, ML + 262, yy + 4, f'U_{{{b}}}', 11.5, 'B')
    text(c, ML + 292, yy + 4, f'{b}F→{b+1}F', 10, 'R', K55)
text(c, ML + 40, fy0 + 9 * fh + 20, 'U_{b}: b층과 b+1층 사이 경계를 위로 통과한 연인원', 10.5, 'R', K55)
# right: choice chain
rx = 470
text(c, rx, 142, '선택 규칙: 방문 그룹 1개의 이동', 13, 'B')
steps = [
    ('유입·체류', '요일·시간대별 도착, 그룹 단위로 함께 이동'),
    ('퇴장 또는 목적지 층 선택', '확률적 선택 · 현재층 i에서 어느 층 j로도 이동 가능'),
    ('이동수단 선택', '계단 · 에스컬레이터 · 엘리베이터 중 확률적 선택'),
    ('지나는 모든 경계에 기록', '위로 지나간 경계마다 U에 그룹 인원을 더함'),
]
for i, (t, s) in enumerate(steps):
    y0 = 166 + i * 62
    dot(c, rx + 8, y0 + 8, 8, Color(1, 1, 1), K100, 1)
    text(c, rx + 8, y0 + 12, str(i + 1), 10.5, 'B', K100, 'c')
    if i < 3:
        line(c, rx + 8, y0 + 16, rx + 8, y0 + 54, K30, .75)
    text(c, rx + 28, y0 + 12, t, 13.5, 'B')
    text(c, rx + 28, y0 + 31, s, 11.5, 'R', K55)
line(c, rx, 420, W - ML, 420, K12, .75)
text(c, rx, 440, '목적지 효용', 11, 'B', K55)
text(c, rx, 460, 'V_{ij} = ln A_{j} + γ x_{j} − α ln d_{ij} − β ln I_{ij}', 14, 'R', K100)
text(c, rx, 480, 'γ는 실측 집객 계수가 아닌 가정한 민감도 값 · 하행 편향항 δ_{down} = 0 (생략)', 11, 'R', K55)
d.note('model', '9층 8경계 U1~U8, 4단계 선택 규칙')

# ---------------------------------------------------------------- 08 AUFR zoom
c = d.slide('03 시뮬레이션 조건과 실험 설계', '인접한 두 경계를 비교해 상행유량비를 계산한다',
            '3개 층 · 2개 경계만 확대한다. 예: b = 4,  AUFR_{4} = U_{4} / U_{3}', SRC)
d.inventory[-1] = (d.n, 'subtitle', '3개 층 · 2개 경계만 확대한다. 예: b = 4, AUFR4 = U4 / U3')
# 3 floor bands
fx, fw = ML + 40, 230
fl = [('5F', 160), ('4F', 250), ('3F', 340)]
for nm, y0 in fl:
    rect(c, fx, y0, fw, 70, stroke=K55, sw=.75)
    text(c, fx - 12, y0 + 40, nm, 13, 'B', K75, 'r')
line(c, fx - 6, 250, fx + fw + 6, 250, K100, 1.5)
line(c, fx - 6, 340, fx + fw + 6, 340, K100, 1.5)
text(c, fx + fw + 20, 246, 'U_{4}', 15, 'B'); text(c, fx + fw + 56, 246, '4F → 5F', 11, 'R', K55)
text(c, fx + fw + 20, 336, 'U_{3}', 15, 'B'); text(c, fx + fw + 56, 336, '3F → 4F', 11, 'R', K55)
text(c, fx, 440, '위로 통과한 연인원만 경계에 기록한다 (층 안의 체류량이 아님)', 10.5, 'R', K55)
# right: formula
rx = 640
frac(c, rx + 70, 232, 'U_{4}', 'U_{3}', 30)
text(c, rx + 40, 240, 'AUFR_{4}  =', 26, 'R', K100, 'r')
text(c, rx, 300, '분자  U_{4}:  4F→5F 경계 통과량', 12.5, 'R', K75)
text(c, rx, 324, '분모  U_{3}:  3F→4F 경계 통과량', 12.5, 'R', K75)
line(c, rx, 346, W - ML, 346, K12, .75)
text(c, rx, 372, '실제 값으로 읽기', 11, 'B', K55)
text(c, rx, 394, '연속형 · 추가 앵커 유인 없음(γ=0) · 200회 평균', 11, 'R', K55)
text(c, rx, 418, 'U_{3} ≈ 4,654명,  U_{4} ≈ 3,068명', 12.5, 'R', K100)
r4 = prof[(prof.cell_id == 'aik_e1_g0_cont') & (prof.boundary_order == 4)].iloc[0]
text(c, rx, 442, f'AUFR_{{4}}(반복별 비율의 평균) = {r4.AUFR_mean:.3f}', 12.5, 'B')
text(c, rx, 470, '경계 통과량의 비이며, 같은 방문객의 도달 확률이 아니다', 11, 'R', K55)
d.note('zoom', 'AUFR4=U4/U3, 연속형 γ=0 AUFR4=%.3f' % r4.AUFR_mean)

# ---------------------------------------------------------------- 09 design
c = d.slide('03 시뮬레이션 조건과 실험 설계', '이동 저항과 앵커 배치를 나누어 비교했다',
            '실험 1은 이동 저항 × 유인 강도의 교차, 실험 2는 총량을 고정한 배치 변형이다', '출처: 수정 논문 3.2절 · <표 2> · aik_cells.csv · aik_checks.csv')
# E1 matrix
text(c, ML, 146, '실험 1 (E1)  이동 저항 × 유인 강도', 14, 'B')
text(c, ML, 165, '완전 교차 8개 셀 · 셀당 200회', 11.5, 'R', K55)
mx0, my0, cwid, rh = ML + 90, 196, 76, 46
for j, g in enumerate([0, 2, 4, 8]):
    text(c, mx0 + j * cwid + cwid / 2, my0 - 8, f'γ = {g}', 12, 'B', K75, 'c')
for i, (nm, col, sub) in enumerate([('연속형', CONT, '저항 1.0 · 25초'), ('분절형', FRAG, '저항 2.45 · 55초')]):
    yy = my0 + i * rh
    text(c, ML, yy + 20, nm, 12.5, 'B', col)
    text(c, ML, yy + 36, sub, 9.5, 'R', K55)
    for j in range(4):
        rect(c, mx0 + j * cwid + 3, yy + 3, cwid - 6, rh - 6, stroke=col, sw=1)
        text(c, mx0 + j * cwid + cwid / 2, yy + 28, '200', 14, 'R', K100, 'c')
text(c, mx0, my0 + 2 * rh + 24, '8셀 × 200회 = 1,600회', 13, 'B')
text(c, ML, my0 + 2 * rh + 50, '경계 상행유량 U와 AUFR을 모든 셀에서 같은 방식으로 집계', 11, 'R', K55)
text(c, ML, my0 + 2 * rh + 68, '각 층의 앵커 비중 x_{j}는 반복마다 0–0.5 균등분포에서 추출', 11, 'R', K55)
line(c, W / 2 + 6, 140, W / 2 + 6, 440, K12, .75)
# E2 matrix
ex = W / 2 + 24
text(c, ex, 146, '실험 2 (E2)  총량 고정 · 배치 변형', 14, 'B')
text(c, ex, 165, '2–9층 앵커 비중 합계 ≈ 1.60 · 1층 0.05 고정', 11.5, 'R', K55)
pats = ['TOP1', 'STEP3', 'UNIFORM', 'LOW3']
ew = 74
EL = 98  # label column width
for j, p in enumerate(pats):
    text(c, ex + EL + j * ew + ew / 2, my0 - 8, p, 11.5, 'B', SC[p], 'c')
rows2 = [('γ=4 연속형', [100, 100, 100, 100]), ('γ=4 분절형', [100, 100, 100, 100]), ('γ=0 대조 연속형', [100, None, 100, None])]
for i, (nm, vals) in enumerate(rows2):
    yy = my0 + i * 40
    text(c, ex, yy + 24, nm, 11, 'R', K75)
    for j, v in enumerate(vals):
        if v:
            rect(c, ex + EL + j * ew + 4, yy + 3, ew - 8, 32, stroke=SC[pats[j]], sw=1, dash=[3, 2] if i == 2 else None)
            text(c, ex + EL + j * ew + ew / 2, yy + 25, str(v), 13, 'R', K100, 'c')
text(c, ex, my0 + 3 * 40 + 22, '800회 + 200회 = 1,000회', 13, 'B')
text(c, ex, my0 + 3 * 40 + 44, '가정한 유인 강도에서의 배치 비교이며 최적화 문제가 아니다', 11, 'R', K55)
line(c, ML, 440, W - ML, 440, K12, .75)
text(c, ML, 466, 'E1 1,600회 + E2 1,000회 = 2,600회', 15, 'B')
text(c, ML + 330, 466, '반복당 4일 · 경계 누락 0 · U = 0 사례 0', 12.5, 'R', K75)
text(c, ML, 488, 'γ는 실측 보정값이 아니라 모형 민감도를 확인하기 위한 가정값이다', 11, 'R', K55)
d.note('design', 'E1 1600 + E2 1000 = 2600')

# ---------------------------------------------------------------- 10 U profile
c = d.slide('04 층간 상행유량 감소와 프로그램 구성', '추가 앵커 유인이 없는 조건에서도 상행유량은 위로 갈수록 줄었다',
            '추가 앵커 유인이 없는 조건(γ = 0) · 경계별 평균 상행유량 U (반복별 4일 합계의 200회 평균)', SRC)
ax = Ax(ML + 54, 150, ML + 560, 380, (1, 8), (0, 14000))
for v in range(0, 14001, 3500):
    line(c, ax.x0, ax.Yv(v), ax.x1, ax.Yv(v), K12, .75)
    text(c, ax.x0 - 8, ax.Yv(v) + 4, f'{v:,}', 10.5, 'R', K55, 'r')
text(c, ML, 136, '상행 통과량 (명)', 10.5, 'R', K55)
data = {}
for nm, cid, col in [('연속형', 'aik_e1_g0_cont', CONT), ('분절형', 'aik_e1_g0_frag', FRAG)]:
    s = prof[prof.cell_id == cid].sort_values('boundary_order')
    data[nm] = s.U_mean.tolist()
    pts = [(ax.X(b), ax.Yv(u)) for b, u in zip(s.boundary_order, s.U_mean)]
    polyline(c, pts, col, 2.2)
    for p in pts:
        dot(c, p[0], p[1], 3.5, col)
for b in range(1, 9):
    text(c, ax.X(b), 400, str(b), 11, 'R', K75, 'c')
text(c, (ax.x0 + ax.x1) / 2, 420, '경계 b  (1 = 1F→2F … 8 = 8F→9F)', 10.5, 'R', K55, 'c')
text(c, ax.X(1) + 12, ax.Yv(12346) - 8, '연속형  12,346명', 12, 'B', CONT)
text(c, ax.X(1) + 96, ax.Yv(9802) + 4, '분절형  9,802명', 12, 'B', FRAG)
text(c, ax.X(8) + 12, ax.Yv(448) - 2, '448명', 12, 'B', CONT)
text(c, ax.X(8) + 12, ax.Yv(408) + 14, '408명', 12, 'B', FRAG)
# value table under axis
ty = 446
for k, (nm, col) in enumerate([('연속형', CONT), ('분절형', FRAG)]):
    text(c, ML, ty + k * 20, nm, 10.5, 'B', col)
    for b in range(8):
        text(c, ax.X(b + 1), ty + k * 20, fmt_int(data[nm][b]), 10.5, 'R', K75, 'c')
# right notes
nx = 696
text(c, nx, 160, '읽는 법', 11, 'B', K55)
yy = wrap(c, nx, 184, 'U₁은 1F→2F 경계 통과량이며 건물 전체 입장객 수가 아니다.'.replace('₁', '_{1}'), 200, 12, 'R', K75, 1.5)
yy = wrap(c, nx, yy + 14, '연속형에서 U_{8}/U_{1} = 3.6% (반복별 비율의 평균)', 200, 12, 'B', K100, 1.5)
yy = wrap(c, nx, yy + 14, '분절형의 첫 경계 U는 연속형보다 20.6% 낮다. 건물 진입 감소율이 아니라 셀별 반복 평균의 비교다.', 200, 12, 'R', K75, 1.5)
yy = wrap(c, nx, yy + 14, 'γ = 0은 앵커 비중 효용항만 0으로 둔 조건이다. 도착·층 선택·이동 저항·체류·퇴장 규칙은 그대로이므로 이동 마찰만의 자연 상태가 아니다.', 200, 11, 'R', K55, 1.5)
d.note('chart', 'U profile g0: 12,346→448 cont; 9,802→408 frag')

# ---------------------------------------------------------------- 11 AUFR local
c = d.slide('04 층간 상행유량 감소와 프로그램 구성', '상행유량은 층마다 같은 비율로 줄지 않았다',
            '추가 앵커 유인이 없는 조건(γ = 0) · 경계 2–8의 국소 AUFR 평균(선)과 200회 반복값의 2.5–97.5 백분위 구간(음영)', SRC)
ax = Ax(ML + 54, 150, ML + 480, 390, (2, 8), (0.40, 0.80))
for v in (0.4, 0.5, 0.6, 0.7, 0.8):
    line(c, ax.x0 - 20, ax.Yv(v), ax.x1 + 20, ax.Yv(v), K12, .75)
    text(c, ax.x0 - 28, ax.Yv(v) + 4, f'{v*100:.0f}%', 10.5, 'R', K55, 'r')
for nm, cid, col in [('연속형', 'aik_e1_g0_cont', CONT), ('분절형', 'aik_e1_g0_frag', FRAG)]:
    s = prof[(prof.cell_id == cid) & (prof.boundary_order >= 2)].sort_values('boundary_order')
    up = [(ax.X(b), ax.Yv(v)) for b, v in zip(s.boundary_order, s.AUFR_q975)]
    lo = [(ax.X(b), ax.Yv(v)) for b, v in zip(s.boundary_order, s.AUFR_q025)]
    band(c, up, lo, col, .12)
    pts = [(ax.X(b), ax.Yv(v)) for b, v in zip(s.boundary_order, s.AUFR_mean)]
    polyline(c, pts, col, 2.2)
    for p in pts:
        dot(c, p[0], p[1], 3.5, col)
    last = s.AUFR_mean.iloc[-1]
    text(c, ax.X(8) + 14, ax.Yv(last) + (-2 if nm == '연속형' else 16), f'{nm}  {last*100:.1f}%', 12, 'B', col)
xl = ['U_{2}/U_{1}', 'U_{3}/U_{2}', 'U_{4}/U_{3}', 'U_{5}/U_{4}', 'U_{6}/U_{5}', 'U_{7}/U_{6}', 'U_{8}/U_{7}']
for k, b in enumerate(range(2, 9)):
    text(c, ax.X(b), 412, xl[k], 10.5, 'R', K75, 'c')
text(c, (ax.x0 + ax.x1) / 2, 434, '인접 경계 쌍 (국소 AUFR)', 10.5, 'R', K55, 'c')
nx = 740
fc = shape[shape.circ == 'cont'].iloc[0]; ff = shape[shape.circ == 'frag'].iloc[0]
text(c, nx - 60, 160, '읽는 법', 11, 'B', K55)
yy = wrap(c, nx - 60, 184, '일정한 비율로 줄었다면 선이 수평이어야 한다. 로그 선형 모형 대비 경계 요인 모형의 F 검정은 연속형 F = %s, 분절형 F = %s (p<.001)였다.' % (f'{fc.F:,.0f}', f'{ff.F:,.0f}'), 224, 12, 'R', K75, 1.5)
yy = wrap(c, nx - 60, yy + 12, '국소 AUFR 51.7%는 직전 경계 대비 유지를 뜻하며, 첫 경계 대비 U_{8}/U_{1} = 3.6%와 다른 값이다.', 224, 12, 'B', K100, 1.5)
yy = wrap(c, nx - 60, yy + 12, '음영은 200회 반복값이 퍼진 범위(2.5–97.5 백분위)이며, 평균의 95% 신뢰구간이 아니다.', 224, 11, 'R', K55, 1.5)
d.note('chart', 'local AUFR g0 cont/frag with 2.5–97.5% bands')

# ---------------------------------------------------------------- 12 AUFR vs contrast
c = d.slide('04 층간 상행유량 감소와 프로그램 구성', '인접층 프로그램 차이와 상행유량비',
            '유인 계수별 통계적 관계 · 연속형 · 인접층 앵커 비중 차이 Δx가 0.1 증가할 때 AUFR의 상대 변화(95% 신뢰구간)',
            '출처: 수정 논문 4.2절 · aik_a2_theta.csv (반복 군집-강건 95% CI)')
ax = Ax(ML + 150, 170, ML + 640, 380, (-4, 22), (0, 1))
for v in range(0, 21, 5):
    line(c, ax.X(v), 160, ax.X(v), 392, K12, .75)
    text(c, ax.X(v), 412, f'{v}%', 10.5, 'R', K55, 'c')
line(c, ax.X(0), 160, ax.X(0), 392, K100, 1)
text(c, ax.X(0), 152, '변화 없음 (0%)', 10.5, 'R', K75, 'c')
text(c, (ax.x0 + ax.x1) / 2, 434, 'AUFR 상대 변화 (%) = (승수 − 1) × 100  ·  퍼센트포인트가 아님', 10.5, 'R', K55, 'c')
for i, g in enumerate([0, 2, 4, 8]):
    r = theta[(theta.gamma == g) & (theta.circ == 'cont')].iloc[0]
    yy = 200 + i * 52
    est, lo_, hi_ = (r.rate_ratio - 1) * 100, (r.rr_lo - 1) * 100, (r.rr_hi - 1) * 100
    lab = 'γ = 0 (대조)' if g == 0 else f'γ = {g}'
    text(c, ML, yy + 4, lab, 13, 'B' if g else 'R', K100 if g else K55)
    solid = g > 0
    col = CONT if solid else K55
    line(c, ax.X(lo_), yy, ax.X(hi_), yy, col, 2)
    line(c, ax.X(lo_), yy - 5, ax.X(lo_), yy + 5, col, 1.5); line(c, ax.X(hi_), yy - 5, ax.X(hi_), yy + 5, col, 1.5)
    dot(c, ax.X(est), yy, 5.5, col if solid else Color(1, 1, 1), col, 1.6)
    sg = lambda v, nd=1: ('−' if v < 0 else '+' if v > 0 else '') + f'{abs(v):.{nd}f}'
    nd = 2 if g == 0 else 1
    text(c, ax.X(hi_) + 14, yy + 4, f'{sg(est, nd)}%', 13, 'B', col, halo=True)
    sm = lambda v, nd=1: ('−' if v < 0 else '') + f'{abs(v):.{nd}f}'
    ci = f'95% CI {sm(lo_, nd)} – {sm(hi_, nd)}' + (' · 0 포함' if lo_ < 0 < hi_ else '')
    text(c, ax.X(hi_) + 14, yy + 20, ci, 10, 'R', K55, halo=True)
yb = 462
line(c, ML, yb - 18, W - ML, yb - 18, K12, .75)
text(c, ML, yb + 6, '유인 계수가 클수록 관계가 컸다. 다만 목적지 효용에 γ × x_{j}가 이미 들어 있으므로 모형 구조 안의 반응이며, 외부 실측으로 검증한 효과가 아니다.', 11.5, 'R', K75)
d.note('chart', 'forest-like: +6.0/+10.9/+18.4% with CI, γ0 control')

# ---------------------------------------------------------------- 13 U auxiliary
c = d.slide('04 층간 상행유량 감소와 프로그램 구성', '절대 유량 변동은 위층 비중으로 더 잘 설명됐다',
            '보조 분석 · 절대 상행유량 U의 잔여 deviance 감소율 · AUFR 결과와 다른 통계량이다', SRC)
text(c, ML, 142, '점: γ = 4 연속형  ·  선: 양의 γ 여섯 조건(γ = 2·4·8 × 두 동선)의 최솟값–최댓값 범위이며 신뢰구간이 아니다', 12, 'R', K55)
cs = cons[cons.exp == 'e1']
preds = [('adjacent contrast (Delta)', 'Δx', '인접층 비중 차이'), ('upper-floor program', 'x_{upper}', '바로 위층 비중'),
         ('mean program above boundary', 'M_{b}', '경계 위쪽 평균 비중')]
ax = Ax(ML + 200, 160, ML + 700, 400, (0, 80), (0, 1))
for v in range(0, 81, 20):
    line(c, ax.X(v), 170, ax.X(v), 400, K12, .75)
    text(c, ax.X(v), 420, f'{v}%', 10.5, 'R', K55, 'c')
for i, (key, sym, nm) in enumerate(preds):
    yy = 214 + i * 66
    sub = cs[cs.predictor == key]
    lo_, hi_ = sub.dev_explained.min() * 100, sub.dev_explained.max() * 100
    v4 = sub[(sub.gamma == 4) & (sub.circ == 'cont')].dev_explained.iloc[0] * 100
    text(c, ML, yy + 2, sym, 16, 'B'); text(c, ML, yy + 22, nm, 11, 'R', K55)
    line(c, ax.X(lo_), yy, ax.X(hi_), yy, K55, 2)
    dot(c, ax.X(v4), yy, 7, CONT)
    text(c, ax.X(v4), yy - 14, f'{v4:.1f}%', 13, 'B', CONT, 'c')
    text(c, ax.X(hi_) + 12, yy + 4, f'범위 {lo_:.0f}–{hi_:.0f}%', 10.5, 'R', K55, halo=True)
text(c, (ax.x0 + ax.x1) / 2, 442, '고정효과 후 남은 deviance의 감소율 (변수를 하나씩 추가한 모형)', 10.5, 'R', K55, 'c')
line(c, ML, 458, W - ML, 458, K12, .75)
text(c, ML, 478, '세 비율을 더해 기여율로 읽지 않으며, 특정 앵커 때문에 이동한 보행자 비율이 아니다. 앞 장의 AUFR 상대 변화와 합치지 않는다.', 11.5, 'R', K75)
d.note('chart', 'dev explained γ4 cont: Δx 10.2, x_upper 60.1, M_b 39.7')

# ---------------------------------------------------------------- 14 moderation forest
c = d.slide('05 이동 저항과 앵커 배치에 따른 차이', '이동 저항이 반응을 항상 약화한 것은 아니었다',
            '분절형에서 프로그램 대비에 대한 AUFR 기울기가 감소한 비율(잠식률)과 95% 신뢰구간', '출처: 수정 논문 4.3절 · aik_a3_moderation.csv (2,000회 군집 부트스트랩)')
ax = Ax(ML + 120, 170, ML + 480, 380, (-10, 14), (0, 1))
for v in range(-10, 15, 5):
    line(c, ax.X(v), 160, ax.X(v), 392, K12, .75)
    text(c, ax.X(v), 412, f'{v}%', 10.5, 'R', K55, 'c')
line(c, ax.X(0), 160, ax.X(0), 392, K100, 1.2)
text(c, ax.X(0), 152, '0 = 약화 없음', 10.5, 'R', K75, 'c')
text(c, (ax.x0 + ax.x1) / 2, 434, '기울기 잠식률 (%) = 1 − 분절형 기울기 / 연속형 기울기', 10.5, 'R', K55, 'c')
for i, g in enumerate([2, 4, 8]):
    r = mod[mod.gamma == g].iloc[0]
    est, lo_, hi_ = r.erosion * 100, r.erosion_lo * 100, r.erosion_hi * 100
    yy = 214 + i * 66
    excl = lo_ > 0 or hi_ < 0
    col = FRAG if excl else K55
    text(c, ML, yy + 4, f'γ = {g}', 13, 'B')
    line(c, ax.X(lo_), yy, ax.X(hi_), yy, col, 2.2)
    line(c, ax.X(lo_), yy - 6, ax.X(lo_), yy + 6, col, 1.5); line(c, ax.X(hi_), yy - 6, ax.X(hi_), yy + 6, col, 1.5)
    dot(c, ax.X(est), yy, 6, col if excl else Color(1, 1, 1), col, 1.8)
    sg = lambda v: ('−' if v < 0 else '') + f'{abs(v):.1f}'
    text(c, ax.X(hi_) + 14, yy - 2, f'{est:.1f}%', 14, 'B', col, halo=True)
    text(c, ax.X(hi_) + 14, yy + 15, f'95% CI [{sg(lo_)}, {sg(hi_)}] · 0을 {"제외" if excl else "포함"}', 10.5, 'R', K55, halo=True)
    d.note('forest', f'γ={g} {est:.1f} [{lo_:.1f},{hi_:.1f}]')
nx = 730
yy = wrap(c, nx, 190, 'γ = 2에서만 신뢰구간이 0을 제외했다.', 174, 12, 'B', K100, 1.5)
yy = wrap(c, nx, yy + 10, 'γ = 4·8에서 0을 포함한다는 것은 약화를 명확히 검출하지 못했다는 뜻이다. 두 동선의 반응이 같다는 증명은 아니다.', 174, 11.5, 'R', K75, 1.5)
d.note('chart', 'moderation forest')

# ---------------------------------------------------------------- 15 anchor matrix
c = d.slide('05 이동 저항과 앵커 배치에 따른 차이', '같은 앵커 총량을 네 가지 방식으로 배치했다',
            '층별 앵커 비중 · 2–9층 합계는 모두 약 1.60 · 막대 길이는 모든 열에서 같은 척도(0–0.85)', '출처: 수정 논문 3.2절 · aik_program_circulation.R · E2 배치 입력')
share = {
    'TOP1': {9: .85, **{f: .107143 for f in range(2, 9)}},
    'STEP3': {f: (.45 if f in (3, 6, 9) else .05) for f in range(2, 10)},
    'UNIFORM': {f: .20 for f in range(2, 10)},
    'LOW3': {f: (.45 if f in (2, 3, 4) else .05) for f in range(2, 10)},
}
names = {'TOP1': '최상층 집중', 'STEP3': '3·6·9층 징검다리', 'UNIFORM': '균등 배치', 'LOW3': '2·3·4층 집중'}
gx0, gw = ML + 44, 190
for j, p in enumerate(['TOP1', 'STEP3', 'UNIFORM', 'LOW3']):
    x = gx0 + j * (gw + 10)
    text(c, x, 148, p, 14, 'B', SC[p])
    text(c, x, 165, names[p], 11, 'R', K55)
    for k, fl in enumerate(range(9, 1, -1)):
        yy = 180 + k * 31
        v = share[p][fl]
        rect(c, x, yy, gw - 50, 20, fill=None, stroke=None)
        rect(c, x, yy + 2, (gw - 50) * v / .85, 18, fill=SC[p])
        text(c, x + (gw - 50) * v / .85 + 6, yy + 16, f'{v:.2f}' if v != .107143 else '0.107', 11, 'R', K100)
    line(c, x, 436, x + gw - 30, 436, K100, .75)
    text(c, x, 456, f'2–9층 합계  {sum(share[p].values()):.2f}', 11.5, 'B', K100)
for k, fl in enumerate(range(9, 1, -1)):
    text(c, gx0 - 12, 180 + k * 31 + 16, f'{fl}F', 11.5, 'R', K75, 'r')
text(c, gx0 - 12, 150, '층', 10.5, 'R', K55, 'r')
text(c, ML + 44, 482, '공통: 1층 앵커 비중 0.05 고정 · TOP1의 2–8층 값은 0.107143', 10.5, 'R', K55)
d.note('matrix', 'anchor shares TOP1/STEP3/UNIFORM/LOW3 sums 1.60')

# ---------------------------------------------------------------- 16 placement results
c = d.slide('05 이동 저항과 앵커 배치에 따른 차이', '최상층 집중 배치에서 최상단 상대 유량이 가장 높았다',
            'γ = 4 · 연속형 · RUI_{b} = U_{b} / U_{1}: 첫 경계 대비 상대 유량 (로그축) · 네 시나리오 안의 비교', SRC)
d.inventory[-1] = (d.n, 'subtitle', 'γ=4 연속형 RUI_b = U_b / U_1 첫 경계 대비 상대 유량 로그축')
ax = Ax(ML + 50, 150, ML + 490, 400, (1, 8), (0.01, 1), ylog=True)
for v, lab in [(1, '100%'), (.1, '10%'), (.01, '1%')]:
    line(c, ax.x0 - 10, ax.Yv(v), ax.x1 + 10, ax.Yv(v), K12, .75)
    text(c, ax.x0 - 16, ax.Yv(v) + 4, lab, 10.5, 'R', K55, 'r')
for v in (.5, .2, .05, .02):
    line(c, ax.x0 - 10, ax.Yv(v), ax.x0 - 3, ax.Yv(v), K30, .75)
labs = {}
for p in ['TOP1', 'STEP3', 'UNIFORM', 'LOW3']:
    s = e2[(e2.pattern == p) & (e2.gamma == 4) & (e2.circ == 'cont')].sort_values('boundary_order')
    pts = [(ax.X(b), ax.Yv(v)) for b, v in zip(s.boundary_order, s.RUI_mean)]
    polyline(c, pts, SC[p], 2.4)
    for q in pts:
        dot(c, q[0], q[1], 3, SC[p])
    labs[p] = (pts[-1], s.RUI_mean.iloc[-1])
off = {'TOP1': 4, 'STEP3': 4, 'UNIFORM': 4, 'LOW3': 4}
for p, (pt, v) in labs.items():
    text(c, pt[0] + 12, pt[1] + 4, p, 12, 'B', SC[p])
for b in range(1, 9):
    text(c, ax.X(b), 420, str(b), 11, 'R', K75, 'c')
text(c, (ax.x0 + ax.x1) / 2 + 20, 440, '경계 b  (1 = 1F→2F … 8 = 8F→9F)', 10.5, 'R', K55, 'c')
# table
tx = 672
text(c, tx, 160, '최종 값 · 100회 반복 평균', 11, 'B', K55)
hdr = [('배치', tx), ('T', tx + 98), ('U_{8}', tx + 158), ('R', tx + 226)]
for h, x in hdr:
    text(c, x, 186, h, 11.5, 'B', K75, 'r' if h != '배치' else 'l')
line(c, tx, 194, W - ML, 194, K30, .75)
for i, p in enumerate(['TOP1', 'STEP3', 'UNIFORM', 'LOW3']):
    r = reach[(reach.pattern == p) & (reach.gamma == 4) & (reach.circ == 'cont')].iloc[0]
    u8 = e2[(e2.pattern == p) & (e2.gamma == 4) & (e2.circ == 'cont') & (e2.boundary_order == 8)].U_mean.iloc[0]
    yy = 220 + i * 30
    text(c, tx, yy, p, 12, 'B', SC[p])
    text(c, tx + 98, yy, f'{r.T_mean*100:.1f}%', 12, 'R', K100, 'r')
    text(c, tx + 158, yy, f'{u8:,.0f}', 12, 'R', K100, 'r')
    text(c, tx + 226, yy, f'{r.R_mean*100:.1f}%', 12, 'R', K100, 'r')
    d.note('table', f'{p} T={r.T_mean*100:.1f} U8={u8:,.0f} R={r.R_mean*100:.1f}')
line(c, tx, 336, W - ML, 336, K30, .75)
yy = 358
for t in ['T = U_{8} / U_{1}  (= RUI_{8}, 반복별 비율의 평균)', 'U_{8}: 8F→9F 경계 통과 연인원(명)', 'R: 경계 2–8 RUI의 평균 (반복별 평균)']:
    text(c, tx, yy, t, 10.5, 'R', K75); yy += 18
yy = wrap(c, tx, yy + 12, '네 시나리오 안의 비교이며, 혼잡·수용 한계를 포함한 실제 최적 배치를 뜻하지 않는다. 방문객의 도달 확률이 아니다.', 232, 11, 'B', K100, 1.45)
d.note('chart', 'RUI curves four placements')

# ---------------------------------------------------------------- 17 limits
c = d.slide('06 현재까지의 분석 결과와 향후 검증', '이 결과를 실제 건물에 그대로 적용할 수는 없다',
            '모형이 다루지 않은 범위와, 그에 대응하는 향후 검증 과제', '출처: 수정 논문 3–5장')
text(c, ML, 150, '해석의 한계', 12, 'B', K55)
text(c, ML + 470, 150, '향후 검증 과제', 12, 'B', K55)
lim = [
    ('비공간적 합성 모형', '실제 평면·시야·동선 네트워크를 직접 재현하지 않았다', '실제 평면의 기하학적 수직동선을 반영한 모형'),
    ('혼잡과 수용량 부재', '상행유량이 커져도 병목·대기·안전·운영 부담은 계산하지 않았다', '혼잡·대기·수용량을 포함한 모델링'),
    ('가정한 유인 계수와 범위', 'γ는 가정한 민감도 값이며, TOP1의 9층 0.85는 E1 층별 상한 0.5 밖이다', '업종별 집객력 보정과 더 넓은 배치 범위의 재실험'),
    ('결과 변수의 범위', 'U는 경계 통과 연인원이며 고유 방문객·체류·소비가 아니다', '실제 시설의 관측 유량으로 규칙을 보정·외부 검증'),
]
for i, (t, s, f) in enumerate(lim):
    y0 = 166 + i * 76
    line(c, ML, y0, W - ML, y0, K12, .75)
    text(c, ML, y0 + 34, f'{i+1}', 22, 'R', K30)
    text(c, ML + 36, y0 + 28, t, 14, 'B')
    assert tw(s, 11.5) <= 376, s
    text(c, ML + 36, y0 + 50, s, 11.5, 'R', K75)
    # limitation -> follow-up connector, aligned with the task text's x-height
    line(c, ML + 424, y0 + 27, ML + 452, y0 + 27, K55, .9)
    c.setFillColor(K55); pth = c.beginPath(); pth.moveTo(ML + 456, Y(y0 + 27)); pth.lineTo(ML + 450, Y(y0 + 24)); pth.lineTo(ML + 450, Y(y0 + 30)); pth.close(); c.drawPath(pth, stroke=0, fill=1)
    wrap(c, ML + 470, y0 + 32, f, 330, 13, 'R', K100, 1.4)
    d.note('limit', f'{t} → {f}')
line(c, ML, 166 + 4 * 76, W - ML, 166 + 4 * 76, K12, .75)

# ---------------------------------------------------------------- 18 summary
c = d.slide('06 현재까지의 분석 결과와 향후 검증', '현재까지의 분석 결과와 향후 과제',
            '모형 안에서 확인된 결과와, 앞으로 검증할 내용을 구분해 정리한다', '출처: 수정 논문 4–5장 · 분석 CSV')
text(c, ML, 146, '현재까지 확인한 것 (모형 안의 결과)', 12, 'B', K55)
res = [
    ('절대 유량과 국소 AUFR는 다른 정보를 준다', '추가 앵커 유인이 없는 연속형(γ=0)에서 U_{8}/U_{1}은 3.6%, 마지막 국소 AUFR는 51.7%였다.'),
    ('프로그램 차이와 AUFR의 관계는 유인 계수가 클수록 컸다', 'Δx 0.1 증가당 AUFR 상대 변화는 γ=2·4·8에서 약 +6.0·+10.9·+18.4%였다.'),
    ('이동 저항의 약화 효과는 조건마다 달랐다', '기울기 잠식률은 γ=2에서만 95% CI가 0을 제외했다 (6.7%).'),
    ('네 배치 중 TOP1이 최상단 상대 유량에 가장 유리했다', 'γ=4 연속형에서 T = 58.7%, U_{8} 평균 약 9,112명 — 보편적 최적안이 아니다.'),
]
for i, (t, s) in enumerate(res):
    y0 = 160 + i * 52
    line(c, ML, y0, ML + 520, y0, K12, .75)
    text(c, ML, y0 + 32, f'{i+1}', 18, 'R', K30)
    text(c, ML + 30, y0 + 22, t, 12.5, 'B')
    text(c, ML + 30, y0 + 40, s, 11, 'R', K75)
    d.note('result', t)
line(c, ML, 160 + 4 * 52, ML + 520, 160 + 4 * 52, K12, .75)
text(c, ML + 580, 146, '앞으로 검증할 것', 12, 'B', K55)
fut = [('실측 검증', '실제 시설의 관측 유량으로 규칙을 보정하고 외부 검증'),
       ('기하학적 수직동선', '실제 평면과 계단·에스컬레이터 배치를 반영'),
       ('혼잡 모델링', '병목·대기·수용량을 포함한 배치 재평가')]
for i, (t, s) in enumerate(fut):
    y0 = 160 + i * 70
    line(c, ML + 580, y0, W - ML, y0, K12, .75)
    text(c, ML + 580, y0 + 26, t, 14, 'B')
    wrap(c, ML + 580, y0 + 46, s, 250, 11.5, 'R', K75, 1.4)
line(c, ML + 580, 160 + 3 * 70, W - ML, 160 + 3 * 70, K12, .75)
text(c, ML, 410, '기여', 11, 'B', K55)
wrap(c, ML, 430, '층간 경계 지표와 프로그램 요약변수를 분리하고, 유인 강도·이동 저항·배치를 같은 실험 틀에서 비교했다.', 520, 12.5, 'R', K100, 1.45)

d.save()
with open(Path(OUT).with_name('title_inventory.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['slide', 'kind', 'text']); w.writerows(d.inventory)
print('built', d.n)
