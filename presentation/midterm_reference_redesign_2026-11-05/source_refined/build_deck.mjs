// Refined 18-page 논문 중간발표 deck: HTML/SVG vector pipeline -> Chromium PDF.
// Every number is read from verified_values.json (written by verify_values.py from analysis/outputs/aik).
// Usage: node build_deck.mjs            (writes build/deck.html, build/layout_audit.json and the final PDF)
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const TASK = path.resolve(HERE, '..');
const BUILD = path.join(HERE, 'build');
const OUT_PDF = path.join(TASK, 'vertical_flow_midterm_reference_refined.pdf');
const V = JSON.parse(fs.readFileSync(path.join(HERE, 'verified_values.json'), 'utf8'));
fs.mkdirSync(BUILD, { recursive: true });

// ------------------------------------------------------------------------------------------- formatting
const MINUS = '−';
const nf0 = (x) => Math.round(x).toLocaleString('en-US');
const pct1 = (x) => (x * 100).toFixed(1).replace('-', MINUS);
const f3 = (x) => x.toFixed(3);
const signed1 = (x) => (x >= 0 ? '+' : MINUS) + Math.abs(x * 100).toFixed(1);
const esc = (s) => String(s).replace(/&/g, '&amp;');

// ------------------------------------------------------------------------------------------- palette
const C = {
  ink: '#000000', body: '#111111', mid: '#3d3d3d', soft: '#636363', faint: '#8a8a8a',
  rule: '#c8c8c8', hair: '#e3e3e3', ghost: '#cfcfcf',
  cont: '#1F4E79', frag: '#9C5A2E', bar: '#2b2b2b', barLight: '#bdbdbd',
};

// ------------------------------------------------------------------------------------------- SVG helpers
const svg = (x, y, w, h, inner, label = '') =>
  `<svg class="abs fig" data-fig="${label}" style="left:${x}pt;top:${y}pt;width:${w}pt;height:${h}pt" viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;
const T = (x, y, s, o = {}) =>
  `<text x="${x}" y="${y}" font-size="${o.size || 11}" font-weight="${o.w || 400}" fill="${o.fill || C.body}" text-anchor="${o.anchor || 'start'}"${o.ls ? ` letter-spacing="${o.ls}"` : ''}${o.noaudit ? ' data-noaudit="1"' : ''}>${s}</text>`;
const L = (x1, y1, x2, y2, o = {}) =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${o.stroke || C.ink}" stroke-width="${o.w || 0.75}"${o.dash ? ` stroke-dasharray="${o.dash}"` : ''} stroke-linecap="${o.cap || 'butt'}"/>`;
const R = (x, y, w, h, o = {}) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${o.fill || 'none'}"${o.stroke ? ` stroke="${o.stroke}" stroke-width="${o.sw || 0.75}"` : ''}${o.op !== undefined ? ` fill-opacity="${o.op}"` : ''}/>`;
const Ci = (cx, cy, r, o = {}) =>
  `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${o.fill === undefined ? C.ink : o.fill}"${o.stroke ? ` stroke="${o.stroke}" stroke-width="${o.sw || 1}"` : ''}/>`;
const P = (d, o = {}) =>
  `<path d="${d}" fill="${o.fill || 'none'}" stroke="${o.stroke || 'none'}" stroke-width="${o.w || 1}"${o.dash ? ` stroke-dasharray="${o.dash}"` : ''}${o.op !== undefined ? ` fill-opacity="${o.op}"` : ''} stroke-linejoin="round" stroke-linecap="round"/>`;
const sb = (s, size) => `<tspan baseline-shift="sub" font-size="${size}">${s}</tspan>`;
const lin = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
const poly = (pts) => pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ');
const arrowUp = (x, y, s = 5, fill = C.ink) => P(`M${x - s * 0.6},${y + s} L${x},${y} L${x + s * 0.6},${y + s} Z`, { fill, stroke: fill, w: 0.5 });
const arrowDown = (x, y, s = 5, fill = C.ink) => P(`M${x - s * 0.6},${y - s} L${x},${y} L${x + s * 0.6},${y - s} Z`, { fill, stroke: fill, w: 0.5 });
const square = (cx, cy, h, o = {}) => R(cx - h, cy - h, 2 * h, 2 * h, { fill: o.fill || '#fff', stroke: o.stroke || C.ink, sw: o.sw || 1.2 });

// ------------------------------------------------------------------------------------------- HTML helpers
const box = (x, y, w, html, cls = '', style = '') =>
  `<div class="abs ${cls}" style="left:${x}pt;top:${y}pt;width:${w}pt;${style}">${html}</div>`;

const SECTIONS = {
  1: '연구 배경과 핵심 질문',
  2: '선행연구와 분석 방법',
  3: '시뮬레이션 조건과 실험 설계',
  4: '층간 상행유량 감소와 프로그램 구성',
  5: '이동 저항과 앵커 배치에 따른 차이',
  6: '현재까지의 분석 결과와 향후 검증',
};

function slide({ no, section, title, subtitle, source, trace, body }) {
  const kicker = section ? `<div class="abs kicker"><span class="kno">${String(section).padStart(2, '0')}</span>${SECTIONS[section]}</div>` : '';
  return `<section class="slide" id="p${no}" data-page="${no}">
${kicker}
<h1 class="abs title">${title}</h1>
${subtitle ? `<p class="abs subtitle">${subtitle}</p>` : ''}
${body}
<div class="abs footrule"></div>
<div class="abs foot-src">${source || ''}</div>
<div class="abs foot-right">${trace ? `<span class="trace">${trace}</span>` : ''}<span class="pno">${no} / 18</span></div>
</section>`;
}

// ------------------------------------------------------------------------------------------- data shortcuts
const prof = V.rq1.profile;
const cont = prof.cont;
const frag = prof.frag;
const M = V.rq2.multipliers;
const DEV = V.rq2.deviance;
const ER = V.rq3.erosion;
const GAP = V.rq3.u1_gap;
const PL = V.rq4.placements;
const PATTERNS = ['TOP1', 'STEP3', 'UNIFORM', 'LOW3'];
const PNAME = { TOP1: '최상층 집중', STEP3: '3·6·9층 징검다리', UNIFORM: '균등', LOW3: '2·3·4층 저층 집중' };

const pages = [];

// =========================================================================================== 01 cover
pages.push(`<section class="slide cover" id="p1" data-page="1">
${box(56, 150, 848, '논문 중간발표', 'cover-kicker')}
<h1 class="abs cover-title" style="left:56pt;top:178pt;width:848pt">다층 상업시설의 프로그램 구성과<br>수직동선 저항에 따른 층간 상행유량비(AUFR)</h1>
${box(56, 278, 848, '인접층 관계와 수직 배치의 에이전트 기반 민감도 분석', 'cover-sub')}
${box(56, 398, 600, '봉성현', 'cover-name')}
${box(56, 424, 600, '성균관대학교 건축학과', 'cover-meta')}
${box(56, 444, 600, '2026. 11. 5.', 'cover-meta')}
</section>`);

// =========================================================================================== 02 structure
{
  const items = [
    ['01', SECTIONS[1], '절대 유량과 함께 상행유량비를 보아야 하는 이유', '3–4'],
    ['02', SECTIONS[2], 'Chang &amp; Penn(1998)의 관측 연구와 네 가지 연구 질문', '5–6'],
    ['03', SECTIONS[3], '합성 9층 층 선택 모형, 상행유량비 계산, 2,600회 실험', '7–9'],
    ['04', SECTIONS[4], '기준선의 감소 형태와 인접층 앵커 비중의 관계', '10–13'],
    ['05', SECTIONS[5], '연속형·분절형 비교와 같은 앵커 총량의 네 가지 배치', '14–16'],
    ['06', SECTIONS[6], '모형의 한계와 다음 검증 과제', '17–18'],
  ];
  let rows = '';
  items.forEach(([n, t, d, pg], i) => {
    const y = 120 + i * 62;
    rows += box(56, y, 40, n, 'toc-no');
    rows += box(108, y - 3, 560, t, 'toc-title');
    rows += box(108, y + 24, 640, d, 'toc-desc');
    rows += box(784, y, 120, `${pg}쪽`, 'toc-pg');
    if (i < items.length - 1) rows += `<div class="abs hair" style="left:108pt;top:${y + 50}pt;width:796pt"></div>`;
  });
  pages.push(slide({ no: 2, title: '발표 구성', body: rows, source: '' }));
}

// =========================================================================================== 03 background
{
  const pts = [
    ['1', '다층 상업시설은 공간을 수직으로 확장하지만, 위층으로 갈수록 이동 부담이 더해진다.'],
    ['2', '이동 중 목적지 선택과 퇴장이 반복되면 상층부로 이어지는 상행 흐름이 달라진다.'],
    ['3', '위층에 목적성 프로그램이 있으면 같은 높이에서도 흐름이 달라질 수 있다.'],
    ['4', '절대 유량만으로는 어느 경계에서 상대적으로 크게 줄었는지 알기 어렵다.'],
  ];
  let left = '';
  pts.forEach(([n, t], i) => {
    const y = 124 + i * 64;
    left += box(56, y + 2, 26, n, 'num-s');
    left += box(84, y, 272, t, 'body13');
  });
  // hypothetical comparison (2 x 2): columns A and B, rows absolute decrease / ratio
  const fx = 384, fw = 520;
  const colA = 128, colB = 330, track = 150;
  let g = '';
  g += T(colA, 14, '상황 A', { size: 13, w: 600, fill: C.ink });
  g += T(colA, 32, '직전 경계 100명 → 현재 경계 50명', { size: 11, fill: C.soft });
  g += T(colB, 14, '상황 B', { size: 13, w: 600, fill: C.ink });
  g += T(colB, 32, '직전 경계 1,000명 → 현재 경계 950명', { size: 11, fill: C.soft });
  g += L(0, 48, fw, 48, { stroke: C.rule });
  // row 1 absolute decrease
  g += T(0, 84, '절대 감소량', { size: 12.5, w: 600, fill: C.ink });
  g += T(0, 101, '직전 − 현재', { size: 10.5, fill: C.soft });
  for (const cx of [colA, colB]) {
    g += R(cx, 78, 60, 14, { fill: C.bar });
    g += T(cx + 68, 90, `${MINUS}50명`, { size: 14, w: 600, fill: C.ink });
  }
  g += L(0, 124, fw, 124, { stroke: C.hair });
  // row 2 ratio
  g += T(0, 160, '상행유량비', { size: 12.5, w: 600, fill: C.ink });
  g += T(0, 177, '현재 ÷ 직전', { size: 10.5, fill: C.soft });
  for (const [cx, r, lab] of [[colA, 0.5, '50%'], [colB, 0.95, '95%']]) {
    g += R(cx, 154, track, 14, { fill: C.hair });
    g += R(cx, 154, track * r, 14, { fill: C.bar });
    g += T(cx + track + 10, 167, lab, { size: 16, w: 700, fill: C.ink });
  }
  g += T(colA, 196, '0', { size: 9.5, fill: C.faint, anchor: 'middle' });
  g += T(colA + track, 196, '100%', { size: 9.5, fill: C.faint, anchor: 'middle' });
  g += T(colB, 196, '0', { size: 9.5, fill: C.faint, anchor: 'middle' });
  g += T(colB + track, 196, '100%', { size: 9.5, fill: C.faint, anchor: 'middle' });
  g += L(0, 210, fw, 210, { stroke: C.rule });
  const fig = svg(fx, 120, fw, 214, g, 'p3-hypothetical');
  const right = fig
    + box(fx, 344, fw, '절대 감소량은 같지만 상행유량비는 50%와 95%로 다르다.', 'body13 strong')
    + box(fx, 366, fw, '가상 예시 · 본 연구의 시뮬레이션 수치가 아님', 'note-s');
  const q = box(56, 404, 120, '핵심 질문', 'label-s')
    + box(56, 422, 848, '인접한 층간 경계의 상행유량비(AUFR)는 프로그램 구성과 어떤 관계가 있으며, 그 관계는 이동 저항과 수직 배치에 따라 어떻게 달라지는가?', 'question');
  pages.push(slide({
    no: 3, section: 1,
    title: '절대 유량만으로는 구간별 감소를 비교하기 어렵다',
    subtitle: '같은 인원이 줄어도 직전 경계의 규모에 따라 의미가 다르므로, 인접 경계 사이의 비율을 함께 본다.',
    body: left + `<div class="abs vrule" style="left:368pt;top:122pt;height:262pt"></div>` + right + q,
    source: '주: 상황 A·B는 개념 설명용 가상 예시이며 본 연구의 수치가 아니다 · 핵심 질문: 수정 논문(v3) 1.1절',
  }));
}

