import httpx

from grammar_cli.models import Category, CheckResult, Severity, Suggestion

_CATEGORY_MAP = {
    "GRAMMAR": Category.CORRECTNESS,
    "TYPOS": Category.CORRECTNESS,
    "PUNCTUATION": Category.CORRECTNESS,
    "CASING": Category.CORRECTNESS,
    "SPELLING": Category.CORRECTNESS,
    "STYLE": Category.CLARITY,
    "REDUNDANCY": Category.CLARITY,
    "PLAIN_ENGLISH": Category.CLARITY,
    "CONFUSED_WORDS": Category.CORRECTNESS,
    "COMPOUNDING": Category.ENGAGEMENT,
    "COLLOCATIONS": Category.ENGAGEMENT,
    "SEMANTICS": Category.CLARITY,
    "MISC": Category.CLARITY,
    "TYPOGRAPHY": Category.DELIVERY,
}

_ISSUE_TYPE_SEVERITY = {
    "misspelling": Severity.ERROR,
    "typographical": Severity.ERROR,
    "grammar": Severity.ERROR,
    "style": Severity.WARNING,
    "duplication": Severity.WARNING,
    "inconsistency": Severity.WARNING,
    "non-conformance": Severity.INFO,
    "register": Severity.INFO,
    "locale-violation": Severity.INFO,
    "whitespace": Severity.INFO,
}

API_URL = "https://api.languagetool.org/v2/check"


class LanguageToolEngine:
    @property
    def name(self) -> str:
        return "LanguageTool"

    @property
    def supports_deep_analysis(self) -> bool:
        return False

    def check(self, text: str, language: str = "en-US") -> CheckResult:
        response = httpx.post(
            API_URL,
            data={"text": text, "language": language, "level": "picky"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        suggestions = []
        for match in data.get("matches", []):
            rule = match.get("rule", {})
            category_id = rule.get("category", {}).get("id", "MISC")
            issue_type = rule.get("issueType", "grammar")

            suggestions.append(Suggestion(
                offset=match["offset"],
                length=match["length"],
                message=match.get("message", ""),
                short_message=match.get("shortMessage", ""),
                replacements=[r["value"] for r in match.get("replacements", [])[:5]],
                category=_CATEGORY_MAP.get(category_id, Category.CLARITY),
                severity=_ISSUE_TYPE_SEVERITY.get(issue_type, Severity.WARNING),
                rule_id=rule.get("id", ""),
                sentence=match.get("sentence", ""),
                engine=self.name,
            ))

        return CheckResult(text=text, suggestions=suggestions, language=language)
