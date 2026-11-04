const fs = require('fs');
const path = require('path');
const {
  pptx, C, S,
  text, rect, line, circle, startSlide, smallLabel, paragraph, valueLabel,
  floorStack, axis, lineChart, horizontalBars, forestPlot, addNotes,
  warnIfSlideHasOverlaps, warnIfSlideElementsOutOfBounds,
} = require('./modern_helpers');

const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'presentation_data.json'), 'utf8'));
const extra = JSON.parse(fs.readFileSync(path.join(__dirname, 'v2_extra_data.json'), 'utf8'));
const OUT = path.resolve(__dirname, '..', 'vertical_flow_final_modern_academic.pptx');

const SRC_PAPER = '출처: 수정 논문 8쪽 본문 및 표·그림';
const SRC_DATA = '출처: 확정 실행 코드와 분석 CSV · 2,600회 시뮬레이션';
const SRC_CP = '출처: Chang & Penn (1998), Environment and Planning B 25(4), 507–522';

const notes = [
  '안녕하세요. 다층 상업시설의 프로그램 배치와 수직동선 마찰이 층간 상행유량에 미치는 영향을 분석한 연구를 발표하겠습니다. 본 발표는 에이전트 기반 시뮬레이션 민감도 분석의 조건부 결과를 다룹니다.',
  '발표는 연구 배경과 분석 단위, 중심 선행연구, 실험 설계, 네 가지 연구 질문의 결과, 계획적 시사점과 한계 순서로 진행하겠습니다.',
  '다층 상업시설에서는 높이 자체뿐 아니라 층간 이동을 반복하는 과정에서 상행 통과량이 달라집니다. 위층 프로그램의 유인력과 동선 마찰이 이 흐름에 어떤 관계를 갖는지 분리해서 살펴볼 필요가 있습니다.',
  '본 연구는 절대 상행유량 U, 인접 경계 유량의 비인 AUFR, 첫 경계 대비 마지막 경계의 상대 유량 T를 구분합니다. 이 셋은 동일한 지표가 아니며, 고유 방문객 생존율도 아닙니다.',
  'Chang과 Penn은 런던 바비칸의 다층 복합공간에서 수평 전환과 수직 층 분리를 함께 분석했습니다. 본 연구는 그 모형을 복제하지 않고, 복합요인 문제의식을 층 단위 통제 실험으로 전환했습니다.',
  'RQ1은 프로그램 중립 조건의 감쇠 형상, RQ2는 프로그램 대비와 AUFR 및 절대 유량의 관계, RQ3은 동선 마찰의 조절 효과, RQ4는 같은 프로그램 총량에서 수직 배치별 결과를 묻습니다.',
  '모형은 실제 건물을 복제한 것이 아니라 합성 9층의 비공간적 층 단위 선택 모형입니다. 가상 방문 그룹이 체류 후 다음 층과 이동 여부를 선택하고, 여덟 개 상행 경계의 통과 연인원을 기록합니다.',
  'AUFR는 같은 반복에서 특정 경계의 상행 통과량을 바로 아래 경계 통과량으로 나눈 값입니다. U1은 1층에서 2층으로 올라간 통과량이며 전체 입장객이 아닙니다.',
  'E1은 동선 두 조건과 유인 계수 네 수준을 완전 교차한 1,600회 민감도 분석입니다. E2는 프로그램 총량을 고정하고 네 수직 배치를 비교한 1,000회 실험입니다.',
  '프로그램 유인 계수가 0인 연속형에서 첫 경계 유량은 평균 1만 2천346명, 마지막 경계는 448명입니다. 분절형의 첫 경계 유량은 약 20.6퍼센트 낮았습니다.',
  '국소 AUFR는 절대 유량과 다른 질문에 답합니다. 연속형의 마지막 국소 AUFR는 약 51.7퍼센트였고, 감소 형상은 일정한 로그 선형 감쇠로 충분히 설명되지 않았습니다.',
  '인접층 앵커 비중 차이가 0.1 커질 때 AUFR의 회귀모형상 상대 변화는 유인 계수 2, 4, 8에서 각각 약 6.0, 10.9, 18.4퍼센트였습니다. 이는 퍼센트포인트 증가가 아닙니다.',
  '절대 상행유량을 대상으로 한 별도 분석에서는 바로 위층 프로그램 비중이 잔여 데비언스를 가장 많이 줄였습니다. AUFR 회귀와 절대 유량 보조 분석을 같은 결과로 합치면 안 됩니다.',
  '분절형의 원척도 AUFR 기울기 잠식률은 감마 2에서 6.7퍼센트였고 신뢰구간이 0을 제외했습니다. 감마 4와 8의 신뢰구간은 0을 포함하며, 이를 효과가 없다는 증명으로 해석하지 않습니다.',
  'E2는 2층부터 9층의 프로그램 비중 합을 약 1.60으로 유지하면서 최상층 집중, 징검다리, 균등, 저층 집중을 비교했습니다. 도식은 실제 입력 비중을 그대로 표시합니다.',
  '감마 4 연속형에서 첫 경계 대비 마지막 경계 상대 유량은 TOP1이 58.7퍼센트로 가장 높았습니다. TOP1의 마지막 경계 절대 유량도 평균 약 9,112명이었습니다. 이 결과는 네 시나리오와 모형 조건 안에서의 비교입니다.',
  '모형은 비공간적이고 혼잡, 수용량, 실제 평면, 체류와 소비를 반영하지 않습니다. 특히 TOP1의 높은 집중 비중은 실험 1의 범위를 넘어가므로 실제 시설의 최적 배치로 일반화할 수 없습니다.',
  '정리하면 높이에 따라 절대 상행유량은 크게 줄었지만 국소 AUFR는 별도의 구간 패턴을 보였습니다. 프로그램 대비의 관계는 유인 강도에 따라 커졌고, 최상층 집중형은 네 시나리오 중 가장 높은 상대 유량을 보였습니다. 현장 보정과 외부 검증이 다음 단계입니다.',
];