// =========================================================================================== 04 analytical units
{
  const cols = [
    {
      label: '경계 상행유량',
      q: '경계 <i>b</i>를 얼마나 많이 통과했는가?',
      f: 'U<sub><i>r</i>,<i>b</i></sub>',
      d: `반복 <i>r</i>에서 <i>b</i>층 → <i>b</i>+1층 경계를 위로 통과한 그룹 인원의 4일 합계(연인원). <i>b</i> = 1…8.`,
      n: 'U<sub>1</sub>은 건물 입장객 수가 아니다.',
    },
    {
      label: '층간 상행유량비 AUFR',
      q: '바로 아래 경계와 비교해 얼마나 이어졌는가?',
      f: `AUFR<sub><i>r</i>,<i>b</i></sub> = U<sub><i>r</i>,<i>b</i></sub> / U<sub><i>r</i>,<i>b</i>${MINUS}1</sub>`,
      d: '같은 반복 <i>r</i> 안에서 인접한 두 경계의 통과량을 나눈다. <i>b</i> = 2…8.',
      n: '같은 사람이 계속 올라간 비율(생존율)이 아니다.',
    },
    {
      label: '최상단 상대 유량',
      q: '첫 경계에 비해 마지막 경계는 어느 정도인가?',
      f: 'T<sub><i>r</i></sub> = U<sub><i>r</i>,8</sub> / U<sub><i>r</i>,1</sub>',
      d: `마지막 경계(8F → 9F)와 첫 경계(1F → 2F)의 비.<br>T<sub><i>r</i></sub> = AUFR<sub><i>r</i>,2</sub> × AUFR<sub><i>r</i>,3</sub> × … × AUFR<sub><i>r</i>,8</sub>`,
      n: '방문객이 최상층에 도달할 확률이 아니다.',
    },
  ];
  let b = '';
  cols.forEach((c, i) => {
    const x = 56 + i * 288;
    b += `<div class="abs toprule" style="left:${x}pt;top:122pt;width:268pt"></div>`;
    b += box(x, 132, 268, c.label, 'label-s');
    b += box(x, 152, 268, c.q, 'q15');
    b += box(x, 214, 268, c.f, 'formula');
    b += box(x, 268, 268, c.d, 'body125');
    b += box(x, 352, 268, `<span class="not">아님</span>${c.n}`, 'body12 mid');
  });
  b += `<div class="abs hair" style="left:56pt;top:420pt;width:848pt"></div>`;
  b += box(56, 432, 848, '조건별 값은 반복마다 비율을 먼저 계산한 뒤 평균한다. 평균 유량끼리 나눈 비가 아니다.', 'body13');
  pages.push(slide({
    no: 4, section: 1,
    title: '세 지표는 서로 다른 질문에 답한다',
    subtitle: '모두 같은 경계 통과량에서 계산하지만, 크기 · 인접 경계 비율 · 첫 경계 대비 비율을 따로 읽는다.',
    body: b,
    source: '출처: 수정 논문(v3) 3.3절, 식 (3)–(4) · <i>r</i> = 시뮬레이션 반복, <i>b</i> = 경계 순서(1 = 1F → 2F, 8 = 8F → 9F)',
  }));
}

// =========================================================================================== 05 prior study
{
  const rows = [
    ['대상', '런던의 두 다층 복합지역<br><b>Barbican</b> — 주거·업무·교육·예술·회의 기능 결합<br><b>South Bank</b> — Waterloo역 인접 예술·문화 복합지역', '실제 건물을 복제하지 않은 <b>합성 9층</b> 상업시설<br>1층 출입구 1개 · 층 규모 동일'],
    ['자료', '시간대별 게이트 관측 보행량<br>South Bank는 역 주변 연결 체계 변경 전후 비교', 'GAMA 시뮬레이션 출력 2,600회 (반복당 4일)'],
    ['모형', 'IMCM — 수평 방향 전환 깊이·점 깊이, 통합도 가중치, 층 분리, 주요 경로, 전이 공간을 결합', '비공간적 층 선택 로짓 — 목적지 매력(γ·<i>x</i>), 층수 거리, 수단별 이동 저항'],
    ['주요 결과', '수평 방향 전환 깊이가 수직 층 분리보다 관측 보행 흐름에 더 중요한 요인', '8개 층간 경계의 상행유량 U와 상행유량비 AUFR을 조건별로 비교'],
  ];
  let b = '';
  b += box(160, 120, 352, 'Chang &amp; Penn (1998) · 관측 연구', 'colhead');
  b += box(544, 120, 360, '본 연구 · 합성 층 선택 모형', 'colhead');
  b += `<div class="abs blackrule" style="left:56pt;top:144pt;width:848pt"></div>`;
  const ys = [154, 232, 284, 342];
  rows.forEach(([k, a, c], i) => {
    const y = ys[i];
    b += box(56, y, 96, k, 'rowhead');
    b += box(160, y, 356, a, 'body12');
    b += box(544, y, 360, c, 'body12');
    b += `<div class="abs hair" style="left:56pt;top:${(ys[i + 1] || 394) - 8}pt;width:848pt"></div>`;
  });
  b += box(56, 402, 96, '관계', 'rowhead');
  b += box(160, 402, 356, '<b>이어받은 것</b> — 다층 이동에는 여러 조건이 함께 작용한다는 문제의식', 'body12');
  b += box(544, 402, 360, '<b>이어받지 않은 것</b> — 통합도·가시성·방향 전환 같은 공간 변수, 관측 자료, 검증 관계', 'body12');
  b += box(56, 448, 848, '관측 연구의 결과는 본 모형의 타당성을 검증하지 않는다. 본 연구는 그 모형을 재현하거나 개선하지 않는다.', 'body13 strong');
  pages.push(slide({
    no: 5, section: 2,
    title: '관측된 다층 복합공간과 가상 층 선택 모형',
    subtitle: 'Chang &amp; Penn(1998)의 문제의식을 이어받되, 관측 결과를 본 모형의 검증 근거로 쓰지 않는다.',
    body: b,
    source: '출처: Chang, D. &amp; Penn, A. (1998), Environment and Planning B 25(4), 507–538 (pp. 507–509, 512–513, 520, 523–538) · 수정 논문(v3) 2.1절',
  }));
}

// =========================================================================================== 06 research questions
{
  const qs = [
    ['RQ1', '추가 유인이 없을 때, 상행유량은 높이에 따라 어떻게 줄어드는가?', 'U, AUFR', 'γ = 0 · 연속형·분절형'],
    ['RQ2', '인접한 두 층의 앵커 비중 차이는 상행유량비와 어떤 관계가 있는가?', 'Δ<i>x</i> +0.1당 AUFR 배수<br>보조: U의 잔여 deviance 감소율', 'γ = 2 · 4 · 8'],
    ['RQ3', '이동 저항이 커지면 그 관계는 약해지는가?', '분절형의 AUFR 기울기 잠식률 · 95% 신뢰구간', '연속형 vs 분절형'],
    ['RQ4', '같은 앵커 총량을 다르게 배치하면 상층부 유량은 어떻게 달라지는가?', 'T = U<sub>8</sub>/U<sub>1</sub>, U<sub>8</sub>', '네 가지 배치 · γ = 4'],
  ];
  let b = '';
  qs.forEach(([rq, q, m, c], i) => {
    const y = 134 + i * 88;
    b += box(56, y + 4, 40, String(i + 1), 'qnum');
    b += box(96, y + 30, 40, rq, 'trace-s');
    b += box(96, y, 480, q, 'q17');
    b += box(612, y + 2, 34, '지표', 'label-s');
    b += box(652, y + 1, 252, m, 'body12 mid');
    b += box(612, y + 45, 34, '조건', 'label-s');
    b += box(652, y + 44, 252, c, 'body12 mid');
    if (i < qs.length - 1) b += `<div class="abs hair" style="left:56pt;top:${y + 76}pt;width:848pt"></div>`;
  });
  pages.push(slide({
    no: 6, section: 2,
    title: '핵심 질문을 네 가지로 나누어 분석했다',
    subtitle: '기준선 → 인접층 프로그램 → 이동 저항 → 수직 배치 순서로, 질문마다 지표와 실험 조건을 분리한다.',
    body: b,
    source: '출처: 수정 논문(v3) 2.3절, 표 1',
    trace: 'RQ1–RQ4',
  }));
}

