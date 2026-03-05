import re

from grammar_cli.models import Category, CheckResult, Severity, Suggestion

_PATTERNS: list[tuple[str, str, Category, Severity, str]] = [
    (r"\bme and him\b", "he and I", Category.CORRECTNESS, Severity.ERROR, "Use subject pronouns for sentence subjects"),
    (r"\bit were\b", "it was", Category.CORRECTNESS, Severity.ERROR, "Subject-verb agreement: 'it' requires 'was'"),
    (r"\bvery unique\b", "unique", Category.CLARITY, Severity.WARNING, "'Unique' is absolute and doesn't need 'very'"),
    (r"\bin order to\b", "to", Category.CLARITY, Severity.WARNING, "'In order to' can be simplified to 'to'"),
    (r"\bat this point in time\b", "now", Category.CLARITY, Severity.WARNING, "Wordy phrase — simplify"),
    (r"\bdue to the fact that\b", "because", Category.CLARITY, Severity.WARNING, "Wordy phrase — simplify"),
    (r"\bi think\b", "I believe", Category.DELIVERY, Severity.INFO, "Consider a more confident tone"),
    (r"\breally\s+\w+", None, Category.ENGAGEMENT, Severity.INFO, "Intensifier 'really' weakens your writing"),
    (r"\bbasically\b", None, Category.ENGAGEMENT, Severity.INFO, "Filler word — consider removing"),
]


class MockEngine:
    @property
    def name(self) -> str:
        return "MockEngine"

    @property
    def supports_deep_analysis(self) -> bool:
        return False

    def check(self, text: str, language: str = "en-US") -> CheckResult:
        suggestions = []
        lower = text.lower()

        for pattern, replacement, category, severity, message in _PATTERNS:
            for match in re.finditer(pattern, lower):
                replacements = [replacement] if replacement else []
                suggestions.append(Suggestion(
                    offset=match.start(),
                    length=match.end() - match.start(),
                    message=message,
                    replacements=replacements,
                    category=category,
                    severity=severity,
                    rule_id=f"MOCK_{category.value.upper()}",
                    sentence=text,
                    engine=self.name,
                ))

        suggestions.sort(key=lambda s: s.offset)
        return CheckResult(text=text, suggestions=suggestions, language=language)
