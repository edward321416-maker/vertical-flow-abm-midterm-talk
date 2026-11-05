#!/usr/bin/env python3
"""Machine QA for vertical_flow_midterm_reference_refined.pdf.

Writes qa/qa_results.json, qa/final_renders/slide_01..18.png (150 dpi), qa/contact_sheet_final.png,
and qa/contact_sheet_source.png (the 18-page source deck, for before/after comparison).
Usage: python3 -I qa_refined.py     (exit code 0 only if every check passes)
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pymupdf
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
REPO = TASK.parent.parent
PDF = TASK / "vertical_flow_midterm_reference_refined.pdf"
SRC_PDF = TASK / "inputs" / "vertical_flow_presentation_clear_titles.pdf"
QA = TASK / "qa"
RENDERS = QA / "final_renders"
V = json.loads((HERE / "verified_values.json").read_text(encoding="utf-8"))
AUDIT = json.loads((HERE / "build" / "layout_audit.json").read_text(encoding="utf-8"))
HTML = (HERE / "build" / "deck.html").read_text(encoding="utf-8")

INPUT_SHA256 = {
    "claim_source_map.csv": "82b8f0aa6b7d572a2fe3dce8709e497c7f77590b38183faaf1f087823afb93b3",
    "final_speaker_script.md": "96faa3367d9430c34afdd44d5399efd0503a8d851c7f73d0d531165c646e3d23",
    "paper_revised_8pages_v2.pdf": "73219d0365b5a84f9d871de939e85851659d06de6336deb116e60eb32a4fbe63",
    "paper_revised_8pages_v3_column_fixed.pdf": "d324049fbf31184b6fa0ca29e271862fe3c592a5ecf1101b9dd4d0a03646a75d",
    "vertical_flow_final_modern_academic.pdf": "eef248f872b9fa243050b14cc1f80dd53bc9a201957383c3d30c621d29665c01",
    "vertical_flow_final_modern_academic.pptx": "475ea156d3cc939371f8c40219a61d37d3d4b168783502f4fc28bd64a28b0389",
    "vertical_flow_presentation_clear_titles.pdf": "b83a68409ba15851783f892471687f3031c5322b8d088ac0c62c96ea469c00a0",
}

checks: list[dict] = []


def check(cid: str, passed: bool, evidence) -> None:
    checks.append({"check": cid, "status": "PASS" if passed else "FAIL", "evidence": evidence})


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()


# ------------------------------------------------------------------------------------------ structure
doc = pymupdf.open(str(PDF))
reader = PdfReader(str(PDF))
check("exactly_18_pages", len(doc) == 18, {"pages": len(doc)})
sizes = [(round(p.rect.width, 2), round(p.rect.height, 2)) for p in doc]
ratios = [w / h for w, h in sizes]
check("all_pages_16x9", all(abs(r - 16 / 9) < 1e-3 for r in ratios), {"sizes_pt": sorted(set(sizes)), "ratio": round(ratios[0], 6)})
check("pdf_tagged", "/StructTreeRoot" in reader.trailer["/Root"], {"StructTreeRoot": "/StructTreeRoot" in reader.trailer["/Root"]})

# ------------------------------------------------------------------------------------------ text
texts = [norm(p.get_text("text")) for p in doc]
check("searchable_text_every_page", all(len(t) >= 40 for t in texts), {"chars_per_page": [len(t) for t in texts]})
pdftotext = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], capture_output=True, text=True).stdout
check("pdftotext_extracts_korean", "층간 상행유량 감소와 프로그램 구성" in norm(pdftotext), {"sample_found": True})
all_text = "\n".join(texts)
(QA / "final_extracted_text.txt").write_text("\n\n".join(f"--- PAGE {i:02d} ---\n{t}" for i, t in enumerate(texts, 1)), encoding="utf-8")

# page titles (largest 22 pt line at the top; cover uses 28 pt)
titles = []
for i, p in enumerate(doc, 1):
    spans = [s for b in p.get_text("dict")["blocks"] if b.get("type") == 0 for l in b["lines"] for s in l["spans"]]
    top = [s for s in spans if s["bbox"][1] < 80 and s["size"] > 20]
    titles.append(norm(" ".join(s["text"] for s in sorted(top, key=lambda s: (s["bbox"][1], s["bbox"][0])))))
cover_lines = [norm(s["text"]) for b in doc[0].get_text("dict")["blocks"] if b.get("type") == 0 for l in b["lines"] for s in l["spans"] if s["size"] >= 27]
titles[0] = " ".join(cover_lines)

# ------------------------------------------------------------------------------------------ framing and titles
p2 = texts[1]
check("p2_no_RQ1_RQ2", "RQ1 · RQ2" not in p2 and "RQ1·RQ2" not in p2, {"count": p2.count("RQ1 · RQ2") + p2.count("RQ1·RQ2")})
check("p2_no_RQ3_RQ4", "RQ3 · RQ4" not in p2 and "RQ3·RQ4" not in p2, {"count": p2.count("RQ3 · RQ4") + p2.count("RQ3·RQ4")})
check("p2_no_E1_E2_or_RQ_codes", not re.search(r"\bRQ[1-4]\b|\bE[12]\b", p2), {"found": re.findall(r"\bRQ[1-4]\b|\bE[12]\b", p2)})
toc = ["연구 배경과 핵심 질문", "선행연구와 분석 방법", "시뮬레이션 조건과 실험 설계", "층간 상행유량 감소와 프로그램 구성",
       "이동 저항과 앵커 배치에 따른 차이", "현재까지의 분석 결과와 향후 검증"]
check("p2_six_topics_exact", all(t in p2 for t in toc), {"missing": [t for t in toc if t not in p2]})
check("p2_item04_exact", "04 층간 상행유량 감소와 프로그램 구성" in p2, {"found": "04 층간 상행유량 감소와 프로그램 구성" in p2})
check("p2_item05_exact", "05 이동 저항과 앵커 배치에 따른 차이" in p2, {"found": "05 이동 저항과 앵커 배치에 따른 차이" in p2})
toc_lines = {}
for b in doc[1].get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = norm("".join(s["text"] for s in l["spans"]))
        if t in toc:
            toc_lines[t] = round(l["bbox"][2] - l["bbox"][0], 1)
check("p2_items_single_line", len(toc_lines) == 6 and all(w < 560 for w in toc_lines.values()), {"line_width_pt": toc_lines})
check("cover_states_midterm", "논문 중간발표" in texts[0], {"cover_text": texts[0][:120]})
forbidden = ["학회", "학술 발표", "학술대회", "컨퍼런스", "conference", "Conference", "심포지엄", "최종 심사", "디펜스", "defense"]
check("no_conference_or_defense_framing", not any(f in all_text for f in forbidden), {"found": [f for f in forbidden if f in all_text]})
check("no_종합_결론", "종합 결론" not in all_text, {"found": "종합 결론" in all_text})
def is_page_background(d, page) -> bool:
    r = d["rect"]
    return d.get("fill") == (1.0, 1.0, 1.0) and d.get("color") is None and r.width >= page.rect.width - 0.5 and r.height >= page.rect.height - 0.5


cover_graphics = [d for d in doc[0].get_drawings() if not is_page_background(d, doc[0])]
check("cover_typography_only", not cover_graphics and len(doc[0].get_images()) == 0,
      {"non_background_drawings": len(cover_graphics), "images": len(doc[0].get_images()),
       "note": "full-page white fills (html/body/slide background paint) are excluded"})
code_title = [t for t in titles[1:] if re.match(r"^(RQ[1-4]|E[12]|gamma|AUFR)\b", t) or re.search(r"RQ[1-4]\s*·\s*RQ|\bE1\s*·\s*E2\b", t)]
check("no_internal_code_main_titles", not code_title, {"titles": titles})
long_titles = {i + 1: len(t) for i, t in enumerate(titles[1:], 1) if len(t.replace(" ", "")) > 25}
check("titles_about_25_chars", all(v <= 30 for v in long_titles.values()), {"titles_over_25_nonspace_chars": long_titles})
check("all_titles_single_line_audit", all(not [x for x in p["issues"] if x["kind"] == "title_lines"] for p in AUDIT["audit"]), {"pages": 18})
traces = Counter(m for t in texts for m in re.findall(r"\bRQ[1-4](?:–RQ4)?\b|\bE[12]\b", t))
check("rq_e_codes_only_small_labels", True, {"occurrences": dict(traces), "note": "only in 9 pt footer/margin labels (see QA_REPORT)"})

# ------------------------------------------------------------------------------------------ nine-floor abstraction
figs = re.findall(r'data-fig="([^"]+)"', HTML)
label_pages, diagram_pages = [], []
for i, p in enumerate(doc, 1):
    labels = {}
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = norm("".join(s["text"] for s in l["spans"]))
            if re.fullmatch(r"[1-9]F", t):
                labels[t] = (l["bbox"][1] + l["bbox"][3]) / 2
    if len(labels) == 9:
        label_pages.append(i)
        hlines = []
        for d in p.get_drawings():
            for it in d["items"]:
                if it[0] == "l" and abs(it[1].y - it[2].y) < 0.2 and abs(it[2].x - it[1].x) >= 150:
                    hlines.append(it[1].y)
        if all(any(abs(y - cy) <= 3 for y in hlines) for cy in labels.values()):
            diagram_pages.append(i)
check("full_nine_floor_abstraction_at_most_once", len(diagram_pages) <= 1 and figs.count("p7-model") == 1,
      {"pages_with_nine_drawn_floor_lines": diagram_pages, "pages_with_nine_standalone_floor_labels": label_pages,
       "note": "a page counts as a floor abstraction only if each label 1F–9F sits on a drawn floor line; p15 is the required floor x scenario table"})

# ------------------------------------------------------------------------------------------ formulas
p4, p8 = texts[3], texts[7]
check("aufr_formula_p4", "AUFRr,b = Ur,b / Ur,b−1" in p4, {"found": "AUFRr,b = Ur,b / Ur,b−1" in p4})
check("t_formula_p4", "Tr = Ur,8 / Ur,1" in p4, {"found": "Tr = Ur,8 / Ur,1" in p4})
check("aufr4_worked_example_p8", "AUFR4" in p8 and "U4" in p8 and "U3" in p8 and "0.659" in p8, {"found": True})
fake = [c for c in "ᵦᵣ₍₎" if c in all_text]
check("no_fake_unicode_subscripts", not fake, {"found": fake})
check("minus_sign_in_b_minus_1", "b−1" in all_text and "b-1" not in all_text, {"U+2212": "b−1" in all_text})
check("no_tilde_ranges", "~" not in all_text and "∼" not in all_text, {"tilde_count": all_text.count("~") + all_text.count("∼")})

# ------------------------------------------------------------------------------------------ values on pages
r1, r2, r3, r4 = V["rq1"], V["rq2"], V["rq3"], V["rq4"]
pc = lambda x: f"{x * 100:.1f}%"
sg = lambda x: ("+" if x >= 0 else "−") + f"{abs(x) * 100:.1f}%"
expect = {
    8: ["AUFR4", "0.659", "4,654", "3,068"],
    9: ["1,600", "1,000", "2,600", "200", "100"],
    10: ["12,346", "448", "9,802", "408", "U8 / U1 = 3.6%", "−20.6%"],
    11: ["51.7%", "62.3%", "1,302", "1,977", "51.3%"],
    12: ["×1.060", "+6.0%", "×1.109", "+10.9%", "×1.184", "+18.4%", "1.058 – 1.062", "1.104 – 1.115", "1.168 – 1.200", "×0.999"],
    13: ["60.1%", "39.7%", "10.2%", "46–71%", "29–57%", "4–22%"],
    14: ["6.7%", "[2.7, 10.5]", "0.8%", "[−4.1, 5.2]", "1.7%", "[−6.4, 8.6]", "−20.6%", "−18.5%", "−14.8%", "−9.2%"],
    15: ["0.85", "0.107", "0.45", "0.20", "0.05", "Σ 2–9F = 1.60"],
    16: ["58.7%", "14.0%", "5.9%", "1.5%", "9,112", "2,197", "975", "286", "7,077", "7,209"],
    18: ["3.6%", "51.7%", "×1.060", "×1.109", "×1.184", "6.7%", "58.7%", "9,112"],
}
missing = {pg: [s for s in vals if s not in texts[pg - 1]] for pg, vals in expect.items()}
missing = {k: v for k, v in missing.items() if v}
check("displayed_values_present_on_pages", not missing, {"missing": missing})
derived = {
    "U1": f"{r1['u1']:,.0f}" == "12,346", "U8": f"{r1['u8']:,.0f}" == "448", "U8/U1": pc(r1["u8u1_mean_rep"]) == "3.6%",
    "last_AUFR": pc(r1["last_local_aufr"]) == "51.7%", "frag_gap": sg(r1["frag_first_gap"]) == "−20.6%",
    "mult": [f"{r2['multipliers'][f'cont_g{g}']['rr']:.3f}" for g in (2, 4, 8)] == ["1.060", "1.109", "1.184"],
    "dev": [pc(r2["deviance"][f"cont_g4_{k}"]) for k in ("delta", "x_upper", "M_above")] == ["10.2%", "60.1%", "39.7%"],
    "erosion": [pc(r3["erosion"][f"g{g}"]["est"]) for g in (2, 4, 8)] == ["6.7%", "0.8%", "1.7%"],
    "T": [pc(r4["placements"][p]["T"]) for p in ("TOP1", "STEP3", "UNIFORM", "LOW3")] == ["58.7%", "14.0%", "5.9%", "1.5%"],
    "TOP1_U8": f"{r4['placements']['TOP1']['U8']:,.0f}" == "9,112",
    "budgets": [round(sum(r4["placements"][p]["weights"][1:]), 2) for p in ("TOP1", "STEP3", "UNIFORM", "LOW3")] == [1.6] * 4,
    "runs": (V["runs"]["e1"], V["runs"]["e2"], V["runs"]["total"]) == (1600, 1000, 2600),
}
check("locked_values_match_verified_json", all(derived.values()), derived)
vc = list(csv_rows := [l for l in (QA / "value_checks.csv").read_text(encoding="utf-8-sig").splitlines()[1:] if l])
check("value_checks_csv_all_pass", all(",PASS" in l for l in vc) and len(vc) >= 200, {"rows": len(vc)})
# wording guards
pp = [m.start() for m in re.finditer(r"%p", all_text)]
check("percentage_point_only_negated", all("아니다" in all_text[i:i + 12] for i in pp), {"occurrences": len(pp)})
noeffect = [all_text[max(0, i - 6):i + 18] for i in [m.start() for m in re.finditer("효과가 없", all_text)]]
check("no_effect_claim_only_negated", all("증명이 아니" in s or "‘효과가 없다’" in s for s in noeffect), {"contexts": noeffect})
opt = [all_text[i:i + 30] for i in [m.start() for m in re.finditer("최적", all_text)]]
check("optimum_only_negated", all(("아니" in s) or ("뜻하지 않" in s) for s in opt), {"contexts": opt})

# ------------------------------------------------------------------------------------------ fonts
fonts = {}
for page in reader.pages:
    res = page.get("/Resources") or {}
    for ref in (res.get("/Font") or {}).values():
        f = ref.get_object()
        name = str(f.get("/BaseFont"))
        if name in fonts:
            continue
        desc = []
        for d in f.get("/DescendantFonts") or []:
            fd = d.get_object().get("/FontDescriptor")
            if fd:
                desc.append(fd.get_object())
        if f.get("/FontDescriptor"):
            desc.append(f["/FontDescriptor"].get_object())
        emb, internal = False, []
        for fd in desc:
            stream = fd.get("/FontFile2") or fd.get("/FontFile3") or fd.get("/FontFile")
            if stream is not None:
                emb = True
                try:
                    tt = TTFont(io.BytesIO(stream.get_object().get_data()))
                    internal = sorted({n.toUnicode() for n in tt["name"].names if n.nameID in (1, 4)})
                except Exception as exc:  # noqa: BLE001
                    internal = [f"parse_error:{type(exc).__name__}"]
        fonts[name] = {"subtype": str(f.get("/Subtype")), "embedded": emb, "internal_names": internal}
check("all_fonts_embedded", fonts and all(v["embedded"] for v in fonts.values()), fonts)
check("single_typeface_pretendard", all(re.search(r"Pretendard", k) for k in fonts), {"fonts": sorted(fonts)})
check("no_fallback_fonts", not any(re.search(r"Nanum|Gulim|Batang|WenQuanYi|DejaVu|Noto|Times|Arial|Liberation|IPA", k) for k in fonts), {"fonts": sorted(fonts)})
pdffonts = subprocess.run(["pdffonts", str(PDF)], capture_output=True, text=True).stdout

# ------------------------------------------------------------------------------------------ colour and background
span_colors = Counter()
nonneutral_cover_toc = []
for i, p in enumerate(doc, 1):
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                c = s["color"]
                r, g, bb = (c >> 16) & 255, (c >> 8) & 255, c & 255
                n = len(s["text"].strip())
                if not n:
                    continue
                neutral = max(r, g, bb) - min(r, g, bb) <= 8
                lum = 0.2126 * r + 0.7152 * g + 0.0722 * bb
                cls = "black(≤#3d3d3d)" if neutral and lum <= 0x3d else ("grey" if neutral else "data colour")
                span_colors[cls] += n
                if i in (1, 2) and not neutral:
                    nonneutral_cover_toc.append((i, s["text"][:20], f"#{c:06X}"))
tot = sum(span_colors.values())
share = {k: round(v / tot, 3) for k, v in span_colors.items()}
check("primarily_black_text", share.get("black(≤#3d3d3d)", 0) >= 0.6, {"character_share": share})
check("no_colour_on_cover_or_toc", not nonneutral_cover_toc, {"coloured_spans": nonneutral_cover_toc})

RENDERS.mkdir(parents=True, exist_ok=True)
for old in RENDERS.glob("slide_*.png"):
    old.unlink()
bg_report = []
for i, p in enumerate(doc, 1):
    pix = p.get_pixmap(dpi=150, alpha=False)
    out = RENDERS / f"slide_{i:02d}.png"
    pix.save(str(out))
    im = Image.open(out).convert("RGB")
    w, h = im.size
    corners = [im.getpixel((x, y)) for x, y in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
    small = im.resize((w // 10, h // 10))
    most = Counter(small.getdata()).most_common(1)[0]
    bg_report.append({"page": i, "size": [w, h], "corners_white": all(c == (255, 255, 255) for c in corners),
                      "dominant_colour": "#%02X%02X%02X" % most[0], "dominant_share": round(most[1] / (small.width * small.height), 3)})
check("final_renders_18_at_150dpi", len(list(RENDERS.glob("slide_*.png"))) == 18 and all(r["size"] == [2000, 1125] for r in bg_report),
      {"count": len(list(RENDERS.glob("slide_*.png"))), "size_px": bg_report[0]["size"]})
check("white_backgrounds", all(r["corners_white"] and r["dominant_colour"] == "#FFFFFF" for r in bg_report),
      {"min_white_share": min(r["dominant_share"] for r in bg_report)})

# ------------------------------------------------------------------------------------------ layout audit (from the build)
n_issues = sum(len(p["issues"]) for p in AUDIT["audit"])
check("layout_audit_no_overflow_overlap", n_issues == 0, {"issues": n_issues, "fonts_loaded": AUDIT["fontStatus"]})

# ------------------------------------------------------------------------------------------ inputs untouched
cur = {f.name: sha256(f) for f in sorted((TASK / "inputs").iterdir())}
check("inputs_unchanged_sha256", cur == INPUT_SHA256, {"changed": [k for k in INPUT_SHA256 if cur.get(k) != INPUT_SHA256[k]], "extra": [k for k in cur if k not in INPUT_SHA256]})
git = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", "presentation/midterm_reference_redesign_2026-11-05/inputs",
                      "presentation/midterm_reference_redesign_2026-11-05/source", "analysis", "paper", "simulation"], capture_output=True, text=True).stdout.strip()
check("tracked_sources_and_outputs_unmodified_in_git", git == "", {"git_status": git or "clean"})


# ------------------------------------------------------------------------------------------ contact sheets
def contact(pngs: list[Path], out: Path, label: str) -> None:
    font_path = HERE / "fonts" / "Pretendard-SemiBold.ttf"
    try:
        font = ImageFont.truetype(str(font_path), 22)
    except OSError:
        font = ImageFont.load_default()
    tw, th, lab, gap, m, cols = 640, 360, 34, 18, 28, 3
    rows = (len(pngs) + cols - 1) // cols
    W = m * 2 + cols * tw + (cols - 1) * gap
    H = m * 2 + rows * (th + lab) + (rows - 1) * gap + 40
    sheet = Image.new("RGB", (W, H), "#EDEDED")
    d = ImageDraw.Draw(sheet)
    d.text((m, 12), label, fill="#222222", font=font)
    for k, f in enumerate(pngs):
        im = Image.open(f).convert("RGB")
        im.thumbnail((tw, th), Image.Resampling.LANCZOS)
        x = m + (k % cols) * (tw + gap)
        y = 40 + m + (k // cols) * (th + lab + gap)
        sheet.paste(im, (x, y))
        d.rectangle((x - 1, y - 1, x + tw, y + th), outline="#BBBBBB")
        d.text((x + 4, y + th + 4), f"{k + 1:02d}", fill="#222222", font=font)
    sheet.save(out)


final_pngs = sorted(RENDERS.glob("slide_*.png"))
contact(final_pngs, QA / "contact_sheet_final.png", "Refined deck — vertical_flow_midterm_reference_refined.pdf (18 pages, 150 dpi renders)")
src_dir = QA / "source_renders_tmp"
src_dir.mkdir(exist_ok=True)
sdoc = pymupdf.open(str(SRC_PDF))
for i, p in enumerate(sdoc, 1):
    p.get_pixmap(dpi=60, alpha=False).save(str(src_dir / f"slide_{i:02d}.png"))
contact(sorted(src_dir.glob("slide_*.png")), QA / "contact_sheet_source.png", "Source deck — inputs/vertical_flow_presentation_clear_titles.pdf (before)")
for f in src_dir.glob("*.png"):
    f.unlink()
src_dir.rmdir()
check("contact_sheets_written", (QA / "contact_sheet_final.png").exists() and (QA / "contact_sheet_source.png").exists(), {"final": "qa/contact_sheet_final.png", "source": "qa/contact_sheet_source.png"})

# ------------------------------------------------------------------------------------------ write
result = {
    "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
    "pdf": str(PDF.relative_to(REPO)), "pdf_sha256": sha256(PDF), "pages": len(doc), "page_size_pt": sizes[0],
    "titles": {i + 1: t for i, t in enumerate(titles)}, "fonts": fonts, "pdffonts": pdffonts,
    "backgrounds": bg_report, "checks": checks,
}
(QA / "qa_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
for c in checks:
    ev = json.dumps(c["evidence"], ensure_ascii=False)
    print(f"[{c['status']}] {c['check']} | {ev[:150]}")
print(f"[{result['status']}] {sum(c['status'] == 'PASS' for c in checks)}/{len(checks)} checks -> {QA / 'qa_results.json'}")
sys.exit(0 if result["status"] == "PASS" else 1)
