"""
File Solver — Image Processor

Handles .png / .jpg / .jpeg / .webp files.

Strategy
--------
1. Try to use the OpenAI vision API (multimodal) if the file is small enough
   to be sent as a base64 data URI — this handles handwriting, diagrams,
   equations, tables, and MCQs without needing a local Tesseract install.
2. Fall back to Tesseract OCR if OpenAI vision is not available (e.g. model
   does not support vision) or if the caller requests local-only processing.

The ImageProcessor itself only *extracts* text / describes the content.  The
actual problem-solving happens in the solver layer.
"""

from __future__ import annotations

import base64
from pathlib import Path

# PIL is a required dep
from PIL import Image

from .base import BaseProcessor, ExtractionResult


def _encode_image_base64(path: Path) -> str:
    """Return a base64-encoded string of the image bytes."""
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("utf-8")


def _image_mime(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(ext, "image/png")


def _tesseract_ocr(path: Path) -> str:
    """Run Tesseract OCR and return extracted text.  Raises ImportError if not installed."""
    try:
        import pytesseract  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "pytesseract is not installed. Run: pip install pytesseract\n"
            "Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
        ) from exc

    img = Image.open(path)
    return pytesseract.image_to_string(img)


class ImageProcessor(BaseProcessor):
    """
    Extract content from image files.

    When ``openai_client`` is provided the image is sent directly to the
    vision-capable model for multimodal understanding.  Otherwise Tesseract
    OCR is used as the fallback.
    """

    def __init__(self, openai_client=None, model: str = "gpt-4o"):
        self._client = openai_client
        self._model = model

    def extract(self, path: Path) -> ExtractionResult:
        warnings: list[str] = []

        # Validate the image can be opened
        try:
            with Image.open(path) as img:
                img.verify()  # check for corruption
        except Exception as exc:
            raise ValueError(f"Cannot open image '{path}': {exc}") from exc

        if self._client is not None:
            # ── Vision API path ───────────────────────────────────────────────
            try:
                b64 = _encode_image_base64(path)
                mime = _image_mime(path)
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "You are an expert at reading academic documents. "
                                        "Please transcribe EVERYTHING visible in this image "
                                        "exactly as it appears: all text, numbers, equations, "
                                        "tables, multiple-choice options, question numbers, "
                                        "code snippets, and any other content. "
                                        "Preserve the original structure and ordering. "
                                        "If something is handwritten or unclear, do your best "
                                        "to transcribe it and note any uncertain parts in "
                                        "[brackets]. Do NOT solve — only transcribe."
                                    ),
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime};base64,{b64}",
                                        "detail": "high",
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=4096,
                )
                text = response.choices[0].message.content or ""
            except Exception as exc:
                warnings.append(
                    f"Vision API extraction failed ({exc}); falling back to OCR."
                )
                text = self._fallback_ocr(path, warnings)
        else:
            # ── Local OCR fallback ────────────────────────────────────────────
            text = self._fallback_ocr(path, warnings)

        if not text.strip():
            warnings.append(
                "No text could be extracted from the image. "
                "The image may be blank or the content unreadable."
            )

        return ExtractionResult(
            raw_text=text,
            pages=[text],
            file_type="image",
            warnings=warnings,
        )

    def _fallback_ocr(self, path: Path, warnings: list[str]) -> str:
        try:
            return _tesseract_ocr(path)
        except (ImportError, Exception) as exc:
            warnings.append(f"OCR failed: {exc}")
            return ""
