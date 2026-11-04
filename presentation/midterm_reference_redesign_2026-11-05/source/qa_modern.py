#!/usr/bin/env python3
"""Final structural, raster, text, font, and content QA for the modern deck."""

from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools.ttLib import TTFont
from PIL import Image, ImageStat
from pypdf import PdfReader

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent
QA = ROOT / "qa"
QA.mkdir(parents=True, exist_ok=True)
PPTX = ROOT / "vertical_flow_final_modern_academic.pptx"
PDF = ROOT / "vertical_flow_final_modern_academic.pdf"
PNG_DIR = ROOT / "slide_png"
EXPECTED = 18

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def natural_key(value: str | Path) -> tuple[int, str]:
    name = Path(value).stem
    match = re.search(r"(\d+)", name)
    return (int(match.group(1)) if match else 0, str(value))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def xml_text(payload: bytes) -> str:
    root = ET.fromstring(payload)
    return "\n".join(node.text or "" for node in root.findall(".//a:t", NS))


checks: list[dict[str, object]] = []


def check(name: str, passed: bool, evidence: object) -> None:
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})


with zipfile.ZipFile(PPTX) as archive:
    names = archive.namelist()
    check("PPTX ZIP integrity", archive.testzip() is None, "testzip=None")
    slides = sorted(
        [name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)],
        key=natural_key,
    )
    notes = sorted(
        [name for name in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)],
        key=natural_key,
    )
    check("Exactly 18 slides", len(slides) == EXPECTED, f"count={len(slides)}")
    check("Exactly 18 speaker-note parts", len(notes) == EXPECTED, f"count={len(notes)}")

    presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
    size = presentation.find("p:sldSz", NS)
    cx, cy = int(size.attrib["cx"]), int(size.attrib["cy"])
    ratio = cx / cy
    check("16:9 slide ratio", abs(ratio - 16 / 9) < 0.002, f"{cx}x{cy}, ratio={ratio:.6f}")

    texts = [xml_text(archive.read(name)) for name in slides]
    all_text = "\n".join(texts)
    (QA / "extracted_slide_text.txt").write_text(
        "\n\n".join(f"--- SLIDE {index:02d} ---\n{text}" for index, text in enumerate(texts, 1)),
        encoding="utf-8",
    )
    check("Every slide has substantive text", all(len(text.strip()) >= 30 for text in texts), [len(text.strip()) for text in texts])
    placeholders = re.findall(r"(?i)\b(?:lorem|ipsum|todo|xxx|insert)\b", all_text)
    check("No placeholder text", not placeholders, placeholders)

    required = [
        "다층 상업시설의 프로그램 배치와",
        "U₁ = 1F → 2F",
        "Tᵣ = U₍ᵣ,8₎ / U₍ᵣ,1₎",
        "12,346명",
        "448명",
        "3.6%",
        "51.7%",
        "+6.0%",
        "+10.9%",
        "+18.4%",
        "10.2%",
        "60.1%",
        "39.7%",
        "6.7%",
        "58.7%",
        "9,112명",
        "혼잡·수용",
    ]
    missing = [value for value in required if value not in all_text]
    check("Required paper-aligned claims present", not missing, f"missing={missing}")

    background_failures: list[int] = []
    for index, name in enumerate(slides, 1):
        root = ET.fromstring(archive.read(name))
        colors = [node.attrib.get("val", "").upper() for node in root.findall("./p:cSld/p:bg/p:bgPr/a:solidFill/a:srgbClr", NS)]
        if colors != ["FFFFFF"]:
            background_failures.append(index)
    check("Every PPTX slide has explicit pure-white background", not background_failures, f"failures={background_failures}")

    empty_notes: list[int] = []
    for index, name in enumerate(notes, 1):
        note_text = xml_text(archive.read(name)).strip()
        if len(note_text) < 40:
            empty_notes.append(index)
    check("Every slide has substantive speaker notes", not empty_notes, f"empty_or_short={empty_notes}")

    media = [name for name in names if name.startswith("ppt/media/") and not name.endswith("/")]
    check("Deck is native text/vector", len(media) == 0, f"embedded_media_count={len(media)}")


