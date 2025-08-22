from __future__ import annotations
import logging

from src.core.interfaces import FileItem, TextExtractionStrategy

logger = logging.getLogger(__name__)


class TXTTextStrategy(TextExtractionStrategy):
    def can_handle(self, extension: str) -> bool:
        return extension.lower() in {"txt", "csv", "log", "md"}

    def extract_text(self, file: FileItem) -> str:
        try:
            with open(file.bytes_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.warning("TXT read failed for %s: %s", file.source_uri, e)
            return ""
