"""Configuration management for workout tracker."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


@dataclass
class Config:
    vault_path: str = "/home/conner/Documents/ObsidianVault"
    units: Literal["metric", "imperial"] = "metric"
    default_split: str = "PPL"
    theme: Literal["dark", "light"] = "dark"
    ai_enabled: bool = False
    ai_provider: Literal["openai", "ollama", "local"] = "openai"

    @property
    def gym_path(self) -> Path:
        return Path(self.vault_path) / "Gym"

    @property
    def workouts_path(self) -> Path:
        return self.gym_path / "Workouts"

    @property
    def goals_path(self) -> Path:
        return self.gym_path / "Goals"

    def ensure_dirs(self) -> None:
        self.workouts_path.mkdir(parents=True, exist_ok=True)
        self.goals_path.mkdir(parents=True, exist_ok=True)


CONFIG_FILE = Path.home() / ".config" / "workout-tracker" / "config.json"
_config: Config | None = None


def load_config() -> Config:
    global _config
    if _config is not None:
        return _config

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        _config = Config(**data)
    else:
        _config = Config()
        save_config(_config)

    _config.ensure_dirs()
    return _config


def save_config(config: Config) -> None:
    global _config
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(asdict(config), f, indent=2)
    _config = config


def get_config() -> Config:
    if _config is None:
        return load_config()
    return _config
