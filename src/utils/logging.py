from __future__ import annotations
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    if logging.getLogger().handlers:
        return
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
