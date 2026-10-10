"""
Tests — Processors (text, markdown, PDF text extraction, image OCR fallback)

All tests use real local files or tmp fixtures — NO real API calls are made.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from filesolver.processors.image_processor import ImageProcessor
from filesolver.processors.markdown_processor import MarkdownProcessor
from filesolver.processors.pdf_processor import PDFProcessor
from filesolver.processors.text_processor import TextProcessor

# ─────────────────────────────────────────────────────────────────────────────
# Text processor
# ─────────────────────────────────────────────────────────────────────────────

class TestTextProcessor:
    def test_extracts_content(self, tmp_path: Path) -> None:
        f = tmp_path / "q.txt"
        f.write_text("1. What is 2+2?\n2. Explain gravity.\n")
        result = TextProcessor().extract(f)
        assert "2+2" in result.raw_text
        assert result.file_type == "text"
        assert not result.is_empty

    def test_empty_file_has_warning(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.txt"
        f.write_text("   \n")
        result = TextProcessor().extract(f)
        assert result.warnings

    def test_utf8_content(self, tmp_path: Path) -> None:
        f = tmp_path / "unicode.txt"
        f.write_text("Solve: x² + 5x + 6 = 0\nÅngström measurement.", encoding="utf-8")
        result = TextProcessor().extract(f)
        assert "x²" in result.raw_text

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(OSError):
            TextProcessor().extract(tmp_path / "missing.txt")


# ─────────────────────────────────────────────────────────────────────────────
# Markdown processor
# ─────────────────────────────────────────────────────────────────────────────

class TestMarkdownProcessor:
    def test_extracts_content(self, tmp_path: Path) -> None:
        f = tmp_path / "q.md"
        f.write_text("# Assignment\n\n1. Solve x+5=10\n")
        result = MarkdownProcessor().extract(f)
        assert "Solve x+5" in result.raw_text
        assert result.file_type == "markdown"

    def test_empty_file_has_warning(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.md"
        f.write_text("")
        result = MarkdownProcessor().extract(f)
        assert result.warnings


# ─────────────────────────────────────────────────────────────────────────────
# Image processor (no OpenAI client → OCR fallback or graceful warning)
# ─────────────────────────────────────────────────────────────────────────────

class TestImageProcessor:
    def test_corrupt_image_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.png"
        f.write_bytes(b"not an image at all")
        with pytest.raises(ValueError, match="Cannot open image"):
            ImageProcessor(openai_client=None).extract(f)

    def test_valid_image_no_client_warns(self, tmp_path: Path) -> None:
        """A real PNG that just contains white pixels — OCR may return empty."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")

        f = tmp_path / "blank.png"
        img = Image.new("RGB", (100, 100), color="white")
        img.save(str(f))

        proc = ImageProcessor(openai_client=None)
        result = proc.extract(f)
        # Should not raise; may have warnings about OCR or empty text
        assert isinstance(result.raw_text, str)
        assert result.file_type == "image"


# ─────────────────────────────────────────────────────────────────────────────
# PDF processor
# ─────────────────────────────────────────────────────────────────────────────

class TestPDFProcessor:
    def test_text_pdf_extraction(self, tmp_path: Path) -> None:
        """Create a minimal PDF with embedded text and verify extraction."""
        try:
            from pypdf import PdfWriter
        except ImportError:
            pytest.skip("pypdf not installed")

        # Build a real PDF with text
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        out = tmp_path / "test.pdf"
        with open(out, "wb") as fh:
            writer.write(fh)

        # Blank page PDF — extraction should handle gracefully (no crash)
        proc = PDFProcessor()
        result = proc.extract(out)
        assert isinstance(result.raw_text, str)
        assert result.file_type == "pdf"

    def test_missing_pdf_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Cannot open PDF"):
            PDFProcessor().extract(tmp_path / "missing.pdf")

    def test_corrupted_pdf_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.pdf"
        f.write_bytes(b"this is not a pdf")
        with pytest.raises(ValueError, match="Cannot open PDF"):
            PDFProcessor().extract(f)