// =========================================================================================== 07 agent model (only full nine-floor abstraction)
{
  const yF = (f) => 452 - (f - 1) * 40; // floor f line
  const yB = (b) => yF(b) - 20; // boundary b between floor b and b+1
  let g = '';
  const ox = 0; // svg origin = page x 56, y 112
  const oy = 112;
  const Y = (y) => y - oy;
  for (let f = 1; f <= 9; f += 1) {
    g += L(36, Y(yF(f)), 236, Y(yF(f)), { stroke: f === 1 ? '#8f8f8f' : C.rule, w: f === 1 ? 1.1 : 0.8 });
    g += T(28, Y(yF(f)) + 4, `${f}F`, { size: 11, fill: C.soft, anchor: 'end' });
  }
  // measured boundaries (gates) on the right
  const grp = [1, 2, 3, 4, 5];
  g += T(256, Y(yF(9)) + 4, '상행 경계', { size: 10, w: 600, fill: C.soft });
  for (let b = 1; b <= 8; b += 1) {
    const yy = Y(yB(b));
    g += L(256, yy, 276, yy, { stroke: C.ink, w: 2.2 });
    g += T(284, yy + 4, `U${sb(b, 8)}`, { size: 11.5, w: 600, fill: C.ink });
    if (grp.includes(b)) g += T(312, yy + 4, '+<tspan font-style="italic">n</tspan>', { size: 11, w: 700, fill: C.ink });
  }
  // example group path: 1F -> 4F -> 6F -> exit via 1F (schematic, so black: colour is reserved for data)
  const x1 = 68, x2 = 112, x3 = 156;
  g += L(x1, Y(yF(1)) - 4, x1, Y(yF(4)) + 7, { stroke: C.ink, w: 1.8 }) + arrowUp(x1, Y(yF(4)) + 1, 6, C.ink);
  g += L(x1, Y(yF(4)), x2, Y(yF(4)), { stroke: C.ink, w: 1.1, dash: '2 2' });
  g += L(x2, Y(yF(4)) - 4, x2, Y(yF(6)) + 7, { stroke: C.ink, w: 1.8 }) + arrowUp(x2, Y(yF(6)) + 1, 6, C.ink);
  g += L(x2, Y(yF(6)), x3, Y(yF(6)), { stroke: C.ink, w: 1.1, dash: '2 2' });
  g += L(x3, Y(yF(6)) + 4, x3, Y(yF(1)) - 7, { stroke: C.faint, w: 1.2, dash: '4 3' }) + arrowDown(x3, Y(yF(1)) - 1, 6, C.faint);
  for (const [x, f] of [[x1, 1], [x2, 4], [x3, 6]]) g += Ci(x, Y(yF(f)), 4.2, { fill: '#fff', stroke: C.ink, sw: 1.3 });
  g += T(x1 - 8, Y(yF(1)) + 17, '도착', { size: 10, fill: C.soft, anchor: 'middle' });
  g += T(x3 + 8, Y(yF(1)) + 17, '퇴장', { size: 10, fill: C.soft, anchor: 'middle' });
  g += T(x1 + 6, Y(yB(2)) + 4, '1F→4F', { size: 9.5, fill: C.mid });
  g += T(x2 + 6, Y(yB(5)) - 6, '4F→6F', { size: 9.5, fill: C.mid });
  g += T(x3 + 6, Y(yB(3)) + 4, '6F→1F 하행', { size: 9.5, fill: C.soft });
  const diagram = svg(56, oy, 352, 370, g, 'p7-model');
  const key = box(56, 486, 380,
    `<span class="key-dot"></span>확률적 선택 지점 &nbsp; <span class="key-gate"></span>상행 경계 기록 위치 &nbsp; <span class="key-n">+<i>n</i></span> 예시 그룹이 더하는 인원`, 'key');
  const steps = [
    ['1', '도착과 체류', '1층 출입구로 방문 그룹이 도착한다(기본 7집단/분, 그룹 인원 1 + Poisson(0.75)명). 그룹은 층에서 확률적으로 체류한다.'],
    ['2', '퇴장 또는 목적지 층 선택 · 상위 로짓', `목적지 효용 V<sub><i>ij</i></sub> = ln A<sub><i>j</i></sub> + γ<i>x</i><sub><i>j</i></sub> ${MINUS} α ln <i>d</i><sub><i>ij</i></sub> ${MINUS} β ln Ī<sub><i>ij</i></sub>. 퇴장 효용은 체류 시간에 따라 커지고, 퇴장하면 1층으로 내려와 나간다.`],
    ['3', '이동 수단 선택 · 하위 로짓', '계단 · 에스컬레이터 · 엘리베이터 중 하나를 확률적으로 고른다. 수단마다 저항과 소요시간이 다르다.'],
    ['4', '경계 기록', `이동이 지나는 모든 상행 경계에 그룹 인원을 더한다 → U<sub>1</sub>…U<sub>8</sub>(4일 합산 연인원). 위 예시 그룹은 U<sub>1</sub>–U<sub>5</sub>에만 더해지고 하행은 U에 넣지 않는다.`],
  ];
  let r = '';
  steps.forEach(([n, h, t], i) => {
    const y = 120 + i * 88;
    r += box(452, y, 24, n, 'qnum small');
    r += box(480, y, 424, h, 'h14');
    r += box(480, y + 22, 424, t, 'body12');
  });
  r += `<div class="abs hair" style="left:452pt;top:470pt;width:452pt"></div>`;
  r += box(452, 478, 452, 'γ = 0이면 추가 앵커 유인만 0이 되고, 목적지·퇴장 선택은 그대로 작동한다.', 'body12 strong');
  pages.push(slide({
    no: 7, section: 3,
    title: '가상 방문 그룹의 층 선택과 경계 기록',
    subtitle: '실제 평면과 에스컬레이터를 재현하지 않은 합성 9층 층 선택 모형(GAMA 2025.06.4) · 유량은 8개 상행 경계에서만 기록한다.',
    body: diagram + key + r,
    source: '출처: 수정 논문(v3) 3.1절, 식 (1)–(2), 표 2 · simulation/vertical_flow.gaml (목적지 효용, 퇴장 효용, 경계 통과 기록)',
  }));
}

// =========================================================================================== 08 AUFR worked example (three-floor crop)
{
  const u3 = cont[2].U_mean, u4 = cont[3].U_mean, a4 = V.rq1.aufr4;
  const oy = 112;
  const Y = (y) => y - oy;
  let g = '';
  const yF = { 5: 160, 4: 280, 3: 400 };
  g += L(40, Y(130), 300, Y(130), { stroke: C.hair, w: 0.8, dash: '3 3' });
  g += T(40, Y(124), '6F 이상 생략', { size: 9.5, fill: C.faint });
  g += L(40, Y(430), 300, Y(430), { stroke: C.hair, w: 0.8, dash: '3 3' });
  g += T(40, Y(446), '2F 이하 생략', { size: 9.5, fill: C.faint });
  for (const f of [5, 4, 3]) {
    g += L(40, Y(yF[f]), 380, Y(yF[f]), { stroke: '#9a9a9a', w: 1 });
    g += T(30, Y(yF[f]) + 4, `${f}F`, { size: 12, w: 600, fill: C.mid, anchor: 'end' });
  }
  const sc = 200 / u3;
  const bars = [[4, 220, u4, '4F → 5F'], [3, 340, u3, '3F → 4F']];
  for (const [b, y, u, lab] of bars) {
    g += R(40, Y(y) - 9, u * sc, 18, { fill: C.cont });
    g += T(40 + u * sc + 10, Y(y) - 2, `U${sb(b, 9.5)}`, { size: 14, w: 700, fill: C.ink });
    g += T(40 + u * sc + 34, Y(y) - 2, lab, { size: 11, fill: C.soft });
    g += T(40 + u * sc + 10, Y(y) + 18, `평균 ${nf0(u)}명`, { size: 11, fill: C.soft });
  }
  const crop = svg(56, oy, 392, 350, g, 'p8-crop');
  let r = '';
  r += box(492, 128, 412, `<span class="frac-lhs">AUFR<sub>4</sub> =</span><span class="frac"><span class="num">U<sub>4</sub></span><span class="den">U<sub>3</sub></span></span>`, 'formula-xl');
  r += box(492, 214, 412, `연속형 · γ = 0에서 반복별 U<sub>4</sub> ÷ U<sub>3</sub>의 평균 = <b>${f3(a4)}</b>`, 'body14');
  r += box(492, 236, 412, '200회 반복 · 각 반복 안에서 먼저 나눈 뒤 평균', 'note-s');
  const cautions = [
    ['같은 반복 <i>r</i>', '분자와 분모는 같은 시뮬레이션 반복에서 계산한다.'],
    ['인접 경계', '경계 <i>b</i>와 <i>b</i>' + MINUS + '1, 두 경계만 비교한다 (<i>b</i> = 2…8).'],
    ['연인원의 비율', '같은 방문객이 계속 올라간 비율(생존율)이 아니다.'],
    ['U<sub>1</sub>의 의미', '1F → 2F 통과량이며 건물 입장객 수가 아니다.'],
  ];
  cautions.forEach(([k, t], i) => {
    const y = 286 + i * 44;
    r += `<div class="abs hair" style="left:492pt;top:${y - 10}pt;width:412pt"></div>`;
    r += box(492, y, 110, k, 'rowhead');
    r += box(606, y, 298, t, 'body12');
  });
  pages.push(slide({
    no: 8, section: 3,
    title: '상행유량비(AUFR)는 바로 아래 경계와 비교한다',
    subtitle: '3–5층만 확대한 계산 예: 같은 반복 안에서 4F → 5F 통과량을 3F → 4F 통과량으로 나눈다.',
    body: crop + r,
    source: '출처: analysis/outputs/aik/aik_a1_profile.csv (실험 1, γ = 0, 연속형, 200회) · 막대 길이는 평균 통과량에 비례',
    trace: 'RQ1 · E1',
  }));
}

