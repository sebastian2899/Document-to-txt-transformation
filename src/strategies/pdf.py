from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

from src.core.interfaces import FileItem, TextExtractionStrategy, OCREngine

logger = logging.getLogger(__name__)

try:
    import PyPDF2
except Exception:  # pragma: no cover - optional
    PyPDF2 = None  # type: ignore


class PDFTextStrategy(TextExtractionStrategy):
    """Extract text from PDFs. If no text is found (scanned PDFs),
    optionally apply OCR by converting pages to images using pdf2image.

    OCR flow requires poppler (for pdf2image) and pillow + pytesseract.
    We keep OCR optional; if unavailable, we return whatever text we can.
    """

    def __init__(self, ocr: Optional[OCREngine] = None):
        self.ocr = ocr

    def can_handle(self, extension: str) -> bool:
        return extension.lower() == "pdf"

    def extract_text(self, file: FileItem) -> str:
        if PyPDF2 is None:
            logger.warning("PyPDF2 not installed. Skipping text extraction for: %s", file.source_uri)
            return ""
        text = self._extract_text_pdf(file.bytes_path)
        if text.strip():
            return text
        # Fallback to OCR if available
        if self.ocr is None:
            logger.info("No text found in PDF and OCR is disabled: %s", file.source_uri)
            return text
        try:
            ocr_text = self._ocr_pdf(file.bytes_path)
            return ocr_text
        except Exception as e:
            logger.exception("OCR failed for PDF %s: %s", file.source_uri, e)
            return text

    def _extract_text_pdf(self, path: Path) -> str:
        out = []
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)  # type: ignore[attr-defined]
                for page in reader.pages:
                    out.append(page.extract_text() or "")
        except Exception as e:  # corrupted or encrypted
            logger.warning("PDF read failed for %s: %s", path, e)
        return "\n".join(out)

    def _ocr_pdf(self, path: Path) -> str:
        try:
            from pdf2image import convert_from_path  # optional dep
        except Exception:
            logger.warning("pdf2image not installed. Cannot OCR PDF: %s", path)
            return ""
        images = convert_from_path(str(path))
        texts = []
        for img in images:
            # Save to a temp file-like path if needed; PIL Image works directly with OCR engine if wrapper accepts path only
            # So, save temporarily
            tmp = Path(path.parent) / f".__page_ocr_tmp.png"
            img.save(tmp, format="PNG")
            try:
                assert self.ocr is not None
                texts.append(self.ocr.image_to_text(tmp))
            finally:
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:
                    pass
        return "\n".join(texts)
