from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from grammar_cli.models import CATEGORY_COLORS, Category, CheckResult, Severity

console = Console()


def render_annotated_text(result: CheckResult) -> None:
    text = Text(result.text)
    for s in sorted(result.suggestions, key=lambda s: s.offset):
        style = CATEGORY_COLORS.get(s.category, "white")
        text.stylize(f"underline {style}", s.offset, s.end)

    console.print()
    console.print(Panel(text, title="[bold]Checked Text[/bold]", border_style="dim"))


def render_suggestions(result: CheckResult) -> None:
    if not result.suggestions:
        console.print("\n[bold green]No issues found![/bold green]")
        return

    for i, s in enumerate(result.suggestions, 1):
        style = CATEGORY_COLORS.get(s.category, "white")
        severity_icon = {"error": "X", "warning": "!", "info": "i"}[s.severity.value]

        snippet = result.text[max(0, s.offset - 20):s.end + 20]
        highlighted = Text(snippet)
        start = min(20, s.offset)
        highlighted.stylize(f"underline {style}", start, start + s.length)

        console.print(f"\n  [{style}][{severity_icon}][/{style}] {s.message}")
        console.print(f"      {highlighted}")
        if s.replacements:
            replacements_str = ", ".join(f"[bold]{r}[/bold]" for r in s.replacements[:3])
            console.print(f"      Suggestion: {replacements_str}")


def render_score(result: CheckResult) -> None:
    scores = result.scores
    overall = result.overall_score

    if overall >= 80:
        score_style = "bold green"
    elif overall >= 60:
        score_style = "bold yellow"
    else:
        score_style = "bold red"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Category", style="dim")
    table.add_column("Score", justify="right")
    table.add_column("Bar")

    for cat in Category:
        score = scores[cat.value]
        bar_filled = score // 5
        bar_empty = 20 - bar_filled
        color = CATEGORY_COLORS[cat].split()[-1]
        bar = f"[{color}]{'=' * bar_filled}[/{color}][dim]{'.' * bar_empty}[/dim]"
        table.add_row(cat.value.capitalize(), f"[{color}]{score}[/{color}]", bar)

    console.print()
    console.print(Panel(table, title=f"[{score_style}]Score: {overall}/100[/{score_style}]", border_style="dim"))


def render_summary(result: CheckResult) -> None:
    counts: dict[str, int] = {}
    for cat in Category:
        counts[cat.value] = sum(1 for s in result.suggestions if s.category == cat)

    total = len(result.suggestions)
    errors = sum(1 for s in result.suggestions if s.severity == Severity.ERROR)
    warnings = sum(1 for s in result.suggestions if s.severity == Severity.WARNING)
    infos = sum(1 for s in result.suggestions if s.severity == Severity.INFO)

    console.print(f"\n  [bold]{total}[/bold] issues: [red]{errors} errors[/red], [yellow]{warnings} warnings[/yellow], [blue]{infos} info[/blue]")
    parts = [f"{counts[c.value]} {c.value}" for c in Category if counts[c.value] > 0]
    if parts:
        console.print(f"  Categories: {', '.join(parts)}")


def render_diff(result: CheckResult) -> None:
    original = result.text
    corrected = apply_fixes(result)
    if original == corrected:
        return

    console.print()
    console.print(Panel(
        Text.assemble(
            ("[red]- ", "bold red"), (original, "red"),
            "\n",
            ("[green]+ ", "bold green"), (corrected, "green"),
        ),
        title="[bold]Diff[/bold]",
        border_style="dim",
    ))


def apply_fixes(result: CheckResult) -> str:
    text = result.text
    for s in sorted(result.suggestions, key=lambda s: s.offset, reverse=True):
        if s.replacements:
            text = text[:s.offset] + s.replacements[0] + text[s.end:]
    return text


def render_full(result: CheckResult) -> None:
    render_annotated_text(result)
    render_suggestions(result)
    render_score(result)
    render_summary(result)
