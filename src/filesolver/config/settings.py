"""
File Solver — Configuration Management

Reads settings from environment variables / .env file.
Validates required values and raises clear errors on misconfiguration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load .env from the current working directory (or any parent)
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

_MB = 1024 * 1024
DEFAULT_MAX_FILE_SIZE_MB = 50
DEFAULT_MODEL = "gpt-4o"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf", ".txt", ".md"}


# ─────────────────────────────────────────────────────────────────────────────
# Config dataclass
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Config:
    """Application-wide configuration loaded from the environment."""

    openai_api_key: str
    solver_model: str = DEFAULT_MODEL
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_MB * _MB
    output_directory: str | None = None
    debug: bool = False

    # Derived / computed
    supported_extensions: frozenset = field(
        default_factory=lambda: frozenset(SUPPORTED_EXTENSIONS)
    )

    # ── validation ────────────────────────────────────────────────────────────

    def __post_init__(self) -> None:
        if not self.openai_api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not configured.\n\n"
                "Set it as an environment variable before running File Solver:\n\n"
                "  export OPENAI_API_KEY=sk-...\n\n"
                "Or create a .env file in the current directory (see .env.example)."
            )


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""


# ─────────────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────────────


def load_config(*, debug: bool = False) -> Config:
    """
    Build a :class:`Config` from environment variables.

    Raises :class:`ConfigurationError` with a user-friendly message if any
    required variable is missing.
    """
    raw_max = os.getenv("MAX_FILE_SIZE", str(DEFAULT_MAX_FILE_SIZE_MB))
    try:
        max_mb = int(raw_max)
    except ValueError:
        max_mb = DEFAULT_MAX_FILE_SIZE_MB

    return Config(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        solver_model=os.getenv("SOLVER_MODEL", DEFAULT_MODEL),
        max_file_size_bytes=max_mb * _MB,
        output_directory=os.getenv("OUTPUT_DIRECTORY"),
        debug=debug,
    )
