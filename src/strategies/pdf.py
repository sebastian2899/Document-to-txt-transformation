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

# Optional image preprocessing for better OCR
try:  # pragma: no cover - optional
    from PIL import Image as PILImage
    from PIL import ImageOps, ImageFilter
except Exception:  # pragma: no cover - optional
    PILImage = None  # type: ignore
    ImageOps = None  # type: ignore
    ImageFilter = None  # type: ignore


class PDFTextStrategy(TextExtractionStrategy):
    """Extract text from PDFs. If no text is found (scanned PDFs),
    optionally apply OCR by converting pages to images using pdf2image.

    OCR flow requires poppler (for pdf2image) and pillow + pytesseract.
    We keep OCR optional; if unavailable, we return whatever text we can.
    """

    def __init__(
        self,
        ocr: Optional[OCREngine] = None,
        poppler_path: Optional[str] = None,
        ocr_lang: Optional[str] = None,
        ocr_dpi: int = 300,
    ):
        self.ocr = ocr
        self.poppler_path = poppler_path
        self.ocr_lang = ocr_lang
        self.ocr_dpi = ocr_dpi

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
            from pdf2image.exceptions import PDFInfoNotInstalledError
        except Exception:
            logger.warning("pdf2image not installed. Cannot OCR PDF: %s", path)
            return ""
        try:
            images = convert_from_path(
                str(path), dpi=self.ocr_dpi, poppler_path=self.poppler_path
            )
        except Exception as e:
            # Handle missing poppler gracefully
            try:
                from pdf2image.exceptions import PDFInfoNotInstalledError  # type: ignore
            except Exception:
                PDFInfoNotInstalledError = None  # type: ignore
            if 'PDFInfoNotInstalledError' in type(e).__name__ or (
                PDFInfoNotInstalledError and isinstance(e, PDFInfoNotInstalledError)  # type: ignore
            ):
                logger.warning(
                    "Poppler not installed or not in PATH. Install it (e.g., brew install poppler) or pass --poppler-path. File: %s",
                    path,
                )
                return ""
            raise
        texts = []
        for img in images:
            # Save to a temp file-like path if needed; PIL Image works directly with OCR engine if wrapper accepts path only
            # So, save temporarily
            # Light preprocessing: grayscale + autocontrast + median filter
            proc = img.convert("L")
            # upscale to help OCR on small fonts
            try:
                if PILImage is not None:
                    w, h = proc.size
                    proc = proc.resize((int(w * 2), int(h * 2)), resample=PILImage.BICUBIC)
            except Exception:
                pass
            if ImageOps is not None:
                proc = ImageOps.autocontrast(proc)
            if ImageFilter is not None:
                try:
                    proc = proc.filter(ImageFilter.MedianFilter())
                except Exception:
                    pass
            # simple binarization
            try:
                proc = proc.point(lambda p: 255 if p > 180 else 0)
            except Exception:
                pass
            tmp = Path(path.parent) / f".__page_ocr_tmp.png"
            proc.save(tmp, format="PNG")
            try:
                assert self.ocr is not None
                page_text = self.ocr.image_to_text(tmp, lang=self.ocr_lang)
                logger.debug("OCR page text length: %s", len(page_text))
                texts.append(page_text)
            finally:
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:
                    pass
        return "\n".join(texts)
