"""Supplement vault storage — markdown read/write for supplements."""

from datetime import datetime
from pathlib import Path

from ..models import Supplement, SupplementFrequency, SupplementTiming
from .base import BaseStore


class SupplementStore(BaseStore):
    """Read/write supplement markdown files in vault/Supplements/."""

    def _supplement_file(self, supplement_id: str) -> Path:
        return self.config.supplements_path / f"{supplement_id}.md"

    def save_supplement(self, supplement: Supplement) -> None:
        self.config.supplements_path.mkdir(parents=True, exist_ok=True)

        fm = {
            "name": supplement.name,
            "dosage": supplement.dosage,
            "frequency": supplement.frequency.value,
            "timing": supplement.timing.value,
            "custom_days": supplement.custom_days,
            "custom_time": supplement.custom_time.isoformat()
            if supplement.custom_time
            else None,
            "notes": supplement.notes,
            "enabled": supplement.enabled,
            "last_taken": supplement.last_taken.isoformat()
            if supplement.last_taken
            else None,
        }

        body = f"""# {supplement.name}

**Dosage:** {supplement.dosage}
**Frequency:** {supplement.frequency.value}
**Timing:** {supplement.timing.value}
"""
        if supplement.notes:
            body += f"\n**Notes:** {supplement.notes}\n"

        content = self._write_frontmatter(fm, body)
        self._supplement_file(supplement.supplement_id).write_text(content)

    def load_supplements(self) -> list[Supplement]:
        supplements = []
        for path in self.config.supplements_path.glob("*.md"):
            content = path.read_text()
            fm, body = self._parse_frontmatter(content)
            try:
                supplement = Supplement(
                    name=fm.get("name", path.stem),
                    dosage=fm.get("dosage", ""),
                    frequency=SupplementFrequency(fm.get("frequency", "daily")),
                    timing=SupplementTiming(fm.get("timing", "morning")),
                    custom_days=fm.get("custom_days", []),
                    custom_time=(
                        datetime.fromisoformat(fm["custom_time"]).time()
                        if fm.get("custom_time")
                        else None
                    ),
                    notes=fm.get("notes", ""),
                    enabled=fm.get("enabled", True),
                    last_taken=(
                        datetime.fromisoformat(fm["last_taken"])
                        if fm.get("last_taken")
                        else None
                    ),
                    supplement_id=path.stem,
                )
                supplements.append(supplement)
            except (ValueError, KeyError):
                pass
        return sorted(supplements, key=lambda s: s.name)

    def delete_supplement(self, supplement_id: str) -> None:
        path = self._supplement_file(supplement_id)
        if path.exists():
            path.unlink()
