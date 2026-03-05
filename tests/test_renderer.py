from grammar_cli.models import Category, CheckResult, Severity, Suggestion
from grammar_cli.renderer import apply_fixes


def _s(offset, length, replacement, category=Category.CORRECTNESS):
    return Suggestion(
        offset=offset, length=length, message="msg",
        replacements=[replacement] if replacement else [],
        category=category, severity=Severity.ERROR,
        rule_id="R", sentence="s", engine="test",
    )


class TestApplyFixes:
    def test_single_replacement(self):
        result = CheckResult(text="me and him went", suggestions=[_s(0, 10, "he and I")])
        assert apply_fixes(result) == "he and I went"

    def test_multiple_replacements(self):
        result = CheckResult(text="me and him think it were bad", suggestions=[
            _s(0, 10, "he and I"),
            _s(17, 7, "it was"),
        ])
        assert apply_fixes(result) == "he and I think it was bad"

    def test_no_suggestions_returns_original(self):
        result = CheckResult(text="perfect text")
        assert apply_fixes(result) == "perfect text"

    def test_suggestion_without_replacement_ignored(self):
        result = CheckResult(text="some text", suggestions=[_s(0, 4, None)])
        assert apply_fixes(result) == "some text"

    def test_replacement_shorter_than_original(self):
        result = CheckResult(text="very unique thing", suggestions=[_s(0, 11, "unique")])
        assert apply_fixes(result) == "unique thing"

    def test_replacement_longer_than_original(self):
        result = CheckResult(text="its good", suggestions=[_s(0, 3, "it's")])
        assert apply_fixes(result) == "it's good"

    def test_adjacent_replacements(self):
        result = CheckResult(text="ab", suggestions=[_s(0, 1, "A"), _s(1, 1, "B")])
        assert apply_fixes(result) == "AB"
