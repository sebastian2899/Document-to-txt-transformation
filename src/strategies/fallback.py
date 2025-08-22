from __future__ import annotations
from src.core.interfaces import FileItem, TextExtractionStrategy


class FallbackStrategy(TextExtractionStrategy):
    """Default strategy when no other strategy can handle the file type."""

    def can_handle(self, extension: str) -> bool:
        return True  # acts as catch-all but should be last in order

    def extract_text(self, file: FileItem) -> str:
        # No extraction. Could add future generic handlers.
        return ""
