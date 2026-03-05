import json
import sys
from pathlib import Path

import click
from rich.console import Console

from grammar_cli.checker import Checker
from grammar_cli.clipboard import read_clipboard
from grammar_cli.config import load_config
from grammar_cli.engines.languagetool import LanguageToolEngine
from grammar_cli.engines.mock_engine import MockEngine
from grammar_cli.interactive import run_interactive
from grammar_cli.renderer import apply_fixes, render_diff, render_full

console = Console()


@click.group()
def cli():
    """grammarCLI — Terminal grammar checker with Grammarly-like UX."""


@cli.command()
@click.argument("file", required=False, type=click.Path(exists=True))
@click.option("--clipboard", "from_clipboard", is_flag=True, help="Read text from clipboard")
@click.option("--language", "-l", default=None, help="Language code (e.g. en-US, de-DE, auto)")
@click.option("--fix", is_flag=True, help="Output corrected text")
@click.option("--in-place", is_flag=True, help="Fix file in place (requires --fix)")
@click.option("--interactive", "-i", is_flag=True, help="Step through suggestions interactively")
@click.option("--deep", is_flag=True, help="Enable AI-powered deep analysis")
@click.option("--json-output", "--json", "json_out", is_flag=True, help="Output results as JSON")
@click.option("--diff", is_flag=True, help="Show diff of original vs corrected")
@click.option("--mock", is_flag=True, hidden=True, help="Use mock engine (for testing)")
def check(file, from_clipboard, language, fix, in_place, interactive, deep, json_out, diff, mock):
    """Check text for grammar, spelling, and style issues."""
    config = load_config()
    lang = language or config.language

    # Read input text
    text = _read_input(file, from_clipboard)
    if not text.strip():
        console.print("[red]No text to check.[/red]")
        raise SystemExit(1)

    # Build engines
    engines = []
    if mock:
        engines.append(MockEngine())
    else:
        engines.append(LanguageToolEngine())
    if deep:
        engines.append(MockEngine())

    checker = Checker(engines)

    with console.status("[bold]Checking...[/bold]"):
        result = checker.check(text, lang, deep=deep)

    # Output
    if json_out:
        click.echo(json.dumps(result.to_dict(), indent=2))
    elif interactive:
        corrected = run_interactive(result)
        if fix and file and in_place:
            Path(file).write_text(corrected)
            console.print(f"[green]Saved to {file}[/green]")
        elif fix:
            click.echo(corrected)
    elif fix:
        corrected = apply_fixes(result)
        if file and in_place:
            Path(file).write_text(corrected)
            console.print(f"[green]Saved to {file}[/green]")
        else:
            click.echo(corrected)
    else:
        render_full(result)
        if diff:
            render_diff(result)


def _read_input(file: str | None, from_clipboard: bool) -> str:
    if from_clipboard:
        return read_clipboard()
    if file:
        return Path(file).read_text()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    console.print("[red]Provide a file, pipe text via stdin, or use --clipboard.[/red]")
    raise SystemExit(1)


if __name__ == "__main__":
    cli()
