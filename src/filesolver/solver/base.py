"""
File Solver — Solver Base

Defines the abstract Solver interface.  Any AI provider or local model
can be plugged in by implementing :class:`BaseSolver`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SolverResult:
    """Result returned by a solver."""

    solution_text: str          # The full formatted answer
    model_used: str = ""        # e.g. "gpt-4o"
    prompt_tokens: int = 0
    completion_tokens: int = 0


class BaseSolver(ABC):
    """Abstract interface for all solver backends."""

    @abstractmethod
    def solve(self, extracted_text: str, file_type: str) -> SolverResult:
        """
        Solve the problems described in *extracted_text*.

        Parameters
        ----------
        extracted_text:
            The content extracted from the source file.
        file_type:
            One of ``"text"``, ``"markdown"``, ``"pdf"``, ``"image"``.
            Used to tailor the system prompt.

        Returns
        -------
        SolverResult
        """
