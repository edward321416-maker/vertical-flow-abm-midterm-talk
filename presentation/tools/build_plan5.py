"""참고 이미지(Street Choreographies)의 그림 문법으로 옮긴 '수직 동선의 안무' 시안. 모든 값은 CSV에서 읽는다.

위조건 A = 최상층 집중, 아래조건 B = 저층 집중 (γ=4, 연속형, 100회 반복 평균). 축 = 경계 8개(1→2층 ... 8→9층)를 가로로 펼친 수직 동선.
"""
import collections
import csv
import math
import os

AIK = r"D:\vcpf\repo\analysis\outputs\sim\aik"
OUT = r"D:\Temp\claude\D--Users-admin-Desktop-2-----\5d671f74-c77a-47c0-9dc7-d57885767bf7\scratchpad\plan5_artifact.html"
LOCAL = r"D:\Users\admin\Desktop\2학기 논문\발표자료\01_과정\기획안_05_안무시트.html"

rep = list(csv.DictReader(open(os.path.join(AIK, "aik_boundary_rep.csv"), encoding="utf-8-sig")))


def load(cid):
    xs, acc, n = collections.defaultdict(list), collections.defaultdict(collections.Counter), collections.Counter()
    for r in rep:
        if r["cell_id"] != cid:
            continue
        b = int(r["boundary_order"])
        xs[b].append(float(r["x_upper"]))
        for k in ("U", "U_esc", "U_stairs", "U_elev"):
            acc[b][k] += float(r[k])
        n[b] += 1
    return {b: {"x": sum(xs[b]) / len(xs[b]), **{k: v / n[b] for k, v in acc[b].items()}} for b in range(1, 9)}


A, B = load("aik_e2_top1_g4_cont"), load("aik_e2_low3_g4_cont")
BL, RD = "#2a5fd6", "#d63a2a"
INK, MUT = "#14202b", "#5a6a77"
UMAX = max(d["U"] for d in list(A.values()) + list(B.values()))
GMAX = max(max(d["U_esc"], d["U_elev"]) for d in list(A.values()) + list(B.values()))

W, H = 1600, 990
XS = [215 + i * 175 for i in range(8)]


def fmt(v):
    return f"{v:,.0f}"


def heat_color(t):
    stops = [(0, (43, 68, 255)), (0.25, (138, 43, 226)), (0.5, (230, 25, 156)), (0.75, (255, 59, 48)), (1.0, (255, 154, 31))]
    t = max(0, min(1, t))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return "#%02x%02x%02x" % tuple(int(c0[i] + (c1[i] - c0[i]) * u) for i in range(3))
    return "#ff9a1f"