// =========================================================================================== 09 experiment design
{
  const e1 = V.runs.e1_cells, e2 = V.runs.e2_cells;
  const n = (id) => (e1[id] ?? e2[id]);
  let b = '';
  b += box(56, 118, 360, '실험 1 · 이동 저항 × 앵커 유인 계수', 'h15');
  b += box(420, 121, 32, 'E1', 'trace-s right');
  b += box(492, 118, 380, '실험 2 · 같은 앵커 총량의 배치 변형', 'h15');
  b += box(872, 121, 32, 'E2', 'trace-s right');
  // E1 matrix
  let g = '';
  const gx = [176, 232, 288, 344];
  g += T(0, 22, '이동 저항', { size: 10.5, fill: C.soft });
  ['0', '2', '4', '8'].forEach((gm, i) => g += T(gx[i] - 56 + 28, 22, `γ = ${gm}`, { size: 11.5, w: 600, fill: C.ink, anchor: 'middle' }));
  g += T(372, 22, '계', { size: 11.5, w: 600, fill: C.ink, anchor: 'middle' });
  g += L(0, 32, 396, 32, { stroke: C.ink, w: 0.9 });
  const rowsE1 = [['cont', '연속형', '저항 1.0 · 경계당 25초'], ['frag', '분절형', '저항 2.45 · 경계당 55초']];
  rowsE1.forEach(([c, lab, sub2], i) => {
    const y = 60 + i * 46;
    g += T(0, y, lab, { size: 12.5, w: 600, fill: C.ink });
    g += T(0, y + 15, sub2, { size: 10, fill: C.soft });
    let tot = 0;
    [0, 2, 4, 8].forEach((gm, j) => { const v = n(`aik_e1_g${gm}_${c}`); tot += v; g += T(gx[j] - 28, y + 4, nf0(v), { size: 13, fill: C.body, anchor: 'middle' }); });
    g += T(372, y + 4, nf0(tot), { size: 13, w: 600, fill: C.ink, anchor: 'middle' });
    g += L(0, y + 24, 396, y + 24, { stroke: C.hair });
  });
  const colTot = (gm) => n(`aik_e1_g${gm}_cont`) + n(`aik_e1_g${gm}_frag`);
  g += T(0, 158, '계', { size: 12, w: 600, fill: C.ink });
  [0, 2, 4, 8].forEach((gm, j) => g += T(gx[j] - 28, 158, nf0(colTot(gm)), { size: 12, fill: C.mid, anchor: 'middle' }));
  g += T(372, 158, nf0(V.runs.e1), { size: 14, w: 700, fill: C.ink, anchor: 'middle' });
  g += L(0, 140, 396, 140, { stroke: C.ink, w: 0.9 });
  b += svg(56, 150, 396, 170, g, 'p9-e1');
  b += box(56, 330, 396, '• 층별 앵커 비중 <i>x</i>: 반복마다 0–0.5 균등분포에서 추출<br>• γ: 실측 집객계수가 아닌 민감도 분석의 가정값<br>• 칸의 숫자 = 반복 횟수', 'body12 mid');
  // E2 matrix
  let h = '';
  const hx = [204, 266, 328];
  h += T(0, 22, '배치', { size: 10.5, fill: C.soft });
  [['γ = 4', '연속형'], ['γ = 4', '분절형'], ['γ = 0 대조', '연속형']].forEach(([a, c2], i) => {
    h += T(hx[i], 10, a, { size: 11.5, w: 600, fill: C.ink, anchor: 'middle' });
    h += T(hx[i], 25, c2, { size: 10.5, fill: C.soft, anchor: 'middle' });
  });
  h += T(388, 22, '계', { size: 11.5, w: 600, fill: C.ink, anchor: 'middle' });
  h += L(0, 32, 412, 32, { stroke: C.ink, w: 0.9 });
  PATTERNS.forEach((p, i) => {
    const y = 56 + i * 30;
    h += T(0, y, p, { size: 12.5, w: 600, fill: C.ink });
    h += T(72, y, PNAME[p], { size: 10.5, fill: C.soft });
    const ids = [`aik_e2_${p.toLowerCase()}_g4_cont`, `aik_e2_${p.toLowerCase()}_g4_frag`, `aik_e2_${p.toLowerCase()}_g0_cont`];
    let rowTot = 0;
    ids.forEach((id, j) => { const v = n(id); rowTot += v || 0; h += T(hx[j], y, v ? nf0(v) : '—', { size: 13, fill: v ? C.body : C.faint, anchor: 'middle' }); });
    h += T(388, y, nf0(rowTot), { size: 13, w: 600, fill: C.ink, anchor: 'middle' });
    h += L(0, y + 11, 412, y + 11, { stroke: C.hair });
  });
  const e2col = (suffix) => PATTERNS.reduce((s, p) => s + (n(`aik_e2_${p.toLowerCase()}_${suffix}`) || 0), 0);
  h += L(0, 158, 412, 158, { stroke: C.ink, w: 0.9 });
  h += T(0, 176, '계', { size: 12, w: 600, fill: C.ink });
  ['g4_cont', 'g4_frag', 'g0_cont'].forEach((s, j) => h += T(hx[j], 176, nf0(e2col(s)), { size: 12, fill: C.mid, anchor: 'middle' }));
  h += T(388, 177, nf0(V.runs.e2), { size: 14, w: 700, fill: C.ink, anchor: 'middle' });
  b += svg(492, 150, 412, 184, h, 'p9-e2');
  b += box(492, 344, 412, '• 1층 0.05 고정 · 2–9층 앵커 비중 합 1.60 (층별 값은 15쪽)<br>• γ = 0 대조군: UNIFORM · TOP1, 연속형', 'body12 mid');
  b += `<div class="abs blackrule" style="left:56pt;top:430pt;width:848pt"></div>`;
  b += box(56, 442, 848, `실험 1 ${nf0(V.runs.e1)}회 + 실험 2 ${nf0(V.runs.e2)}회 = 총 ${nf0(V.runs.total)}회 · 반복당 4일 · 누락 경계 0 · U = 0인 경계 0`, 'body14 strong');
  pages.push(slide({
    no: 9, section: 3,
    title: '이동 저항과 앵커 배치를 나누어 비교했다',
    subtitle: '실험 1은 이동 저항과 유인 계수를 교차하고, 실험 2는 앵커 총량을 고정한 채 배치만 바꾼다.',
    body: b,
    source: '출처: analysis/outputs/aik/aik_cells.csv · aik_checks.csv · analysis/R/experiments/aik_program_circulation.R',
    trace: 'E1 · E2',
  }));
}

// =========================================================================================== 10 baseline absolute flow
{
  const oy = 112, ox = 56;
  const xb = (b) => 120 + (b - 1) * 66;
  const yv = lin(0, 14000, 340, 30);
  let g = '';
  g += L(64, 340, xb(8) + 14, 340, { stroke: C.ink, w: 0.9 });
  g += L(64, 30, 64, 340, { stroke: C.ink, w: 0.9 });
  for (const t of [0, 4000, 8000, 12000]) {
    g += L(60, yv(t), 64, yv(t), { stroke: C.ink, w: 0.9 });
    g += T(56, yv(t) + 4, t === 0 ? '0' : nf0(t), { size: 10.5, fill: C.soft, anchor: 'end' });
  }
  g += T(0, 14, '상행 통과량 U (명, 4일 합계)', { size: 10.5, fill: C.soft });
  for (let b = 1; b <= 8; b += 1) {
    g += L(xb(b), 340, xb(b), 344, { stroke: C.ink, w: 0.9 });
    g += T(xb(b), 358, `U${sb(b, 8)}`, { size: 11, w: 600, fill: C.ink, anchor: 'middle' });
    g += T(xb(b), 375, `${b}F→${b + 1}F`, { size: 9.5, fill: C.soft, anchor: 'middle' });
  }
  const cpts = cont.map((d) => [xb(d.b), yv(d.U_mean)]);
  const fpts = frag.map((d) => [xb(d.b), yv(d.U_mean)]);
  g += P(poly(fpts), { stroke: C.frag, w: 2, dash: '6 4' });
  g += P(poly(cpts), { stroke: C.cont, w: 2.2 });
  fpts.forEach(([x, y]) => g += square(x, y, 3.2, { stroke: C.frag }));
  cpts.forEach(([x, y]) => g += Ci(x, y, 3.6, { fill: '#fff', stroke: C.cont, sw: 1.6 }));
  // direct labels
  g += T(xb(1) - 10, cpts[0][1] + 4, nf0(cont[0].U_mean), { size: 12.5, w: 700, fill: C.cont, anchor: 'end' });
  g += T(xb(1) - 10, fpts[0][1] + 4, nf0(frag[0].U_mean), { size: 12.5, w: 700, fill: C.frag, anchor: 'end' });
  g += T(xb(2) + 12, cpts[1][1] - 8, '연속형', { size: 12, w: 600, fill: C.cont });
  g += T(xb(2) - 20, fpts[1][1] + 22, '분절형', { size: 12, w: 600, fill: C.frag });
  g += T(xb(8) + 22, cpts[7][1] - 6, nf0(cont[7].U_mean), { size: 12.5, w: 700, fill: C.cont });
  g += T(xb(8) + 22, cpts[7][1] + 10, nf0(frag[7].U_mean), { size: 12.5, w: 700, fill: C.frag });
  // first-boundary gap bracket
  g += L(xb(1) + 14, cpts[0][1], xb(1) + 14, fpts[0][1], { stroke: C.frag, w: 1 });
  g += L(xb(1) + 10, cpts[0][1], xb(1) + 14, cpts[0][1], { stroke: C.frag, w: 1 });
  g += L(xb(1) + 10, fpts[0][1], xb(1) + 14, fpts[0][1], { stroke: C.frag, w: 1 });
  g += T(xb(1) + 20, (cpts[0][1] + fpts[0][1]) / 2 + 4, `${signed1(V.rq1.frag_first_gap)}%`, { size: 12, w: 700, fill: C.frag });
  const chart = svg(ox, oy, 640, 380, g, 'p10-U');
  let r = '';
  r += box(728, 128, 176, `U<sub>8</sub> / U<sub>1</sub> = ${pct1(V.rq1.u8u1_mean_rep)}%`, 'stat');
  r += box(728, 158, 176, '연속형 · 반복별 비율의 평균. 첫 경계 대비 마지막 경계의 크기', 'body115 mid');
  r += `<div class="abs hair" style="left:728pt;top:214pt;width:176pt"></div>`;
  r += box(728, 226, 176, `분절형 첫 경계 ${signed1(V.rq1.frag_first_gap)}%`, 'h14 frag');
  r += box(728, 248, 176, `${nf0(frag[0].U_mean)}명 vs ${nf0(cont[0].U_mean)}명. 건물 전체 입장객의 감소율이 아니다.`, 'body115 mid');
  r += `<div class="abs hair" style="left:728pt;top:304pt;width:176pt"></div>`;
  r += box(728, 316, 176, 'U<sub>1</sub>은 1F → 2F 경계 통과량이며 건물 입장객 수가 아니다.', 'body115 mid');
  pages.push(slide({
    no: 10, section: 4,
    title: '추가 유인이 없어도 위층일수록 통과량이 줄었다',
    subtitle: 'γ = 0 · 실험 1 · 조건별 200회 반복 평균 · U = 반복당 4일 합산 상행 통과 연인원(고유 방문객 아님)',
    body: chart + r,
    source: '출처: analysis/outputs/aik/aik_a1_profile.csv (U_mean, RUI_mean) · aik_boundary_rep.csv',
    trace: 'RQ1 · E1',
  }));
}

