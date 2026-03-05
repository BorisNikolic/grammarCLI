from dataclasses import dataclass, field
from enum import Enum


class Category(Enum):
    CORRECTNESS = "correctness"
    CLARITY = "clarity"
    ENGAGEMENT = "engagement"
    DELIVERY = "delivery"


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


CATEGORY_COLORS = {
    Category.CORRECTNESS: "bold red",
    Category.CLARITY: "yellow",
    Category.ENGAGEMENT: "blue",
    Category.DELIVERY: "green",
}

SEVERITY_WEIGHTS = {
    Severity.ERROR: 5,
    Severity.WARNING: 2,
    Severity.INFO: 1,
}


@dataclass
class Suggestion:
    offset: int
    length: int
    message: str
    replacements: list[str]
    category: Category
    severity: Severity
    short_message: str = ""
    rule_id: str = ""
    sentence: str = ""
    engine: str = ""

    @property
    def end(self) -> int:
        return self.offset + self.length

    def to_dict(self) -> dict:
        return {
            "offset": self.offset,
            "length": self.length,
            "message": self.message,
            "short_message": self.short_message,
            "replacements": self.replacements,
            "category": self.category.value,
            "severity": self.severity.value,
            "rule_id": self.rule_id,
            "sentence": self.sentence,
            "engine": self.engine,
        }


@dataclass
class CheckResult:
    text: str
    suggestions: list[Suggestion] = field(default_factory=list)
    language: str = "en-US"

    @property
    def scores(self) -> dict[str, int]:
        category_scores = {}
        for cat in Category:
            cat_suggestions = [s for s in self.suggestions if s.category == cat]
            deduction = sum(SEVERITY_WEIGHTS[s.severity] for s in cat_suggestions)
            category_scores[cat.value] = max(0, 100 - deduction * 3)
        return category_scores

    @property
    def overall_score(self) -> int:
        scores = self.scores
        if not scores:
            return 100
        return sum(scores.values()) // len(scores)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "language": self.language,
            "overall_score": self.overall_score,
            "scores": self.scores,
            "suggestions": [s.to_dict() for s in self.suggestions],
        }
