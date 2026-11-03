"""발표 시각화 기획안 3판: 데이터 우선 원칙, 슬라이드별 설계표, 실데이터 SVG 시안(5번 후보 2개 + 6번 산점도)."""
import base64
import collections
import csv
import io
import os

AIK = r"D:\vcpf\repo\analysis\outputs\sim\aik"
OUT = r"D:\Temp\claude\D--Users-admin-Desktop-2-----\5d671f74-c77a-47c0-9dc7-d57885767bf7\scratchpad\plan3_artifact.html"
LOCAL = r"D:\Users\admin\Desktop\2학기 논문\발표자료\01_과정\기획안_03_시각화_기획.html"
BUTTERFLY = r"D:\Users\admin\Desktop\2학기 논문\발표자료\01_과정\slide_05\slide_05.png"

# ---------- 데이터 ----------
rep = list(csv.DictReader(open(os.path.join(AIK, "aik_boundary_rep.csv"), encoding="utf-8-sig")))
M = {}
for circ in ("cont", "frag"):
    acc = collections.defaultdict(collections.Counter)
    n = collections.Counter()
    for r in rep:
        if r["cell_id"] == f"aik_e1_g0_{circ}":
            b = int(r["boundary_order"])
            for k in ("U", "U_esc", "U_stairs", "U_elev"):
                acc[b][k] += float(r[k])
            n[b] += 1
    M[circ] = {b: {k: v / n[b] for k, v in acc[b].items()} for b in acc}
B = list(range(1, 9))
FIRST_ELEV = next(b for b in B if M["cont"][b]["U_elev"] > M["cont"][b]["U_esc"])

CE, CS, CL = "#f0701e", "#16a085", "#7b4fd1"      # 에스컬레이터, 계단, 엘리베이터
NAVY, BROWN = "#1d4e80", "#b0602e"


def fmt(v):
    return f"{v:,.0f}"


# ---------- 시안 D1: 흐름 탑 (연속형, 수단별 폭) ----------
def tower():
    W, Hh = 900, 600
    cx, rh, top, bh = 450, 58, 64, 44
    sc = 440 / M["cont"][1]["U"]
    s = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="경계마다 상향 인원을 수단별 폭으로 쌓아 올린 탑">']
    prev = None
    rows = {}
    for b in B:
        y = top + (8 - b) * rh
        m = M["cont"][b]
        tw = m["U"] * sc
        x = cx - tw / 2
        segs = []
        for key, c in (("U_esc", CE), ("U_stairs", CS), ("U_elev", CL)):
            w = m[key] * sc
            segs.append((x, x + w, c))
            x += w
        rows[b] = (y, segs, m)
    for b in B[:-1]:                                   # 연결 사다리꼴(아래 b -> 위 b+1)
        y0, segs0, _ = rows[b]
        y1, segs1, _ = rows[b + 1]
        for (a0, a1, c), (c0, c1, _) in zip(segs0, segs1):
            s.append(f'<polygon points="{a0:.1f},{y0:.1f} {a1:.1f},{y0:.1f} {c1:.1f},{y1+bh:.1f} {c0:.1f},{y1+bh:.1f}" fill="{c}" opacity=".22"/>')
    for b in B:
        y, segs, m = rows[b]
        for (a0, a1, c) in segs:
            s.append(f'<rect x="{a0:.1f}" y="{y}" width="{max(a1-a0, 0.6):.1f}" height="{bh}" fill="{c}"/>')
        s.append(f'<text x="{cx-250}" y="{y+bh/2+6}" text-anchor="end" class="fl">{b}→{b+1}층</text>')
        ex = cx + m["U"] * sc / 2 + 14
        s.append(f'<text x="{ex:.1f}" y="{y+bh/2+7}" class="val">{fmt(m["U"])}</text>')
    yb, _, _ = rows[FIRST_ELEV]
    s.append(f'<line x1="{cx-215}" x2="{cx+215}" y1="{yb-6}" y2="{yb-6}" stroke="#14202b" stroke-dasharray="4 4" stroke-width="1.4"/>')
    s.append(f'<text x="{cx+125}" y="{yb-12}" class="tag">{FIRST_ELEV}→{FIRST_ELEV+1}층부터 엘리베이터가 더 많음</text>')
    s.append('<text x="14" y="590" class="src">폭 = 경계별 4일 모의 평균 상향 인원(선형 눈금), 색 = 수단 · γ=0 연속형 · 200회 반복 평균</text>')
    s.append('</svg>')
    return "".join(s)


