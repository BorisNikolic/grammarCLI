from grammar_cli.models import Category, CheckResult, Severity, Suggestion


def _make_suggestion(
    offset=0, length=5, category=Category.CORRECTNESS, severity=Severity.ERROR, **kwargs
) -> Suggestion:
    defaults = dict(
        message="test", replacements=["fix"], short_message="",
        rule_id="TEST", sentence="test sentence", engine="test",
    )
    defaults.update(kwargs)
    return Suggestion(offset=offset, length=length, category=category, severity=severity, **defaults)


class TestSuggestion:
    def test_end_property(self):
        s = _make_suggestion(offset=10, length=5)
        assert s.end == 15

    def test_to_dict_contains_all_fields(self):
        s = _make_suggestion()
        d = s.to_dict()
        assert d["offset"] == 0
        assert d["length"] == 5
        assert d["category"] == "correctness"
        assert d["severity"] == "error"
        assert d["replacements"] == ["fix"]

    def test_to_dict_serializes_enums_as_strings(self):
        s = _make_suggestion(category=Category.CLARITY, severity=Severity.WARNING)
        d = s.to_dict()
        assert d["category"] == "clarity"
        assert d["severity"] == "warning"


class TestCheckResult:
    def test_empty_suggestions_gives_perfect_score(self):
        r = CheckResult(text="hello")
        assert r.overall_score == 100
        assert all(v == 100 for v in r.scores.values())

    def test_errors_reduce_correctness_score(self):
        r = CheckResult(text="hello", suggestions=[
            _make_suggestion(category=Category.CORRECTNESS, severity=Severity.ERROR),
        ])
        assert r.scores["correctness"] < 100
        assert r.scores["clarity"] == 100

    def test_multiple_categories_scored_independently(self):
        r = CheckResult(text="hello", suggestions=[
            _make_suggestion(category=Category.CORRECTNESS, severity=Severity.ERROR),
            _make_suggestion(offset=10, category=Category.CLARITY, severity=Severity.WARNING),
        ])
        assert r.scores["correctness"] < r.scores["clarity"]

    def test_overall_score_is_average(self):
        r = CheckResult(text="hello", suggestions=[
            _make_suggestion(category=Category.CORRECTNESS, severity=Severity.ERROR),
        ])
        scores = r.scores
        assert r.overall_score == sum(scores.values()) // len(scores)

    def test_score_never_below_zero(self):
        suggestions = [
            _make_suggestion(offset=i * 5, category=Category.CORRECTNESS, severity=Severity.ERROR)
            for i in range(20)
        ]
        r = CheckResult(text="x" * 100, suggestions=suggestions)
        assert r.scores["correctness"] >= 0

    def test_to_dict(self):
        r = CheckResult(text="hello", language="de-DE", suggestions=[
            _make_suggestion(),
        ])
        d = r.to_dict()
        assert d["text"] == "hello"
        assert d["language"] == "de-DE"
        assert "overall_score" in d
        assert "scores" in d
        assert len(d["suggestions"]) == 1
