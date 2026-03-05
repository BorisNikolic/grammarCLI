import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".grammarrc.toml"


@dataclass
class Config:
    language: str = "en-US"
    level: str = "picky"
    disabled_rules: list[str] = field(default_factory=list)
    disabled_categories: list[str] = field(default_factory=list)


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()

    with open(CONFIG_PATH, "rb") as f:
        data = tomllib.load(f)

    return Config(
        language=data.get("language", "en-US"),
        level=data.get("level", "picky"),
        disabled_rules=data.get("disabled_rules", []),
        disabled_categories=data.get("disabled_categories", []),
    )
