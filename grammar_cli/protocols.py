from typing import Protocol

from grammar_cli.models import CheckResult


class GrammarEngine(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def supports_deep_analysis(self) -> bool: ...

    def check(self, text: str, language: str = "en-US") -> CheckResult: ...
