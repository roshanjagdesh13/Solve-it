"""
File Solver — Core Engine

Orchestrates the full solve pipeline for a single file:
  1. Validate input
  2. Detect file type
  3. Extract content via the appropriate processor
  4. Send to the solver
  5. Write the output file

This module is intentionally decoupled from the CLI so it can be used
programmatically or tested in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from filesolver.config.settings import Config
from filesolver.output.writer import write_solution
from filesolver.processors.base import ExtractionResult
from filesolver.processors.image_processor import ImageProcessor
from filesolver.processors.markdown_processor import MarkdownProcessor
from filesolver.processors.pdf_processor import PDFProcessor
from filesolver.processors.text_processor import TextProcessor
from filesolver.solver.base import BaseSolver, SolverResult
from filesolver.solver.openai_solver import OpenAISolver
from filesolver.utils.file_utils import build_output_path, detect_file_type, validate_file

# ─────────────────────────────────────────────────────────────────────────────
# Progress callback type
# ─────────────────────────────────────────────────────────────────────────────

ProgressCallback = Callable[[int, int, str], None]  # (step, total, message)


# ─────────────────────────────────────────────────────────────────────────────
# Result
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class EngineResult:
    """Outcome of processing a single file."""

    input_path: Path
    output_path: Path
    file_type: str
    extraction: ExtractionResult
    solution: SolverResult
    success: bool = True
    error: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────────────────────────────────────


class Engine:
    """
    Top-level orchestrator.

    Parameters
    ----------
    config:
        Application configuration (API key, model, limits, …).
    solver:
        Optional pre-built solver.  If None, :class:`OpenAISolver` is created
        automatically from *config*.
    progress:
        Optional callback invoked at each pipeline step with
        ``(step_number, total_steps, description)``.
    """

    TOTAL_STEPS = 4

    def __init__(
        self,
        config: Config,
        *,
        solver: BaseSolver | None = None,
        progress: ProgressCallback | None = None,
    ):
        self._config = config
        self._progress = progress or (lambda *_: None)

        # Build solver
        if solver is not None:
            self._solver = solver
        else:
            self._solver = OpenAISolver(
                api_key=config.openai_api_key,
                model=config.solver_model,
            )

        # Build the shared OpenAI client for image/vision extraction
        self._openai_client = self._build_openai_client(config.openai_api_key)

    # ── Public ────────────────────────────────────────────────────────────────

    def process(
        self,
        input_path: Path,
        *,
        output_dir: Path | None = None,
        output_file: Path | None = None,
    ) -> EngineResult:
        """
        Run the full pipeline for *input_path*.

        Returns an :class:`EngineResult`.  Never raises — errors are captured
        into ``EngineResult.error`` with ``success=False``.
        """
        try:
            return self._run(input_path, output_dir=output_dir, output_file=output_file)
        except Exception as exc:
            return EngineResult(
                input_path=input_path,
                output_path=Path(""),
                file_type="",
                extraction=ExtractionResult(raw_text=""),
                solution=SolverResult(solution_text=""),
                success=False,
                error=str(exc),
            )

    # ── Private ───────────────────────────────────────────────────────────────

    def _run(
        self,
        input_path: Path,
        *,
        output_dir: Path | None,
        output_file: Path | None,
    ) -> EngineResult:
        # Step 1 — Read / validate
        self._progress(1, self.TOTAL_STEPS, "Reading file...")
        validate_file(input_path, self._config.max_file_size_bytes)
        file_type = detect_file_type(input_path)

        # Step 2 — Extract
        self._progress(2, self.TOTAL_STEPS, "Extracting content...")
        processor = self._get_processor(file_type)
        extraction = processor.extract(input_path)

        if extraction.is_empty:
            raise ValueError(
                "No text could be extracted from the file. "
                "The file may be blank, corrupted, or in an unreadable format."
            )

        # Step 3 — Solve
        self._progress(3, self.TOTAL_STEPS, "Solving...")
        solution = self._solver.solve(extraction.raw_text, file_type)

        # Step 4 — Write output
        self._progress(4, self.TOTAL_STEPS, "Writing solution...")
        cfg_output_dir = (
            Path(self._config.output_directory)
            if self._config.output_directory
            else None
        )
        effective_output_dir = output_dir or cfg_output_dir
        out_path = build_output_path(
            input_path,
            output_dir=effective_output_dir,
            output_file=output_file,
        )
        write_solution(
            out_path,
            input_path,
            solution,
            warnings=extraction.warnings or None,
        )

        return EngineResult(
            input_path=input_path,
            output_path=out_path,
            file_type=file_type,
            extraction=extraction,
            solution=solution,
            success=True,
        )

    def _get_processor(self, file_type: str):
        img_proc = ImageProcessor(
            openai_client=self._openai_client,
            model=self._config.solver_model,
        )
        processors = {
            "image": img_proc,
            "pdf": PDFProcessor(image_processor=img_proc),
            "text": TextProcessor(),
            "markdown": MarkdownProcessor(),
        }
        if file_type not in processors:
            raise ValueError(f"No processor available for file type: '{file_type}'")
        return processors[file_type]

    @staticmethod
    def _build_openai_client(api_key: str):
        try:
            from openai import OpenAI  # type: ignore
            return OpenAI(api_key=api_key)
        except ImportError:
            return None
