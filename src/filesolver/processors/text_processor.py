"""
File Solver — Text Processor

Handles plain .txt files.  Reads content directly without OCR.
"""

from __future__ import annotations

from pathlib import Path

from .base import BaseProcessor, ExtractionResult


class TextProcessor(BaseProcessor):
    """Process plain-text files (.txt)."""

    def extract(self, path: Path) -> ExtractionResult:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise OSError(f"Cannot read file '{path}': {exc}") from exc

        warnings: list[str] = []
        if not text.strip():
            warnings.append("File appears to be empty or contains only whitespace.")

        return ExtractionResult(
            raw_text=text,
            pages=[text],
            file_type="text",
            warnings=warnings,
        )
