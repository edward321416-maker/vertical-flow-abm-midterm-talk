#!/usr/bin/env python3
"""Extract every text object of the current 18-page deck into title_inventory.csv.

Sources scanned (read-only):
  1. inputs/vertical_flow_presentation_clear_titles.pdf  (main 18-page source; every text line,
     with font, size, colour, position and hidden/duplicate flags)
  2. inputs/vertical_flow_final_modern_academic.pptx     (prior deck lineage: slide text and
     speaker notes, so that framing that survives only in an older layer is still inventoried)

Spaces: the PowerPoint export stores Pretendard runs as positioned glyphs without space
characters ("발표구성"). `text_display` re-inserts a space wherever the glyph gap exceeds
0.18 em, which reproduces the visible wording; `text_extracted` keeps the raw text layer.

Roles are assigned by layout rules for this deck (960 x 540 pt) plus explicit per-page rules
for chart pages. Usage: python3 -I extract_title_inventory.py
"""
from __future__ import annotations

import csv
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

import pymupdf

TASK = Path(__file__).resolve().parent.parent
PDF = TASK / "inputs" / "vertical_flow_presentation_clear_titles.pdf"
PPTX = TASK / "inputs" / "vertical_flow_final_modern_academic.pptx"
OUT = TASK / "title_inventory.csv"

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

INTERNAL_CODE = re.compile(r"\bRQ[1-4]\b|\bE[12]\b|gamma|\bAUFR\b|γ")
CHART_PAGES = {10, 11, 12, 13, 14, 15, 16}


def display_text(chars: list[dict], size: float) -> str:
    out = []
    prev = None
    for ch in chars:
        c = ch["c"]
        if prev is not None and c != " " and out and out[-1] != " ":
            gap = ch["bbox"][0] - prev["bbox"][2]
            if gap > 0.18 * size:
                out.append(" ")
        out.append(c)
        prev = ch
    return re.sub(r"\s+", " ", "".join(out)).strip()


def classify(page: int, y: float, x: float, size: float, bold: bool, text: str, title_size: float) -> str:
    t = text.strip()
    if re.fullmatch(r"\d{1,2} / 18", t) and y > 500:
        return "footer_page_number"
    if re.fullmatch(r"\d{2} / 18", t) and y < 80:
        return "header_page_number"
    if re.fullmatch(r"\d{2}", t) and y < 60 and x > 850:
        return "header_page_marker"
    if y > 505 and size <= 9.5:
        return "footnote_source" if t.startswith("출처") else "footnote"
    if page == 1:
        if size >= 20:
            return "cover_title"
        if y < 80:
            return "cover_kicker"
        if bold:
            return "cover_presenter"
        if "대학교" in t:
            return "cover_affiliation"
        return "cover_subtitle"
    if abs(size - title_size) < 0.01 and y < 60:
        return "page_title"
    if y < 80 and size < 13:
        return "page_subtitle"
    if page == 2:
        if re.fullmatch(r"0[1-6]", t):
            return "toc_number"
        if size >= 15:
            return "toc_item"
        return "toc_description"
    if page in CHART_PAGES:
        if re.fullmatch(r"[-−]?\d+(\.\d+)?k?%?", t) and size <= 10.5:
            return "chart_axis_tick"
        if t in {"연속형", "분절형"}:
            return "chart_legend"
        if re.fullmatch(r"U\d(/U\d)?", t):
            return "chart_axis_category"
        if re.fullmatch(r"γ=\d", t):
            return "chart_row_label"
        if size >= 18:
            return "chart_value_callout"
        if page in (15, 16) and t in {"TOP1", "STEP3", "UNIFORM", "LOW3", "배치", "층", "U₈ 평균", "R"}:
            return "table_heading" if t in {"배치", "층", "U₈ 평균", "R"} or page == 15 else "chart_row_label"
        if re.fullmatch(r"[1-9]F", t):
            return "table_row_label"
        if re.fullmatch(r"0\.\d+", t) or re.fullmatch(r"[\d,]+명", t):
            return "table_cell_value"
        return "chart_annotation"
    if (re.fullmatch(r"[1-9]F", t) or re.fullmatch(r"U[1-8]", t) or t in {"=", "4", "U", "AUFR", "T", "r", "r,b"}
            or re.fullmatch(r"AUFR\d", t) or re.fullmatch(r"[1-9]F\s*→\s*[1-9]F", t)):
        return "diagram_label"
    if re.fullmatch(r"0[1-9]", t):
        return "list_number"
    if size >= 14 or bold:
        return "internal_heading"
    return "body_text"


def issues_for(page: int, role: str, text: str) -> str:
    notes = []
    if re.search(r"RQ[1-4]\s*·\s*RQ[1-4]", text) and role in {"toc_item", "page_title", "internal_heading"}:
        notes.append("internal code used as audience-facing heading")
    if re.fullmatch(r"E1\s*·\s*E2.*", text) and role in {"toc_item", "page_title", "internal_heading"}:
        notes.append("E1/E2 code used as heading")
    if "학회" in text or "학술 발표" in text:
        notes.append("conference framing; replace with 논문 중간발표")
    if text.strip() in {"연구 발표"} and role == "cover_kicker":
        notes.append("generic kicker; spec requires 논문 중간발표")
    if re.search(r"\br,b\b|\(r,b\)|\(r,8\)|ᵦ|x_j|x_upper|M_above", text):
        notes.append("subscript typeset as plain/fallback text")
    if "종합 결론" in text:
        notes.append("spec: avoid 종합 결론")
    if role == "page_title" and len(text) > 30:
        notes.append(f"title length {len(text)} chars > ~25")
    return "; ".join(notes)