# ---------- 시안 D3: 마주 보는 흐름 탑 (연속형 / 분절형) ----------
def mirrored():
    W, Hh = 900, 600
    cx, gap, rh, top, bh = 450, 56, 58, 70, 44
    sc = 330 / M["cont"][1]["U"]
    s = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="연속형과 분절형의 경계별 상향 인원을 수단별로 쌓아 마주 보게 놓은 그래프">']
    s.append(f'<text x="{cx-gap-6}" y="40" text-anchor="end" class="h" fill="{NAVY}">연속형 동선</text>')
    s.append(f'<text x="{cx+gap+6}" y="40" class="h" fill="{BROWN}">분절형 동선</text>')
    for side, circ, sign in (("L", "cont", -1), ("R", "frag", 1)):
        rows = {}
        for b in B:
            y = top + (8 - b) * rh
            m = M[circ][b]
            off = 0.0
            segs = []
            for key, c in (("U_esc", CE), ("U_stairs", CS), ("U_elev", CL)):
                w = m[key] * sc
                a0 = cx + sign * gap + sign * off
                a1 = a0 + sign * w
                segs.append((min(a0, a1), max(a0, a1), c))
                off += w
            rows[b] = (y, segs, m, off)
        for b in B[:-1]:
            y0, s0, _, _ = rows[b]
            y1, s1, _, _ = rows[b + 1]
            for (a0, a1, c), (c0, c1, _) in zip(s0, s1):
                s.append(f'<polygon points="{a0:.1f},{y0:.1f} {a1:.1f},{y0:.1f} {c1:.1f},{y1+bh:.1f} {c0:.1f},{y1+bh:.1f}" fill="{c}" opacity=".2"/>')
        for b in B:
            y, segs, m, off = rows[b]
            for (a0, a1, c) in segs:
                s.append(f'<rect x="{a0:.1f}" y="{y}" width="{max(a1-a0, 0.6):.1f}" height="{bh}" fill="{c}"/>')
            ex = cx + sign * (gap + off + 10)
            s.append(f'<text x="{ex:.1f}" y="{y+bh/2+7}" text-anchor="{"end" if sign<0 else "start"}" class="val" fill="{NAVY if sign<0 else BROWN}">{fmt(m["U"])}</text>')
    for b in B:
        y = top + (8 - b) * rh
        s.append(f'<text x="{cx}" y="{y+bh/2+6}" text-anchor="middle" class="fl">{b}→{b+1}층</text>')
    yb = top + (8 - FIRST_ELEV) * rh
    s.append(f'<line x1="40" x2="860" y1="{yb-7}" y2="{yb-7}" stroke="#14202b" stroke-dasharray="4 4" stroke-width="1.4"/>')
    s.append(f'<text x="860" y="{yb-11}" text-anchor="end" class="tag">{FIRST_ELEV}→{FIRST_ELEV+1}층부터 엘리베이터 우세</text>')
    s.append(f'<text x="{cx}" y="{top+8*rh+26}" text-anchor="middle" class="tag">분절형은 첫 경계부터 -20.6%</text>')
    s.append('<text x="14" y="590" class="src">폭 = 경계별 4일 모의 평균 상향 인원(선형 눈금), 색 = 수단(주황 에스컬레이터, 청록 계단, 보라 엘리베이터) · γ=0 · 200회 반복 평균</text>')
    s.append('</svg>')
    return "".join(s)