function note(slide, n) {
  addNotes(slide, notes[n - 1]);
}

function keyLine(slide, x, y, w, no, titleValue, body) {
  text(slide, String(no).padStart(2, '0'), x, y, 0.48, 0.34, { fontSize: 11, bold: true, color: C.MID, charSpacing: 1.1 });
  text(slide, titleValue, x + 0.82, y - 0.01, w - 0.82, 0.34, { fontSize: 17, bold: true, color: C.BLACK });
  text(slide, body, x + 0.82, y + 0.39, w - 0.82, 0.55, { fontSize: 12.2, color: C.MID, valign: 'top', breakLine: true });
  line(slide, x + 0.82, y + 1.08, w - 0.82, 0, C.HAIR, 0.55);
}

function legend(slide, items, x, y) {
  let xx = x;
  for (const item of items) {
    line(slide, xx, y + 0.12, 0.37, 0, item.color, 2, item.dash || 'solid');
    if (item.marker === 'square') rect(slide, xx + 0.13, y + 0.065, 0.11, 0.11, { fill: C.WHITE, line: item.color, width: 1.2 });
    else circle(slide, xx + 0.13, y + 0.065, 0.11, C.WHITE, item.color, 1.1);
    text(slide, item.label, xx + 0.47, y, item.w || 1.16, 0.24, { fontSize: 9.8, color: C.MID, audit: false });
    xx += item.step || 1.72;
  }
}

function boundarySection(slide, x, y, w, h, labelMode = 'U') {
  const gap = h / 9;
  for (let f = 1; f <= 9; f += 1) {
    const yy = y + h - f * gap;
    line(slide, x, yy, w, 0, C.BLACK, f === 1 || f === 9 ? 1.15 : 0.65);
    text(slide, `${f}F`, x - 0.52, yy - 0.11, 0.42, 0.22, { fontSize: 8.5, color: C.MID, align: 'right', audit: false });
  }
  for (let b = 1; b <= 8; b += 1) {
    const yy = y + h - b * gap - gap * 0.50;
    line(slide, x + w * 0.58, yy + 0.13, 0, -gap * 0.45, C.BLACK, 1.05, 'solid', 'triangle');
    if (labelMode === 'U') {
      text(slide, `U${b}`, x + w * 0.65, yy - 0.02, 0.42, 0.25, { fontSize: 9.2, bold: true, color: C.BLACK, audit: false });
    }
  }
}

// 01 — cover
{
  const slide = pptx.addSlide();
  slide.background = { color: C.WHITE };
  text(slide, '다층 상업시설의 프로그램 배치와\n수직동선 마찰이 층간 상행유량에\n미치는 영향', 0.82, 1.12, 7.95, 1.84, {
    fontSize: 32, bold: true, color: C.BLACK, breakLine: true, valign: 'top',
  });
  text(slide, '에이전트 기반 시뮬레이션 민감도 분석', 0.84, 3.05, 6.55, 0.36, {
    fontSize: 16.5, color: C.MID,
  });
  line(slide, 0.84, 3.63, 2.60, 0, C.BLACK, 1.1);
  text(slide, '대한건축학회 학술 발표 · 봉성현', 0.84, 3.86, 4.40, 0.30, {
    fontSize: 11.5, color: C.MID,
  });
  boundarySection(slide, 9.78, 1.00, 1.85, 5.55, 'U');
  text(slide, '9층 · 8개 상행 경계', 9.55, 6.72, 2.30, 0.27, {
    fontSize: 10, color: C.MID, align: 'center',
  });
  text(slide, '01 / 18', 12.03, 7.10, 0.63, 0.19, { fontSize: 8.1, color: C.LIGHT, align: 'right' });
  note(slide, 1);
}

// 02 — structure
{
  const slide = startSlide('발표 구성', 2, SRC_PAPER, '연구 질문과 분석 지표를 중심으로 결과를 단계적으로 분리한다.');
  keyLine(slide, 0.86, 1.70, 5.55, 1, '문제와 분석 단위', '수직 확장, 경계 상행유량 U, 국소 AUFR의 차이');
  keyLine(slide, 0.86, 3.18, 5.55, 2, '선행연구와 모형', 'Chang & Penn(1998), 합성 9층 에이전트 모형');
  keyLine(slide, 0.86, 4.66, 5.55, 3, 'E1 · E2 실험', '동선 마찰·유인 강도·프로그램 수직 배치 비교');
  keyLine(slide, 6.92, 1.70, 5.55, 4, 'RQ1 · RQ2', '기본 감쇠, 프로그램 대비와 AUFR·절대 유량');
  keyLine(slide, 6.92, 3.18, 5.55, 5, 'RQ3 · RQ4', '동선 마찰의 조절 효과, 수직 배치 시나리오');
  keyLine(slide, 6.92, 4.66, 5.55, 6, '시사점과 한계', '모형 안의 조건부 결과와 현장 검증의 범위');
  note(slide, 2);
}

