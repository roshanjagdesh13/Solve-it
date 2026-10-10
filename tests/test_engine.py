"""
Tests — Core Engine (integration tests using mock solver, no real API calls)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from filesolver.config.settings import Config
from filesolver.engine import Engine
from filesolver.solver.base import BaseSolver, SolverResult


class MockSolver(BaseSolver):
    def solve(self, text: str, file_type: str) -> SolverResult:
        return SolverResult(solution_text=f"SOLVED: {text[:40]}", model_used="mock")


def _config(tmp_path: Path) -> Config:
    return Config(
        openai_api_key="sk-fake-key-for-tests",
        solver_model="gpt-4o",
        max_file_size_bytes=10 * 1024 * 1024,
        output_directory=str(tmp_path / "out"),
    )


class TestEngine:
    def test_solves_text_file(self, tmp_path: Path) -> None:
        f = tmp_path / "q.txt"
        f.write_text("1. What is 2+2?\n2. Explain gravity.\n")

        engine = Engine(_config(tmp_path), solver=MockSolver())
        result = engine.process(f)

        assert result.success
        assert result.output_path.exists()
        assert result.output_path.name == "q.txt.solved"
        assert result.file_type == "text"

    def test_solves_markdown_file(self, tmp_path: Path) -> None:
        f = tmp_path / "q.md"
        f.write_text("# Quiz\n\n1. Define recursion.\n")

        engine = Engine(_config(tmp_path), solver=MockSolver())
        result = engine.process(f)

        assert result.success
        assert result.output_path.name == "q.md.solved"

    def test_missing_file_returns_failure(self, tmp_path: Path) -> None:
        engine = Engine(_config(tmp_path), solver=MockSolver())
        result = engine.process(tmp_path / "nope.txt")
        assert not result.success
        assert "not found" in result.error.lower()

    def test_empty_file_returns_failure(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.txt"
        f.write_text("")
        engine = Engine(_config(tmp_path), solver=MockSolver())
        result = engine.process(f)
        assert not result.success

    def test_unsupported_file_returns_failure(self, tmp_path: Path) -> None:
        f = tmp_path / "report.docx"
        f.write_bytes(b"fake docx content")
        engine = Engine(_config(tmp_path), solver=MockSolver())
        result = engine.process(f)
        assert not result.success
        assert "Unsupported" in result.error or "unsupported" in result.error.lower()

    def test_output_respects_custom_dir(self, tmp_path: Path) -> None:
        f = tmp_path / "q.txt"
        f.write_text("Hello question")
        custom = tmp_path / "custom_out"

        engine = Engine(_config(tmp_path), solver=MockSolver())
        result = engine.process(f, output_dir=custom)

        assert result.success
        assert result.output_path.parent == custom

    def test_output_respects_custom_file(self, tmp_path: Path) -> None:
        f = tmp_path / "q.txt"
        f.write_text("Hello question")
        override = tmp_path / "my_answer.txt"

        engine = Engine(_config(tmp_path), solver=MockSolver())
        result = engine.process(f, output_file=override)

        assert result.success
        assert result.output_path == override

    def test_oversized_file_returns_failure(self, tmp_path: Path) -> None:
        f = tmp_path / "big.txt"
        f.write_bytes(b"x" * 200)
        cfg = Config(
            openai_api_key="sk-fake",
            max_file_size_bytes=100,
        )
        engine = Engine(cfg, solver=MockSolver())
        result = engine.process(f)
        assert not result.success
        assert "large" in result.error.lower()

    def test_progress_callback_called(self, tmp_path: Path) -> None:
        f = tmp_path / "q.txt"
        f.write_text("What is AI?\n")
        steps: list[int] = []

        def cb(step: int, total: int, msg: str) -> None:
            steps.append(step)

        engine = Engine(_config(tmp_path), solver=MockSolver(), progress=cb)
        result = engine.process(f)

        assert result.success
        assert steps == [1, 2, 3, 4]


class TestConfigValidation:
    def test_missing_api_key_raises(self) -> None:
        from filesolver.config.settings import ConfigurationError
        with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
            Config(openai_api_key="")