// =========================================================================================== 11 baseline local AUFR
{
  const oy = 112;
  const xb = (b) => 100 + (b - 2) * 80;
  const yv = lin(0.45, 0.75, 330, 30);
  let g = '';
  g += L(48, 330, 600, 330, { stroke: C.ink, w: 0.9 });
  g += L(48, 30, 48, 330, { stroke: C.ink, w: 0.9 });
  for (const t of [0.5, 0.6, 0.7]) {
    g += L(44, yv(t), 48, yv(t), { stroke: C.ink, w: 0.9 });
    g += T(40, yv(t) + 4, `${Math.round(t * 100)}%`, { size: 10.5, fill: C.soft, anchor: 'end' });
  }
  g += T(0, 14, 'AUFR (반복별 비율의 평균)', { size: 10.5, fill: C.soft });
  for (let b = 2; b <= 8; b += 1) {
    g += L(xb(b), 330, xb(b), 334, { stroke: C.ink, w: 0.9 });
    g += T(xb(b), 348, `U${sb(b, 8)}/U${sb(b - 1, 8)}`, { size: 11, w: 600, fill: C.ink, anchor: 'middle' });
    g += T(xb(b), 365, `${b}F→${b + 1}F`, { size: 9.5, fill: C.soft, anchor: 'middle' });
  }
  const band = (rows, color) => {
    const up = rows.slice(1).map((d) => [xb(d.b), yv(d.AUFR_q975)]);
    const dn = rows.slice(1).map((d) => [xb(d.b), yv(d.AUFR_q025)]).reverse();
    return P(poly(up.concat(dn)) + ' Z', { fill: color, op: 0.09 });
  };
  g += band(frag, C.frag) + band(cont, C.cont);
  // constant-ratio reference
  const ref = V.rq1.geo_ratio;
  g += L(48, yv(ref), 600, yv(ref), { stroke: C.faint, w: 0.9, dash: '4 3' });
  const cp = cont.slice(1).map((d) => [xb(d.b), yv(d.AUFR_mean)]);
  const fp = frag.slice(1).map((d) => [xb(d.b), yv(d.AUFR_mean)]);
  g += P(poly(fp), { stroke: C.frag, w: 2, dash: '6 4' });
  g += P(poly(cp), { stroke: C.cont, w: 2.2 });
  fp.forEach(([x, y]) => g += square(x, y, 3.2, { stroke: C.frag }));
  cp.forEach(([x, y]) => g += Ci(x, y, 3.6, { fill: '#fff', stroke: C.cont, sw: 1.6 }));
  g += T(xb(2) - 10, cp[0][1] + 4, '연속형', { size: 12, w: 600, fill: C.cont, anchor: 'end' });
  g += T(xb(2) - 10, fp[0][1] + 10, '분절형', { size: 12, w: 600, fill: C.frag, anchor: 'end' });
  // last local AUFR label
  const last = cont[7].AUFR_mean;
  g += L(xb(8) + 6, cp[6][1], xb(8) + 20, cp[6][1] - 18, { stroke: C.cont, w: 0.9 });
  g += T(xb(8) + 24, cp[6][1] - 30, `${pct1(last)}%`, { size: 15, w: 700, fill: C.cont });
  g += T(xb(8) + 24, cp[6][1] - 16, '마지막 국소 AUFR (U₈/U₇)', { size: 10, fill: C.cont, noaudit: true });
  g += T(xb(8) + 14, fp[6][1] + 22, `분절형 ${pct1(frag[7].AUFR_mean)}%`, { size: 10, fill: C.frag });
  g += T(608, yv(ref) - 4, '일정 비율로', { size: 10, fill: C.soft });
  g += T(608, yv(ref) + 10, `줄었다면 ${pct1(ref)}%`, { size: 10, fill: C.soft });
  const chart = svg(56, oy, 680, 372, g, 'p11-AUFR');
  let r = '';
  r += box(760, 128, 144, '일정 비율 감쇠 기각', 'h14');
  r += box(760, 150, 144, `로그 선형 모형 대비 경계 요인 모형 F = ${nf0(V.rq1.shape.cont.F)}(연속형) · ${nf0(V.rq1.shape.frag.F)}(분절형), p &lt; 0.001`, 'body115 mid');
  r += `<div class="abs hair" style="left:760pt;top:238pt;width:144pt"></div>`;
  r += box(760, 250, 144, `${pct1(last)}%는 U<sub>8</sub>/U<sub>1</sub>(${pct1(V.rq1.u8u1_mean_rep)}%)이 아니다`, 'h14');
  r += box(760, 294, 144, '국소 비율은 바로 아래 경계 대비, U<sub>8</sub>/U<sub>1</sub>은 첫 경계 대비 값이다.', 'body115 mid');
  pages.push(slide({
    no: 11, section: 4,
    title: '감소 비율은 경계마다 달랐다',
    subtitle: 'γ = 0 · AUFR<sub><i>b</i></sub> = U<sub><i>b</i></sub> / U<sub><i>b</i>' + MINUS + '1</sub>(같은 반복) · 점: 200회 평균 · 띠: 반복별 값의 2.5–97.5% 범위 · 점선: (U<sub>8</sub>/U<sub>1</sub>)<sup>1/7</sup>',
    body: chart + r,
    source: '출처: analysis/outputs/aik/aik_a1_profile.csv (AUFR_mean, AUFR_q025, AUFR_q975) · aik_a1_shape.csv',
    trace: 'RQ1 · E1',
  }));
}

// =========================================================================================== 12 adjacent-floor program & AUFR (coefficient plot)
{
  const oy = 112;
  const xm = lin(0.98, 1.22, 120, 500);
  const rows = [['0', M.cont_g0, true], ['2', M.cont_g2], ['4', M.cont_g4], ['8', M.cont_g8]];
  const ry = (i) => 64 + i * 72;
  let g = '';
  for (const t of [1.0, 1.05, 1.1, 1.15, 1.2]) {
    g += L(xm(t), 330, xm(t), 334, { stroke: C.ink, w: 0.9 });
    g += T(xm(t), 348, `×${t.toFixed(2)}`, { size: 11, w: 600, fill: C.ink, anchor: 'middle' });
    g += T(xm(t), 365, t === 1 ? '0%' : `+${Math.round((t - 1) * 100)}%`, { size: 9.5, fill: C.soft, anchor: 'middle' });
  }
  g += L(xm(0.98), 330, xm(1.22), 330, { stroke: C.ink, w: 0.9 });
  g += L(xm(1), 26, xm(1), 330, { stroke: C.faint, w: 1, dash: '4 3' });
  g += T(xm(1) + 5, 22, '관계 없음 (×1.00)', { size: 10, fill: C.soft });
  g += T(xm(0.98), 384, 'AUFR 상대 배수 (Δ<tspan font-style="italic">x</tspan> +0.1당)', { size: 10.5, fill: C.soft });
  rows.forEach(([gm, m, ctrl], i) => {
    const y = ry(i);
    g += T(0, y + 4, `γ = ${gm}`, { size: 13, w: 600, fill: ctrl ? C.soft : C.ink });
    if (ctrl) g += T(0, y + 19, '대조', { size: 10, fill: C.soft });
    g += L(xm(m.lo), y, xm(m.hi), y, { stroke: ctrl ? C.faint : C.cont, w: 2.4 });
    g += L(xm(m.lo), y - 6, xm(m.lo), y + 6, { stroke: ctrl ? C.faint : C.cont, w: 1.2 });
    g += L(xm(m.hi), y - 6, xm(m.hi), y + 6, { stroke: ctrl ? C.faint : C.cont, w: 1.2 });
    g += Ci(xm(m.rr), y, 5, { fill: ctrl ? '#fff' : C.cont, stroke: ctrl ? C.faint : C.cont, sw: 1.4 });
    // value column
    const pctTxt = `${signed1(m.rr - 1)}%`;
    g += T(528, y + 1, `×${f3(m.rr)}`, { size: 14, w: 700, fill: ctrl ? C.soft : C.ink });
    g += T(586, y + 1, `(${pctTxt})`, { size: 12, w: 600, fill: ctrl ? C.soft : C.cont });
    g += T(528, y + 17, `95% CI ${f3(m.lo)} – ${f3(m.hi)}${ctrl ? ' · 1 포함' : ''}`, { size: 10.5, fill: C.soft });
  });
  const chart = svg(56, oy, 650, 392, g, 'p12-mult');
  let r = '';
  r += box(736, 128, 168, '퍼센트포인트가 아닌 상대 변화', 'h14');
  r += box(736, 170, 168, 'AUFR 0.60에 ×1.109를 적용하면 0.665가 된다. 증가는 +10.9%이고 +10.9%p가 아니다.', 'body115 mid');
  r += `<div class="abs hair" style="left:736pt;top:250pt;width:168pt"></div>`;
  r += box(736, 262, 168, '모형 안의 연관', 'h14');
  r += box(736, 284, 168, '목적지 효용에 γ·<i>x</i>가 들어 있는 모형에서 나타난 관계이며, 현장에서 검증된 효과가 아니다. γ = 0이면 신뢰구간이 1을 포함한다.', 'body115 mid');
  pages.push(slide({
    no: 12, section: 4,
    title: '인접층 앵커 차이가 클수록 상행유량비가 높았다',
    subtitle: '연속형 · Δ<i>x</i> = 바로 위층 ' + MINUS + ' 바로 아래층 앵커 비중 · Δ<i>x</i>가 0.1 커질 때 AUFR의 상대 배수와 95% 신뢰구간(반복 군집-강건)',
    body: chart + r,
    source: '출처: analysis/outputs/aik/aik_a2_theta.csv · 경계 고정효과와 10Δ<i>x</i>를 넣은 log AUFR 회귀, 반복 단위 군집 표준오차(HC1), <i>t</i>(199)',
    trace: 'RQ2 · E1',
  }));
}

// =========================================================================================== 13 absolute-flow auxiliary (dot plot)
{
  const oy = 112;
  const xv = lin(0, 0.8, 236, 596);
  const preds = [
    ['x_upper', '바로 위층 앵커 비중', '<tspan font-style="italic">x</tspan>' + sb('upper', 8.5)],
    ['M_above', '경계 위 모든 층의 평균 비중', `M${sb('<tspan font-style="italic">b</tspan>', 8.5)}`],
    ['delta', '인접층 비중 차이', `Δ<tspan font-style="italic">x</tspan>${sb('<tspan font-style="italic">b</tspan>', 8.5)}`],
  ];
  const conds = [['cont', 2], ['cont', 4], ['cont', 8], ['frag', 2], ['frag', 4], ['frag', 8]];
  let g = '';
  for (const t of [0, 0.2, 0.4, 0.6, 0.8]) {
    g += L(xv(t), 300, xv(t), 304, { stroke: C.ink, w: 0.9 });
    g += T(xv(t), 318, `${Math.round(t * 100)}%`, { size: 10.5, fill: C.soft, anchor: 'middle' });
  }
  g += L(xv(0), 300, xv(0.8), 300, { stroke: C.ink, w: 0.9 });
  g += T(xv(0), 338, '기준 모형 대비 잔여 deviance 감소율 (U, 준포아송)', { size: 10.5, fill: C.soft });
  preds.forEach(([key, name, sym], i) => {
    const y = 56 + i * 82;
    g += T(0, y, name, { size: 12.5, w: 600, fill: C.ink });
    g += T(0, y + 18, sym, { size: 12, fill: C.mid });
    const vals = conds.map(([c, gm]) => DEV[`${c}_g${gm}_${key}`]);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    g += L(xv(lo), y, xv(hi), y, { stroke: C.ghost, w: 3, cap: 'round' });
    conds.forEach(([c, gm]) => {
      if (c === 'cont' && gm === 4) return;
      g += Ci(xv(DEV[`${c}_g${gm}_${key}`]), y, 3.6, { fill: '#fff', stroke: '#8f8f8f', sw: 1.1 });
    });
    const v = DEV[`cont_g4_${key}`];
    g += Ci(xv(v), y, 6, { fill: C.cont });
    g += T(xv(v), y - 12, `${pct1(v)}%`, { size: 14, w: 700, fill: C.cont, anchor: 'middle' });
    g += T(xv(0.8) + 8, y + 4, `${Math.round(lo * 100)}–${Math.round(hi * 100)}%`, { size: 10.5, fill: C.soft });
  });
  // minimal key
  g += Ci(4, 366, 5, { fill: C.cont });
  g += T(14, 370, 'γ = 4 · 연속형', { size: 10.5, fill: C.mid });
  g += Ci(112, 366, 3.6, { fill: '#fff', stroke: '#8f8f8f', sw: 1.1 });
  g += T(121, 370, '나머지 다섯 조건 (γ = 2·4·8 × 연속형·분절형)', { size: 10.5, fill: C.mid });
  g += T(xv(0.8) + 8, 30, '여섯 조건 범위', { size: 9.5, fill: C.faint });
  const chart = svg(56, oy, 660, 380, g, 'p13-dev');
  let r = '';
  r += box(744, 128, 160, '절대 유량 U의 보조 분석', 'h14');
  r += box(744, 150, 160, '앞 장의 AUFR 배수와 다른 통계량이다. 두 결과를 하나로 합치지 않는다.', 'body115 mid');
  r += `<div class="abs hair" style="left:744pt;top:222pt;width:160pt"></div>`;
  r += box(744, 234, 160, '세 값은 더하지 않는다', 'h14');
  r += box(744, 256, 160, '변수를 하나씩 따로 추가한 모형의 결과이며, 보행자의 60.1%가 특정 앵커 때문에 이동했다는 뜻이 아니다.', 'body115 mid');
  r += `<div class="abs hair" style="left:744pt;top:346pt;width:160pt"></div>`;
  r += box(744, 358, 160, '여섯 조건 모두 <i>x</i><sub>upper</sub> &gt; M<sub><i>b</i></sub> &gt; Δ<i>x</i><sub><i>b</i></sub> 순서였다.', 'body115 mid');
  pages.push(slide({
    no: 13, section: 4,
    title: '절대 유량은 바로 위층 비중과 더 밀접했다',
    subtitle: '보조 분석 · 종속변수 U · 경계·반복 고정효과 기준 모형에 변수 하나를 더했을 때 잔여 deviance가 줄어든 비율',
    body: chart + r,
    source: '출처: analysis/outputs/aik/aik_a2b_constructs.csv (dev_explained) · 감소율 = (기준 deviance ' + MINUS + ' 추가 후 deviance) / 기준 deviance',
    trace: 'RQ2 · E1',
  }));
}

