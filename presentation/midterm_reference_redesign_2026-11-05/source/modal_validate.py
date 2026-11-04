"""One-shot Modal CPU validation of the generated PPTX container.

No service is deployed. The local entrypoint uploads only the generated PPTX bytes to
the already-authenticated Modal workspace, validates the OOXML archive remotely, and
returns structural metadata.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path

import modal


app = modal.App("vertical-flow-pptx-validation-20261105")
image = modal.Image.debian_slim(python_version="3.12")


@app.function(image=image, timeout=300)
def validate_pptx(blob: bytes) -> dict[str, object]:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        bad = archive.testzip()
        names = archive.namelist()
        slides = [name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
        notes = [name for name in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)]
        media = [name for name in names if name.startswith("ppt/media/") and not name.endswith("/")]
        return {
            "zip_integrity": bad is None,
            "slide_count": len(slides),
            "notes_count": len(notes),
            "embedded_media_count": len(media),
            "archive_bytes": len(blob),
        }


@app.local_entrypoint()
def main(pptx_path: str):
    path = Path(pptx_path).resolve()
    result = validate_pptx.remote(path.read_bytes())
    print(json.dumps({"pptx": str(path), "remote_validation": result}, ensure_ascii=False))