def pdf_rows() -> list[dict]:
    doc = pymupdf.open(str(PDF))
    rows: list[dict] = []
    for pno in range(len(doc)):
        page = doc[pno]
        W, H = page.rect.width, page.rect.height
        raw = page.get_text("rawdict")
        lines = []
        for block in raw["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                spans = [s for s in line["spans"] if "".join(c["c"] for c in s["chars"]).strip()]
                if not spans:
                    continue
                chars = [c for s in spans for c in s["chars"]]
                main = max(spans, key=lambda s: len(s["chars"]))
                lines.append({
                    "x": round(line["bbox"][0], 1), "y": round(line["bbox"][1], 1),
                    "size": round(main["size"], 1), "font": main["font"], "color": f"#{main['color']:06X}",
                    "alpha": main.get("alpha", 255),
                    "raw": "".join(c["c"] for c in chars),
                    "display": display_text(chars, main["size"]),
                    "bold": "Bold" in main["font"] or "SemiBold" in main["font"],
                })
        sizes = [ln["size"] for ln in lines if ln["y"] < 60 and ln["x"] < 200]
        title_size = max(sizes) if sizes else 0
        counts = Counter(ln["display"] for ln in lines)
        lines.sort(key=lambda ln: (ln["y"], ln["x"]))
        for i, ln in enumerate(lines, 1):
            flags = []
            if ln["color"] in {"#FFFFFF", "#FEFEFE"}:
                flags.append("white_text")
            if ln["alpha"] == 0:
                flags.append("alpha0")
            if ln["x"] < 0 or ln["y"] < 0 or ln["x"] > W or ln["y"] > H:
                flags.append("off_page")
            if ln["size"] < 4:
                flags.append("tiny")
            if counts[ln["display"]] > 1:
                flags.append(f"duplicate_x{counts[ln['display']]}")
            if " " not in ln["raw"] and " " in ln["display"]:
                flags.append("spaces_missing_in_text_layer")
            role = classify(pno + 1, ln["y"], ln["x"], ln["size"], ln["bold"], ln["display"], title_size)
            rows.append({
                "page": pno + 1, "source": PDF.name, "object_no": i, "role": role,
                "font": ln["font"], "size_pt": ln["size"], "color": ln["color"],
                "x_pt": ln["x"], "y_pt": ln["y"], "flags": " ".join(flags),
                "text_extracted": ln["raw"], "text_display": ln["display"],
                "issue": issues_for(pno + 1, role, ln["display"]),
            })
    return rows


def pptx_rows() -> list[dict]:
    rows: list[dict] = []
    with zipfile.ZipFile(PPTX) as z:
        names = z.namelist()
        def num(n):
            return int(re.search(r"(\d+)\.xml$", n).group(1))
        slides = sorted([n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)], key=num)
        notes = {num(n): n for n in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)}
        for s in slides:
            k = num(s)
            root = ET.fromstring(z.read(s))
            j = 0
            for para in root.iter("{%s}p" % NS["a"]):
                t = "".join(r.text or "" for r in para.iter("{%s}t" % NS["a"])).strip()
                if not t:
                    continue
                j += 1
                rows.append({
                    "page": k, "source": PPTX.name + " (prior deck slide text)", "object_no": j,
                    "role": "prior_slide_text", "font": "", "size_pt": "", "color": "", "x_pt": "", "y_pt": "",
                    "flags": "prior_layer", "text_extracted": t, "text_display": t,
                    "issue": issues_for(k, "page_title" if j == 1 else "internal_heading", t),
                })
        for k in sorted(notes):
            root = ET.fromstring(z.read(notes[k]))
            t = " ".join((n.text or "").strip() for n in root.iter("{%s}t" % NS["a"]) if (n.text or "").strip())
            t = re.sub(r"^\s*\d+\s*$", "", t).strip()
            if t:
                rows.append({
                    "page": k, "source": PPTX.name + " (speaker notes)", "object_no": 1,
                    "role": "speaker_notes", "font": "", "size_pt": "", "color": "", "x_pt": "", "y_pt": "",
                    "flags": "notes_layer", "text_extracted": t, "text_display": t,
                    "issue": issues_for(k, "notes", t),
                })
    return rows


def main() -> None:
    rows = pdf_rows() + pptx_rows()
    fields = ["page", "source", "object_no", "role", "font", "size_pt", "color", "x_pt", "y_pt",
              "flags", "text_extracted", "text_display", "issue"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    by_role = Counter(r["role"] for r in rows)
    print(f"[OK] {len(rows)} rows -> {OUT}")
    print("roles:", dict(by_role))
    print("issues:", sum(1 for r in rows if r["issue"]))


if __name__ == "__main__":
    main()
