"""Drawing helpers for the midterm deck (reportlab, vector, top-left origin)."""
import re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color

W, H = 960, 540
pdfmetrics.registerFont(TTFont('R', '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'))
pdfmetrics.registerFont(TTFont('G', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('GB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('B', '/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf'))

# black with opacity levels (rendered as flat greys on white)
K100, K75, K55, K30, K12 = (HexColor(h) for h in ('#000000', '#404040', '#737373', '#B3B3B3', '#E3E3E3'))
CONT, FRAG = HexColor('#1F4E89'), HexColor('#C8641E')
SC = {'TOP1': HexColor('#1F4E89'), 'STEP3': HexColor('#2A9D8F'),
      'UNIFORM': HexColor('#8C8C8C'), 'LOW3': HexColor('#C8641E')}
ML = 56
CW = W - 2 * ML
TOKEN = re.compile(r'(_\{[^}]*\}|\^\{[^}]*\}|−|[\u0391-\u03c9])')


def Y(y):
    return H - y


def tw(s, size, font='R'):
    """width of rich string"""
    w = 0
    for part in TOKEN.split(s):
        if not part:
            continue
        if part[0] in '_^' and len(part) > 1 and part[1] == '{':
            w += pdfmetrics.stringWidth(part[2:-1].replace('−', '–'), font, size * .66)
        elif part == '−':
            w += size * .6
        elif '\u0391' <= part <= '\u03c9':
            w += pdfmetrics.stringWidth(part, 'GB' if font == 'B' else 'G', size * .95)
        else:
            w += pdfmetrics.stringWidth(part, font, size)
    return w


def text(c, x, y, s, size=12, font='R', color=K100, align='l'):
    """baseline y in top-origin coords; supports _{sub} ^{sup} and drawn minus"""
    w = tw(s, size, font)
    if align == 'c':
        x -= w / 2
    elif align == 'r':
        x -= w
    c.setFillColor(color)
    c.setStrokeColor(color)
    cx = x
    for part in TOKEN.split(s):
        if not part:
            continue
        if part[0] in '_^' and len(part) > 1 and part[1] == '{':
            sz = size * .66
            dy = -size * .22 if part[0] == '_' else size * .38
            c.setFont(font, sz)
            sb = part[2:-1].replace('−', '–')
            c.drawString(cx, Y(y) + dy, sb)
            cx += pdfmetrics.stringWidth(sb, font, sz)
        elif part == '−':
            c.setLineWidth(max(.7, size * .07))
            c.line(cx + size * .08, Y(y) + size * .27, cx + size * .52, Y(y) + size * .27)
            cx += size * .6
        elif '\u0391' <= part <= '\u03c9':
            gf = 'GB' if font == 'B' else 'G'
            c.setFont(gf, size * .95)
            c.drawString(cx, Y(y), part)
            cx += pdfmetrics.stringWidth(part, gf, size * .95)
        else:
            c.setFont(font, size)
            c.drawString(cx, Y(y), part)
            cx += pdfmetrics.stringWidth(part, font, size)
    return w


def wrap(c, x, y, s, width, size=12, font='R', color=K75, lead=1.5, align='l'):
    """simple Korean-friendly wrap by characters/words; returns next y"""
    lines, cur = [], ''
    for ch in s:
        if ch == '\n':
            lines.append(cur); cur = ''; continue
        if tw(cur + ch, size, font) > width and cur:
            # prefer break at last space
            if ' ' in cur and ch != ' ':
                i = cur.rfind(' ')
                if i > len(cur) * .5:
                    lines.append(cur[:i]); cur = cur[i + 1:] + ch; continue
            lines.append(cur); cur = ch.lstrip()
        else:
            cur += ch
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines):
        text(c, x, y + i * size * lead, ln, size, font, color, align)
    return y + len(lines) * size * lead


def line(c, x1, y1, x2, y2, color=K100, w=.75, dash=None):
    c.setStrokeColor(color); c.setLineWidth(w)
    c.setDash(dash) if dash else c.setDash()
    c.line(x1, Y(y1), x2, Y(y2))
    c.setDash()


def rect(c, x, y, w, h, fill=None, stroke=None, sw=.75, dash=None):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(sw)
    c.setDash(dash) if dash else c.setDash()
    c.rect(x, Y(y + h), w, h, fill=fill is not None, stroke=stroke is not None)
    c.setDash()


def dot(c, x, y, r=4, fill=K100, stroke=None, sw=1.2):
    c.setFillColor(fill if fill is not None else Color(1, 1, 1))
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(sw)
    c.circle(x, Y(y), r, fill=1, stroke=1)


def polyline(c, pts, color, w=1.8, dash=None):
    c.setStrokeColor(color); c.setLineWidth(w)
    c.setDash(dash) if dash else c.setDash()
    p = c.beginPath()
    p.moveTo(pts[0][0], Y(pts[0][1]))
    for x, y in pts[1:]:
        p.lineTo(x, Y(y))
    c.drawPath(p, stroke=1, fill=0)
    c.setDash()


def band(c, upper, lower, color, alpha=.14):
    c.saveState()
    c.setFillColor(color); c.setFillAlpha(alpha)
    p = c.beginPath()
    p.moveTo(upper[0][0], Y(upper[0][1]))
    for x, y in upper[1:]:
        p.lineTo(x, Y(y))
    for x, y in reversed(lower):
        p.lineTo(x, Y(y))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def frac(c, cx, axis_y, num, den, size=22, color=K100):
    """fraction centered at cx; axis_y = y of fraction bar"""
    wn, wd = tw(num, size), tw(den, size)
    w = max(wn, wd) + 8
    text(c, cx, axis_y - size * .32, num, size, 'R', color, 'c')
    line(c, cx - w / 2, axis_y, cx + w / 2, axis_y, color, 1)
    text(c, cx, axis_y + size * .95, den, size, 'R', color, 'c')
    return w


class Deck:
    def __init__(self, path, total=18):
        self.c = canvas.Canvas(path, pagesize=(W, H))
        self.c.setTitle('다층 상업시설의 프로그램 배치와 수직동선 마찰 — 논문 중간발표')
        self.c.setAuthor('Bong Seong-Hyun')
        self.c.setSubject('논문 중간발표 (18 slides)')
        self.total = total
        self.n = 0
        self.inventory = []

    def slide(self, section, title, subtitle, source=None):
        c = self.c
        if self.n:
            c.showPage()
        self.n += 1
        c.setFillColor(HexColor('#FFFFFF')); c.rect(0, 0, W, H, fill=1, stroke=0)
        text(c, ML, 44, section, 10, 'R', K55)
        text(c, ML, 80, title, 22, 'B', K100)
        text(c, ML, 104, subtitle, 12.5, 'R', K55)
        self.inventory.append((self.n, 'title', title))
        self.inventory.append((self.n, 'subtitle', subtitle))
        if self.n > 0:
            text(c, W - ML, 510, f'{self.n} / {self.total}', 10, 'R', K55, 'r')
            if source:
                text(c, ML, 510, source, 10, 'R', K55)
        return c

    def note(self, kind, s):
        self.inventory.append((self.n, kind, s))

    def save(self):
        self.c.save()