// 03 — background
{
  const slide = startSlide('연구 배경', 3, SRC_PAPER, '수직 확장은 면적을 늘리지만, 상층부 접근 흐름을 자동으로 보장하지 않는다.');
  boundarySection(slide, 1.05, 1.70, 2.25, 4.65, 'U');
  line(slide, 3.75, 2.23, 1.16, 0, C.BLACK, 1.0, 'solid', 'triangle');
  text(slide, '층간 이동을\n반복할수록', 3.55, 2.55, 1.58, 0.75, { fontSize: 13.5, bold: true, color: C.BLACK, align: 'center', breakLine: true });
  line(slide, 3.75, 4.62, 1.16, 0, C.BLACK, 1.0, 'solid', 'triangle');
  text(slide, '목적지 선택·\n퇴장이 누적', 3.55, 4.94, 1.58, 0.75, { fontSize: 13.5, bold: true, color: C.BLACK, align: 'center', breakLine: true });
  text(slide, '설계 변수', 5.60, 1.82, 1.25, 0.30, { fontSize: 10, bold: true, color: C.MID, charSpacing: 1.0 });
  text(slide, '위층 프로그램의 유인', 5.60, 2.27, 3.00, 0.42, { fontSize: 21, bold: true, color: C.BLACK });
  paragraph(slide, '상층부에 배치된 목적성 프로그램이\n다음 경계의 상행 선택과 어떤 관계를 갖는가?', 5.60, 2.82, 3.42, 0.90, { fontSize: 13.3, color: C.MID });
  line(slide, 5.60, 3.92, 3.42, 0, C.RULE, 0.7);
  text(slide, '이동 조건', 9.47, 1.82, 1.25, 0.30, { fontSize: 10, bold: true, color: C.MID, charSpacing: 1.0 });
  text(slide, '수직동선의 마찰', 9.47, 2.27, 2.70, 0.42, { fontSize: 21, bold: true, color: C.BLACK });
  paragraph(slide, '연속형과 분절형 이동 조건이\n프로그램 대비에 대한 반응을 얼마나 바꾸는가?', 9.47, 2.82, 2.84, 0.90, { fontSize: 13.3, color: C.MID });
  line(slide, 9.47, 3.92, 2.84, 0, C.RULE, 0.7);
  text(slide, '핵심', 5.60, 4.38, 0.70, 0.25, { fontSize: 10, bold: true, color: C.MID, charSpacing: 1.0 });
  paragraph(slide, '“얼마나 올라갔는가”와 “인접 경계에서 얼마나 유지됐는가”를 분리해야 한다.', 5.60, 4.86, 6.72, 0.88, { fontSize: 19, bold: true, color: C.BLACK });
  note(slide, 3);
}

// 04 — metrics
{
  const slide = startSlide('연구 문제와 분석 단위', 4, SRC_PAPER, '상행 흐름을 세 가지 서로 다른 양으로 읽는다.');
  boundarySection(slide, 0.96, 1.72, 2.10, 4.72, 'U');
  text(slide, '경계 상행유량', 3.72, 1.72, 2.10, 0.29, { fontSize: 10, bold: true, color: C.MID, charSpacing: 0.7 });
  text(slide, 'U₍ᵣ,ᵦ₎', 3.72, 2.14, 2.10, 0.56, { fontSize: 31, bold: true, color: C.BLACK });
  paragraph(slide, '반복 r에서 경계 b를\n상향 통과한 연인원', 3.72, 2.80, 2.35, 0.72, { fontSize: 13, color: C.MID });
  line(slide, 6.31, 1.66, 0, 4.78, C.RULE, 0.7);
  text(slide, '국소 층간 상행유량비', 6.83, 1.72, 2.50, 0.29, { fontSize: 10, bold: true, color: C.MID, charSpacing: 0.7 });
  text(slide, 'AUFR₍ᵣ,ᵦ₎ = U₍ᵣ,ᵦ₎ / U₍ᵣ,ᵦ₋₁₎', 6.83, 2.14, 5.44, 0.56, { fontSize: 24, bold: true, color: C.BLACK });
  paragraph(slide, '같은 반복의 인접 경계 통과량 비율\n고유 방문객 생존율·도달 확률이 아님', 6.83, 2.80, 5.10, 0.72, { fontSize: 13, color: C.MID });
  line(slide, 6.83, 3.82, 5.40, 0, C.HAIR, 0.7);
  text(slide, '최상단 상대 유량 지수', 6.83, 4.23, 2.50, 0.29, { fontSize: 10, bold: true, color: C.MID, charSpacing: 0.7 });
  text(slide, 'Tᵣ = U₍ᵣ,8₎ / U₍ᵣ,1₎', 6.83, 4.66, 4.25, 0.55, { fontSize: 25, bold: true, color: C.BLACK });
  paragraph(slide, '보고값 = meanᵣ(Tᵣ) · 반복별 비율의 평균\n국소 AUFR와 같은 지표가 아님', 6.83, 5.29, 5.10, 0.72, { fontSize: 13, color: C.MID });
  text(slide, 'U₁ = 1F → 2F 상행 통과량 · 전체 입장객이 아님', 0.96, 6.62, 5.35, 0.25, { fontSize: 10.7, bold: true, color: C.BLACK });
  note(slide, 4);
}

