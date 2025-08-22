from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Iterable, Iterator

from src.core.interfaces import FileItem, FileProvider


logger = logging.getLogger(__name__)


class LocalFileProvider(FileProvider):
    """Reads files from a local directory path.

    Usage example:
        provider = LocalFileProvider()
        items = provider.list_items("/path/to/folder")
    """

    def list_items(self, uri: str) -> Iterable[FileItem]:
        base = Path(uri).expanduser().resolve()
        if not base.exists() or not base.is_dir():
            logger.error("Local path does not exist or is not a directory: %s", base)
            return []
        return list(_iter_files(base))


def _iter_files(base: Path) -> Iterator[FileItem]:
    for root, _, files in os.walk(base):
        root_path = Path(root)
        for f in files:
            p = root_path / f
            if not p.is_file():
                continue
            ext = p.suffix.lower().lstrip('.')
            rel_dir = p.parent.relative_to(base)
            yield FileItem(
                source_uri=str(p),
                name=p.stem,
                extension=ext,
                bytes_path=p,
                relative_dir=rel_dir,
            )