# ---------- 6번 산점도 시안: 같은 y, 다른 x ----------
def scatter():
    import math
    rows = [r for r in rep if r["cell_id"] == "aik_e1_g4_cont" and float(r["U"]) > 0]
    ylog = [math.log(float(r["U"])) for r in rows]
    bk = [r["boundary_order"] for r in rows]
    rk = [r["rep_id"] for r in rows]
    xs = [float(r["x_upper"]) for r in rows]
    ds = [float(r["delta"]) for r in rows]

    def demean(v):                      # 경계와 반복의 평균을 번갈아 빼서 고정효과를 제거
        v = v[:]
        for _ in range(30):
            for key in (bk, rk):
                s, n = collections.defaultdict(float), collections.Counter()
                for k, x in zip(key, v):
                    s[k] += x
                    n[k] += 1
                v = [x - s[k] / n[k] for k, x in zip(key, v)]
        return v
    Y, XU, DL = demean(ylog), demean(xs), demean(ds)
    ys = [math.exp(v) for v in Y]
    dev = {}
    for r in csv.DictReader(open(os.path.join(AIK, "aik_a2b_constructs.csv"), encoding="utf-8-sig")):
        if r["cell_id"] == "aik_e1_g4_cont":
            dev[r["predictor"]] = float(r["dev_explained"])
    W, Hh = 900, 400
    pw, ph = 380, 270
    ylo, yhi = 0.55, 1.75
    s = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="같은 세로축에 대해 가로축만 바꾼 산점도 두 개">']

    def panel(ox, xraw, xdm, xmin, xmax, title, d, color, xt):
        out = [f'<text x="{ox}" y="30" class="h2">{title}</text>',
               f'<text x="{ox+pw}" y="30" text-anchor="end" class="val" fill="{color}">설명 비중 {d*100:.0f}%</text>']
        sx = lambda v: ox + (v - xmin) / (xmax - xmin) * pw
        sy = lambda v: 60 + ph - (v - ylo) / (yhi - ylo) * ph
        out.append(f'<line x1="{ox}" x2="{ox+pw}" y1="{60+ph}" y2="{60+ph}" stroke="#14202b" stroke-width="1.2"/>')
        out.append(f'<line x1="{ox}" x2="{ox}" y1="60" y2="{60+ph}" stroke="#14202b" stroke-width="1.2"/>')
        for tv in (0.6, 0.8, 1.0, 1.2, 1.4, 1.6):
            out.append(f'<line x1="{ox}" x2="{ox+pw}" y1="{sy(tv):.1f}" y2="{sy(tv):.1f}" stroke="{"#9aa5ae" if tv == 1.0 else "#e3e7ea"}"/>')
            if ox < 100:
                out.append(f'<text x="{ox-8}" y="{sy(tv)+5:.1f}" text-anchor="end" class="mut">{tv:.1f}</text>')
        for xv, yv in zip(xraw, ys):
            out.append(f'<circle cx="{sx(xv):.1f}" cy="{sy(yv):.1f}" r="2.1" fill="{color}" opacity=".25"/>')
        b1 = sum(x * yv for x, yv in zip(xdm, Y)) / sum(x * x for x in xdm)
        mx = sum(xraw) / len(xraw)
        x0, x1 = xmin, xmax
        out.append(f'<line x1="{sx(x0):.1f}" x2="{sx(x1):.1f}" y1="{sy(math.exp(b1*(x0-mx))):.1f}" y2="{sy(math.exp(b1*(x1-mx))):.1f}" stroke="#14202b" stroke-width="3"/>')
        out.append(f'<text x="{ox+pw/2}" y="{60+ph+34}" text-anchor="middle" class="mut">{xt}</text>')
        return "".join(out)

    s.append(panel(60, xs, XU, 0.0, 0.5, "바로 위층의 앵커 비중", dev["upper-floor program"], NAVY, "위층 앵커 비중 (0~0.5)"))
    s.append(panel(500, ds, DL, -0.5, 0.5, "인접층 격차 (위 - 아래)", dev["adjacent contrast (Delta)"], BROWN, "인접층 앵커 비중 차이 (-0.5~0.5)"))
    s.append(f'<text x="14" y="388" class="src">점 1개 = 한 경계의 한 반복({len(rows):,}개), 세로축 = 같은 경계·같은 반복의 평균 대비 상향 인원(배) · γ=4 연속형 · 선 = 고정효과를 뺀 직선 맞춤</text>')
    s.append('</svg>')
    return "".join(s)


D1, D3, SC = tower(), mirrored(), scatter()
img = ""
try:
    from PIL import Image
    im = Image.open(BUTTERFLY).convert("RGB")
    im.thumbnail((1200, 675))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    img = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
except Exception as e:
    print("no butterfly image", e)