// 05 — prior work
{
  const slide = startSlide('중심 선행연구와 본 연구의 위치', 5, SRC_CP, '복합공간의 관찰·모형화 문제를 층 단위 통제 실험으로 전환한다.');
  smallLabel(slide, '비교 항목', 0.86, 1.62, 1.35);
  smallLabel(slide, 'Chang & Penn (1998)', 2.62, 1.62, 3.65);
  smallLabel(slide, '본 연구', 7.23, 1.62, 4.35);
  line(slide, 0.86, 2.02, 11.70, 0, C.BLACK, 1.0);
  const rows = [
    ['공간', '런던 바비칸의 실제 다층 복합공간', '실제 평면을 복제하지 않은 합성 9층'],
    ['접근', 'IMCM과 관찰 보행 흐름 비교', '에이전트 선택 규칙의 민감도 분석'],
    ['중심 변수', '수평 방향 전환·수직 층 분리·발생·유인', '프로그램 대비·유인 강도·동선 마찰'],
    ['분석 단위', '공간 구성과 관측 통행량', '8개 층간 상행 경계의 U와 AUFR'],
    ['해석 범위', '실제 복합공간의 구성과 이동 관계', '명시한 모형과 네 배치 안의 조건부 결과'],
  ];
  rows.forEach((row, i) => {
    const yy = 2.17 + i * 0.91;
    text(slide, row[0], 0.86, yy, 1.30, 0.56, { fontSize: 11, bold: true, color: C.BLACK, valign: 'top' });
    text(slide, row[1], 2.62, yy, 3.75, 0.61, { fontSize: 12.3, color: C.BODY, valign: 'top', breakLine: true });
    text(slide, row[2], 7.23, yy, 4.78, 0.61, { fontSize: 12.3, color: C.BODY, valign: 'top', breakLine: true });
    line(slide, 0.86, yy + 0.69, 11.70, 0, C.HAIR, 0.6);
  });
  text(slide, '복제 관계가 아니라 연구 문제의 계보', 7.23, 6.71, 4.60, 0.25, { fontSize: 10.3, bold: true, color: C.BLACK });
  note(slide, 5);
}

// 06 — RQs
{
  const slide = startSlide('연구 질문 RQ1–RQ4', 6, SRC_PAPER, '지표·설명변수·실험 범위를 질문별로 분리한다.');
  const rq = [
    ['RQ1', '높이에 따라 기본 상행유량은 어떤 형상으로 감쇠하는가?', 'γ = 0 · U와 국소 AUFR'],
    ['RQ2', '인접층 프로그램 대비는 AUFR와 어떤 관계를 갖는가?', 'Δx = +0.1 · 상대 변화 / 절대 유량 보조 분석'],
    ['RQ3', '분절형 동선은 프로그램 대비에 대한 AUFR 반응을 약화하는가?', '기울기 잠식률 · 95% 신뢰구간'],
    ['RQ4', '같은 프로그램 총량에서 수직 배치는 최상단 상대 유량을 바꾸는가?', 'TOP1 · STEP3 · UNIFORM · LOW3'],
  ];
  rq.forEach((row, i) => {
    const yy = 1.61 + i * 1.27;
    text(slide, row[0], 0.86, yy, 0.85, 0.35, { fontSize: 12, bold: true, color: C.BLACK, charSpacing: 0.8 });
    text(slide, row[1], 2.03, yy - 0.03, 7.98, 0.48, { fontSize: 18, bold: true, color: C.BLACK, valign: 'top' });
    text(slide, row[2], 10.35, yy + 0.01, 2.20, 0.54, { fontSize: 10.5, color: C.MID, align: 'right', valign: 'top', breakLine: true });
    line(slide, 2.03, yy + 0.79, 10.52, 0, C.HAIR, 0.6);
  });
  note(slide, 6);
}

// 07 — model
{
  const slide = startSlide('합성 9층 에이전트 모형', 7, SRC_DATA, '실제 평면 복제가 아닌 비공간적 층 단위 선택 모형');
  floorStack(slide, 0.98, 1.68, 1.52, 4.95, { arrow: true, labels: true });
  const steps = [
    ['01', '가상 방문 그룹', '층별 체류 후 다음 행동을 선택'],
    ['02', '목적지 선택', '프로그램 비중과 유인 계수 γ 반영'],
    ['03', '이동 조건', '연속형 / 분절형 수직동선 저항'],
    ['04', '경계 기록', 'U₁–U₈ 상행 통과 연인원 집계'],
  ];
  steps.forEach((s, i) => {
    const x = 3.24 + i * 2.30;
    text(slide, s[0], x, 1.90, 0.42, 0.25, { fontSize: 9.5, bold: true, color: C.MID, charSpacing: 1.0 });
    text(slide, s[1], x, 2.34, 1.92, 0.42, { fontSize: 16, bold: true, color: C.BLACK });
    paragraph(slide, s[2], x, 2.90, 1.82, 0.86, { fontSize: 11.7, color: C.MID });
    if (i < steps.length - 1) line(slide, x + 1.88, 2.55, 0.29, 0, C.BLACK, 0.9, 'solid', 'triangle');
  });
  line(slide, 3.24, 4.17, 8.95, 0, C.RULE, 0.7);
  valueLabel(slide, '9층', '합성 수직 공간', 3.24, 4.62, 1.55);
  valueLabel(slide, '8개', '상행 경계', 5.33, 4.62, 1.55);
  valueLabel(slide, '2,600회', 'E1 + E2 반복', 7.42, 4.62, 1.82);
  valueLabel(slide, '0건', '누락 경계·U=0', 10.07, 4.62, 1.75);
  paragraph(slide, '에이전트는 고유 방문객 추적 단위가 아니라 통과 연인원 생성 단위다.', 3.24, 5.88, 8.95, 0.55, { fontSize: 13.5, bold: true, color: C.BLACK });
  note(slide, 7);
}