// =========================================================================================== 14 moderation by friction (forest plot)
{
  const oy = 112;
  const xe = lin(-0.1, 0.15, 84, 414);
  const gs = [2, 4, 8];
  const ry = (i) => 62 + i * 78;
  let g = '';
  for (const t of [-0.1, -0.05, 0, 0.05, 0.1, 0.15]) {
    g += L(xe(t), 286, xe(t), 290, { stroke: C.ink, w: 0.9 });
    g += T(xe(t), 304, `${Math.round(t * 100)}%`.replace('-', MINUS), { size: 10.5, fill: C.soft, anchor: 'middle' });
  }
  g += L(xe(-0.1), 286, xe(0.15), 286, { stroke: C.ink, w: 0.9 });
  g += L(xe(0), 24, xe(0), 286, { stroke: C.ink, w: 1 });
  g += T(xe(0) + 5, 20, '0 = 기울기 감소 없음', { size: 10, fill: C.soft });
  g += T(xe(-0.1), 322, '분절형의 AUFR 기울기 잠식률 (점: 추정값, 선: 95% 신뢰구간)', { size: 10.5, fill: C.soft });
  gs.forEach((gm, i) => {
    const e = ER[`g${gm}`];
    const y = ry(i);
    const col = e.includes_zero ? C.soft : C.ink;
    g += T(0, y + 4, `γ = ${gm}`, { size: 13, w: 600, fill: C.ink });
    g += L(xe(e.lo), y, xe(e.hi), y, { stroke: col, w: 2.4 });
    g += L(xe(e.lo), y - 6, xe(e.lo), y + 6, { stroke: col, w: 1.2 });
    g += L(xe(e.hi), y - 6, xe(e.hi), y + 6, { stroke: col, w: 1.2 });
    g += Ci(xe(e.est), y, 5, e.includes_zero ? { fill: '#fff', stroke: C.ink, sw: 1.5 } : { fill: C.ink });
    g += T(440, y - 2, `${pct1(e.est)}%`, { size: 14, w: 700, fill: C.ink });
    g += T(486, y - 2, `[${pct1(e.lo)}, ${pct1(e.hi)}]`, { size: 11.5, fill: C.mid });
    g += T(440, y + 15, e.includes_zero ? '신뢰구간이 0 포함 · 감소를 명확히 검출하지 못함' : '신뢰구간이 0 제외 · 감소 검출', { size: 10.5, w: e.includes_zero ? 400 : 600, fill: e.includes_zero ? C.soft : C.ink });
  });
  const chart = svg(56, oy, 660, 352, g, 'p14-erosion');
  // level-gap side panel
  let h = '';
  const xg = lin(0, 0.25, 56, 124);
  h += T(0, 12, '절대 유량 수준', { size: 13, w: 600, fill: C.ink });
  h += T(0, 28, '분절형 첫 경계 U의 차이', { size: 10.5, fill: C.soft });
  [0, 2, 4, 8].forEach((gm, i) => {
    const v = GAP[`g${gm}`];
    const y = 60 + i * 34;
    h += T(0, y + 4, `γ = ${gm}`, { size: 11.5, w: 600, fill: C.ink });
    h += R(xg(0), y - 6, xg(-v) - xg(0), 12, { fill: C.frag });
    h += T(xg(-v) + 4, y + 4, `${signed1(v)}%`, { size: 11.5, w: 600, fill: C.frag });
  });
  h += T(0, 206, '모든 γ에서 분절형이 낮았다.', { size: 10.5, fill: C.mid });
  const side = svg(736, 128, 168, 220, h, 'p14-level');
  const note = `<div class="abs hair" style="left:56pt;top:452pt;width:848pt"></div>`
    + box(56, 462, 848, '0을 포함한다는 것은 ‘효과가 없다’는 증명이 아니라, 이 반복 수에서 감소를 명확히 검출하지 못했다는 뜻이다. 유량 수준 차이와 기울기 변화는 서로 다른 결과다.', 'body12 strong');
  pages.push(slide({
    no: 14, section: 5,
    title: '이동 저항이 커져도 관계가 늘 약해지지는 않았다',
    subtitle: '잠식률 = 1 ' + MINUS + ' (분절형 기울기 ÷ 연속형 기울기) · Δ<i>x</i>에 대한 원척도 AUFR 기울기 · 95% 신뢰구간(반복 군집 부트스트랩 2,000회)',
    body: chart + side + note,
    source: '출처: analysis/outputs/aik/aik_a3_moderation.csv (erosion, erosion_lo, erosion_hi) · aik_boundary_rep.csv (첫 경계 U 평균)',
    trace: 'RQ3 · E1',
  }));
}

// =========================================================================================== 15 anchor placement matrix
{
  const colX = [112, 310, 508, 706];
  const rowY = (f) => 182 + (9 - f) * 28;
  const scale = 128 / 0.85;
  let b = '';
  let g = '';
  const oy = 112;
  const Y = (y) => y - oy;
  PATTERNS.forEach((p, i) => {
    const x = colX[i] - 56;
    g += T(x, Y(128), p, { size: 14, w: 700, fill: C.ink });
    g += T(x, Y(146), PNAME[p], { size: 11, fill: C.soft });
  });
  g += L(0, Y(160), 848, Y(160), { stroke: C.ink, w: 0.9 });
  for (let f = 9; f >= 1; f -= 1) {
    const y = f === 1 ? rowY(1) + 14 : rowY(f);
    g += T(0, Y(y) + 4, `${f}F`, { size: 12, w: 600, fill: f === 1 ? C.faint : C.ink });
    if (f !== 1 && f !== 2) g += L(28, Y(y) + 14, 848, Y(y) + 14, { stroke: C.hair, w: 0.6 });
    PATTERNS.forEach((p, i) => {
      const w = PL[p].weights[f - 1];
      const x = colX[i] - 56;
      const strong = w >= 0.4;
      g += R(x, Y(y) - 6, w * scale, 12, { fill: f === 1 ? C.barLight : (strong ? C.bar : '#6f6f6f') });
      const lab = Math.abs(w - 0.107143) < 1e-6 ? '0.107' : w.toFixed(2);
      g += T(x + w * scale + 6, Y(y) + 4, lab, { size: 11.5, w: strong ? 700 : 400, fill: f === 1 ? C.faint : (strong ? C.ink : C.mid) });
    });
    if (f === 2) g += L(28, Y(y) + 14, 848, Y(y) + 14, { stroke: C.rule, w: 0.75, dash: '3 2' });
  }
  g += L(0, Y(436), 848, Y(436), { stroke: C.ink, w: 0.9 });
  PATTERNS.forEach((p, i) => {
    const x = colX[i] - 56;
    const s = PL[p].weights.slice(1).reduce((a, c) => a + c, 0);
    g += T(x, Y(456), `Σ 2–9F = ${s.toFixed(2)}`, { size: 12.5, w: 700, fill: C.ink });
  });
  b += svg(56, oy, 848, 360, g, 'p15-matrix');
  b += box(56, 478, 848, '1F는 모든 배치에서 0.05로 고정(회색) · TOP1의 9층 0.85는 실험 1의 층별 범위(0–0.5)를 넘는 비교 시나리오 · TOP1 합계는 소수 반올림으로 1.600001', 'note-s');
  pages.push(slide({
    no: 15, section: 5,
    title: '같은 앵커 총량을 네 가지로 배치했다',
    subtitle: '실험 2 입력값 · 층별 앵커 비중(막대 길이는 네 배치 모두 같은 척도) · 2–9층 합은 모두 1.60',
    body: b,
    source: '출처: analysis/R/experiments/aik_program_circulation.R (PATTERN_X) · analysis/outputs/aik/aik_checks.csv (budget_S01_S08)',
    trace: 'RQ4 · E2',
  }));
}