html = f'''<title>시각화 기획안</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>
/* 레이아웃: 한 칼럼 문서. 진단, 원칙, 슬라이드별 설계표, 시안(실데이터 SVG), 판단 요청. */
:root {{
  --bg:#f5f7f8; --surface:#ffffff; --fg:#14202b; --muted:#5a6a77; --line:#d7dee3; --accent:#1f5fbf; --accent-soft:#e4edf9;
  --warn:#8a5a00; --warn-soft:#fbf1dc; --font:"Noto Sans KR","Malgun Gothic","Apple SD Gothic Neo",sans-serif;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#0f171e; --surface:#17222b; --fg:#e5ebf0; --muted:#9fb0bd; --line:#2b3a46; --accent:#7fb0f5; --accent-soft:#1c2f45;
  --warn:#e6bd6a; --warn-soft:#32280f; color-scheme:dark; }} }}
:root[data-theme="dark"] {{
  --bg:#0f171e; --surface:#17222b; --fg:#e5ebf0; --muted:#9fb0bd; --line:#2b3a46; --accent:#7fb0f5; --accent-soft:#1c2f45;
  --warn:#e6bd6a; --warn-soft:#32280f; color-scheme:dark; }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--font); font-size:16px; line-height:1.7; padding-block:28px 64px;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); }}
main {{ max-width:880px; margin:0 auto; display:flex; flex-direction:column; gap:40px; }}
h1 {{ font-size:1.5rem; line-height:1.35; margin:0; text-wrap:balance; }}
h2 {{ font-size:1.15rem; margin:0 0 10px; text-wrap:balance; }}
p {{ margin:0; }}
.meta {{ color:var(--muted); font-size:.9rem; }}
.box {{ background:var(--surface); border:1px solid var(--line); border-radius:6px; padding:16px 18px; }}
.box.warn {{ background:var(--warn-soft); border-color:transparent; }}
.box.warn h2 {{ color:var(--warn); }}
ul.plain {{ margin:0; padding-left:1.2em; display:flex; flex-direction:column; gap:6px; }}
.concept {{ display:flex; flex-direction:column; gap:12px; }}
.tag {{ font-size:.8rem; color:var(--muted); }}
.claim {{ font-weight:700; font-size:1.05rem; line-height:1.5; text-wrap:balance; }}
.stage {{ background:#fff; border:1px solid var(--line); border-radius:6px; padding:12px; overflow-x:auto; }}
.stage svg, .stage img {{ display:block; width:100%; min-width:560px; height:auto; }}
dl {{ margin:0; display:grid; grid-template-columns:5.4em minmax(0,1fr); gap:4px 10px; font-size:.93rem; }}
dt {{ color:var(--muted); }} dd {{ margin:0; }}
code {{ font-family:ui-monospace,Consolas,monospace; font-size:.82rem; background:var(--accent-soft); padding:1px 5px; border-radius:3px; overflow-wrap:anywhere; }}
table {{ border-collapse:collapse; width:100%; font-size:.88rem; }}
th,td {{ text-align:left; padding:8px 10px 8px 0; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:500; white-space:nowrap; }}
.scroll {{ overflow-x:auto; }}
svg text {{ font-family:"Noto Sans KR","Malgun Gothic",sans-serif; fill:#14202b; }}
svg .h {{ font-size:19px; font-weight:800; }} svg .h2 {{ font-size:16px; font-weight:700; }}
svg .fl {{ font-size:14px; font-weight:700; }} svg .val {{ font-size:15px; font-weight:800; }}
svg .mut {{ font-size:12.5px; fill:#5a6a77; }} svg .tag {{ font-size:12.5px; font-weight:700; }}
svg .src {{ font-size:11.5px; fill:#5a6a77; }}
</style>
<main>
  <header>
    <h1>시각화 기획안</h1>
    <p class="meta">앞서 만든 단면 렌더 슬라이드는 폐기합니다 · 실제 시뮬레이션 CSV로 그린 시안으로 방향을 고릅니다</p>
  </header>

  <section class="box warn" aria-labelledby="dx">
    <h2 id="dx">무엇이 잘못됐나</h2>
    <ul class="plain">
      <li><strong>그림이 주인공이었습니다.</strong> 3D 렌더가 화면 대부분을 차지하고, 데이터는 가장자리의 작은 숫자였습니다. 보는 사람이 그림에서 읽을 값이 없었습니다.</li>
      <li><strong>생성형 느낌의 원인:</strong> 질감 있는 렌더, 장식용 인물, 부드러운 조명, 데이터와 무관한 가구. 모두 "그럴듯해 보이는 것"이지 연구 결과가 아닙니다.</li>
      <li><strong>고칠 방향:</strong> 건축은 렌더가 아니라 <em>도면의 언어</em>(단면, 층 축)로 쓰고, 모든 면적이 데이터를 담게 합니다.</li>
    </ul>
  </section>

  <section class="box" aria-labelledby="pr">
    <h2 id="pr">원칙 6개</h2>
    <ul class="plain">
      <li><strong>한 장에 한 질문.</strong> 슬라이드 제목이 질문이고, 그림이 그 답입니다.</li>
      <li><strong>그림 면적의 대부분이 데이터.</strong> 장식, 배경, 질감은 쓰지 않습니다.</li>
      <li><strong>3초 안에 읽혀야 합니다.</strong> 그림 안에 결과 문장 하나와 큰 숫자 하나를 직접 적습니다.</li>
      <li><strong>건축은 층 축으로.</strong> 세로축을 건물의 층으로 맞춰 모든 그래프가 같은 단면 위에 놓이게 합니다. 렌더는 표지 한 장에만 씁니다.</li>
      <li><strong>색의 뜻을 고정합니다.</strong> 연속형 남색, 분절형 갈색, 수단 3색(주황 에스컬레이터, 청록 계단, 보라 엘리베이터), 강조 하나.</li>
      <li><strong>CSV에서 읽은 값만.</strong> 연출한 요소는 넣지 않습니다. 필요하면 「연출」이라고 표시합니다.</li>
    </ul>
  </section>

  <section aria-labelledby="tb">
    <h2 id="tb">슬라이드별 설계 (질문, 데이터, 그림 형태)</h2>
    <div class="scroll">
      <table>
        <tr><th>장</th><th>질문</th><th>그림 (모두 실데이터)</th><th>3초 읽기</th></tr>
        <tr><td>1 표지</td><td>-</td><td>설계 건물 렌더(유일한 렌더)</td><td>건축 설계 수업의 발표</td></tr>
        <tr><td>2 서론</td><td>위층은 왜 비는가</td><td>층 축을 따라 줄어드는 인원 막대 하나(100 → 3.6)</td><td>맨 위에는 3.6%</td></tr>
        <tr><td>3 이론</td><td>구조와 유인을 어떻게 가르나</td><td>γ=0 대 γ=4 감소선 2개(<code>aik_e2_profile.csv</code>)</td><td>같은 건물, 유인만 얹으면 선이 올라간다</td></tr>
        <tr><td>4 방법</td><td>무엇을 바꿨나</td><td>앵커 배치 4종의 층별 막대 4개 + 실험 격자 표</td><td>총량 같음, 위치만 다름</td></tr>
        <tr><td><strong>5 기준선</strong></td><td>구조만의 몫은</td><td><strong>아래 시안 D1, D2, D3 중 선택</strong></td><td>줄어든다, 수단이 바뀐다</td></tr>
        <tr><td><strong>6 위층 앵커</strong></td><td>무엇이 올리나</td><td><strong>같은 세로축의 산점도 2개(1,600점)</strong>: 위층 앵커 대 인접층 격차</td><td>왼쪽은 기울고, 오른쪽은 평평하다</td></tr>
        <tr><td>7 동선 마찰</td><td>서로 깎는가</td><td>γ별 잠식률 + 신뢰구간 점 그래프, 연속형과 분절형 기울기 겹쳐 그림</td><td>두 선이 거의 포개진다</td></tr>
        <tr><td>8 배치</td><td>어디에 두나</td><td>배치 4종 행: 층별 앵커 막대(왼쪽) + 층별 감소선(가운데) + 최상층 도달(오른쪽)</td><td>저층에 몰면 위가 끊긴다</td></tr>
        <tr><td>9 결론</td><td>이론은 어디까지</td><td>γ에 따른 1번 경계 인원과 8번 경계 인원, 연속형과 분절형</td><td>구조는 간격, 프로그램은 기울기</td></tr>
      </table>
    </div>
  </section>

  <section class="concept" aria-labelledby="c5">
    <p class="tag">5번 슬라이드 시안</p>
    <h2 id="c5">구조만의 몫: 세 가지 형태</h2>
  </section>

  <section class="concept" aria-labelledby="d1">
    <p class="tag">D1</p>
    <h2 id="d1">흐름 탑 (연속형 하나)</h2>
    <p class="claim">경계를 오를 때마다 흐름의 폭이 줄고, {FIRST_ELEV}→{FIRST_ELEV+1}층부터 주력 수단이 바뀐다.</p>
    <div class="stage">{D1}</div>
    <dl>
      <dt>데이터</dt><dd>경계 8개의 평균 인원을 수단별로 나눈 값. 폭이 곧 인원입니다.</dd>
      <dt>장점</dt><dd>탑 모양이 건물 단면처럼 읽히고, 줄어드는 정도와 수단 전환이 한 그림에 있습니다.</dd>
      <dt>단점</dt><dd>분절형과의 비교(-20.6%)가 없습니다.</dd>
    </dl>
  </section>

  <section class="concept" aria-labelledby="d2">
    <p class="tag">D2</p>
    <h2 id="d2">나비 차트 (앞서 만든 것)</h2>
    <p class="claim">연속형과 분절형의 감소를 한 번에 비교하고, 반복의 변동 범위까지 보인다.</p>
    <div class="stage"><img src="{img}" alt="앞서 만든 나비 차트 슬라이드"></div>
    <dl>
      <dt>데이터</dt><dd>평균 인원, 1층 대비 %, 직전 대비 감소, 200회 반복 범위, 로그 직선 검정.</dd>
      <dt>장점</dt><dd>분석 정보가 가장 많고 이미 완성되어 있습니다.</dd>
      <dt>단점</dt><dd>수단 구성이 없고, 숫자 중심이라 건축 단면의 느낌이 약합니다.</dd>
    </dl>
  </section>

  <section class="concept" aria-labelledby="d3">
    <p class="tag">D3</p>
    <h2 id="d3">마주 보는 흐름 탑 (연속형 / 분절형)</h2>
    <p class="claim">두 동선 모두 위로 갈수록 줄고, 분절형은 처음부터 20.6% 적다. 수단 전환은 두 동선에서 똑같다.</p>
    <div class="stage">{D3}</div>
    <dl>
      <dt>데이터</dt><dd>D1에 분절형을 더한 것. 두 쪽 모두 폭이 인원이고 색이 수단입니다.</dd>
      <dt>장점</dt><dd>나비 차트의 비교와 D1의 수단 전환을 합쳤습니다. 건축 단면의 언어를 유지합니다.</dd>
      <dt>단점</dt><dd>200회 반복 변동 범위와 로그 직선 검정은 따로 한 줄로 넣어야 합니다.</dd>
    </dl>
  </section>

  <section class="concept" aria-labelledby="s6">
    <p class="tag">6번 슬라이드 시안</p>
    <h2 id="s6">같은 세로축, 다른 가로축</h2>
    <p class="claim">사람을 위로 올리는 것은 층 사이 격차가 아니라 바로 위층의 앵커다.</p>
    <div class="stage">{SC}</div>
    <dl>
      <dt>데이터</dt><dd><code>aik_boundary_rep.csv</code>의 1,600개 점(γ=4 연속형). 세로축은 논문의 설명 비중과 같은 양(경계와 반복의 영향을 뺀 상향 인원)이고, 설명 비중은 <code>aik_a2b_constructs.csv</code> 값입니다.</dd>
      <dt>보이는 것</dt><dd>왼쪽은 점이 가파르게 올라가고 오른쪽은 완만하게 퍼집니다. 같은 세로축이라 기울기 차이가 그대로 보입니다.</dd>
    </dl>
  </section>

  <section class="box" aria-labelledby="rec">
    <h2 id="rec">추천</h2>
    <ul class="plain">
      <li><strong>5번은 D3</strong>입니다. 건축 단면의 언어로 데이터를 그대로 보이고, 두 동선과 수단 전환을 한 장에 담습니다. D2의 반복 범위와 로그 직선 검정은 아래 한 줄로 붙이거나 백업으로 둡니다.</li>
      <li><strong>시뮬레이션 장면(사람이 돌아다니는 그림)은 본편에서 뺍니다.</strong> 이 모델에는 층 평면이 없어 연출이 되고, 연출은 데이터를 가립니다. 꼭 필요하면 방법 장에 실제 GAMA 출력 한 컷을 작은 삽화로만 쓰겠습니다.</li>
      <li>6번부터는 모두 같은 틀(세로축 = 층, 색 의미 고정)로 데이터 그림을 먼저 만들어 한 장씩 승인받겠습니다.</li>
    </ul>
  </section>

  <section class="box warn" aria-labelledby="ask">
    <h2 id="ask">정해 주실 것</h2>
    <ul class="plain">
      <li>5번 슬라이드: D1, D2, D3 중 무엇으로 할지</li>
      <li>6번 산점도 방향이 맞는지</li>
      <li>시뮬레이션 장면을 본편에서 완전히 빼도 되는지, 방법 장에 작게만 둘지</li>
    </ul>
  </section>
</main>
'''
open(OUT, "w", encoding="utf-8").write(html)
i = html.index("</style>") + len("</style>")
open(LOCAL, "w", encoding="utf-8").write('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n' + html[:i] + '\n</head><body>' + html[i:] + '</body></html>\n')
print("ok", len(html), "FIRST_ELEV", FIRST_ELEV, "img", bool(img))
