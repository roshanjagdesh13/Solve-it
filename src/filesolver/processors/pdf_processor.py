"""
File Solver — PDF Processor

Handles .pdf files including:
- Native text PDFs  (fast, pypdf)
- Scanned / image-only PDFs  (pdf2image → ImageProcessor per page)

Each page's text is tracked independently so that original question ordering
is preserved in the final output.
"""

from __future__ import annotations

from pathlib import Path

from .base import BaseProcessor, ExtractionResult
from .image_processor import ImageProcessor

# Minimum characters per page to consider it a "text" page (vs. scanned)
_TEXT_PAGE_THRESHOLD = 30


class PDFProcessor(BaseProcessor):
    """
    Extract content from PDF files.

    Text PDFs are parsed directly with pypdf.
    Scanned pages are rasterised with pdf2image and processed via
    :class:`ImageProcessor` (which uses vision API or Tesseract).
    """

    def __init__(self, image_processor: ImageProcessor | None = None):
        self._image_proc = image_processor or ImageProcessor()

    def extract(self, path: Path) -> ExtractionResult:
        try:
            import pypdf  # type: ignore
        except ImportError as exc:
            raise ImportError("pypdf is required: pip install pypdf") from exc

        warnings: list[str] = []
        pages: list[str] = []

        try:
            reader = pypdf.PdfReader(str(path))
        except Exception as exc:
            raise ValueError(f"Cannot open PDF '{path}': {exc}") from exc

        if reader.is_encrypted:
            try:
                reader.decrypt("")  # try empty password
            except Exception as e:
                raise ValueError(
                    f"PDF '{path}' is encrypted and requires a password. "
                    "File Solver does not support password-protected PDFs."
                ) from e

        total = len(reader.pages)
        if total == 0:
            raise ValueError(f"PDF '{path}' has no pages.")

        for page_num, page in enumerate(reader.pages, start=1):
            text = self._extract_page_text(page)

            if len(text.strip()) >= _TEXT_PAGE_THRESHOLD:
                pages.append(f"--- Page {page_num} ---\n{text.strip()}")
            else:
                # Scanned page: rasterise and run through image processor
                scanned_text = self._extract_scanned_page(path, page_num - 1, warnings)
                if scanned_text:
                    pages.append(f"--- Page {page_num} (scanned) ---\n{scanned_text.strip()}")
                else:
                    warnings.append(f"Page {page_num}: no text could be extracted.")
                    pages.append(f"--- Page {page_num} ---\n[Content could not be extracted]")

        raw_text = "\n\n".join(pages)

        return ExtractionResult(
            raw_text=raw_text,
            pages=pages,
            file_type="pdf",
            warnings=warnings,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_page_text(page) -> str:
        try:
            return page.extract_text() or ""
        except Exception:
            return ""

    def _extract_scanned_page(
        self, pdf_path: Path, page_index: int, warnings: list[str]
    ) -> str:
        """Rasterise a single PDF page and run image extraction on it."""
        try:
            from pdf2image import convert_from_path  # type: ignore
        except ImportError:
            warnings.append(
                "pdf2image is not installed; scanned pages cannot be processed. "
                "Run: pip install pdf2image  (also install poppler)."
            )
            return ""

        try:
            images = convert_from_path(
                str(pdf_path),
                first_page=page_index + 1,
                last_page=page_index + 1,
                dpi=200,
            )
        except Exception as exc:
            warnings.append(f"Could not rasterise page {page_index + 1}: {exc}")
            return ""

        if not images:
            return ""

        # Save to a temp file and run the image processor
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            images[0].save(str(tmp_path), "PNG")
            result = self._image_proc.extract(tmp_path)
            return result.raw_text
        except Exception as exc:
            warnings.append(f"Image extraction failed for scanned page: {exc}")
            return ""
        finally:
            try:
                tmp_path.unlink()
            except OSError:
                pass