// =========================================================================================== 16 anchor-placement results (small multiples + table)
{
  const oy = 112;
  const panelX = [44, 192, 340, 488];
  const pw = 136;
  const yv = lin(0, 1.05, 330, 60);
  const anchorB = { TOP1: [8], STEP3: [2, 5, 8], UNIFORM: [], LOW3: [1, 2, 3] };
  let g = '';
  for (const t of [0, 0.5, 1]) g += T(36, yv(t) + 4, `${Math.round(t * 100)}%`, { size: 10.5, fill: C.soft, anchor: 'end' });
  PATTERNS.forEach((p, i) => {
    const px = panelX[i];
    const xb = (b) => px + 8 + (b - 1) * (120 / 7);
    g += T(px, 18, p, { size: 13, w: 700, fill: C.ink });
    g += T(px, 34, PNAME[p], { size: 10.5, fill: C.soft });
    g += L(px, 330, px + pw, 330, { stroke: C.ink, w: 0.9 });
    g += L(px, yv(1), px + pw, yv(1), { stroke: C.hair, w: 0.6 });
    g += L(px, yv(0.5), px + pw, yv(0.5), { stroke: C.hair, w: 0.6 });
    PATTERNS.filter((q) => q !== p).forEach((q) => {
      g += P(poly(PL[q].traj.map((d) => [xb(d.b), yv(d.RUI_mean)])), { stroke: C.ghost, w: 1 });
    });
    const pts = PL[p].traj.map((d) => [xb(d.b), yv(d.RUI_mean)]);
    g += P(poly(pts), { stroke: C.cont, w: 2.2 });
    pts.forEach(([x, y]) => g += Ci(x, y, 2.6, { fill: C.cont }));
    for (const ab of anchorB[p]) g += P(`M${xb(ab) - 4},${342} L${xb(ab)},${335} L${xb(ab) + 4},${342} Z`, { fill: C.ink });
    g += T(xb(1), 356, '1', { size: 9.5, fill: C.soft, anchor: 'middle' });
    g += T(xb(8), 356, '8', { size: 9.5, fill: C.soft, anchor: 'middle' });
    g += T(px + pw, 18, `T ${pct1(PL[p].T)}%`, { size: 13, w: 700, fill: C.cont, anchor: 'end' });
  });
  g += T(44, 376, '경계 b (1 = 1F→2F … 8 = 8F→9F)', { size: 10, fill: C.soft });
  g += P('M300,378 L304,371 L308,378 Z', { fill: C.ink });
  g += T(314, 378, '앵커 비중 0.45 이상인 층으로 들어가는 경계', { size: 10, fill: C.soft });
  // TOP1 rebound annotation inside the TOP1 panel
  const tp = PL.TOP1.traj;
  g += T(panelX[0] + pw, yv(0.95), '상층부 재증가', { size: 9.5, w: 600, fill: C.mid, anchor: 'end' });
  g += T(panelX[0] + pw, yv(0.95) + 15, `U${sb(6, 7.5)} ${nf0(tp[5].U_mean)} → U${sb(7, 7.5)} ${nf0(tp[6].U_mean)}`, { size: 9.5, fill: C.mid, anchor: 'end' });
  g += T(panelX[0] + pw, yv(0.95) + 30, `→ U${sb(8, 7.5)} ${nf0(tp[7].U_mean)}명`, { size: 9.5, fill: C.mid, anchor: 'end' });
  const chart = svg(56, oy, 640, 384, g, 'p16-traj');
  // final-value table
  let h = '';
  h += T(0, 12, '마지막 경계 8F → 9F', { size: 12.5, w: 600, fill: C.ink });
  h += T(0, 42, '배치', { size: 10.5, fill: C.soft });
  h += T(118, 42, 'T', { size: 10.5, fill: C.soft, anchor: 'end' });
  h += T(184, 42, `U${sb(8, 8)} (명)`, { size: 10.5, fill: C.soft, anchor: 'end' });
  h += L(0, 50, 184, 50, { stroke: C.ink, w: 0.9 });
  PATTERNS.forEach((p, i) => {
    const y = 74 + i * 30;
    const bold = p === 'TOP1' ? 700 : 400;
    h += T(0, y, p, { size: 12.5, w: bold, fill: C.ink });
    h += T(118, y, `${pct1(PL[p].T)}%`, { size: 12.5, w: bold, fill: C.ink, anchor: 'end' });
    h += T(184, y, nf0(PL[p].U8), { size: 12.5, w: bold, fill: C.ink, anchor: 'end' });
    h += L(0, y + 10, 184, y + 10, { stroke: C.hair });
  });
  const table = svg(720, 124, 184, 200, h, 'p16-table');
  let r = '';
  r += box(720, 336, 184, 'T와 U<sub>8</sub>은 도달 확률이나 고유 방문객 수가 아니다(U<sub>8</sub> = 4일 합산 연인원).', 'body11 mid');
  r += box(720, 380, 184, 'TOP1–STEP3, STEP3–UNIFORM 차이: Holm 보정 후 <i>p</i> &lt; 0.001', 'body11 mid');
  r += `<div class="abs hair" style="left:720pt;top:420pt;width:184pt"></div>`;
  r += box(720, 428, 184, '혼잡·수용 한계가 없는 모형에서 네 배치를 비교한 결과이며 실제 최적 배치가 아니다.', 'body11 strong');
  pages.push(slide({
    no: 16, section: 5,
    title: '네 배치 중 최상층 집중형의 상단 유량이 가장 컸다',
    subtitle: 'γ = 4 · 연속형 · 100회 평균 · RUI<sub><i>b</i></sub> = U<sub><i>b</i></sub> / U<sub>1</sub>(첫 경계 대비 상대 유량) · T = RUI<sub>8</sub> = U<sub>8</sub> / U<sub>1</sub> · 회색 선은 다른 세 배치',
    body: chart + table + r,
    source: '출처: analysis/outputs/aik/aik_e2_profile.csv (RUI_mean, U_mean) · aik_a4_reach.csv (T_mean) · aik_a4_contrasts.csv (p_holm)',
    trace: 'RQ4 · E2',
  }));
}

// =========================================================================================== 17 limits and validation tasks
{
  const rows = [
    ['실제 평면과 수직동선 기하가 없다', '비공간적 층 선택 모형이므로 평면 우회, 방향 전환, 시야, 수직동선 위치의 효과를 다루지 못한다.', '기하 기반 수직동선 모형', '실제 평면과 에스컬레이터·엘리베이터의 위치·연결을 반영'],
    ['혼잡과 수용량이 없다', '유량이 커져도 대기·병목·수용 한계가 계산되지 않아, TOP1의 높은 유량이 실현 가능한지 알 수 없다.', '혼잡·용량 모형', '대기·병목·수용 한계를 넣고 배치 순위가 유지되는지 확인'],
    ['유인 계수 γ와 TOP1의 9층 0.85는 가정값이다', 'γ는 실측 집객계수가 아니며, 0.85는 실험 1의 층별 범위(0–0.5)를 벗어난다.', '실측 자료 보정', '층별 통과 집계·목적지 선택 자료로 γ와 앵커 비중을 보정'],
    ['경계 통과량은 고유 방문객 수가 아니다', '같은 사람의 반복 통과를 포함한 연인원이므로 T와 U를 도달 확률·체류·소비로 읽을 수 없다.', '실측 통과·궤적 비교', '실제 경계 통과 집계와 개인 이동 궤적 자료로 외부 검증'],
  ];
  let b = '';
  b += box(56, 120, 260, '한계', 'colhead');
  b += box(336, 120, 300, '해석에 주는 제한', 'colhead');
  b += box(660, 120, 244, '향후 검증 과제', 'colhead');
  b += `<div class="abs blackrule" style="left:56pt;top:144pt;width:848pt"></div>`;
  rows.forEach(([l, s, t, td], i) => {
    const y = 156 + i * 80;
    b += box(56, y, 24, String(i + 1), 'qnum small');
    b += box(80, y, 236, l, 'h14');
    b += box(336, y, 300, s, 'body12');
    b += box(660, y, 244, t, 'h13');
    b += box(660, y + 20, 244, td, 'body12 mid');
    if (i < rows.length - 1) b += `<div class="abs hair" style="left:56pt;top:${y + 68}pt;width:848pt"></div>`;
  });
  pages.push(slide({
    no: 17, section: 6,
    title: '네 가지 한계마다 검증 과제가 남아 있다',
    subtitle: '결과는 합성 9층 · 가정한 유인 계수 · 혼잡 없는 층 선택 모형 안에서만 성립한다.',
    body: b,
    source: '출처: 수정 논문(v3) 3.1–3.2절, 5.2절 · analysis/outputs/aik/aik_checks.csv (E1 x 범위 0–0.5, TOP1 9층 0.85)',
  }));
}

// =========================================================================================== 18 current findings and next validation
{
  const f = [
    ['기준선', `위층일수록 U가 줄었고 감소 비율은 경계마다 달랐다.`, `U<sub>8</sub>/U<sub>1</sub> ${pct1(V.rq1.u8u1_mean_rep)}% · 마지막 국소 AUFR ${pct1(V.rq1.last_local_aufr)}% · 일정 비율 감쇠 기각`],
    ['인접층 프로그램', 'Δ<i>x</i>가 0.1 클수록 AUFR이 높았다(모형 안의 연관).', `γ = 2·4·8에서 ×${f3(M.cont_g2.rr)} · ×${f3(M.cont_g4.rr)} · ×${f3(M.cont_g8.rr)}`],
    ['이동 저항', '기울기 감소는 γ = 2에서만 신뢰구간이 0을 제외했다.', `${pct1(ER.g2.est)}% [${pct1(ER.g2.lo)}, ${pct1(ER.g2.hi)}] · γ = 4·8은 0 포함`],
    ['앵커 배치', '같은 총량의 네 배치 중 TOP1의 T와 U<sub>8</sub>이 가장 높았다.', `T ${pct1(PL.TOP1.T)}% · U<sub>8</sub> ${nf0(PL.TOP1.U8)}명 (γ = 4, 9층 0.85, 혼잡 없음)`],
  ];
  let b = '';
  b += box(56, 120, 480, '현재까지의 결과', 'colhead');
  b += `<div class="abs blackrule" style="left:56pt;top:144pt;width:500pt"></div>`;
  f.forEach(([k, s, v], i) => {
    const y = 156 + i * 72;
    b += box(56, y, 24, String(i + 1), 'qnum small');
    b += box(80, y, 100, k, 'rowhead');
    b += box(184, y - 1, 372, s, 'h13');
    b += box(184, y + 21, 372, v, 'body12 mid');
    if (i < f.length - 1) b += `<div class="abs hair" style="left:56pt;top:${y + 60}pt;width:500pt"></div>`;
  });
  const nx = [
    ['실측 자료 검증', '실제 시설의 층간 통과 집계와 목적지·수단 선택 자료로 입력값을 보정하고 외부 검증한다.'],
    ['기하 기반 수직동선 모형', '실제 평면, 수직동선의 위치·연결, 방향 전환을 모형에 넣는다.'],
    ['혼잡·용량 모형', '대기·병목·수용 한계를 넣어 배치 순위가 유지되는지 확인한다.'],
  ];
  b += box(596, 120, 308, '다음 검증 (서로 별개의 후속 작업)', 'colhead');
  b += `<div class="abs blackrule" style="left:596pt;top:144pt;width:308pt"></div>`;
  nx.forEach(([k, s], i) => {
    const y = 156 + i * 88;
    b += box(596, y, 28, String.fromCharCode(65 + i), 'qnum small');
    b += box(624, y, 280, k, 'h13');
    b += box(624, y + 21, 280, s, 'body12 mid');
    if (i < nx.length - 1) b += `<div class="abs hair" style="left:596pt;top:${y + 76}pt;width:308pt"></div>`;
  });
  b += `<div class="abs hair" style="left:56pt;top:446pt;width:848pt"></div>`;
  b += box(56, 456, 848, 'TOP1의 우위는 네 가지 시나리오와 이 모형 조건 안의 조건부 결과이며, 실제 건물의 보편적 최적 배치를 뜻하지 않는다.', 'body13 strong');
  pages.push(slide({
    no: 18, section: 6,
    title: '현재까지의 결과와 다음 검증',
    subtitle: '명시한 모형 조건 안에서 확인한 결과이며, 실제 건물에서 성립하는지는 다음 단계에서 검증한다.',
    body: b,
    source: '출처: 10–16쪽의 분석 결과 (analysis/outputs/aik/) · 수정 논문(v3) 5절',
  }));
}