def icon(kind, x, y, color):
    """축측도 선화 아이콘 44x40, 왼쪽 위 (x, y)."""
    p = []
    if kind == "elev":
        p += [f"M{x+6},{y+14} L{x+24},{y+14} L{x+24},{y+36} L{x+6},{y+36} Z", f"M{x+6},{y+14} L{x+14},{y+8} L{x+32},{y+8} L{x+24},{y+14}",
              f"M{x+24},{y+14} L{x+32},{y+8} L{x+32},{y+30} L{x+24},{y+36}", f"M{x+15},{y+14} L{x+15},{y+36}"]
    else:
        p += [f"M{x+3},{y+34} L{x+29},{y+12} L{x+41},{y+12} L{x+15},{y+34} Z", f"M{x+3},{y+34} L{x+3},{y+38} L{x+15},{y+38} L{x+15},{y+34}"]
        p += [f"M{x+10+i*5},{y+28-i*3.7} L{x+16+i*5},{y+28-i*3.7}" for i in range(4)]
    return "".join(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.3"/>' for d in p)


def lens(x, base, hu, hd, w, fu, fd, opacity, stroke_only=False):
    """위쪽 반 = 조건 A, 아래쪽 반 = 조건 B 인 잎 모양 글리프."""
    out = []
    for h, col, sign in ((hu, fu, -1), (hd, fd, 1)):
        if h < 0.4:
            continue
        tip = base + sign * h
        d = (f"M{x:.1f},{tip:.1f} C{x+w:.1f},{base+sign*h*0.62:.1f} {x+w:.1f},{base+sign*h*0.12:.1f} {x:.1f},{base:.1f} "
             f"C{x-w:.1f},{base+sign*h*0.12:.1f} {x-w:.1f},{base+sign*h*0.62:.1f} {x:.1f},{tip:.1f} Z")
        if stroke_only:
            out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.6"/>')
        else:
            out.append(f'<path d="{d}" fill="{col}" fill-opacity="{opacity}" stroke="{col}" stroke-width="1"/>')
    return "".join(out)


def sheet():
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="수직 동선을 가로로 펼쳐 배치 두 가지를 위아래로 마주 놓은 연결 분석 시트">']
    s.append('<defs><filter id="blur" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="9"/></filter></defs>')
    # 제목 태그
    s.append(f'<rect x="40" y="16" width="190" height="16" fill="{INK}"/><text x="46" y="28" class="tg">VERTICAL CHOREOGRAPHIES</text>')
    s.append(f'<text x="40" y="48" class="sm">수직 동선의 안무 · 앵커 배치에 따른 층간 흐름 · 수직 동선을 거리처럼 펼친 시트</text>')
    # 수직 기준선(전체 관통) + 십자
    yA = dict(icon=72, sec=134, heat=266, tag=322, base=500, tagb=650, heatb=734, secb=796, iconb=890)
    for x in XS:
        s.append(f'<line x1="{x}" x2="{x}" y1="62" y2="935" stroke="{INK}" stroke-width="0.9" stroke-dasharray="1.5 3.5"/>')
    s.append(f'<line x1="70" x2="{XS[-1]+110}" y1="{yA["base"]}" y2="{yA["base"]}" stroke="{INK}" stroke-width="0.8" stroke-dasharray="1.5 3.5"/>')

    def block(data, color, up):
        c = color
        ys = (yA["sec"], yA["heat"], yA["tag"], yA["icon"]) if up else (yA["secb"], yA["heatb"], yA["tagb"], yA["iconb"])
        ysec, yheat, ytag, yicon = ys
        ycen = yheat if up else yheat
        # 단면 띠: 층 칸 + 앵커 덩어리 + 동선 연결선
        pts = []
        for i, b in enumerate(range(1, 9)):
            x = XS[i]
            d = data[b]
            top, hh = ysec, 72
            s.append(f'<rect x="{x-62}" y="{top}" width="124" height="{hh}" fill="#f3f4f5" stroke="#9aa3ab" stroke-width="1"/>')
            ah = d["x"] / 0.85 * 62
            s.append(f'<rect x="{x-52}" y="{top+hh-6-ah:.1f}" width="104" height="{max(ah,1.5):.1f}" fill="#3a4147" fill-opacity=".88"/>')
            s.append(f'<line x1="{x-62}" x2="{x+62}" y1="{top+hh}" y2="{top+hh}" stroke="{INK}" stroke-width="2.4"/>')
            pts.append((x, top + 6, top + hh))
        for (x0, t0, b0), (x1, t1, b1) in zip(pts, pts[1:]):
            s.append(f'<path d="M{x0+62},{b0} L{x1-62},{t1}" stroke="{c}" stroke-width="1.5" fill="none"/>')
        # 흐름 히트 띠
        s.append(f'<line x1="70" x2="{XS[-1]+110}" y1="{ycen}" y2="{ycen}" stroke="{c}" stroke-width="3.2" opacity=".85"/>')
        for i, b in enumerate(range(1, 9)):
            x = XS[i]
            u = data[b]["U"]
            t = u / UMAX
            hgt = 7 + 34 * t
            s.append(f'<ellipse cx="{x}" cy="{ycen}" rx="86" ry="{hgt:.1f}" fill="{heat_color(t)}" opacity=".86" filter="url(#blur)"/>')
        # 태그
        for i, b in enumerate(range(1, 9)):
            x = XS[i]
            s.append(f'<rect x="{x-58}" y="{ytag}" width="116" height="30" fill="{INK}"/>')
            s.append(f'<text x="{x}" y="{ytag+13}" text-anchor="middle" class="tg">{b}→{b+1}층</text>')
            s.append(f'<text x="{x}" y="{ytag+25}" text-anchor="middle" class="tg">{fmt(data[b]["U"])}명 · 앵커 {data[b]["x"]:.2f}</text>')
        # 축측도 아이콘: 그 경계의 주력 수단
        for i, b in enumerate(range(1, 9)):
            kind = "elev" if data[b]["U_elev"] > data[b]["U_esc"] else "esc"
            s.append(icon(kind, XS[i] - 22, yicon, c))
        for i in range(8):                       # 십자
            for yy in ((ysec + 36), ycen):
                s.append(f'<path d="M{XS[i]-5},{yy} L{XS[i]+5},{yy} M{XS[i]},{yy-5} L{XS[i]},{yy+5}" stroke="#fff" stroke-width="2.4"/>')

    block(A, BL, True)
    block(B, RD, False)
    # 글리프 띠(가운데): 위 = A, 아래 = B. 채움 = 에스컬레이터, 선 = 엘리베이터
    base = yA["base"]
    k = 118 / GMAX
    for series, dx, so in (("U_esc", -13, False), ("U_elev", 13, True)):
        for pts, col, sign, dash in ((A, BL, -1, "2 3"), (B, RD, 1, "2 3")):
            line = []
            for i, b in enumerate(range(1, 9)):
                line.append((XS[i] + dx, base + sign * pts[b][series] * k))
            s.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in line) + f'" fill="none" stroke="{col}" stroke-width="1.1" stroke-dasharray="{dash}" opacity="{.9 if not so else .55}"/>')
    for i, b in enumerate(range(1, 9)):
        x = XS[i]
        for series, dx, so, w in (("U_esc", -13, False, 15), ("U_elev", 13, True, 11)):
            s.append(lens(x + dx, base, A[b][series] * k, B[b][series] * k, w, BL, RD, 0.62, stroke_only=so))
    # 십자(글리프 띠)
    for x in XS:
        s.append(f'<path d="M{x-5},{base} L{x+5},{base} M{x},{base-5} L{x},{base+5}" stroke="{INK}" stroke-width="1.2"/>')
    # 좌측 세로 라벨
    for txt, yc, col in (("A · 최상층 집중 (위)", 215, BL), ("에스컬레이터(채움) · 엘리베이터(선)", 500, INK), ("B · 저층 집중 (아래)", 790, RD)):
        s.append(f'<text transform="translate(30,{yc}) rotate(-90)" text-anchor="middle" class="sm" fill="{col}">{txt}</text>')
    # 범례(우측 하단)
    s.append(f'<text x="{W-60}" y="{H-34}" text-anchor="end" class="src">띠 색 = 그 경계로 올라오는 4일 평균 상향 인원(파랑 적음 → 주황 많음, 모든 줄 같은 눈금) · 글리프 높이 = 수단별 인원(선형, 위 A 아래 B)</text>')
    s.append(f'<text x="{W-60}" y="{H-18}" text-anchor="end" class="src">검은 덩어리 = 도착하는 층의 앵커 비중(0~0.85) · 선 위 아이콘 = 그 경계의 주력 수단 · γ=4 연속형 · 100회 반복 평균 · 자료 aik_boundary_rep.csv</text>')
    s.append('</svg>')
    return "".join(s)


