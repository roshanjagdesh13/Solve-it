"""
File Solver — CLI Entry Point

Commands
--------
  filesolver solve <files/dir>  [options]
  filesolver --help
  filesolver --version
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

VERSION = "1.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# Root group
# ─────────────────────────────────────────────────────────────────────────────

@click.group()
@click.version_option(version=VERSION, prog_name="File Solver")
def cli() -> None:
    """
    \b
    File Solver — AI-powered question solver
    ─────────────────────────────────────────
    Solve questions inside images, PDFs, and text files using AI.

    \b
    Quick start:
      filesolver solve question.pdf
      filesolver solve math.png
      filesolver solve assignment.txt

    \b
    Requires OPENAI_API_KEY set as an environment variable or in a .env file.
    """


# ─────────────────────────────────────────────────────────────────────────────
# `solve` command
# ─────────────────────────────────────────────────────────────────────────────

@cli.command("solve")
@click.argument("inputs", nargs=-1, required=True, metavar="FILE_OR_DIR...")
@click.option(
    "--output", "-o",
    "output_dir",
    default=None,
    help="Directory to write .solved files into.",
    metavar="DIR",
)
@click.option(
    "--output-file", "-f",
    "output_file",
    default=None,
    help="Exact filename for the output (single-file mode only).",
    metavar="FILE",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Show full stack traces on errors.",
)
def solve_command(
    inputs: tuple[str, ...],
    output_dir: str | None,
    output_file: str | None,
    debug: bool,
) -> None:
    """
    Solve questions in one or more files (or a directory).

    \b
    Examples:
      filesolver solve question.pdf
      filesolver solve math.png --output answers/
      filesolver solve question.pdf --output-file final.txt
      filesolver solve q1.pdf q2.png q3.txt
      filesolver solve ./questions/
    """
    from filesolver.cli.display import (
        print_banner,
        print_batch_summary,
        print_error,
        print_failure,
        print_step,
        print_success,
    )
    from filesolver.config.settings import ConfigurationError, load_config
    from filesolver.engine import Engine
    from filesolver.utils.file_utils import is_supported

    print_banner()

    # ── Load config ───────────────────────────────────────────────────────────
    try:
        config = load_config(debug=debug)
    except ConfigurationError as exc:
        print_error(str(exc))
        sys.exit(1)

    # ── Collect input files ───────────────────────────────────────────────────
    all_files: list[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            all_files.extend(sorted(p.iterdir()))
        else:
            all_files.append(p)

    if not all_files:
        print_error("No input files found.")
        sys.exit(1)

    # ── Single vs batch ───────────────────────────────────────────────────────
    out_dir  = Path(output_dir)  if output_dir  else None
    out_file = Path(output_file) if output_file else None

    if out_file and len(all_files) > 1:
        print_error("--output-file can only be used with a single input file.")
        sys.exit(1)

    # ── Build engine ──────────────────────────────────────────────────────────
    is_batch = len(all_files) > 1

    batch_results: list[tuple[Path, bool, str, Path]] = []

    for file_path in all_files:
        # Skip directories inside a directory argument
        if file_path.is_dir():
            continue

        # Skip unsupported formats (batch) or error on single
        if not is_supported(file_path):
            if is_batch:
                batch_results.append((file_path, False, "unsupported", Path("")))
                continue
            else:
                print_error(
                    f"Unsupported file format: '{file_path.suffix}'\n"
                    "Supported: .png .jpg .jpeg .webp .pdf .txt .md"
                )
                sys.exit(1)

        if is_batch:
            from filesolver.cli.display import console
            console.print(f"\n[bold cyan]Processing:[/bold cyan] {file_path.name}")

        def _progress(step: int, total: int, message: str) -> None:
            print_step(step, total, message)

        engine = Engine(config, progress=_progress)
        result = engine.process(
            file_path,
            output_dir=out_dir,
            output_file=out_file,
        )

        if result.success:
            print_success(result.output_path)
            batch_results.append((file_path, True, "", result.output_path))
        else:
            print_failure(file_path, result.error, debug=debug)
            batch_results.append((file_path, False, result.error, Path("")))

    if is_batch:
        print_batch_summary(batch_results)

    # Exit with error code if any file failed
    failures = [r for r in batch_results if not r[1] and not r[2].startswith("unsupported")]
    if failures:
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point for `python -m filesolver`
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