// 08 — AUFR definition
{
  const slide = startSlide('층간 경계와 AUFR 정의', 8, SRC_PAPER, '수식의 분자·분모가 실제 어느 경계에 위치하는지 직접 표시한다.');
  boundarySection(slide, 0.98, 1.70, 2.20, 4.78, 'U');
  line(slide, 2.44, 3.09, 1.34, 0, C.CONT, 1.1, 'dash');
  line(slide, 2.44, 3.62, 1.34, 0, C.FRAG, 1.1, 'dash');
  text(slide, '분자 Uᵣ,ᵦ', 3.94, 2.95, 1.52, 0.30, { fontSize: 11.5, bold: true, color: C.CONT });
  text(slide, '분모 Uᵣ,ᵦ₋₁', 3.94, 3.48, 1.72, 0.30, { fontSize: 11.5, bold: true, color: C.FRAG });
  line(slide, 5.69, 1.65, 0, 4.86, C.RULE, 0.7);
  text(slide, 'AUFR₍ᵣ,ᵦ₎', 6.35, 1.90, 1.76, 0.58, { fontSize: 29, bold: true, color: C.BLACK });
  text(slide, '=   U₍ᵣ,ᵦ₎', 8.20, 1.90, 2.30, 0.48, { fontSize: 26, bold: true, color: C.CONT, align: 'center' });
  line(slide, 8.63, 2.47, 1.68, 0, C.BLACK, 1.1);
  text(slide, 'U₍ᵣ,ᵦ₋₁₎', 8.30, 2.54, 2.30, 0.48, { fontSize: 26, bold: true, color: C.FRAG, align: 'center' });
  line(slide, 6.35, 3.43, 5.50, 0, C.HAIR, 0.7);
  const cautions = [
    ['같은 반복 r', '분자와 분모는 동일한 시뮬레이션 반복에서 계산'],
    ['인접 경계', 'b와 b−1의 통과량을 비교'],
    ['연인원 비율', '고유 방문객의 생존율·최상층 도달 확률이 아님'],
    ['U₁의 의미', '1F→2F 상행 통과량이며 전체 입장객이 아님'],
  ];
  cautions.forEach((c, i) => {
    const yy = 3.78 + i * 0.62;
    text(slide, c[0], 6.35, yy, 1.24, 0.27, { fontSize: 10.8, bold: true, color: C.BLACK });
    text(slide, c[1], 7.79, yy, 4.26, 0.31, { fontSize: 11.5, color: C.MID });
  });
  note(slide, 8);
}

// 09 — experiments
{
  const slide = startSlide('E1 · E2 실험 설계', 9, SRC_DATA, '민감도 분석과 프로그램 수직 배치 비교를 분리한다.');
  line(slide, 6.66, 1.60, 0, 4.98, C.RULE, 0.75);
  text(slide, 'E1', 0.88, 1.63, 0.50, 0.31, { fontSize: 11, bold: true, color: C.BLACK, charSpacing: 1.0 });
  text(slide, '마찰 × 유인 강도', 1.58, 1.57, 3.65, 0.48, { fontSize: 21, bold: true, color: C.BLACK });
  const e1 = [
    ['동선 조건', '연속형 · 분절형'],
    ['유인 계수 γ', '0 · 2 · 4 · 8'],
    ['반복', '2 × 4 × 200 = 1,600회'],
    ['주요 질문', 'RQ1 · RQ2 · RQ3'],
  ];
  e1.forEach((r, i) => {
    const yy = 2.43 + i * 0.79;
    text(slide, r[0], 0.88, yy, 1.38, 0.29, { fontSize: 10.5, bold: true, color: C.MID });
    text(slide, r[1], 2.55, yy - 0.02, 3.38, 0.34, { fontSize: 14, bold: i === 2, color: C.BLACK });
    line(slide, 0.88, yy + 0.46, 5.48, 0, C.HAIR, 0.55);
  });
  paragraph(slide, 'γ는 실측 보정값이 아니라\n모형 민감도를 확인하기 위한 가정값', 0.88, 5.77, 4.90, 0.72, { fontSize: 12.5, color: C.MID });
  text(slide, 'E2', 7.17, 1.63, 0.50, 0.31, { fontSize: 11, bold: true, color: C.BLACK, charSpacing: 1.0 });
  text(slide, '프로그램 총량 × 수직 배치', 7.87, 1.57, 4.45, 0.48, { fontSize: 21, bold: true, color: C.BLACK });
  const e2 = [
    ['프로그램 총량', '2–9F 합계 ≈ 1.60'],
    ['배치', 'TOP1 · STEP3 · UNIFORM · LOW3'],
    ['핵심 조건', 'γ=4 · 연속형/분절형 + γ=0 대조'],
    ['반복', '1,000회'],
    ['주요 질문', 'RQ4'],
  ];
  e2.forEach((r, i) => {
    const yy = 2.43 + i * 0.69;
    text(slide, r[0], 7.17, yy, 1.42, 0.29, { fontSize: 10.5, bold: true, color: C.MID });
    text(slide, r[1], 8.88, yy - 0.02, 3.65, 0.37, { fontSize: 13.2, bold: i === 3, color: C.BLACK });
    line(slide, 7.17, yy + 0.42, 5.36, 0, C.HAIR, 0.55);
  });
  text(slide, '총 2,600회 · 경계 누락 0 · U=0 사례 0', 7.17, 6.10, 5.20, 0.30, { fontSize: 12, bold: true, color: C.BLACK });
  note(slide, 9);
}

