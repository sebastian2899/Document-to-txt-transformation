# Document Text Extraction Pipeline (Strategy Pattern)

This project demonstrates a scalable, extensible text extraction pipeline using the Strategy pattern and a Provider abstraction.

- Strategies per file type: PDF (with optional OCR fallback), DOCX, Image, TXT, Fallback
- Providers: Local (working), S3/Azure stubs ready for future integration
- Pipeline preserves folder structure under output directory
- CLI with optional OCR toggle

## Quickstart

1) Create and activate a virtualenv (optional but recommended).

2) Install requirements:

```bash
pip install -r requirements.txt
```

3) Run locally over a folder of files:

```bash
python -m src.app --input /path/to/input --output /path/to/output --ocr
```

- `--ocr` is optional; enables OCR for images and scanned PDFs.
- If Tesseract is not on PATH, specify `--tesseract-cmd`.

Outputs are written as `.txt` files mirroring the input subfolder structure.

## Architecture

- `src/core/interfaces.py` defines `FileProvider`, `TextExtractionStrategy`, `OCREngine`, and the `FileItem` data model.
- `src/providers/local.py` implements a `LocalFileProvider` (reads a local directory). Stubs exist for `S3` and `Azure` in `providers/s3_stub.py` and `providers/azure_stub.py`.
- `src/strategies/` contains strategies:
  - `txt.py` for plain text-like files
  - `docx.py` for Word documents
  - `image.py` for images via OCR
  - `pdf.py` for PDFs; uses PyPDF2 and falls back to OCR via `pdf2image` if no text
  - `fallback.py` default no-op
- `src/strategies/factory.py` chooses the appropriate strategy given a file extension.
- `src/utils/ocr.py` provides a thin wrapper around Tesseract OCR (optional).
- `src/utils/logging.py` configures simple logging.
- `src/pipeline.py` orchestrates provider -> strategy -> output.
- `src/app.py` provides a CLI.

## Future Cloud Providers

- Implement `S3FileProvider` with `boto3`:
  - List objects by prefix, download to local temp, yield `FileItem` with `relative_dir` based on key prefix.
- Implement `AzureBlobFileProvider` with `azure-storage-blob` similarly.

## Notes

- OCR requires installing the Tesseract binary separately and may need Poppler for `pdf2image`.
- All optional deps fail gracefully; the pipeline still processes supported types.
