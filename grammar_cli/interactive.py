import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from grammar_cli.models import CATEGORY_COLORS, CheckResult, Suggestion

console = Console()


def _render_suggestion_context(text: str, suggestion: Suggestion, index: int, total: int) -> None:
    style = CATEGORY_COLORS.get(suggestion.category, "white")

    start = max(0, suggestion.offset - 40)
    end = min(len(text), suggestion.end + 40)
    snippet = text[start:end]

    highlighted = Text(snippet)
    highlight_start = suggestion.offset - start
    highlighted.stylize(f"underline {style}", highlight_start, highlight_start + suggestion.length)

    console.print(f"\n[bold][{index}/{total}][/bold] [{style}]{suggestion.category.value.upper()}[/{style}] — {suggestion.message}")
    console.print(Panel(highlighted, border_style="dim"))

    if suggestion.replacements:
        for i, r in enumerate(suggestion.replacements[:5], 1):
            console.print(f"  [{style}]{i}[/{style}]) [bold]{r}[/bold]")

    console.print("\n  [dim]Enter=accept first, 1-5=pick replacement, s=skip, a=accept all, q=quit[/dim]")


def run_interactive(result: CheckResult) -> str:
    text = result.text
    if not result.suggestions:
        console.print("[bold green]No issues found![/bold green]")
        return text

    accepted: list[tuple[Suggestion, str]] = []
    suggestions = sorted(result.suggestions, key=lambda s: s.offset)

    for i, s in enumerate(suggestions, 1):
        if not s.replacements:
            _render_suggestion_context(text, s, i, len(suggestions))
            console.print(f"  [dim](No replacement available — info only)[/dim]")
            _wait_key("  Press any key to continue...")
            continue

        _render_suggestion_context(text, s, i, len(suggestions))

        choice = _wait_key("  > ")
        if choice == "q":
            break
        elif choice == "a":
            for remaining in suggestions[i - 1:]:
                if remaining.replacements:
                    accepted.append((remaining, remaining.replacements[0]))
            break
        elif choice == "s" or choice == "\n" and not s.replacements:
            continue
        elif choice == "\n" or choice == "\r":
            accepted.append((s, s.replacements[0]))
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(s.replacements):
                accepted.append((s, s.replacements[idx]))

    # Apply accepted fixes in reverse order
    for s, replacement in sorted(accepted, key=lambda x: x[0].offset, reverse=True):
        text = text[:s.offset] + replacement + text[s.end:]

    console.print(f"\n[bold green]Applied {len(accepted)} fix(es).[/bold green]")
    return text


def _wait_key(prompt: str) -> str:
    console.print(prompt, end="")
    if sys.stdin.isatty():
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        console.print()
        return ch
    return input().strip() or "\n"