// 10 — RQ1 absolute U
{
  const slide = startSlide('RQ1 — 기본 상행유량 감쇠', 10, SRC_DATA, 'γ=0 · 절대 상행유량 U · 평균');
  const cont = data.rq1.continuous.map((d) => d.U_mean);
  const frag = data.rq1.fragmented.map((d) => d.U_mean);
  lineChart(slide, 1.18, 1.76, 8.20, 4.46, [
    { values: cont, color: C.CONT, marker: 'circle', width: 2.2 },
    { values: frag, color: C.FRAG, marker: 'square', width: 2.0, dash: 'dash' },
  ], {
    yMin: 0, yMax: 14000, yTicks: [0, 3500, 7000, 10500, 14000],
    yFormatter: (v) => v === 0 ? '0' : `${(v / 1000).toFixed(1)}k`,
    labels: ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8'],
  });
  legend(slide, [
    { label: '연속형', color: C.CONT, marker: 'circle' },
    { label: '분절형', color: C.FRAG, marker: 'square', dash: 'dash' },
  ], 1.20, 6.53);
  text(slide, '상행 통과량(명)', 0.68, 1.45, 1.25, 0.24, { fontSize: 9.2, color: C.MID });
  line(slide, 9.86, 1.74, 0, 4.95, C.RULE, 0.7);
  valueLabel(slide, '12,346명', '연속형 U₁', 10.30, 1.85, 2.10, C.CONT);
  valueLabel(slide, '448명', '연속형 U₈', 10.30, 3.10, 2.10, C.CONT);
  valueLabel(slide, '3.6%', '평균 반복별 U₈ / U₁', 10.30, 4.36, 2.10, C.BLACK);
  text(slide, '분절형 U₁은\n연속형보다 20.6% 낮음', 10.30, 5.61, 2.08, 0.63, { fontSize: 12, bold: true, color: C.FRAG, breakLine: true, valign: 'top' });
  note(slide, 10);
}

// 11 — RQ1 local AUFR
{
  const slide = startSlide('RQ1 — 구간별 AUFR 비교', 11, SRC_DATA, '경계 2–8의 국소 비율 · 절대 유량과 분리해서 해석');
  const cont = data.rq1.continuous.slice(1).map((d) => d.AUFR_mean * 100);
  const frag = data.rq1.fragmented.slice(1).map((d) => d.AUFR_mean * 100);
  lineChart(slide, 1.18, 1.84, 8.20, 4.28, [
    { values: cont, color: C.CONT, marker: 'circle', width: 2.2 },
    { values: frag, color: C.FRAG, marker: 'square', width: 2.0, dash: 'dash' },
  ], {
    yMin: 40, yMax: 75, yTicks: [40, 50, 60, 70],
    yFormatter: (v) => `${v}%`,
    labels: ['U2/U1', 'U3/U2', 'U4/U3', 'U5/U4', 'U6/U5', 'U7/U6', 'U8/U7'],
  });
  legend(slide, [
    { label: '연속형', color: C.CONT, marker: 'circle' },
    { label: '분절형', color: C.FRAG, marker: 'square', dash: 'dash' },
  ], 1.20, 6.48);
  line(slide, 9.86, 1.74, 0, 4.95, C.RULE, 0.7);
  valueLabel(slide, '51.7%', '연속형 마지막 국소 AUFR', 10.30, 1.91, 2.18, C.CONT);
  text(slide, '일정비 감쇠 아님', 10.30, 3.28, 2.15, 0.35, { fontSize: 16.5, bold: true, color: C.BLACK });
  paragraph(slide, `로그 선형 모형 대비 경계 요인 모형\nF = ${extra.rq1_shape.cont.F.toFixed(1)} · p < .001`, 10.30, 3.78, 2.20, 0.74, { fontSize: 11.5, color: C.MID });
  line(slide, 10.30, 4.85, 1.98, 0, C.HAIR, 0.6);
  paragraph(slide, '국소 AUFR는 “직전 경계 대비 유지”를 말한다.\nU₈/U₁=3.6%와 동일한 값이 아니다.', 10.30, 5.15, 2.24, 0.98, { fontSize: 11.5, bold: true, color: C.BLACK });
  note(slide, 11);
}

// 12 — RQ2 relative effect
{
  const slide = startSlide('RQ2 — 프로그램 대비와 AUFR', 12, SRC_DATA, '연속형 · 인접층 앵커 비중 차이 Δx가 0.1 증가할 때의 회귀모형상 상대 변화');
  forestPlot(slide, 2.02, 1.83, 7.65, 3.75, data.rq2.effects.map((d, i) => ({
    label: `γ=${d.gamma}`, estimate: d.percent, lo: d.lo, hi: d.hi,
    color: [C.CONT2, C.CONT, '1E4F73'][i],
  })), { min: 0, max: 22, ticks: [0, 5, 10, 15, 20], showValues: false });
  text(slide, 'AUFR 상대 변화(%)', 5.00, 5.91, 2.16, 0.25, { fontSize: 10, color: C.MID, align: 'center' });
  line(slide, 10.17, 1.70, 0, 4.98, C.RULE, 0.7);
  valueLabel(slide, '+6.0%', 'γ=2', 10.55, 1.90, 1.70, C.CONT2);
  valueLabel(slide, '+10.9%', 'γ=4', 10.55, 3.07, 1.70, C.CONT);
  valueLabel(slide, '+18.4%', 'γ=8', 10.55, 4.24, 1.70, '1E4F73');
  paragraph(slide, '퍼센트포인트 증가가 아니라\n회귀모형의 상대적 변화', 10.55, 5.62, 1.78, 0.72, { fontSize: 11.2, bold: true, color: C.BLACK });
  note(slide, 12);
}

