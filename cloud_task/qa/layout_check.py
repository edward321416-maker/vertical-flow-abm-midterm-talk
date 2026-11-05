"""QA: layout audit of the final PDF.

For every page: text objects stay inside a 16pt safe margin, no two text objects
overlap, minimum font size, fonts embedded, white background, and colour used
only on data slides. Also renders every page at 150 dpi plus a contact sheet
into cloud_task/qa/renders/ for visual review.

Usage: python3 cloud_task/qa/layout_check.py [deck.pdf]
"""
import sys, csv, itertools
from pathlib import Path
import numpy as np
import pypdfium2 as pdfium
import pypdfium2.raw as raw
import ctypes
from pypdf import PdfReader
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / 'cloud_task' / 'output' / 'vertical_flow_midterm_refined.pdf'
RD = REPO / 'cloud_task' / 'qa' / 'renders'
RD.mkdir(parents=True, exist_ok=True)
MARGIN = 16
COLOR_FREE = {1, 2, 4, 5, 6, 17, 18}   # cover, contents, text-only slides: no chart colour expected

doc = pdfium.PdfDocument(str(PDF))
rows, fails = [], 0


def rec(page, item, value, ok):
    global fails
    rows.append([page, item, value, 'PASS' if ok else 'FAIL'])
    fails += 0 if ok else 1


# fonts embedded (pypdf walk of page resources)
reader = PdfReader(str(PDF))
fonts = {}
for pg in reader.pages:
    for f in (pg['/Resources'].get('/Font') or {}).values():
        f = f.get_object()
        fd = f.get('/FontDescriptor')
        emb = bool(fd and any(k in fd.get_object() for k in ('/FontFile', '/FontFile2', '/FontFile3')))
        fonts[f['/BaseFont']] = emb
for name, emb in sorted(fonts.items()):
    rec(0, f'font {name} embedded', emb, emb)

thumbs = []
for i in range(len(doc)):
    page = doc[i]
    W, H = page.get_size()
    boxes, sizes = [], []
    tp = page.get_textpage()
    for obj in page.get_objects(filter=[raw.FPDF_PAGEOBJ_TEXT]):
        l, b, r, t = obj.get_bounds()
        c_fs = ctypes.c_float()
        raw.FPDFTextObj_GetFontSize(obj.raw, ctypes.byref(c_fs))
        sizes.append(c_fs.value * abs(obj.get_matrix().get()[3]))
        n = raw.FPDFTextObj_GetText(obj.raw, tp.raw, None, 0)
        buf = ctypes.create_string_buffer(n)
        raw.FPDFTextObj_GetText(obj.raw, tp.raw, ctypes.cast(buf, ctypes.POINTER(ctypes.c_ushort)), n)
        s_ = buf.raw.decode('utf-16-le', 'ignore').rstrip('\x00')
        boxes.append((l, b, r, t, s_))
    gfx, allg = [], []
    for obj in page.get_objects(filter=[raw.FPDF_PAGEOBJ_PATH]):
        l, b_, r, t = obj.get_bounds()
        if r - l > W - 1 and t - b_ > H - 1:
            continue  # full-page white background
        allg.append((l, b_, r, t))
        if l < MARGIN - 1 or r > W - MARGIN + 1 or b_ < MARGIN - 1 or t > H - MARGIN + 1:
            gfx.append((round(l), round(b_), round(r), round(t)))
    rec(i + 1, 'graphics (lines/bars/boxes) inside 16pt safe area', f'{len(gfx)} outside {gfx[:3]}', not gfx)
    # content must also respect the 56pt side margins used by the grid (allow 4pt tolerance)
    wide = [g for g in allg if g[2] > W - 56 + 4 or g[0] < 56 - 4] + [bx for bx in boxes if bx[2] > W - 56 + 4 or bx[0] < 56 - 4]
    rec(i + 1, 'nothing outside the 56pt side margins (±4pt)', f'{len(wide)} {[tuple(round(v) for v in w[:4]) for w in wide[:3]]}', not wide)
    out = [bx for bx in boxes if bx[0] < MARGIN - .5 or bx[2] > W - MARGIN + .5 or bx[1] < MARGIN - .5 or bx[3] > H - MARGIN + .5]
    rec(i + 1, 'text inside 16pt safe area', f'{len(out)} outside', not out)
    # overlap between text objects (shrink 1pt to ignore touching baselines; ignore sub/superscripts
    # glued to their base glyph, which overlap by design within 3pt horizontally)
    ov = 0
    for a, b in itertools.combinations(boxes, 2):
        ix = min(a[2], b[2]) - max(a[0], b[0])
        iy = min(a[3], b[3]) - max(a[1], b[1])
        if ix > 1.5 and iy > 1.5:
            ov += 1
            print(f'  p{i+1} overlap: {a[4]!r} x {b[4]!r}')
    rec(i + 1, 'overlapping text objects', ov, ov == 0)
    mn = min(sizes) if sizes else 0
    rec(i + 1, 'min font size (pt; subscripts are 0.66x)', f'{mn:.1f}', mn >= 6.5)
    small = sum(1 for s in sizes if s < 10 and s > 7.5)
    rows.append([i + 1, 'text objects 7.5–10pt (non-subscript small text)', small, 'INFO'])
    img = page.render(scale=150 / 72).to_pil().convert('RGB')
    img.save(RD / f'slide_{i+1:02d}.png')
    a = np.asarray(img).astype(int)
    rec(i + 1, 'white background (corners)', a[3, 3].tolist(), (a[3, 3] == 255).all() and (a[-4, -4] == 255).all())
    sat = (a.max(2) - a.min(2)) > 40
    colored = sat.mean()
    ok = colored < 0.0005 if (i + 1) in COLOR_FREE else True
    rec(i + 1, 'coloured pixel share', f'{colored*100:.2f}%', ok)
    thumbs.append(img.resize((480, 270)))

sheet = Image.new('RGB', (3 * 480 + 4 * 8, 6 * 270 + 7 * 8), '#9a9a9a')
for k, t in enumerate(thumbs):
    sheet.paste(t, (8 + (k % 3) * 488, 8 + (k // 3) * 278))
sheet.save(RD / 'contact_sheet.png')
with open(REPO / 'cloud_task' / 'qa' / 'layout_check.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['slide', 'check', 'value', 'result']); w.writerows(rows)
print(f'{sum(r[-1] != "INFO" for r in rows)} checks, {fails} failed')
for r in rows:
    if r[-1] == 'FAIL':
        print('FAIL', r)
sys.exit(1 if fails else 0)
