"""AI notes vault storage — save AI-generated notes to vault."""

import re
from datetime import datetime
from pathlib import Path

import yaml

from .base import BaseStore


class AIStore(BaseStore):
    """Save AI-generated notes to vault/AI-Notes/."""

    def save_ai_note(
        self, title: str, content: str, tags: list[str] | None = None
    ) -> Path:
        """Save an AI-generated note to the vault."""
        self.config.ai_notes_path.mkdir(parents=True, exist_ok=True)

        safe_title = re.sub(r"[^\w\- ]", "", title).strip().replace(" ", "-")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}-{safe_title}.md"
        filepath = self.config.ai_notes_path / filename

        fm = {
            "title": title,
            "created": datetime.now().isoformat(),
            "tags": tags or ["ai-coach"],
        }

        note_body = f"# {title}\n\n{content}\n"

        if tags:
            note_body += f"\n---\n*Tags: {', '.join(tags)}*"

        full_content = f"---\n{yaml.dump(fm, sort_keys=False)}---\n\n{note_body}\n"
        filepath.write_text(full_content)
        return filepath
