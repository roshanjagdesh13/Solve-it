"""
Tests — Solver layer (mock responses, no real API calls)
"""

from __future__ import annotations

import pytest

from filesolver.solver.base import BaseSolver, SolverResult
from filesolver.solver.prompts import SYSTEM_PROMPTS, get_system_prompt

# ─────────────────────────────────────────────────────────────────────────────
# Mock solver for testing the interface
# ─────────────────────────────────────────────────────────────────────────────

class MockSolver(BaseSolver):
    """Returns a canned response without touching any real API."""

    def __init__(self, response: str = "Mock solution.") -> None:
        self._response = response

    def solve(self, extracted_text: str, file_type: str) -> SolverResult:
        return SolverResult(
            solution_text=self._response,
            model_used="mock-model",
            prompt_tokens=10,
            completion_tokens=20,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMockSolver:
    def test_returns_result(self) -> None:
        solver = MockSolver("Answer: 42")
        result = solver.solve("What is the answer?", "text")
        assert result.solution_text == "Answer: 42"
        assert result.model_used == "mock-model"

    def test_result_has_token_counts(self) -> None:
        solver = MockSolver()
        result = solver.solve("Q", "text")
        assert result.prompt_tokens >= 0
        assert result.completion_tokens >= 0


class TestSystemPrompts:
    def test_all_file_types_have_prompts(self) -> None:
        for ft in ("text", "markdown", "pdf", "image"):
            prompt = get_system_prompt(ft)
            assert len(prompt) > 50, f"Prompt for {ft!r} is too short"

    def test_unknown_file_type_returns_default(self) -> None:
        prompt = get_system_prompt("unknown_type_xyz")
        assert prompt  # Should return the default, not crash

    def test_prompts_mention_key_rules(self) -> None:
        for ft, prompt in SYSTEM_PROMPTS.items():
            assert "solve" in prompt.lower(), f"Prompt for {ft!r} should mention 'solve'"


class TestOpenAISolverMissingKey:
    def test_empty_api_key_raises(self) -> None:
        from filesolver.solver.openai_solver import OpenAISolver
        with pytest.raises(ValueError, match="api_key"):
            OpenAISolver(api_key="")
