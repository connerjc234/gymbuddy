"""Base storage class with shared frontmatter helpers."""

from typing import Any

import yaml

from ..config import Config


class BaseStore:
    """Shared frontmatter parsing/writing for all vault stores."""

    def __init__(self, config: Config) -> None:
        self.config = config

    @staticmethod
    def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
                return fm, body
        return {}, content

    @staticmethod
    def _write_frontmatter(fm: dict[str, Any], body: str) -> str:
        return f"---\n{yaml.dump(fm, sort_keys=False)}---\n\n{body}\n"
