"""
Tests — Utility helpers (file detection, output path, validation)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from filesolver.utils.file_utils import (
    build_output_path,
    detect_file_type,
    is_supported,
    validate_file,
)

# ─────────────────────────────────────────────────────────────────────────────
# detect_file_type
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("filename,expected", [
    ("photo.png",      "image"),
    ("photo.PNG",      "image"),
    ("scan.jpg",       "image"),
    ("scan.jpeg",      "image"),
    ("scan.webp",      "image"),
    ("doc.pdf",        "pdf"),
    ("notes.txt",      "text"),
    ("readme.md",      "markdown"),
])
def test_detect_file_type_supported(filename: str, expected: str) -> None:
    assert detect_file_type(Path(filename)) == expected


def test_detect_file_type_unsupported() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        detect_file_type(Path("report.docx"))


def test_detect_file_type_no_extension() -> None:
    with pytest.raises(ValueError):
        detect_file_type(Path("Makefile"))


# ─────────────────────────────────────────────────────────────────────────────
# is_supported
# ─────────────────────────────────────────────────────────────────────────────

def test_is_supported_true() -> None:
    assert is_supported(Path("q.pdf"))
    assert is_supported(Path("img.webp"))
    assert is_supported(Path("notes.MD"))   # case-insensitive


def test_is_supported_false() -> None:
    assert not is_supported(Path("file.docx"))
    assert not is_supported(Path("data.csv"))


# ─────────────────────────────────────────────────────────────────────────────
# build_output_path
# ─────────────────────────────────────────────────────────────────────────────

def test_build_output_path_default() -> None:
    result = build_output_path(Path("/some/dir/question.pdf"))
    assert result == Path("/some/dir/question.pdf.solved")


def test_build_output_path_preserves_original_extension() -> None:
    result = build_output_path(Path("math.png"))
    assert result.name == "math.png.solved"


def test_build_output_path_with_output_dir(tmp_path: Path) -> None:
    result = build_output_path(Path("question.pdf"), output_dir=tmp_path)
    assert result.parent == tmp_path
    assert result.name == "question.pdf.solved"


def test_build_output_path_with_output_file(tmp_path: Path) -> None:
    override = tmp_path / "my_answer.txt"
    result = build_output_path(Path("question.pdf"), output_file=override)
    assert result == override


def test_build_output_path_output_file_takes_priority(tmp_path: Path) -> None:
    override = tmp_path / "final.txt"
    result = build_output_path(
        Path("question.pdf"),
        output_dir=tmp_path / "other",
        output_file=override,
    )
    assert result == override


# ─────────────────────────────────────────────────────────────────────────────
# validate_file
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_file_ok(tmp_path: Path) -> None:
    f = tmp_path / "ok.txt"
    f.write_text("Hello")
    validate_file(f, max_bytes=1024 * 1024)  # should not raise


def test_validate_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        validate_file(tmp_path / "missing.txt", max_bytes=1024)


def test_validate_file_empty(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("")
    with pytest.raises(ValueError, match="empty"):
        validate_file(f, max_bytes=1024)


def test_validate_file_too_large(tmp_path: Path) -> None:
    f = tmp_path / "big.txt"
    f.write_bytes(b"x" * 100)
    with pytest.raises(ValueError, match="too large"):
        validate_file(f, max_bytes=10)
