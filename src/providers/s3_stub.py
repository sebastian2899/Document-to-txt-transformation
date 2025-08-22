from __future__ import annotations
"""S3 provider stub.

Implementations to add later:
- list objects by prefix
- download to local temp path and yield FileItem entries

Notes:
- Use boto3 (s3 client) and smart_open or direct download
- Consider pagination and credentials via AWS_DEFAULT_PROFILE or env vars
"""
from typing import Iterable

from src.core.interfaces import FileItem, FileProvider


class S3FileProvider(FileProvider):
    def list_items(self, uri: str) -> Iterable[FileItem]:  # pragma: no cover - stub
        raise NotImplementedError(
            "S3FileProvider is a stub. Implement using boto3 and return FileItem entries."
        )
