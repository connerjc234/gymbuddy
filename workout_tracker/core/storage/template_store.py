"""Template vault storage — markdown read/write for workout templates."""

import re
from pathlib import Path

from ..models import Exercise, Set, WorkoutTemplate
from .base import BaseStore


class TemplateStore(BaseStore):
    """Read/write template markdown files in vault/Templates/."""

    def _template_file(self, name: str) -> Path:
        safe = re.sub(r"[^\w\- ]", "", name).strip().replace(" ", "-").lower()
        return self.config.templates_path / f"{safe}.md"

    def save_template(self, template: WorkoutTemplate) -> None:
        self.config.templates_path.mkdir(parents=True, exist_ok=True)

        fm = {
            "name": template.name,
            "split_day": template.split_day,
            "notes": template.notes,
        }

        lines = ["## Exercises\n"]
        for ex in template.exercises:
            lines.append(f"### {ex.name}\n")
            if ex.notes:
                lines.append(f"*{ex.notes}*\n")
            lines.append("| Set | Reps | RPE | Warmup |")
            lines.append("|-----|------|-----|--------|")
            for i, s in enumerate(ex.sets, 1):
                rpe = f"{s.rpe:.1f}" if s.rpe is not None else ""
                warmup = "yes" if s.is_warmup else ""
                lines.append(f"| {i} | {s.reps} | {rpe} | {warmup} |")
            lines.append("")

        if template.notes:
            lines.append("## Notes\n")
            lines.append(template.notes + "\n")

        content = self._write_frontmatter(fm, "\n".join(lines))
        self._template_file(template.name).write_text(content)

    def load_template(self, name: str) -> WorkoutTemplate | None:
        path = self._template_file(name)
        if not path.exists():
            return None

        content = path.read_text()
        fm, body = self._parse_frontmatter(content)

        template = WorkoutTemplate(
            name=fm.get("name", name),
            split_day=fm.get("split_day"),
            notes=fm.get("notes", ""),
        )

        current_exercise: Exercise | None = None
        in_exercises = False
        for line in body.splitlines():
            if line.startswith("## Exercises"):
                in_exercises = True
                continue
            if line.startswith("## Notes"):
                in_exercises = False
                continue
            if in_exercises:
                if line.startswith("### "):
                    if current_exercise:
                        template.exercises.append(current_exercise)
                    name = line[4:].strip()
                    current_exercise = Exercise(
                        name=name, order=len(template.exercises)
                    )
                elif (
                    line.startswith("| ") and "Reps" not in line and "-----" not in line
                ):
                    if current_exercise:
                        parts = [p.strip() for p in line.split("|")[1:-1]]
                        if len(parts) >= 2:
                            try:
                                s_num = int(parts[0])
                                reps = int(parts[1])
                                rpe = (
                                    float(parts[2])
                                    if len(parts) > 2 and parts[2]
                                    else None
                                )
                                is_warmup = (
                                    "yes" in parts[3].lower()
                                    if len(parts) > 3
                                    else False
                                )
                                current_exercise.sets.append(
                                    Set(
                                        weight=0,
                                        reps=reps,
                                        rpe=rpe,
                                        is_warmup=is_warmup,
                                        set_number=s_num,
                                    )
                                )
                            except (ValueError, IndexError):
                                pass

        if current_exercise:
            template.exercises.append(current_exercise)
        return template

    def list_templates(self) -> list[str]:
        names = []
        for path in self.config.templates_path.glob("*.md"):
            content = path.read_text()
            fm, _ = self._parse_frontmatter(content)
            name = fm.get("name", path.stem.replace("-", " ").title())
            names.append(name)
        return sorted(names)

    def delete_template(self, name: str) -> None:
        path = self._template_file(name)
        if path.exists():
            path.unlink()
