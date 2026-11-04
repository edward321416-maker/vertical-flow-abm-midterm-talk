const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.defineLayout({ name: 'ACADEMIC_WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'ACADEMIC_WIDE';
pptx.author = '봉성현';
pptx.company = 'Academic research presentation';
pptx.subject = '다층 상업시설의 프로그램 배치와 수직동선 마찰이 층간 상행유량에 미치는 영향';
pptx.title = '다층 상업시설의 프로그램 배치와 수직동선 마찰이 층간 상행유량에 미치는 영향';
pptx.lang = 'ko-KR';
pptx.theme = {
  headFontFace: 'Pretendard',
  bodyFontFace: 'Pretendard',
  lang: 'ko-KR',
};

const W = 13.333;
const H = 7.5;
const FONT = 'Pretendard';
const S = pptx.ShapeType;

const C = {
  WHITE: 'FFFFFF',
  BLACK: '000000',
  INK: '222222',
  BODY: '333333',
  MID: '666666',
  LIGHT: '888888',
  RULE: 'C9C9C9',
  HAIR: 'E5E5E5',
  CONT: '2B6F9E',
  CONT2: '77A8C7',
  FRAG: 'B66A3C',
  FRAG2: 'D5A17D',
  DATA_GRAY: '7A7A7A',
  DATA_LIGHT: 'B7B7B7',
};

function audit(slide, item) {
  if (!slide._auditBoxes) slide._auditBoxes = [];
  slide._auditBoxes.push(item);
}

function text(slide, value, x, y, w, h, options = {}) {
  const { audit: shouldAudit = true, allowOverlap = false, ...pptOptions } = options;
  slide.addText(value, {
    x, y, w, h,
    fontFace: pptOptions.bold ? 'Pretendard SemiBold' : FONT,
    fontSize: 16,
    color: C.BODY,
    margin: 0,
    fit: 'shrink',
    valign: 'mid',
    breakLine: false,
    ...pptOptions,
  });
  if (shouldAudit) audit(slide, { kind: 'text', label: String(value).slice(0, 32), x, y, w, h, allowOverlap });
}

function rect(slide, x, y, w, h, options = {}) {
  const { audit: shouldAudit = false, allowOverlap = true, ...shapeOptions } = options;
  slide.addShape(shapeOptions.radius ? S.roundRect : S.rect, {
    x, y, w, h,
    fill: { color: shapeOptions.fill || C.WHITE, transparency: shapeOptions.transparency || 0 },
    line: {
      color: shapeOptions.line || C.RULE,
      width: shapeOptions.width === undefined ? 0.7 : shapeOptions.width,
      dashType: shapeOptions.dash || 'solid',
    },
  });
  if (shouldAudit) audit(slide, { kind: 'shape', label: 'rect', x, y, w, h, allowOverlap });
}

function line(slide, x, y, w, h, color = C.RULE, width = 0.8, dash = 'solid', endArrowType, beginArrowType) {
  slide.addShape(S.line, {
    x: x + Math.min(0, w),
    y: y + Math.min(0, h),
    w: Math.abs(w),
    h: Math.abs(h),
    flipH: w < 0,
    flipV: h < 0,
    line: { color, width, dashType: dash, endArrowType, beginArrowType },
  });
}

function circle(slide, x, y, d, fill = C.WHITE, stroke = C.BLACK, width = 0.8) {
  slide.addShape(S.ellipse, {
    x, y, w: d, h: d,
    fill: { color: fill },
    line: { color: stroke, width },
  });
}

function startSlide(title, no, source, subtitle = '') {
  const slide = pptx.addSlide();
  slide.background = { color: C.WHITE };
  text(slide, title, 0.66, 0.42, 10.95, 0.48, {
    fontSize: 27, bold: true, color: C.BLACK, valign: 'top',
  });
  if (subtitle) {
    text(slide, subtitle, 0.67, 0.91, 10.9, 0.26, {
      fontSize: 11.5, color: C.MID, valign: 'top',
    });
  }
  text(slide, String(no).padStart(2, '0'), 12.12, 0.48, 0.55, 0.22, {
    fontSize: 9.5, bold: true, color: C.MID, align: 'right', charSpacing: 1.2,
  });
  line(slide, 0.66, 1.24, 12.00, 0, C.RULE, 0.75);
  if (source) {
    line(slide, 0.66, 7.02, 12.00, 0, C.HAIR, 0.55);
    text(slide, source, 0.66, 7.10, 11.35, 0.19, {
      fontSize: 8.8, color: C.LIGHT, valign: 'top',
    });
    text(slide, `${no} / 18`, 12.03, 7.10, 0.63, 0.19, {
      fontSize: 8.8, color: C.LIGHT, align: 'right', valign: 'top',
    });
  }
  return slide;
}

function smallLabel(slide, value, x, y, w, options = {}) {
  text(slide, value, x, y, w, 0.22, {
    fontSize: 9.5, bold: true, color: options.color || C.MID,
    charSpacing: options.charSpacing || 0.6,
    align: options.align || 'left',
  });
}

function paragraph(slide, value, x, y, w, h, options = {}) {
  text(slide, value, x, y, w, h, {
    fontSize: options.fontSize || 15,
    color: options.color || C.BODY,
    breakLine: true,
    valign: options.valign || 'top',
    breakLineOnOverflow: false,
    paraSpaceAfterPt: options.paraSpaceAfterPt || 8,
    bullet: options.bullet,
    bold: options.bold || false,
    ...options,
  });
}

function valueLabel(slide, value, label, x, y, w, color = C.BLACK) {
  text(slide, value, x, y, w, 0.43, { fontSize: 25, bold: true, color, valign: 'top' });
  text(slide, label, x, y + 0.48, w, 0.38, { fontSize: 10.5, color: C.MID, valign: 'top' });
}

function floorStack(slide, x, y, w, h, options = {}) {
  const floors = options.floors || 9;
  const gap = options.gap || 0.035;
  const fh = (h - gap * (floors - 1)) / floors;
  const weights = options.weights || null;
  const max = options.maxWeight || (weights ? Math.max(...weights) : 1);
  for (let floor = 1; floor <= floors; floor += 1) {
    const yy = y + h - floor * fh - (floor - 1) * gap;
    let fill = C.WHITE;
    let ratio = 0;
    if (weights) {
      ratio = weights[floor - 1] / max;
      fill = ratio >= 0.72 ? C.CONT : ratio >= 0.35 ? C.CONT2 : ratio >= 0.16 ? 'D9E8F1' : 'F1F1F1';
    }
    rect(slide, x, yy, w, fh, { fill, line: options.line || C.MID, width: options.lineWidth || 0.55 });
    if (options.labels !== false) {
      text(slide, `${floor}F`, x - 0.42, yy, 0.33, fh, {
        fontSize: options.labelSize || 8.4, color: C.MID, align: 'right', audit: false,
      });
    }
    if (weights && options.showWeights) {
      text(slide, weights[floor - 1].toFixed(2), x + 0.04, yy, w - 0.08, fh, {
        fontSize: 7.6, bold: ratio >= 0.35,
        color: ratio >= 0.35 ? C.WHITE : C.MID,
        align: 'center', audit: false,
      });
    }
  }
  if (options.arrow) {
    line(slide, x + w + 0.19, y + h - 0.02, 0, -(h - 0.04), options.arrowColor || C.BLACK, 1.25, 'solid', 'triangle');
  }
}

function axis(slide, x, y, w, h, yMin, yMax, yTicks, formatter = (v) => String(v)) {
  line(slide, x, y + h, w, 0, C.BLACK, 0.9);
  line(slide, x, y, 0, h, C.BLACK, 0.9);
  for (const tick of yTicks) {
    const yy = y + h - ((tick - yMin) / (yMax - yMin)) * h;
    line(slide, x, yy, w, 0, tick === yMin ? C.BLACK : C.HAIR, tick === yMin ? 0.8 : 0.55);
    text(slide, formatter(tick), x - 0.61, yy - 0.12, 0.51, 0.22, {
      fontSize: 9, color: C.MID, align: 'right', audit: false,
    });
  }
}

function lineChart(slide, x, y, w, h, series, options) {
  axis(slide, x, y, w, h, options.yMin || 0, options.yMax, options.yTicks, options.yFormatter);
  const n = series[0].values.length;
  const px = (i) => x + (i / (n - 1)) * w;
  const py = (v) => y + h - ((v - (options.yMin || 0)) / (options.yMax - (options.yMin || 0))) * h;
  for (let i = 0; i < n; i += 1) {
    text(slide, options.labels[i], px(i) - 0.27, y + h + 0.11, 0.54, 0.24, {
      fontSize: 9.3, color: C.MID, align: 'center', audit: false,
    });
  }
  for (const item of series) {
    for (let i = 0; i < n - 1; i += 1) {
      line(slide, px(i), py(item.values[i]), px(i + 1) - px(i), py(item.values[i + 1]) - py(item.values[i]), item.color, item.width || 2.0, item.dash || 'solid');
    }
    for (let i = 0; i < n; i += 1) {
      if (item.marker === 'square') {
        rect(slide, px(i) - 0.055, py(item.values[i]) - 0.055, 0.11, 0.11, { fill: C.WHITE, line: item.color, width: 1.2 });
      } else {
        circle(slide, px(i) - 0.06, py(item.values[i]) - 0.06, 0.12, C.WHITE, item.color, 1.2);
      }
    }
  }
}

function horizontalBars(slide, x, y, w, h, rows, options = {}) {
  const max = options.max || Math.max(...rows.map((r) => r.value));
  const rowH = h / rows.length;
  rows.forEach((row, i) => {
    const yy = y + i * rowH;
    text(slide, row.label, x, yy + 0.08, 1.50, 0.28, { fontSize: 11.2, bold: true, color: C.INK });
    const bx = x + 1.68;
    const bw = (row.value / max) * (w - 2.75);
    line(slide, bx, yy + 0.23, w - 2.75, 0, C.HAIR, 10);
    line(slide, bx, yy + 0.23, bw, 0, row.color || C.CONT, 10);
    text(slide, row.format ? row.format(row.value) : String(row.value), x + w - 0.95, yy + 0.05, 0.90, 0.32, {
      fontSize: 13, bold: true, color: row.color || C.BLACK, align: 'right',
    });
  });
}

function forestPlot(slide, x, y, w, h, rows, options) {
  const mapX = (v) => x + ((v - options.min) / (options.max - options.min)) * w;
  const rowH = h / rows.length;
  for (const tick of options.ticks) {
    const xx = mapX(tick);
    line(slide, xx, y, 0, h, tick === 0 ? C.MID : C.HAIR, tick === 0 ? 1.1 : 0.55, tick === 0 ? 'dash' : 'solid');
    text(slide, `${tick}`, xx - 0.26, y + h + 0.10, 0.52, 0.22, { fontSize: 9, color: C.MID, align: 'center', audit: false });
  }
  rows.forEach((row, i) => {
    const yy = y + rowH * (i + 0.5);
    text(slide, row.label, x - 0.80, yy - 0.15, 0.65, 0.30, { fontSize: 12, bold: true, color: C.INK, align: 'right' });
    line(slide, mapX(row.lo), yy, mapX(row.hi) - mapX(row.lo), 0, row.color || C.CONT, 2.0);
    line(slide, mapX(row.lo), yy - 0.09, 0, 0.18, row.color || C.CONT, 1.2);
    line(slide, mapX(row.hi), yy - 0.09, 0, 0.18, row.color || C.CONT, 1.2);
    circle(slide, mapX(row.estimate) - 0.065, yy - 0.065, 0.13, row.color || C.CONT, row.color || C.CONT, 0.7);
    if (options.showValues !== false) {
      text(slide, `${row.estimate.toFixed(1)}%  [${row.lo.toFixed(1)}, ${row.hi.toFixed(1)}]`, x + w + 0.18, yy - 0.16, 1.62, 0.32, {
        fontSize: 10.3, bold: row.lo > 0, color: row.lo > 0 ? C.BLACK : C.MID,
      });
    }
  });
}

function addNotes(slide, note) {
  slide.addNotes(note);
}

function warnIfSlideHasOverlaps(slide, slideNo) {
  const boxes = (slide._auditBoxes || []).filter((b) => b.kind === 'text' && !b.allowOverlap);
  const overlaps = [];
  for (let i = 0; i < boxes.length; i += 1) {
    for (let j = i + 1; j < boxes.length; j += 1) {
      const a = boxes[i];
      const b = boxes[j];
      const dx = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
      const dy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
      if (dx > 0.025 && dy > 0.025) overlaps.push(`${a.label} <> ${b.label}`);
    }
  }
  if (overlaps.length) {
    console.warn(`[WARN] Slide ${slideNo} text overlaps: ${overlaps.slice(0, 8).join(' | ')}`);
  }
  return overlaps;
}

function warnIfSlideElementsOutOfBounds(slide, slideNo) {
  const problems = (slide._auditBoxes || []).filter((b) => b.x < -0.001 || b.y < -0.001 || b.x + b.w > W + 0.001 || b.y + b.h > H + 0.001);
  if (problems.length) console.warn(`[WARN] Slide ${slideNo} out of bounds: ${problems.map((b) => b.label).join(' | ')}`);
  return problems;
}

module.exports = {
  pptx, C, W, H, FONT, S,
  text, rect, line, circle, startSlide, smallLabel, paragraph, valueLabel,
  floorStack, axis, lineChart, horizontalBars, forestPlot, addNotes,
  warnIfSlideHasOverlaps, warnIfSlideElementsOutOfBounds,
};
