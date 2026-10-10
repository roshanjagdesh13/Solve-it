"""Solver package."""
from .base import BaseSolver, SolverResult
from .openai_solver import OpenAISolver
from .prompts import get_system_prompt

__all__ = ["BaseSolver", "SolverResult", "OpenAISolver", "get_system_prompt"]
