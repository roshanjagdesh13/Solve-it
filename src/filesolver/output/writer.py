"""
File Solver — Output Writer

Formats and writes the final `.solved` file.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from filesolver.solver.base import SolverResult

_DIVIDER = "=" * 72


def build_solved_content(
    input_path: Path,
    result: SolverResult,
    *,
    warnings: list[str] | None = None,
) -> str:
    """
    Build the text content for the ``.solved`` file.

    Parameters
    ----------
    input_path:
        The original input file path (for the header).
    result:
        The :class:`SolverResult` from the solver.
    warnings:
        Any extraction warnings to include in the header.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("File Solver — Solution Report")
    lines.append(_DIVIDER)
    lines.append(f"Generated : {now}")
    lines.append(f"Input file: {input_path.name}")
    if result.model_used:
        lines.append(f"Model     : {result.model_used}")
    if result.prompt_tokens or result.completion_tokens:
        lines.append(
            f"Tokens    : {result.prompt_tokens} prompt / "
            f"{result.completion_tokens} completion"
        )
    lines.append(_DIVIDER)
    lines.append("")

    # ── Extraction warnings ───────────────────────────────────────────────────
    if warnings:
        lines.append("EXTRACTION NOTES")
        lines.append("-" * 40)
        for w in warnings:
            lines.append(f"  ⚠  {w}")
        lines.append("")

    # ── Solutions ─────────────────────────────────────────────────────────────
    lines.append("SOLUTIONS")
    lines.append(_DIVIDER)
    lines.append("")
    lines.append(result.solution_text.strip())
    lines.append("")
    lines.append(_DIVIDER)
    lines.append("End of File Solver Report")

    return "\n".join(lines)


def write_solution(
    output_path: Path,
    input_path: Path,
    result: SolverResult,
    *,
    warnings: list[str] | None = None,
) -> None:
    """
    Write the solution to *output_path*.

    Creates parent directories if needed.
    Raises :class:`OSError` if the file cannot be written.
    """
    content = build_solved_content(input_path, result, warnings=warnings)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
