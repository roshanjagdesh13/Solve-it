"""
Tests — CLI (using Click's test runner, no real API calls)
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from filesolver.cli.main import cli


def _fake_engine_result(success: bool = True, error: str = ""):
    """Build a mock EngineResult."""
    from filesolver.engine import EngineResult
    from filesolver.processors.base import ExtractionResult
    from filesolver.solver.base import SolverResult

    return EngineResult(
        input_path=Path("q.txt"),
        output_path=Path("q.txt.solved"),
        file_type="text",
        extraction=ExtractionResult(raw_text="content"),
        solution=SolverResult(solution_text="Solution"),
        success=success,
        error=error,
    )


class TestCLIHelp:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "File Solver" in result.output

    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_solve_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["solve", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output


class TestCLISolve:
    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-fake-key"})
    def test_solve_text_file(self, tmp_path: Path) -> None:
        f = tmp_path / "q.txt"
        f.write_text("1. What is 2+2?")

        with patch("filesolver.engine.Engine.process", return_value=_fake_engine_result()):
            runner = CliRunner()
            result = runner.invoke(cli, ["solve", str(f)])
        assert result.exit_code == 0

    def test_solve_missing_api_key(self, tmp_path: Path) -> None:
        f = tmp_path / "q.txt"
        f.write_text("Question")

        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            runner = CliRunner()
            result = runner.invoke(cli, ["solve", str(f)])
        assert result.exit_code != 0

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-fake"})
    def test_output_file_with_multiple_inputs_fails(self, tmp_path: Path) -> None:
        f1 = tmp_path / "q1.txt"
        f1.write_text("Q1")
        f2 = tmp_path / "q2.txt"
        f2.write_text("Q2")

        runner = CliRunner()
        result = runner.invoke(cli, ["solve", str(f1), str(f2), "--output-file", "out.txt"])
        assert result.exit_code != 0
        assert "single" in result.output.lower() or "output-file" in result.output.lower()
