"""
File Solver — Processor Base
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractionResult:
    """Container for content extracted from a source file."""

    raw_text: str
    pages: list[str] = field(default_factory=list)  # per-page breakdown for PDFs
    file_type: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.raw_text.strip()


class BaseProcessor(ABC):
    """Abstract base class that all file-type processors must implement."""

    @abstractmethod
    def extract(self, path: Path) -> ExtractionResult:
        """
        Read *path* and return an :class:`ExtractionResult`.

        Implementations must:
        - Not execute code/macros from the file.
        - Preserve question ordering.
        - Add warning strings (not raise) for recoverable issues.
        """
