from grammar_cli.models import CheckResult, Suggestion
from grammar_cli.protocols import GrammarEngine


class Checker:
    def __init__(self, engines: list[GrammarEngine]):
        self._engines = engines

    def check(self, text: str, language: str = "en-US", deep: bool = False) -> CheckResult:
        all_suggestions: list[Suggestion] = []

        for engine in self._engines:
            if not deep and engine.supports_deep_analysis:
                continue
            result = engine.check(text, language)
            all_suggestions.extend(result.suggestions)

        merged = _deduplicate(all_suggestions)
        merged.sort(key=lambda s: s.offset)
        return CheckResult(text=text, suggestions=merged, language=language)


def _deduplicate(suggestions: list[Suggestion]) -> list[Suggestion]:
    if not suggestions:
        return []

    seen: list[Suggestion] = []
    for s in sorted(suggestions, key=lambda s: (s.offset, -s.severity.value.__len__())):
        overlaps = False
        for existing in seen:
            if s.offset < existing.end and s.end > existing.offset:
                overlaps = True
                break
        if not overlaps:
            seen.append(s)
    return seen