// 13 — RQ2 absolute U
{
  const slide = startSlide('RQ2 — 절대 유량 보조 분석', 13, SRC_DATA, 'γ=4 · 연속형 · 단일 변수 추가에 따른 잔여 데비언스 감소율');
  horizontalBars(slide, 1.02, 2.05, 9.00, 3.15, [
    { label: 'Δx', value: data.rq2.deviance_explained_gamma4_cont['adjacent contrast (Delta)'], color: C.DATA_GRAY, format: (v) => `${v.toFixed(1)}%` },
    { label: 'x_upper', value: data.rq2.deviance_explained_gamma4_cont['upper-floor program'], color: C.CONT, format: (v) => `${v.toFixed(1)}%` },
    { label: 'M_above', value: data.rq2.deviance_explained_gamma4_cont['mean program above boundary'], color: C.CONT2, format: (v) => `${v.toFixed(1)}%` },
  ], { max: 65 });
  text(slide, '변수 정의', 1.02, 5.61, 1.22, 0.26, { fontSize: 9.8, bold: true, color: C.MID, charSpacing: 0.8 });
  text(slide, 'Δx: 인접층 비중 차이   ·   x_upper: 바로 위층 비중   ·   M_above: 경계 위쪽 평균 비중', 2.30, 5.60, 7.86, 0.30, { fontSize: 11.2, color: C.MID });
  line(slide, 10.35, 1.70, 0, 4.95, C.RULE, 0.7);
  text(slide, '해석 분리', 10.78, 1.93, 1.25, 0.28, { fontSize: 10, bold: true, color: C.MID, charSpacing: 0.8 });
  paragraph(slide, '절대 상행유량 U의\n보조 분석이다.', 10.69, 2.45, 1.86, 0.92, { fontSize: 15.5, bold: true, color: C.BLACK });
  line(slide, 10.78, 3.86, 1.51, 0, C.HAIR, 0.6);
  paragraph(slide, '앞 장의 AUFR 회귀효과와\n같은 결과로 합치지 않는다.', 10.69, 4.18, 1.88, 0.92, { fontSize: 11.2, color: C.MID });
  note(slide, 13);
}

// 14 — RQ3
{
  const slide = startSlide('RQ3 — 동선 마찰의 조절 효과', 14, SRC_DATA, '분절형에서 원척도 AUFR 기울기가 감소한 비율 · 95% 신뢰구간');
  forestPlot(slide, 2.02, 1.90, 7.10, 3.70, data.rq3.erosion.map((d, i) => ({
    label: `γ=${d.gamma}`, estimate: d.estimate, lo: d.lo, hi: d.hi,
    color: i === 0 ? C.FRAG : C.DATA_GRAY,
  })), { min: -10, max: 15, ticks: [-10, -5, 0, 5, 10, 15], showValues: false });
  text(slide, '기울기 잠식률(%)', 4.60, 5.95, 2.00, 0.25, { fontSize: 10, color: C.MID, align: 'center' });
  line(slide, 9.64, 1.72, 0, 4.95, C.RULE, 0.7);
  valueLabel(slide, '6.7%', 'γ=2 · CI가 0을 제외', 10.08, 1.95, 2.12, C.FRAG);
  text(slide, 'γ=4 · γ=8', 10.08, 3.34, 1.65, 0.31, { fontSize: 16, bold: true, color: C.BLACK });
  paragraph(slide, '각 0.8%, 1.7%\n두 신뢰구간 모두 0 포함', 10.08, 3.78, 2.16, 0.72, { fontSize: 11.7, color: C.MID });
  line(slide, 10.08, 4.83, 1.98, 0, C.HAIR, 0.6);
  paragraph(slide, '0을 포함한다는 사실은\n“효과가 없음”의 증명이 아니다.', 10.08, 5.12, 2.18, 0.86, { fontSize: 12.4, bold: true, color: C.BLACK });
  note(slide, 14);
}

// 15 — RQ4 arrangements
{
  const slide = startSlide('RQ4 — 앵커 프로그램의 수직 배치', 15, SRC_DATA, '2–9F 프로그램 비중 합계 ≈ 1.60 · 숫자는 실제 입력 비중');
  const names = [
    ['TOP1', '최상층 집중'],
    ['STEP3', '3·6·9층 징검다리'],
    ['UNIFORM', '균등'],
    ['LOW3', '2·3·4층 저층 집중'],
  ];
  names.forEach((n, i) => {
    const x = 1.11 + i * 3.02;
    text(slide, n[0], x, 1.58, 1.95, 0.31, { fontSize: 11, bold: true, color: C.BLACK, align: 'center', charSpacing: 0.8 });
    text(slide, n[1], x - 0.28, 1.92, 2.50, 0.28, { fontSize: 10.2, color: C.MID, align: 'center' });
    floorStack(slide, x + 0.21, 2.34, 1.54, 3.89, {
      weights: data.rq4.weights[n[0]], showWeights: true, labels: true, maxWeight: 0.85,
    });
    const sum = data.rq4.weights[n[0]].slice(1).reduce((a, b) => a + b, 0);
    text(slide, `Σ 2–9F = ${sum.toFixed(2)}`, x - 0.03, 6.47, 2.02, 0.26, { fontSize: 9.5, bold: true, color: C.MID, align: 'center' });
  });
  note(slide, 15);
}

