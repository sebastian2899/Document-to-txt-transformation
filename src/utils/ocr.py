from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

from src.core.interfaces import OCREngine

try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None  # type: ignore
    Image = None  # type: ignore

logger = logging.getLogger(__name__)


class TesseractOCREngine(OCREngine):
    """Thin wrapper around pytesseract. Optional dependency.

    Requires:
      - Tesseract installed on the system
      - python package: pytesseract, pillow
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if pytesseract is None or Image is None:
            raise RuntimeError("pytesseract/Pillow not available. Install them to enable OCR.")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def image_to_text(self, image_path: Path, lang: Optional[str] = None) -> str:
        assert Image is not None and pytesseract is not None
        with Image.open(image_path) as img:
            for config in ("--oem 3 --psm 6", "--oem 3 --psm 3"):
                txt = pytesseract.image_to_string(img, lang=(lang or 'eng'), config=config)
                if txt and txt.strip():
                    return txt.strip()
        return ""
