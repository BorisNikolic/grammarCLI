import json

from click.testing import CliRunner

from grammar_cli.main import cli


runner = CliRunner()


class TestCLI:
    def test_check_stdin_mock(self):
        result = runner.invoke(cli, ["check", "--mock"], input="me and him went\n")
        assert result.exit_code == 0
        assert "Checked Text" in result.output

    def test_check_fix_mock(self):
        result = runner.invoke(cli, ["check", "--mock", "--fix"], input="me and him went\n")
        assert result.exit_code == 0
        assert "he and I went" in result.output

    def test_check_json_mock(self):
        result = runner.invoke(cli, ["check", "--mock", "--json"], input="me and him went\n")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "suggestions" in data
        assert "overall_score" in data
        assert data["overall_score"] <= 100

    def test_check_no_input_exits_with_error(self):
        result = runner.invoke(cli, ["check"])
        assert result.exit_code == 1

    def test_check_empty_input_exits_with_error(self):
        result = runner.invoke(cli, ["check"], input="   \n")
        assert result.exit_code == 1

    def test_check_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("me and him went")
        result = runner.invoke(cli, ["check", str(f), "--mock"])
        assert result.exit_code == 0
        assert "Checked Text" in result.output

    def test_check_fix_in_place(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("me and him went")
        result = runner.invoke(cli, ["check", str(f), "--mock", "--fix", "--in-place"])
        assert result.exit_code == 0
        assert "he and I went" in f.read_text()

    def test_check_diff_mock(self):
        result = runner.invoke(cli, ["check", "--mock", "--diff"], input="me and him went\n")
        assert result.exit_code == 0
        assert "Diff" in result.output

    def test_clean_text_shows_no_issues(self):
        result = runner.invoke(cli, ["check", "--mock"], input="This is a perfectly fine sentence.\n")
        assert result.exit_code == 0
        assert "No issues found" in result.output

    def test_json_output_structure(self):
        result = runner.invoke(cli, ["check", "--mock", "--json"], input="it were bad\n")
        data = json.loads(result.output)
        assert set(data.keys()) == {"text", "language", "overall_score", "scores", "suggestions"}
        assert set(data["scores"].keys()) == {"correctness", "clarity", "engagement", "delivery"}
        for s in data["suggestions"]:
            assert "offset" in s
            assert "length" in s
            assert "category" in s
            assert "severity" in s