// 16 — RQ4 result
{
  const slide = startSlide('RQ4 — 결과와 건축계획적 해석', 16, SRC_DATA, 'γ=4 · 연속형 · 평균 Tᵣ=U₍ᵣ,8₎/U₍ᵣ,1₎ · 네 시나리오 안의 비교');
  const rows = data.rq4.patterns.map((d, i) => ({
    label: d.pattern, value: d.reach_percent,
    color: [C.CONT, C.CONT2, C.DATA_GRAY, '969696'][i],
    format: (v) => `${v.toFixed(1)}%`,
  }));
  horizontalBars(slide, 0.94, 1.74, 7.55, 3.72, rows, { max: 65 });
  text(slide, '반복별 Tᵣ의 평균 · 첫 경계 대비 마지막 경계 상대 유량', 2.36, 5.75, 4.84, 0.26, { fontSize: 10.2, color: C.MID, align: 'center' });
  line(slide, 8.77, 1.66, 0, 4.96, C.RULE, 0.7);
  smallLabel(slide, '배치', 9.19, 1.83, 1.05);
  smallLabel(slide, 'U₈ 평균', 10.53, 1.83, 1.12, { align: 'right' });
  smallLabel(slide, 'R', 11.95, 1.83, 0.56, { align: 'right' });
  line(slide, 9.19, 2.18, 3.31, 0, C.BLACK, 0.9);
  extra.rq4_cont.forEach((d, i) => {
    const yy = 2.42 + i * 0.67;
    text(slide, d.pattern, 9.19, yy, 1.08, 0.29, { fontSize: 11, bold: d.pattern === 'TOP1', color: C.BLACK });
    text(slide, `${Math.round(d.U8).toLocaleString('ko-KR')}명`, 10.33, yy, 1.33, 0.29, { fontSize: 11, bold: d.pattern === 'TOP1', color: C.BLACK, align: 'right' });
    text(slide, `${(d.R * 100).toFixed(1)}%`, 11.78, yy, 0.73, 0.29, { fontSize: 11, color: C.MID, align: 'right' });
    line(slide, 9.19, yy + 0.43, 3.31, 0, C.HAIR, 0.55);
  });
  paragraph(slide, '이번 모형에서는 상층부에 분명한 목적지를 형성할수록 상단 상대 유량이 높았다. 그러나 혼잡·수용 한계를 포함한 실제 최적 배치를 뜻하지 않는다.', 9.19, 5.33, 3.32, 1.05, { fontSize: 11.5, bold: true, color: C.BLACK });
  note(slide, 16);
}

// 17 — limitations
{
  const slide = startSlide('연구 한계', 17, SRC_PAPER, '결과가 유효한 모형 경계를 명시한다.');
  const limits = [
    ['01', '비공간적 합성 모형', '실제 평면·시야·동선 네트워크를 직접 재현하지 않는다.'],
    ['02', '혼잡과 수용량 미반영', '상행유량이 커져도 병목·대기·안전·운영 부담은 계산하지 않는다.'],
    ['03', '프로그램 강도의 범위', 'TOP1의 0.85는 E1의 프로그램 범위를 넘어선 비교 시나리오다.'],
    ['04', '결과 변수의 범위', '통과 연인원과 경계 비율은 체류·소비·만족·고유 방문객 도달률이 아니다.'],
  ];
  limits.forEach((r, i) => {
    const yy = 1.63 + i * 1.19;
    text(slide, r[0], 0.90, yy, 0.46, 0.30, { fontSize: 10, bold: true, color: C.MID, charSpacing: 1.0 });
    text(slide, r[1], 1.65, yy - 0.02, 2.76, 0.35, { fontSize: 16, bold: true, color: C.BLACK });
    text(slide, r[2], 4.64, yy - 0.02, 7.70, 0.48, { fontSize: 12.8, color: C.BODY, valign: 'top', breakLine: true });
    line(slide, 1.65, yy + 0.69, 10.69, 0, C.HAIR, 0.6);
  });
  line(slide, 0.90, 6.48, 11.44, 0, C.BLACK, 1.0);
  text(slide, '다음 단계', 0.90, 6.65, 1.05, 0.25, { fontSize: 10, bold: true, color: C.MID, charSpacing: 0.8 });
  text(slide, '실제 시설의 관측 유량으로 규칙을 보정하고, 공간구성·혼잡을 포함해 외부 검증한다.', 2.20, 6.61, 9.87, 0.34, { fontSize: 13, bold: true, color: C.BLACK });
  note(slide, 17);
}

// 18 — conclusion
{
  const slide = startSlide('종합 결론', 18, SRC_PAPER, '모형 안에서 확인된 결과와 적용 한계를 함께 읽는다.');
  keyLine(slide, 0.92, 1.59, 11.44, 1, '절대 유량과 국소 AUFR는 다른 정보를 준다', '연속형 γ=0에서 U₈/U₁은 3.6%, 마지막 국소 AUFR는 51.7%였다.');
  keyLine(slide, 0.92, 3.09, 11.44, 2, '프로그램 대비의 관계는 유인 강도에 따라 커졌다', 'Δx=0.1 증가 시 AUFR 상대 변화는 γ=2·4·8에서 약 +6.0·+10.9·+18.4%였다.');
  keyLine(slide, 0.92, 4.59, 11.44, 3, '네 배치 중 TOP1의 최상단 상대 유량이 가장 높았다', 'γ=4 연속형에서 meanᵣ(Tᵣ)=58.7%, U₈ 평균 약 9,112명 — 실제 시설의 보편적 최적안은 아니다.');
  line(slide, 0.92, 6.27, 11.44, 0, C.BLACK, 1.0);
  text(slide, '연구의 기여', 0.92, 6.48, 1.22, 0.26, { fontSize: 10, bold: true, color: C.MID, charSpacing: 0.8 });
  text(slide, '층간 경계 지표와 프로그램 요약변수를 분리하고, 강도·동선·배치를 같은 실험 틀에서 비교했다.', 2.41, 6.43, 9.55, 0.36, { fontSize: 13.2, bold: true, color: C.BLACK });
  note(slide, 18);
}

// Diagnostics required by the presentation workflow. Chart labels and markers are
// excluded from text-box auditing because their intentional proximity is structural.
pptx._slides.forEach((slide, index) => {
  warnIfSlideHasOverlaps(slide, index + 1);
  warnIfSlideElementsOutOfBounds(slide, index + 1);
});

pptx.writeFile({ fileName: OUT });
console.log(`[SUCCESS] Wrote ${pptx._slides.length} slides | ${OUT}`);
