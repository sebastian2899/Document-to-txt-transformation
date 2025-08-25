from __future__ import annotations
import logging
from src.core.interfaces import FileItem, TextExtractionStrategy, OCREngine

logger = logging.getLogger(__name__)


class ImageTextStrategy(TextExtractionStrategy):
    """Extract text from images via OCR (PNG, JPG, JPEG, TIFF, BMP)."""

    SUPPORTED = {"png", "jpg", "jpeg", "tiff", "bmp"}

    def __init__(self, ocr: OCREngine | None, ocr_lang: str | None = None):
        self.ocr = ocr
        self.ocr_lang = ocr_lang

    def can_handle(self, extension: str) -> bool:
        return extension.lower() in self.SUPPORTED

    def extract_text(self, file: FileItem) -> str:
        if self.ocr is None:
            logger.info("OCR disabled or unavailable. Cannot extract from image: %s", file.source_uri)
            return ""
        try:
            return self.ocr.image_to_text(file.bytes_path, lang=self.ocr_lang)
        except Exception as e:
            logger.warning("Image OCR failed for %s: %s", file.source_uri, e)
            return ""
