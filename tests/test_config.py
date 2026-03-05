from grammar_cli.config import Config, load_config


class TestConfig:
    def test_defaults(self):
        c = Config()
        assert c.language == "en-US"
        assert c.level == "picky"
        assert c.disabled_rules == []
        assert c.disabled_categories == []

    def test_load_config_returns_defaults_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("grammar_cli.config.CONFIG_PATH", tmp_path / "nonexistent.toml")
        c = load_config()
        assert c.language == "en-US"

    def test_load_config_reads_file(self, tmp_path, monkeypatch):
        config_file = tmp_path / ".grammarrc.toml"
        config_file.write_text('language = "de-DE"\nlevel = "default"\ndisabled_rules = ["RULE1"]')
        monkeypatch.setattr("grammar_cli.config.CONFIG_PATH", config_file)
        c = load_config()
        assert c.language == "de-DE"
        assert c.level == "default"
        assert c.disabled_rules == ["RULE1"]
