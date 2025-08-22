from __future__ import annotations
import argparse
import logging
from pathlib import Path

from src.strategies.factory import StrategyFactory
from src.pipeline import ExtractionPipeline
from src.utils.logging import setup_logging
from src.utils.ocr import TesseractOCREngine


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract text from documents using Strategy pattern.")
    p.add_argument("--input", required=True, help="Input directory (local for now)")
    p.add_argument("--output", required=True, help="Output directory for .txt files")
    p.add_argument("--ocr", action="store_true", help="Enable OCR for images and scanned PDFs")
    p.add_argument("--tesseract-cmd", default=None, help="Path to tesseract binary if not on PATH")
    p.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(getattr(logging, args.log_level.upper(), logging.INFO))

    ocr = None
    if args.ocr:
        try:
            ocr = TesseractOCREngine(tesseract_cmd=args.tesseract_cmd)
        except Exception as e:
            logging.getLogger(__name__).warning("OCR not available: %s", e)

    factory = StrategyFactory(ocr=ocr)
    pipeline = ExtractionPipeline(output_dir=Path(args.output), strategy_factory=factory)
    pipeline.run_local_dir(Path(args.input))


if __name__ == "__main__":
    main()
