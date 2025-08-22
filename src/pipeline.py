from __future__ import annotations
import logging
from pathlib import Path
from typing import Iterable

from src.core.interfaces import FileItem
from src.providers.local import LocalFileProvider
from src.strategies.factory import StrategyFactory

logger = logging.getLogger(__name__)


class ExtractionPipeline:
    def __init__(self, output_dir: Path, strategy_factory: StrategyFactory):
        self.output_dir = Path(output_dir)
        self.strategy_factory = strategy_factory

    def run_over_items(self, items: Iterable[FileItem]) -> None:
        for item in items:
            self._process_item(item)

    def run_local_dir(self, input_dir: Path) -> None:
        provider = LocalFileProvider()
        items = provider.list_items(str(input_dir))
        self.run_over_items(items)

    def _process_item(self, item: FileItem) -> None:
        try:
            strategy = self.strategy_factory.choose(item.extension)
            text = strategy.extract_text(item)
            self._write_output(item, text)
            logger.info("Processed: %s", item.source_uri)
        except Exception as e:
            logger.exception("Failed processing %s: %s", item.source_uri, e)

    def _write_output(self, item: FileItem, text: str) -> None:
        rel_dir = item.relative_dir
        out_dir = self.output_dir / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{item.name}.txt"
        out_path.write_text(text or "", encoding="utf-8")
        logger.debug("Wrote: %s", out_path)
