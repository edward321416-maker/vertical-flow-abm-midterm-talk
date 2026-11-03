"""연결 분석 기획안: 층 줄을 가로질러 프로그램 -> 유량(수단별) -> 도달을 잇는 시트. E2 배치 4종 실데이터 시안 포함."""
import collections
import csv
import os

AIK = r"D:\vcpf\repo\analysis\outputs\sim\aik"
OUT = r"D:\Temp\claude\D--Users-admin-Desktop-2-----\5d671f74-c77a-47c0-9dc7-d57885767bf7\scratchpad\plan4_artifact.html"
LOCAL = r"D:\Users\admin\Desktop\2학기 논문\발표자료\01_과정\기획안_04_연결분석.html"

rep = list(csv.DictReader(open(os.path.join(AIK, "aik_boundary_rep.csv"), encoding="utf-8-sig")))
LAYOUTS = [("aik_e2_top1_g4_cont", "최상층 집중"), ("aik_e2_low3_g4_cont", "저층 집중"),
           ("aik_e2_uniform_g4_cont", "균등 분산"), ("aik_e2_step3_g4_cont", "징검다리형")]
D = {}
for cid, _ in LAYOUTS:
    xs, acc, n = collections.defaultdict(list), collections.defaultdict(collections.Counter), collections.Counter()
    for r in rep:
        if r["cell_id"] != cid:
            continue
        b = int(r["boundary_order"])
        xs[b].append(float(r["x_upper"]))
        if b == 1:
            xs[0].append(float(r["x_lower"]))
        for k in ("U", "U_esc", "U_stairs", "U_elev"):
            acc[b][k] += float(r[k])
        n[b] += 1
    D[cid] = {"x": [sum(xs[f]) / len(xs[f]) for f in range(9)],
              "U": {b: {k: v / n[b] for k, v in acc[b].items()} for b in range(1, 9)}}
UMAX = max(D[c]["U"][b]["U"] for c, _ in LAYOUTS for b in range(1, 9))

CE, CS, CL = "#f0701e", "#16a085", "#7b4fd1"
INK, MUT, RULE, BAND = "#14202b", "#5a6a77", "#e3e7ea", "#fff3d6"


def fmt(v):
    return f"{v:,.0f}"


