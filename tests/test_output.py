"""
Tests — Output writer
"""

from __future__ import annotations

from pathlib import Path

from filesolver.output.writer import build_solved_content, write_solution
from filesolver.solver.base import SolverResult


def _make_result(text: str = "Solution here.") -> SolverResult:
    return SolverResult(
        solution_text=text,
        model_used="gpt-4o",
        prompt_tokens=100,
        completion_tokens=200,
    )


class TestBuildSolvedContent:
    def test_contains_input_filename(self) -> None:
        content = build_solved_content(Path("question.pdf"), _make_result())
        assert "question.pdf" in content

    def test_contains_solution_text(self) -> None:
        content = build_solved_content(Path("q.txt"), _make_result("The answer is X."))
        assert "The answer is X." in content

    def test_contains_model_name(self) -> None:
        content = build_solved_content(Path("q.txt"), _make_result())
        assert "gpt-4o" in content

    def test_contains_token_info(self) -> None:
        content = build_solved_content(Path("q.txt"), _make_result())
        assert "100" in content
        assert "200" in content

    def test_warnings_included(self) -> None:
        content = build_solved_content(
            Path("q.pdf"),
            _make_result(),
            warnings=["Page 3: could not extract text."],
        )
        assert "Page 3" in content

    def test_no_api_key_in_content(self) -> None:
        """Security: API keys must never appear in output."""
        content = build_solved_content(Path("q.txt"), _make_result())
        assert "sk-" not in content


class TestWriteSolution:
    def test_creates_file(self, tmp_path: Path) -> None:
        out = tmp_path / "q.txt.solved"
        write_solution(out, Path("q.txt"), _make_result())
        assert out.exists()

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        out = tmp_path / "nested" / "deep" / "q.txt.solved"
        write_solution(out, Path("q.txt"), _make_result())
        assert out.exists()

    def test_content_is_utf8(self, tmp_path: Path) -> None:
        out = tmp_path / "q.txt.solved"
        write_solution(out, Path("q.txt"), _make_result("Solution with £ and €"))
        text = out.read_text(encoding="utf-8")
        assert "£" in text