SH = sheet()
a8, b8 = A[8], B[8]
html = f'''<title>수직 동선의 안무</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>
/* 레이아웃: 한 칼럼 문서. 인정, 참고 이미지의 그림 문법, 대응표, 시안(가로로 넓게), 판단 요청. */
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
main {{ max-width:1000px; margin:0 auto; display:flex; flex-direction:column; gap:36px; }}
h1 {{ font-size:1.5rem; line-height:1.35; margin:0; text-wrap:balance; }}
h2 {{ font-size:1.15rem; margin:0 0 10px; text-wrap:balance; }}
p {{ margin:0; }}
.meta {{ color:var(--muted); font-size:.9rem; }}
.box {{ background:var(--surface); border:1px solid var(--line); border-radius:6px; padding:16px 18px; }}
.box.warn {{ background:var(--warn-soft); border-color:transparent; }}
.box.warn h2 {{ color:var(--warn); }}
ul.plain, ol.plain {{ margin:0; padding-left:1.3em; display:flex; flex-direction:column; gap:6px; }}
.stage {{ background:#fff; border:1px solid var(--line); border-radius:6px; padding:8px; overflow-x:auto; }}
.stage svg {{ display:block; width:100%; min-width:1000px; height:auto; }}
code {{ font-family:ui-monospace,Consolas,monospace; font-size:.82rem; background:var(--accent-soft); padding:1px 5px; border-radius:3px; overflow-wrap:anywhere; }}
table {{ border-collapse:collapse; width:100%; font-size:.88rem; }}
th,td {{ text-align:left; padding:8px 10px 8px 0; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:500; white-space:nowrap; }}
.scroll {{ overflow-x:auto; }}
svg text {{ font-family:"Noto Sans KR","Malgun Gothic",sans-serif; }}
svg .tg {{ font-size:10.5px; font-weight:700; fill:#fff; }}
svg .sm {{ font-size:12px; font-weight:700; fill:#14202b; }}
svg .src {{ font-size:10.5px; fill:#5a6a77; }}
</style>
<main>
  <header>
    <h1>수직 동선의 안무</h1>
    <p class="meta">참고 이미지의 그림 문법으로 다시 옮긴 시안 · 앞서 만든 막대 시트는 폐기합니다</p>
  </header>

  <section class="box warn" aria-labelledby="ad">
    <h2 id="ad">앞 시안이 달랐던 이유</h2>
    <p>제가 "같은 줄에 데이터를 놓는다"는 생각만 가져오고, 참고 이미지의 그림 언어는 따르지 않았습니다. 막대 차트에 층 줄을 얹은 것이라 참고 이미지와 다른 그림이 됐습니다.</p>
  </section>

  <section class="box" aria-labelledby="gm">
    <h2 id="gm">참고 이미지의 그림 문법과 우리 데이터 대응</h2>
    <div class="scroll">
      <table>
        <tr><th>참고 이미지</th><th>우리 시안</th><th>데이터</th></tr>
        <tr><td>거리를 따라 늘어선 지점</td><td>수직 동선을 가로로 펼친 경계 8개(1→2층 … 8→9층)</td><td><code>boundary_order</code></td></tr>
        <tr><td>지점마다 관통하는 수직 점선과 십자</td><td>같은 경계의 모든 층(레이어)을 꿰뚫는 점선</td><td>-</td></tr>
        <tr><td>위아래의 구조 모듈 축측도</td><td>그 경계의 주력 수단 아이콘(에스컬레이터 또는 엘리베이터)</td><td><code>U_esc</code> 대 <code>U_elev</code></td></tr>
        <tr><td>단면 띠</td><td>층 칸 + 검은 앵커 덩어리 + 층을 잇는 동선선</td><td><code>x_upper</code></td></tr>
        <tr><td>색이 번지는 평면 띠(속도)</td><td>경계로 올라오는 인원을 색과 두께로 번지게 한 띠(한 가지 뜻)</td><td><code>U</code></td></tr>
        <tr><td>검은 태그와 환경 수치</td><td>경계 이름, 인원, 앵커 비중</td><td><code>U</code> <code>x_upper</code></td></tr>
        <tr><td>잎 모양 글리프 쌍과 점선</td><td>수단별 글리프(채움 = 에스컬레이터, 선 = 엘리베이터), 점선이 경계를 잇는다</td><td><code>U_esc</code> <code>U_elev</code></td></tr>
        <tr><td>겨울과 여름의 위아래 대칭</td><td>배치 A(위, 파랑)와 배치 B(아래, 빨강). 글리프는 위 반쪽 = A, 아래 반쪽 = B</td><td>E2 셀 2개</td></tr>
      </table>
    </div>
  </section>

  <section aria-labelledby="sk">
    <h2 id="sk">시안 (실데이터): 최상층 집중 대 저층 집중</h2>
    <div class="stage">{SH}</div>
    <p class="meta" style="margin-top:8px">가로로 넓은 그림입니다. 좁은 화면에서는 옆으로 밀어 보세요.</p>
  </section>

  <section class="box" aria-labelledby="rd">
    <h2 id="rd">이 시트에서 읽히는 것</h2>
    <ul class="plain">
      <li><strong>색 띠:</strong> 위쪽 배치(최상층 집중)는 1→2층의 주황에서 보라로 식다가 마지막 8→9층 경계에서 다시 분홍으로 달아오릅니다. 아래쪽 배치(저층 집중)는 3→4층까지 주황과 붉은색이다가 4→5층부터 파랑과 보라로 식습니다.</li>
      <li><strong>글리프:</strong> 채움(에스컬레이터)은 아래층 경계에서 크고 위로 갈수록 급격히 줄어듭니다. 선(엘리베이터)은 위층에서도 남아서, 위쪽 배치의 마지막 경계에서는 선이 채움보다 커집니다. 점선이 그 변화를 경계마다 이어 줍니다.</li>
      <li><strong>검은 덩어리:</strong> 앵커 층 칸에서만 커집니다(최상층 집중은 8→9층, 저층 집중은 1→2층에서 3→4층까지). 최상층 도달은 위 {fmt(a8["U"])}명, 아래 {fmt(b8["U"])}명입니다.</li>
    </ul>
  </section>

  <section class="box" aria-labelledby="nt">
    <h2 id="nt">정직하게 표시할 것</h2>
    <ul class="plain">
      <li>색의 번짐(블러)은 그림 효과이고, 값은 띠의 두께와 색 단계로만 읽습니다.</li>
      <li>아이콘과 층 칸의 선화는 장식이 아니라 기호입니다. 값을 가진 요소는 검은 덩어리, 띠의 색과 두께, 글리프의 높이입니다.</li>
      <li>수단 전환은 논문 본문에 없는 새로운 연결이라, 발표에 넣기 전에 모델의 수단 선택 규칙을 확인해야 합니다.</li>
    </ul>
  </section>

  <section class="box warn" aria-labelledby="ask">
    <h2 id="ask">정해 주실 것</h2>
    <ul class="plain">
      <li>이 그림 문법이 참고 이미지와 가까운지, 더 가져와야 할 요소(예: 단면 띠를 더 건축 도면답게, 맥락 점선 추가)가 있는지</li>
      <li>비교할 두 조건을 최상층 집중 대 저층 집중으로 둘지, 연속형 대 분절형으로 둘지(5번 슬라이드용)</li>
      <li>가로 펼침(수직 동선을 거리처럼 읽기)이 괜찮은지, 층을 세로로 세운 세로형 시트로 바꿀지</li>
    </ul>
  </section>
</main>
'''
open(OUT, "w", encoding="utf-8").write(html)
i = html.index("</style>") + len("</style>")
open(LOCAL, "w", encoding="utf-8").write('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n' + html[:i] + '\n</head><body>' + html[i:] + '</body></html>\n')
print("ok", len(html), "UMAX", round(UMAX), "GMAX", round(GMAX))
