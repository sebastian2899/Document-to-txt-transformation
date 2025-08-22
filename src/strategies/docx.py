from __future__ import annotations
import logging
from src.core.interfaces import FileItem, TextExtractionStrategy

logger = logging.getLogger(__name__)

try:
    import docx  # python-docx
except Exception:  # pragma: no cover - optional
    docx = None  # type: ignore


class DOCXTextStrategy(TextExtractionStrategy):
    def can_handle(self, extension: str) -> bool:
        return extension.lower() in {"docx"}

    def extract_text(self, file: FileItem) -> str:
        if docx is None:
            logger.warning("python-docx not installed. Skipping: %s", file.source_uri)
            return ""
        try:
            d = docx.Document(str(file.bytes_path))
            return "\n".join(p.text or "" for p in d.paragraphs)
        except Exception as e:
            logger.warning("DOCX read failed for %s: %s", file.source_uri, e)
            return ""