def sheet():
    PW, GAP, X0 = 205, 14, 46
    rh, top = 52, 86
    W, H = 900, top + 9 * rh + 46
    sc = 44 / UMAX
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="배치 4종에서 층별 프로그램과 그 층으로 올라오는 유량을 같은 줄에 놓은 연결 시트">']
    yrow = lambda f: top + (8 - f) * rh
    for f in range(9):                                   # 층 줄: 모든 패널을 가로지르는 점선
        y = yrow(f)
        s.append(f'<line x1="{X0-4}" x2="{W-6}" y1="{y+rh/2}" y2="{y+rh/2}" stroke="{RULE}" stroke-dasharray="2 4"/>')
        s.append(f'<text x="{X0-10}" y="{y+rh/2+5}" text-anchor="end" class="fl">{f+1}층</text>')
    for i, (cid, name) in enumerate(LAYOUTS):
        px = X0 + i * (PW + GAP)
        d = D[cid]
        U1, U8 = d["U"][1]["U"], d["U"][8]["U"]
        s.append(f'<text x="{px}" y="30" class="h2">{name}</text>')
        s.append(f'<text x="{px}" y="54" class="mut">최상층 도달 <tspan class="val" fill="{INK}">{U8/U1*100:.1f}%</tspan> · {fmt(U8)}명</text>')
        axis = px + 124
        for f in range(9):                               # 앵커 층 띠
            if d["x"][f] >= 0.30:
                s.append(f'<rect x="{px-2}" y="{yrow(f)+2}" width="{PW}" height="{rh-4}" fill="{BAND}" rx="3"/>')
        for f in range(9):                               # 프로그램 막대(앵커 비중)
            w = d["x"][f] / 0.85 * 52
            s.append(f'<rect x="{px}" y="{yrow(f)+rh/2-7}" width="{max(w,1.5):.1f}" height="14" fill="{INK}"/>')
            if d["x"][f] >= 0.30:
                s.append(f'<text x="{px+w+5:.1f}" y="{yrow(f)+rh/2+4}" class="mut">{d["x"][f]:.2f}</text>')
        rows = {}
        for b in range(1, 9):                            # 유량 탑: 경계 b 는 도착 층 b 의 줄에 놓는다
            y = yrow(b)
            m = d["U"][b]
            tw = m["U"] * sc
            x = axis - tw / 2
            segs = []
            for key, c in (("U_esc", CE), ("U_stairs", CS), ("U_elev", CL)):
                w = m[key] * sc
                segs.append((x, x + w, c))
                x += w
            rows[b] = (y, segs, m, tw)
        for b in range(1, 8):
            y0, s0, _, _ = rows[b]
            y1, s1, _, _ = rows[b + 1]
            for (a0, a1, c), (c0, c1, _) in zip(s0, s1):
                s.append(f'<polygon points="{a0:.1f},{y0+rh/2-12:.1f} {a1:.1f},{y0+rh/2-12:.1f} {c1:.1f},{y1+rh/2+12:.1f} {c0:.1f},{y1+rh/2+12:.1f}" fill="{c}" opacity=".2"/>')
        for b in range(1, 9):
            y, segs, m, tw = rows[b]
            for (a0, a1, c) in segs:
                s.append(f'<rect x="{a0:.1f}" y="{y+rh/2-12}" width="{max(a1-a0,0.6):.1f}" height="24" fill="{c}"/>')
            s.append(f'<text x="{axis+tw/2+4:.1f}" y="{y+rh/2+4}" class="mut">{fmt(m["U"])}</text>')
    s.append(f'<text x="{X0}" y="{H-12}" class="src">검은 막대 = 그 층의 앵커 비중(0~0.85) · 폭 = 그 층으로 올라오는 경계의 4일 평균 상향 인원(모든 배치 같은 눈금) · 색 = 수단 · 노란 띠 = 앵커 층 · γ=4 연속형 · 100회 반복 평균</text>')
    s.append('</svg>')
    return "".join(s)


SH = sheet()
T = {cid: D[cid]["U"][8]["U"] / D[cid]["U"][1]["U"] * 100 for cid, _ in LAYOUTS}
top1, low3, uni, stp = (D[c]["U"] for c, _ in LAYOUTS)