// ------------------------------------------------------------------------------------------- CSS + document
const FONT_DIR = path.join(HERE, 'fonts');
const face = (w, file) => `@font-face{font-family:'Pretendard';src:url('${path.relative(BUILD, path.join(FONT_DIR, file)).split(path.sep).join('/')}') format('truetype');font-weight:${w};font-style:normal;font-display:block}`;
const CSS = `
${face(400, 'Pretendard-Regular.ttf')}
${face(500, 'Pretendard-Medium.ttf')}
${face(600, 'Pretendard-SemiBold.ttf')}
${face(700, 'Pretendard-Bold.ttf')}
@page { size: 960pt 540pt; margin: 0; }
html, body { margin: 0; padding: 0; background: #ffffff; }
body { font-family: 'Pretendard'; color: ${C.body}; font-kerning: normal; font-synthesis: style; }
.slide { position: relative; width: 960pt; height: 540pt; overflow: hidden; background: #ffffff; break-after: page; page-break-after: always; }
.slide:last-child { break-after: auto; page-break-after: auto; }
.abs { position: absolute; margin: 0; }
div, p, h1 { word-break: keep-all; overflow-wrap: break-word; }
sub { font-size: 0.68em; vertical-align: -0.26em; line-height: 0; }
sup { font-size: 0.68em; vertical-align: 0.42em; line-height: 0; }
i { font-style: italic; }
b { font-weight: 600; color: ${C.ink}; }
svg { overflow: visible; }
svg text { font-family: 'Pretendard'; font-kerning: normal; }
.kicker { left: 56pt; top: 28pt; font-size: 9.5pt; font-weight: 500; color: ${C.soft}; letter-spacing: 0.01em; }
.kicker .kno { font-weight: 700; color: ${C.ink}; margin-right: 8pt; }
.title { left: 56pt; top: 42pt; width: 848pt; font-size: 22pt; font-weight: 600; color: ${C.ink}; line-height: 1.25; letter-spacing: -0.012em; }
.subtitle { left: 56pt; top: 76pt; width: 848pt; font-size: 12pt; font-weight: 400; color: ${C.mid}; line-height: 1.4; }
.footrule { left: 56pt; top: 506pt; width: 848pt; height: 0; border-top: 0.6pt solid ${C.hair}; }
.foot-src { left: 56pt; top: 512pt; width: 700pt; font-size: 8.5pt; color: ${C.faint}; line-height: 1.3; }
.foot-right { left: 760pt; top: 512pt; width: 144pt; text-align: right; font-size: 8.5pt; color: ${C.faint}; line-height: 1.3; }
.foot-right .trace { margin-right: 10pt; letter-spacing: 0.02em; }
.hair { height: 0; border-top: 0.6pt solid ${C.hair}; }
.toprule { height: 0; border-top: 0.9pt solid ${C.ink}; }
.blackrule { height: 0; border-top: 0.9pt solid ${C.ink}; }
.vrule { width: 0; border-left: 0.6pt solid ${C.hair}; }
.cover-kicker { font-size: 13pt; font-weight: 600; color: ${C.ink}; letter-spacing: 0.04em; }
.cover-title { font-size: 28pt; font-weight: 700; color: ${C.ink}; line-height: 1.36; letter-spacing: -0.015em; }
.cover-sub { font-size: 15pt; color: ${C.mid}; line-height: 1.4; }
.cover-name { font-size: 15pt; font-weight: 600; color: ${C.ink}; }
.cover-meta { font-size: 12pt; color: ${C.mid}; }
.toc-no { font-size: 13pt; font-weight: 700; color: ${C.ink}; }
.toc-title { font-size: 17pt; font-weight: 600; color: ${C.ink}; line-height: 1.3; white-space: nowrap; }
.toc-desc { font-size: 12pt; color: ${C.soft}; line-height: 1.35; }
.toc-pg { font-size: 12pt; color: ${C.soft}; text-align: right; }
.num-s { font-size: 10.5pt; font-weight: 700; color: ${C.soft}; }
.qnum { font-size: 15pt; font-weight: 700; color: ${C.ink}; }
.qnum.small { font-size: 13pt; }
.trace-s { font-size: 9pt; color: ${C.faint}; letter-spacing: 0.02em; }
.trace-s.right { text-align: right; }
.label-s { font-size: 10.5pt; font-weight: 500; color: ${C.soft}; }
.colhead { font-size: 13pt; font-weight: 600; color: ${C.ink}; }
.rowhead { font-size: 12.5pt; font-weight: 600; color: ${C.ink}; line-height: 1.45; }
.question { font-size: 15pt; font-weight: 600; color: ${C.ink}; line-height: 1.5; }
.q15 { font-size: 15pt; font-weight: 600; color: ${C.ink}; line-height: 1.4; }
.q17 { font-size: 16.5pt; font-weight: 600; color: ${C.ink}; line-height: 1.4; }
.h13 { font-size: 13pt; font-weight: 600; color: ${C.ink}; line-height: 1.4; }
.h14 { font-size: 13.5pt; font-weight: 600; color: ${C.ink}; line-height: 1.4; }
.h15 { font-size: 14.5pt; font-weight: 600; color: ${C.ink}; line-height: 1.35; }
.h14.frag { color: ${C.frag}; }
.formula { font-size: 19pt; font-weight: 500; color: ${C.ink}; line-height: 1.3; white-space: nowrap; }
.formula-xl { font-size: 26pt; font-weight: 500; color: ${C.ink}; display: flex; align-items: center; gap: 12pt; }
.frac { display: inline-flex; flex-direction: column; align-items: center; }
.frac .num { padding: 0 10pt 4pt; border-bottom: 1.2pt solid ${C.ink}; line-height: 1.15; }
.frac .den { padding: 4pt 10pt 0; line-height: 1.15; }
.stat { font-size: 19pt; font-weight: 700; color: ${C.cont}; line-height: 1.2; white-space: nowrap; }
.body11 { font-size: 11pt; line-height: 1.5; color: ${C.body}; }
.body115 { font-size: 11.5pt; line-height: 1.5; color: ${C.body}; }
.body12 { font-size: 12pt; line-height: 1.55; color: ${C.body}; }
.body125 { font-size: 12.5pt; line-height: 1.55; color: ${C.body}; }
.body13 { font-size: 13pt; line-height: 1.55; color: ${C.body}; }
.body14 { font-size: 14pt; line-height: 1.5; color: ${C.body}; }
.mid { color: ${C.mid}; }
.strong { font-weight: 600; color: ${C.ink}; }
.not { display: inline-block; font-size: 10pt; font-weight: 600; color: ${C.soft}; border: 0.6pt solid ${C.rule}; padding: 0 4pt; margin-right: 6pt; border-radius: 2pt; line-height: 1.5; }
.note-s { font-size: 10pt; color: ${C.soft}; line-height: 1.4; }
.key { font-size: 10pt; color: ${C.soft}; line-height: 1.4; white-space: nowrap; }
.key-dot { display: inline-block; width: 7pt; height: 7pt; border: 1.2pt solid ${C.ink}; border-radius: 50%; vertical-align: -0.5pt; margin-right: 4pt; box-sizing: border-box; }
.key-gate { display: inline-block; width: 14pt; height: 0; border-top: 2.2pt solid ${C.ink}; vertical-align: 3pt; margin-right: 4pt; }
.key-n { font-weight: 700; color: ${C.ink}; margin-right: 3pt; }
`;

const html = `<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>다층 상업시설의 프로그램 구성과 수직동선 저항에 따른 층간 상행유량비(AUFR) — 논문 중간발표</title>
<style>${CSS}</style></head>
<body>
${pages.join('\n')}
</body></html>`;

const htmlPath = path.join(BUILD, 'deck.html');
fs.writeFileSync(htmlPath, html, 'utf8');

// ------------------------------------------------------------------------------------------- render + audit
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto('file://' + htmlPath, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
const fontStatus = await page.evaluate(() => ['400', '500', '600', '700'].map((w) => [w, document.fonts.check(`${w} 16px Pretendard`)]));
const audit = await page.evaluate(() => {
  const PT = 96 / 72;
  const out = [];
  for (const s of document.querySelectorAll('.slide')) {
    const sr = s.getBoundingClientRect();
    const no = Number(s.dataset.page);
    const boxes = [];
    const issues = [];
    const textEls = [...s.querySelectorAll('div.abs, h1.abs, p.abs')].filter((e) => e.textContent.trim());
    for (const e of textEls) {
      const r = e.getBoundingClientRect();
      // overflow of the declared width (content wider than box) or outside slide
      if (e.scrollWidth > e.clientWidth + 1) issues.push({ kind: 'html_overflow_x', text: e.textContent.trim().slice(0, 40) });
      const rect = { x: (r.left - sr.left) / PT, y: (r.top - sr.top) / PT, w: r.width / PT, h: r.height / PT };
      if (rect.x < -0.5 || rect.y < -0.5 || rect.x + rect.w > 960.5 || rect.y + rect.h > 540.5) issues.push({ kind: 'outside_slide', text: e.textContent.trim().slice(0, 40), rect });
      // tight text box using a Range
      const rg = document.createRange(); rg.selectNodeContents(e);
      const tr = rg.getBoundingClientRect();
      boxes.push({ src: 'html', text: e.textContent.trim().slice(0, 40), x: (tr.left - sr.left) / PT, y: (tr.top - sr.top) / PT, w: tr.width / PT, h: tr.height / PT });
    }
    for (const t of s.querySelectorAll('svg text')) {
      if (t.dataset.noaudit) continue;
      const r = t.getBoundingClientRect();
      const rect = { x: (r.left - sr.left) / PT, y: (r.top - sr.top) / PT, w: r.width / PT, h: r.height / PT };
      if (rect.x < -0.5 || rect.y < -0.5 || rect.x + rect.w > 960.5 || rect.y + rect.h > 540.5) issues.push({ kind: 'outside_slide', text: t.textContent.slice(0, 40), rect });
      boxes.push({ src: 'svg', text: t.textContent.slice(0, 40), ...rect });
    }
    // margins: content must stay within x 40..920 except footer
    for (const b of boxes) {
      if (b.x < 40 || b.x + b.w > 920) issues.push({ kind: 'margin', text: b.text, x: +b.x.toFixed(1), right: +(b.x + b.w).toFixed(1) });
    }
    // pairwise overlap of text boxes (shrink by 1pt to ignore touching)
    for (let i = 0; i < boxes.length; i += 1) {
      for (let j = i + 1; j < boxes.length; j += 1) {
        const a = boxes[i], b = boxes[j];
        const dx = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
        const dy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
        if (dx > 1.5 && dy > 1.5) issues.push({ kind: 'text_overlap', a: a.text, b: b.text, dx: +dx.toFixed(1), dy: +dy.toFixed(1) });
      }
    }
    // title on one line (except cover)
    const h1 = s.querySelector('h1.title');
    if (h1) {
      const lines = Math.round(h1.getBoundingClientRect().height / PT / (22 * 1.25));
      if (lines !== 1) issues.push({ kind: 'title_lines', lines, text: h1.textContent });
    }
    const sub = s.querySelector('p.subtitle');
    if (sub) {
      const lines = Math.round(sub.getBoundingClientRect().height / PT / (12 * 1.4));
      if (lines !== 1) issues.push({ kind: 'subtitle_lines', lines, text: sub.textContent.slice(0, 50) });
    }
    out.push({ page: no, n_text_boxes: boxes.length, issues });
  }
  return out;
});
fs.writeFileSync(path.join(BUILD, 'layout_audit.json'), JSON.stringify({ fontStatus, audit }, null, 1));
await page.pdf({ path: OUT_PDF, preferCSSPageSize: true, printBackground: true, tagged: true, outline: true });
await browser.close();

const nIssues = audit.reduce((s, p) => s + p.issues.length, 0);
console.log(`fonts loaded: ${JSON.stringify(fontStatus)}`);
for (const p of audit) if (p.issues.length) console.log(`[page ${p.page}] ${p.issues.length} issue(s): ` + p.issues.map((i) => JSON.stringify(i)).join(' | '));
console.log(`[${nIssues ? 'WARN' : 'OK'}] layout audit: ${nIssues} issue(s) across ${audit.length} pages`);
console.log(`[OK] wrote ${OUT_PDF}`);
