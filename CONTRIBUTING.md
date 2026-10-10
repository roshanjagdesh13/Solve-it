# Contributing to File Solver

Thank you for your interest in contributing! This document explains how to
get started, the code style expectations, and the pull request process.

---

## Getting Started

### 1. Fork and clone

```bash
git clone https://github.com/your-username/file-solver.git
cd file-solver
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install in editable mode with dev dependencies

```bash
pip install -e ".[dev]"
```

### 4. Copy and configure the environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 5. Run the tests

```bash
pytest
```

Tests use mock solvers — they do **not** consume real API credits.

---

## Code Style

- **Formatter / Linter**: [Ruff](https://docs.astral.sh/ruff/)
- **Type hints**: used throughout the codebase
- **Line length**: 100 characters

Run the linter before submitting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

---

## Project Structure

```
src/filesolver/
├── cli/          — Click CLI commands and display helpers
├── config/       — Environment variable loading and validation
├── processors/   — Per-format content extractors
├── solver/       — Solver interface + OpenAI implementation
├── output/       — Solution file writer
├── utils/        — Shared helpers (file detection, path building)
└── engine.py     — Orchestration (runs the full pipeline)
```

---

## Adding a New File Format

1. Create `src/filesolver/processors/yourformat_processor.py` implementing `BaseProcessor`.
2. Register the new extension in `src/filesolver/config/settings.py` (`SUPPORTED_EXTENSIONS`).
3. Add the extension mapping in `src/filesolver/utils/file_utils.py` (`detect_file_type`).
4. Wire the processor into `src/filesolver/engine.py` (`_get_processor`).
5. Write tests in `tests/test_processors.py`.

---

## Adding a New AI Provider

1. Create `src/filesolver/solver/yourprovider_solver.py` implementing `BaseSolver`.
2. Update `src/filesolver/solver/__init__.py` to export it.
3. Wire it into the CLI (e.g. via a `--provider` flag in `cli/main.py`).
4. Add tests using a mock client.

---

## Pull Request Process

1. Create a branch: `git checkout -b feat/my-feature`
2. Make your changes with tests.
3. Ensure `pytest` and `ruff check` pass.
4. Open a pull request describing what changed and why.
5. A maintainer will review and merge.

---

## Reporting Bugs

Open a GitHub Issue with:
- File Solver version (`filesolver --version`)
- Python version (`python --version`)
- Operating system
- Steps to reproduce
- Expected vs. actual behavior

Do **not** include your API key or any personal files in bug reports.

---

## Code of Conduct

Be respectful, constructive, and welcoming to all contributors.
