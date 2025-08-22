from __future__ import annotations
"""Azure Blob provider stub.

Implementations to add later:
- list blobs in a container/prefix
- download to local temp path and yield FileItem entries

Notes:
- Use azure-storage-blob
- Handle connection via connection string or DefaultAzureCredential
"""
from typing import Iterable

from src.core.interfaces import FileItem, FileProvider


class AzureBlobFileProvider(FileProvider):
    def list_items(self, uri: str) -> Iterable[FileItem]:  # pragma: no cover - stub
        raise NotImplementedError(
            "AzureBlobFileProvider is a stub. Implement using azure-storage-blob and return FileItem entries."
        )
