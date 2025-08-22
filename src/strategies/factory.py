from __future__ import annotations
from typing import List, Optional

from src.core.interfaces import TextExtractionStrategy, OCREngine
from src.strategies.pdf import PDFTextStrategy
from src.strategies.docx import DOCXTextStrategy
from src.strategies.image import ImageTextStrategy
from src.strategies.txt import TXTTextStrategy
from src.strategies.fallback import FallbackStrategy


class StrategyFactory:
    def __init__(self, ocr: Optional[OCREngine] = None):
        self._strategies: List[TextExtractionStrategy] = [
            TXTTextStrategy(),
            DOCXTextStrategy(),
            ImageTextStrategy(ocr),
            PDFTextStrategy(ocr),
            FallbackStrategy(),  # keep last
        ]

    def choose(self, extension: str) -> TextExtractionStrategy:
        ext = (extension or "").lower()
        for s in self._strategies:
            if s.can_handle(ext):
                return s
        # Should never reach; fallback exists
        return FallbackStrategy()
