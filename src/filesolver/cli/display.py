"""
File Solver — CLI Display Helpers

All Rich-based terminal rendering lives here so the rest of the code
stays free of presentation concerns.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()


# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────

def print_banner() -> None:
    console.print()
    console.print(Panel.fit(
        "[bold cyan]File Solver[/bold cyan]  [dim]— AI-powered question solver[/dim]",
        border_style="cyan",
    ))
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# File header
# ─────────────────────────────────────────────────────────────────────────────

def print_file_header(path: Path, file_type: str) -> None:
    console.print(f"  [bold]Input :[/bold] {path}")
    console.print(f"  [bold]Type  :[/bold] {file_type.upper()}")
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Step progress
# ─────────────────────────────────────────────────────────────────────────────

_STEP_LABELS = {
    1: "Reading file",
    2: "Extracting content",
    3: "Solving",
    4: "Writing solution",
}

def print_step(step: int, total: int, message: str) -> None:
    label = _STEP_LABELS.get(step, message)
    console.print(f"  [dim][{step}/{total}][/dim] {label}...")


# ─────────────────────────────────────────────────────────────────────────────
# Success / failure
# ─────────────────────────────────────────────────────────────────────────────

def print_success(output_path: Path) -> None:
    console.print()
    console.print("  [bold green]✓ Completed[/bold green]")
    console.print()
    console.print(f"  [bold]Output:[/bold] {output_path}")
    console.print()


def print_failure(input_path: Path, error: str, *, debug: bool = False) -> None:
    console.print()
    console.print(f"  [bold red]✗ Failed:[/bold red] {input_path.name}")
    console.print(f"  [red]{error}[/red]")
    if debug:
        console.print_exception()
    console.print()


def print_error(message: str) -> None:
    console.print(f"\n[bold red]ERROR:[/bold red] {message}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Batch summary
# ─────────────────────────────────────────────────────────────────────────────

def print_batch_summary(
    results: list[tuple[Path, bool, str, Path]],  # (input, success, error, output)
) -> None:
    console.print()
    console.print(Rule("[bold]Batch Summary[/bold]", style="cyan"))
    console.print()

    succeeded = [r for r in results if r[1]]
    skipped   = [r for r in results if r[2].startswith("unsupported")]

    for inp, ok, err, out in results:
        if ok:
            console.print(f"  [green]✓[/green] {inp.name}  →  {out.name}")
        elif err.startswith("unsupported"):
            console.print(f"  [yellow]⊘[/yellow] {inp.name}  [dim]— unsupported format[/dim]")
        else:
            console.print(f"  [red]✗[/red] {inp.name}  [dim]— {err}[/dim]")

    console.print()
    console.print(
        f"  Completed: [green]{len(succeeded)}[/green] / "
        f"{len(results) - len(skipped)}  "
        f"([yellow]{len(skipped)} skipped[/yellow])"
    )
    console.print()
