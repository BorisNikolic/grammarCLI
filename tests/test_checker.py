from grammar_cli.checker import Checker, _deduplicate
from grammar_cli.models import Category, CheckResult, Severity, Suggestion


def _s(offset, length, category=Category.CORRECTNESS, severity=Severity.ERROR, engine="A"):
    return Suggestion(
        offset=offset, length=length, message="msg", replacements=["fix"],
        category=category, severity=severity, rule_id="R", sentence="s", engine=engine,
    )


class FakeEngine:
    def __init__(self, suggestions: list[Suggestion], deep=False):
        self._suggestions = suggestions
        self._deep = deep

    @property
    def name(self) -> str:
        return "FakeEngine"

    @property
    def supports_deep_analysis(self) -> bool:
        return self._deep

    def check(self, text: str, language: str = "en-US") -> CheckResult:
        return CheckResult(text=text, suggestions=self._suggestions, language=language)


class TestChecker:
    def test_single_engine(self):
        engine = FakeEngine([_s(0, 5)])
        checker = Checker([engine])
        result = checker.check("hello world")
        assert len(result.suggestions) == 1

    def test_merges_multiple_engines(self):
        e1 = FakeEngine([_s(0, 5, engine="A")])
        e2 = FakeEngine([_s(10, 3, engine="B")])
        checker = Checker([e1, e2])
        result = checker.check("hello beautiful world")
        assert len(result.suggestions) == 2

    def test_deep_engine_skipped_when_deep_false(self):
        basic = FakeEngine([_s(0, 5)])
        deep = FakeEngine([_s(10, 3)], deep=True)
        checker = Checker([basic, deep])
        result = checker.check("hello world", deep=False)
        assert len(result.suggestions) == 1

    def test_deep_engine_included_when_deep_true(self):
        basic = FakeEngine([_s(0, 5)])
        deep = FakeEngine([_s(10, 3)], deep=True)
        checker = Checker([basic, deep])
        result = checker.check("hello world", deep=True)
        assert len(result.suggestions) == 2

    def test_results_sorted_by_offset(self):
        engine = FakeEngine([_s(20, 3), _s(5, 2), _s(10, 4)])
        checker = Checker([engine])
        result = checker.check("x" * 30)
        offsets = [s.offset for s in result.suggestions]
        assert offsets == sorted(offsets)

    def test_empty_text_returns_empty(self):
        engine = FakeEngine([])
        checker = Checker([engine])
        result = checker.check("")
        assert result.suggestions == []

    def test_no_engines_returns_empty(self):
        checker = Checker([])
        result = checker.check("hello")
        assert result.suggestions == []


class TestDeduplicate:
    def test_no_overlap_keeps_all(self):
        suggestions = [_s(0, 5), _s(10, 5), _s(20, 5)]
        result = _deduplicate(suggestions)
        assert len(result) == 3

    def test_overlapping_keeps_first(self):
        suggestions = [_s(0, 10), _s(5, 10)]
        result = _deduplicate(suggestions)
        assert len(result) == 1
        assert result[0].offset == 0

    def test_identical_offset_keeps_one(self):
        suggestions = [_s(0, 5, engine="A"), _s(0, 5, engine="B")]
        result = _deduplicate(suggestions)
        assert len(result) == 1

    def test_empty_list(self):
        assert _deduplicate([]) == []

    def test_adjacent_non_overlapping_kept(self):
        suggestions = [_s(0, 5), _s(5, 5)]
        result = _deduplicate(suggestions)
        assert len(result) == 2