html = f'''<title>연결 분석 기획안</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>
/* 레이아웃: 한 칼럼 문서. 참고 이미지 읽기, 우리 연구로 옮기기, 데이터 연결표, 실데이터 시안, 발견, 슬라이드 적용, 판단 요청. */
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
ul.plain, ol.plain {{ margin:0; padding-left:1.3em; display:flex; flex-direction:column; gap:6px; }}
.claim {{ font-weight:700; font-size:1.05rem; line-height:1.5; text-wrap:balance; }}
.stage {{ background:#fff; border:1px solid var(--line); border-radius:6px; padding:12px; overflow-x:auto; }}
.stage svg {{ display:block; width:100%; min-width:640px; height:auto; }}
code {{ font-family:ui-monospace,Consolas,monospace; font-size:.82rem; background:var(--accent-soft); padding:1px 5px; border-radius:3px; overflow-wrap:anywhere; }}
table {{ border-collapse:collapse; width:100%; font-size:.88rem; }}
th,td {{ text-align:left; padding:8px 10px 8px 0; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:500; white-space:nowrap; }}
.scroll {{ overflow-x:auto; }}
svg text {{ font-family:"Noto Sans KR","Malgun Gothic",sans-serif; fill:#14202b; }}
svg .h2 {{ font-size:16px; font-weight:800; }} svg .fl {{ font-size:13px; font-weight:700; }}
svg .val {{ font-size:14px; font-weight:800; }} svg .mut {{ font-size:11.5px; fill:#5a6a77; }}
svg .src {{ font-size:11px; fill:#5a6a77; }}
</style>
<main>
  <header>
    <h1>연결 분석 기획안</h1>
    <p class="meta">나비차트와 6번 산점도는 유지 · 시뮬레이션 장면은 제외 · 참고 이미지처럼 데이터를 한 축에 잇는 방법</p>
  </header>

  <section class="box" aria-labelledby="rd">
    <h2 id="rd">참고 이미지가 읽히는 이유</h2>
    <ol class="plain">
      <li><strong>모든 층이 같은 위치 기준선으로 이어집니다.</strong> 점선이 구조 모듈, 단면, 평면, 환경 수치를 같은 지점에서 꿰뚫어서, 눈이 한 지점에서 위아래로 오가며 읽습니다.</li>
      <li><strong>데이터 종류가 한 축 위에 쌓입니다.</strong> 위치마다 구조, 단면, 속도 분포, 소리와 온도와 밀도가 같은 줄에 놓입니다.</li>
      <li><strong>두 조건이 같은 틀에서 대칭입니다.</strong> 겨울과 여름이 위아래로 마주 보아, 비교가 틀 안에서 끝납니다.</li>
      <li><strong>색은 한 가지 의미만 갖습니다.</strong> 나머지는 가는 선과 회색입니다.</li>
    </ol>
  </section>

  <section class="box" aria-labelledby="tr">
    <h2 id="tr">우리 연구로 옮기기: 층 줄을 가로질러 읽는 시트</h2>
    <ul class="plain">
      <li><strong>공통 축 = 건물의 층(세로).</strong> 층마다 한 줄을 두고, 모든 데이터를 그 줄에 놓습니다.</li>
      <li><strong>한 줄 안에 원인과 결과가 이어집니다.</strong> 그 층의 프로그램 → 그 층으로 올라오는 유량(수단별) → 위로 얼마나 이어지나.</li>
      <li><strong>연결 규칙:</strong> 경계 b(b-1층 → b층)는 도착하는 b층의 줄에 놓습니다. 그러면 층의 프로그램과 그 층으로 올라오는 흐름이 한 줄에서 만납니다.</li>
      <li><strong>조건 비교:</strong> 연속형과 분절형은 마주 보게(나비차트), 배치 4종은 나란히 놓습니다.</li>
      <li><strong>연결선:</strong> 같은 층의 가는 점선. 색은 수단 3가지와 앵커 층의 밝은 띠뿐입니다.</li>
    </ul>
  </section>

  <section aria-labelledby="tk">
    <h2 id="tk">데이터를 잇는 키</h2>
    <p class="meta" style="margin-bottom:10px">핵심 표는 <code>aik_boundary_rep.csv</code> 하나이고, (셀, 반복, 경계) 한 행에 아래가 모두 들어 있습니다.</p>
    <div class="scroll">
      <table>
        <tr><th>층</th><th>변수</th><th>원자료</th></tr>
        <tr><td>프로그램</td><td>그 층의 앵커 비중, 인접층 격차, 위층 평균</td><td><code>x_lower</code> <code>x_upper</code> <code>delta</code> <code>M_above</code></td></tr>
        <tr><td>유량</td><td>경계 상향 인원, 수단별 인원</td><td><code>U</code> <code>U_esc</code> <code>U_stairs</code> <code>U_elev</code></td></tr>
        <tr><td>유지</td><td>직전 경계 대비, 1층 대비</td><td><code>AUFR</code> <code>RUI</code></td></tr>
        <tr><td>도달</td><td>최상층 도달, 평균 도달</td><td><code>aik_a4_reach.csv</code></td></tr>
        <tr><td>설명력</td><td>프로그램 변수별 설명 비중</td><td><code>aik_a2b_constructs.csv</code></td></tr>
        <tr><td>변동</td><td>200회 반복의 백분위수</td><td><code>aik_boundary_rep.csv</code>에서 계산</td></tr>
      </table>
    </div>
  </section>

  <section aria-labelledby="sk">
    <h2 id="sk">시안: 배치 4종 연결 시트 (실데이터)</h2>
    <p class="claim" style="margin-bottom:12px">앵커가 있는 줄(노란 띠)을 따라 가면, 그 줄로 올라오는 흐름이 어떻게 달라지는지 한눈에 보인다.</p>
    <div class="stage">{SH}</div>
  </section>

  <section class="box" aria-labelledby="fd">
    <h2 id="fd">연결해서 보면 보이는 것</h2>
    <ul class="plain">
      <li><strong>앵커 층에서 흐름이 되살아납니다.</strong> 최상층 집중은 위로 갈수록 줄던 유량이 8→9층 경계(앵커가 있는 9층으로 올라오는 경계)에서 {fmt(top1[7]["U"])}명(7→8층)에서 {fmt(top1[8]["U"])}명으로 다시 늘어납니다.</li>
      <li><strong>앵커가 끝나는 층 위로 흐름이 무너집니다.</strong> 저층 집중은 앵커 3개 층까지 {fmt(low3[1]["U"])} · {fmt(low3[2]["U"])} · {fmt(low3[3]["U"])}명을 유지하다가 4→5층 경계에서 {fmt(low3[4]["U"])}명으로 떨어집니다. 징검다리형은 앵커 층 뒤마다 계단식으로 떨어집니다.</li>
      <li><strong>수단이 프로그램 위치에 따라 달라집니다(논문 본문에 없는 새 연결).</strong> 같은 건물인데 최상층 집중은 4→5층부터 7→8층 경계에서 엘리베이터가 71~76%이고, 저층 집중은 1→2층 경계에서 17%입니다. 먼 곳에 앵커가 있으면 엘리베이터를 고릅니다.</li>
    </ul>
    <p class="meta" style="margin-top:10px">셋째는 이번에 처음 집계한 값입니다. 모델의 수단 선택 규칙이 만든 결과일 수 있어서, 발표에 넣기 전에 규칙을 확인해야 합니다.</p>
  </section>

  <section aria-labelledby="ap">
    <h2 id="ap">슬라이드에 적용하는 법</h2>
    <p class="meta" style="margin-bottom:10px">시트는 하나의 틀이고, 슬라이드마다 한 층(레이어)씩 켜서 보여 줍니다. 5분 안에 읽히도록 점진적으로 공개합니다.</p>
    <div class="scroll">
      <table>
        <tr><th>장</th><th>켜는 레이어</th><th>그림</th></tr>
        <tr><td>4 방법</td><td>프로그램</td><td>배치 4종의 층별 앵커 막대(시트의 검은 막대 열만)</td></tr>
        <tr><td>5 기준선</td><td>유량(수단별)</td><td><strong>나비차트</strong>(연속형 / 분절형 마주 보기)</td></tr>
        <tr><td>6 위층 앵커</td><td>프로그램 → 유량</td><td><strong>산점도 2개</strong>. 점 하나가 한 줄(경계)의 값이라는 점을 시트 축 그대로 쓴다</td></tr>
        <tr><td>7 동선 마찰</td><td>수위와 기울기</td><td>γ별 잠식률 점 그래프</td></tr>
        <tr><td>8 배치</td><td>프로그램 + 유량 + 도달</td><td><strong>연결 시트 전체</strong>(위 시안)</td></tr>
        <tr><td>9 결론</td><td>전체 요약</td><td>1번 경계 인원과 8번 경계 인원 대비(γ별)</td></tr>
      </table>
    </div>
  </section>

  <section class="box warn" aria-labelledby="ask">
    <h2 id="ask">정해 주실 것</h2>
    <ul class="plain">
      <li>이 연결 시트를 8번(배치) 슬라이드의 본체로 써도 될까요?</li>
      <li>수단 전환(프로그램 위치에 따라 엘리베이터 비중이 달라짐)을 발표에 넣을지, 확인이 끝날 때까지 빼 둘지</li>
      <li>시트가 한 장에 정보가 많습니다. 교수님 대상이라 괜찮은지, 레이어를 둘로 나눌지</li>
    </ul>
  </section>
</main>
'''
open(OUT, "w", encoding="utf-8").write(html)
i = html.index("</style>") + len("</style>")
open(LOCAL, "w", encoding="utf-8").write('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n' + html[:i] + '\n</head><body>' + html[i:] + '</body></html>\n')
print("ok", len(html), {k: round(v, 1) for k, v in T.items()})