reader = PdfReader(str(PDF))
check("PDF has 18 pages", len(reader.pages) == EXPECTED, f"pages={len(reader.pages)}")
pdf_text_lengths = [len((page.extract_text() or "").strip()) for page in reader.pages]
check("PDF text is searchable/selectable on every page", all(length >= 30 for length in pdf_text_lengths), pdf_text_lengths)

page_ratios = []
for page in reader.pages:
    box = page.mediabox
    page_ratios.append(float(box.width) / float(box.height))
check("PDF pages preserve 16:9", all(abs(value - 16 / 9) < 0.003 for value in page_ratios), [round(value, 6) for value in page_ratios])


font_records: dict[str, dict[str, object]] = {}
for page in reader.pages:
    resources = page.get("/Resources")
    if not resources:
        continue
    fonts = resources.get("/Font", {})
    fonts = fonts.get_object() if hasattr(fonts, "get_object") else fonts
    for reference in fonts.values():
        font = reference.get_object()
        descriptors = []
        descendants = font.get("/DescendantFonts")
        if descendants:
            for descendant in descendants:
                descriptor = descendant.get_object().get("/FontDescriptor")
                if descriptor:
                    descriptors.append(descriptor.get_object())
        elif font.get("/FontDescriptor"):
            descriptors.append(font.get("/FontDescriptor").get_object())
        for descriptor in descriptors:
            pdf_name = str(descriptor.get("/FontName"))
            if pdf_name in font_records:
                continue
            stream = descriptor.get("/FontFile2") or descriptor.get("/FontFile3") or descriptor.get("/FontFile")
            internal_names: list[str] = []
            embedded = stream is not None
            if stream is not None:
                payload = stream.get_object().get_data()
                try:
                    ttfont = TTFont(io.BytesIO(payload))
                    for entry in ttfont["name"].names:
                        if entry.nameID in (1, 2, 4):
                            try:
                                value = entry.toUnicode()
                            except Exception:
                                continue
                            if value not in internal_names:
                                internal_names.append(value)
                except Exception as exc:
                    internal_names.append(f"parse_error:{type(exc).__name__}")
            font_records[pdf_name] = {"embedded": embedded, "internal_names": internal_names}

check("Every PDF font has an embedded font stream", all(record["embedded"] for record in font_records.values()), font_records)
pretendard_names = [name for record in font_records.values() for name in record["internal_names"] if "Pretendard" in name]
check("Pretendard is genuinely embedded", bool(pretendard_names), pretendard_names)
forbidden_fallbacks = [name for record in font_records.values() for name in record["internal_names"] if name in {"Gulim", "Batang"}]
check("No Gulim/Batang fallback in final PDF", not forbidden_fallbacks, forbidden_fallbacks)


pngs = sorted(PNG_DIR.glob("slide_*.png"), key=natural_key)
check("Exactly 18 final PNG renders", len(pngs) == EXPECTED, f"count={len(pngs)}")
bad_dimensions: list[str] = []
nonwhite_corners: list[str] = []
for png in pngs:
    with Image.open(png) as image:
        if image.size != (1920, 1080):
            bad_dimensions.append(f"{png.name}:{image.size}")
        image = image.convert("RGB")
        width, height = image.size
        crops = [
            image.crop((0, 0, 24, 24)),
            image.crop((width - 24, 0, width, 24)),
            image.crop((0, height - 24, 24, height)),
            image.crop((width - 24, height - 24, width, height)),
        ]
        means = [ImageStat.Stat(crop).mean for crop in crops]
        if any(min(channel) < 252 for channel in means):
            nonwhite_corners.append(f"{png.name}:{means}")
check("PNG renders are 1920x1080", not bad_dimensions, bad_dimensions)
check("All rendered slide corners are pure/near white", not nonwhite_corners, nonwhite_corners)


payload = {
    "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
    "pptx": str(PPTX.resolve()),
    "pdf": str(PDF.resolve()),
    "png_directory": str(PNG_DIR.resolve()),
    "pptx_sha256": sha256(PPTX),
    "pdf_sha256": sha256(PDF),
    "pdf_fonts": font_records,
    "checks": checks,
}
result_path = QA / "qa_final.json"
result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
for item in checks:
    print(f"[{item['status']}] {item['check']} | {item['evidence']}")
print(f"[{payload['status']}] Final QA | {result_path.resolve()}")
raise SystemExit(0 if payload["status"] == "PASS" else 1)
