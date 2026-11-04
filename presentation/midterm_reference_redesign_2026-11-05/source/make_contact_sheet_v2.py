#!/usr/bin/env python3
"""Create a labeled slide overview for any rendered deck directory."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def natural_key(path: Path) -> tuple[int, str]:
    match = re.search(r"(\d+)", path.stem)
    return (int(match.group(1)) if match else 0, path.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("png_directory", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--cols", type=int, default=2)
    args = parser.parse_args()

    files = sorted(args.png_directory.glob("slide_*.png"), key=natural_key)
    if len(files) != args.expected:
        raise SystemExit(f"Expected {args.expected} PNGs, found {len(files)} at {args.png_directory.resolve()}")

    thumb_w, thumb_h = 640, 360
    label_h, margin, gap = 42, 28, 24
    rows = math.ceil(len(files) / args.cols)
    canvas_w = margin * 2 + args.cols * thumb_w + (args.cols - 1) * gap
    canvas_h = margin * 2 + rows * (thumb_h + label_h) + (rows - 1) * gap
    canvas = Image.new("RGB", (canvas_w, canvas_h), "#E6E9EA")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/NotoSansKR-Medium.ttf", 22)
    except OSError:
        font = ImageFont.load_default()

    for index, file in enumerate(files):
        col = index % args.cols
        row = index // args.cols
        x = margin + col * (thumb_w + gap)
        y = margin + row * (thumb_h + label_h + gap)
        image = Image.open(file).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        canvas.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="#182332")
        draw.text((x + 15, y + thumb_h + 8), f"SLIDE {index + 1:02d}", font=font, fill="#FFFFFF")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output, quality=95)
    print(f"[SUCCESS] Contact sheet | {args.output.resolve()}")


if __name__ == "__main__":
    main()
