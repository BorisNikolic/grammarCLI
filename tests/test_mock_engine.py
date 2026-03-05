from grammar_cli.engines.mock_engine import MockEngine
from grammar_cli.models import Category, Severity


engine = MockEngine()


class TestMockEngine:
    def test_name(self):
        assert engine.name == "MockEngine"

    def test_no_issues_for_clean_text(self):
        result = engine.check("This is a perfectly fine sentence.")
        assert result.suggestions == []

    def test_detects_subject_pronoun_error(self):
        result = engine.check("me and him went to the store")
        assert len(result.suggestions) == 1
        s = result.suggestions[0]
        assert s.category == Category.CORRECTNESS
        assert s.severity == Severity.ERROR
        assert "he and I" in s.replacements

    def test_detects_subject_verb_agreement(self):
        result = engine.check("it were great")
        assert any(s.replacements == ["it was"] for s in result.suggestions)

    def test_detects_clarity_issues(self):
        result = engine.check("This is very unique")
        assert any(s.category == Category.CLARITY for s in result.suggestions)

    def test_detects_wordy_phrases(self):
        for phrase, expected in [
            ("in order to do it", "to"),
            ("due to the fact that it rained", "because"),
            ("at this point in time", "now"),
        ]:
            result = engine.check(phrase)
            assert len(result.suggestions) >= 1, f"No suggestion for: {phrase}"
            assert any(expected in s.replacements for s in result.suggestions)

    def test_detects_engagement_issues(self):
        result = engine.check("this is basically fine")
        assert any(s.category == Category.ENGAGEMENT for s in result.suggestions)

    def test_detects_delivery_issues(self):
        result = engine.check("i think this is good")
        assert any(s.category == Category.DELIVERY for s in result.suggestions)

    def test_suggestions_sorted_by_offset(self):
        result = engine.check("me and him went, it were bad, very unique stuff")
        offsets = [s.offset for s in result.suggestions]
        assert offsets == sorted(offsets)

    def test_multiple_issues_in_one_text(self):
        result = engine.check("me and him think it were very unique")
        assert len(result.suggestions) >= 3

    def test_preserves_original_text(self):
        text = "me and him went"
        result = engine.check(text)
        assert result.text == text

    def test_case_insensitive(self):
        result = engine.check("Me And Him went to the store")
        assert len(result.suggestions) >= 1
