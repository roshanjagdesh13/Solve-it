"""
File Solver — OpenAI Solver

Concrete :class:`BaseSolver` implementation that calls the OpenAI Chat
Completions API.  Supports any model accepted by the API (gpt-4o by default).

Error handling
--------------
- AuthenticationError  → user-friendly message about the API key
- RateLimitError       → inform user and suggest waiting
- APIConnectionError   → network problem message
- Any other API error  → generic message with the original error
"""

from __future__ import annotations

from .base import BaseSolver, SolverResult
from .prompts import get_system_prompt


class OpenAISolver(BaseSolver):
    """Solver backed by the OpenAI Chat Completions API."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        if not api_key:
            raise ValueError("api_key must not be empty.")
        self._model = model
        self._client = self._build_client(api_key)

    # ── Public API ────────────────────────────────────────────────────────────

    def solve(self, extracted_text: str, file_type: str) -> SolverResult:
        """Call the OpenAI API and return a :class:`SolverResult`."""
        system_prompt = get_system_prompt(file_type)
        user_message = (
            "Here is the content extracted from the file. "
            "Please solve all questions contained within it.\n\n"
            "---\n\n"
            + extracted_text
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,      # Lower = more deterministic, better for problem solving
                max_tokens=8192,
            )
        except Exception as exc:
            raise self._translate_error(exc) from exc

        choice = response.choices[0]
        solution = choice.message.content or ""
        usage = response.usage

        return SolverResult(
            solution_text=solution,
            model_used=self._model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _build_client(api_key: str):
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as exc:
            raise ImportError("openai package is required: pip install openai") from exc
        return OpenAI(api_key=api_key)

    @staticmethod
    def _translate_error(exc: Exception) -> Exception:
        """Convert openai SDK errors into user-friendly messages."""
        name = type(exc).__name__

        if "AuthenticationError" in name:
            return RuntimeError(
                "OpenAI API authentication failed.\n"
                "Check that OPENAI_API_KEY is set correctly and has not expired.\n"
                "Do NOT share your API key publicly."
            )
        if "RateLimitError" in name:
            return RuntimeError(
                "OpenAI rate limit reached.\n"
                "Please wait a moment and try again, or check your usage quota at "
                "https://platform.openai.com/account/usage"
            )
        if "APIConnectionError" in name or "APITimeoutError" in name:
            return RuntimeError(
                "Cannot connect to OpenAI API.\n"
                "Check your internet connection and try again."
            )
        if "BadRequestError" in name:
            return RuntimeError(
                f"OpenAI rejected the request: {exc}\n"
                "The file content may be too long or contain unsupported characters."
            )
        return RuntimeError(f"OpenAI API error: {exc}")
