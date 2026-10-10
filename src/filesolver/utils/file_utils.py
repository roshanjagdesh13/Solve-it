"""
File Solver — Utility Helpers
"""

from __future__ import annotations

from pathlib import Path

from filesolver.config.settings import SUPPORTED_EXTENSIONS

# ─────────────────────────────────────────────────────────────────────────────
# File-type detection
# ─────────────────────────────────────────────────────────────────────────────

IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp"})
PDF_EXTENSIONS = frozenset({".pdf"})
TEXT_EXTENSIONS = frozenset({".txt"})
MARKDOWN_EXTENSIONS = frozenset({".md"})


def detect_file_type(path: Path) -> str:
    """
    Return a normalised file-type string for *path*.

    Returns one of: ``"image"``, ``"pdf"``, ``"text"``, ``"markdown"``.

    Raises :class:`ValueError` for unsupported extensions.
    """
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in PDF_EXTENSIONS:
        return "pdf"
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext in MARKDOWN_EXTENSIONS:
        return "markdown"
    raise ValueError(
        f"Unsupported file type: '{ext}'\n"
        f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )


def is_supported(path: Path) -> bool:
    """Return True when *path* has a supported extension."""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


# ─────────────────────────────────────────────────────────────────────────────
# Output-path helpers
# ─────────────────────────────────────────────────────────────────────────────


def build_output_path(
    input_path: Path,
    *,
    output_dir: Path | None = None,
    output_file: Path | None = None,
) -> Path:
    """
    Compute the path for the ``.solved`` output file.

    Priority:
    1. ``output_file`` if provided (used as-is).
    2. ``output_dir`` directory + ``<original_filename>.solved``.
    3. Same directory as *input_path* + ``<original_filename>.solved``.
    """
    if output_file is not None:
        return output_file

    solved_name = input_path.name + ".solved"

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / solved_name

    return input_path.parent / solved_name


# ─────────────────────────────────────────────────────────────────────────────
# File validation
# ─────────────────────────────────────────────────────────────────────────────


def validate_file(path: Path, max_bytes: int) -> None:
    """
    Validate that *path* exists, is a regular file, is non-empty, and is within
    the size limit.

    Raises :class:`ValueError` with a user-friendly message on failure.
    """
    if not path.exists():
        raise ValueError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    size = path.stat().st_size
    if size == 0:
        raise ValueError(f"File is empty: {path}")
    if size > max_bytes:
        limit_mb = max_bytes // (1024 * 1024)
        actual_mb = size / (1024 * 1024)
        raise ValueError(
            f"File is too large: {actual_mb:.1f} MB "
            f"(limit is {limit_mb} MB). "
            "Set MAX_FILE_SIZE in .env to override."
        )
