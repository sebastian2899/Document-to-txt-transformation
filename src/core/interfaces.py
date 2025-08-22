# Strategy interfaces and data models
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class FileItem:
    source_uri: str  # May be local path or cloud URI like s3://bucket/key
    name: str
    extension: str
    bytes_path: Path  # Local path where the file bytes are available
    relative_dir: Path  # Relative directory to preserve structure in outputs


class FileProvider(ABC):
    """Abstraction over where files come from (local, S3, Azure, ...)."""

    @abstractmethod
    def list_items(self, uri: str) -> Iterable[FileItem]:
        """Return iterable of FileItem for a given uri (folder or prefix)."""
        raise NotImplementedError


class TextExtractionStrategy(ABC):
    """Strategy to extract text from a specific file type."""

    @abstractmethod
    def can_handle(self, extension: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def extract_text(self, file: FileItem) -> str:
        raise NotImplementedError


class OCREngine(ABC):
    """Abstraction for OCR engine (e.g., Tesseract)."""

    @abstractmethod
    def image_to_text(self, image_path: Path, lang: Optional[str] = None) -> str:
        raise NotImplementedError
