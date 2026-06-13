"""Obsidian vault storage layer for workout tracker."""

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .config import get_config
from .models import Exercise, Goal, GoalMetric, Set, Workout, WorkoutTemplate


class VaultStorage:
    def __init__(self) -> None:
        self.config = get_config()

    def _workout_file(self, workout_date: date) -> Path:
        return self.config.workouts_path / f"{workout_date.isoformat()}.md"

    def _goal_file(self, goal: Goal) -> Path:
        safe_name = re.sub(r"[^\w\-]", "-", goal.name.lower())
        return self.config.goals_path / f"{goal.target_date.isoformat()}-{safe_name}.md"

    def _parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
                return fm, body
        return {}, content

    def _write_frontmatter(self, fm: dict[str, Any], body: str) -> str:
        return f"---\n{yaml.dump(fm, sort_keys=False)}---\n\n{body}\n"

    def save_workout(self, workout: Workout) -> None:
        self.config.workouts_path.mkdir(parents=True, exist_ok=True)

        fm = {
            "date": workout.date.isoformat(),
            "split": workout.split_day,
            "duration_min": workout.duration_min,
            "completed": workout.completed,
        }

        lines = ["## Exercises\n"]
        for ex in workout.exercises:
            lines.append(f"### {ex.name}\n")
            if ex.notes:
                lines.append(f"*{ex.notes}*\n")
            lines.append("| Set | Weight | Reps | RPE |")
            lines.append("|-----|--------|------|-----|")
            for i, s in enumerate(ex.sets, 1):
                rpe = f"{s.rpe:.1f}" if s.rpe is not None else ""
                warmup = " (warmup)" if s.is_warmup else ""
                lines.append(f"| {i} | {s.weight} | {s.reps} | {rpe} |{warmup}")
            lines.append("")

        if workout.notes:
            lines.append("## Notes\n")
            lines.append(workout.notes + "\n")

        content = self._write_frontmatter(fm, "\n".join(lines))
        self._workout_file(workout.date).write_text(content)

    def load_workout(self, workout_date: date) -> Workout | None:
        path = self._workout_file(workout_date)
        if not path.exists():
            return None

        content = path.read_text()
        fm, body = self._parse_frontmatter(content)

        workout = Workout(
            date=workout_date,
            split_day=fm.get("split"),
            duration_min=fm.get("duration_min"),
            completed=fm.get("completed", True),
            notes="",
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
                        workout.exercises.append(current_exercise)
                    name = line[4:].strip()
                    current_exercise = Exercise(name=name, order=len(workout.exercises))
                elif (
                    line.startswith("| ")
                    and "Weight" not in line
                    and "-----" not in line
                ):
                    if current_exercise:
                        parts = [p.strip() for p in line.split("|")[1:-1]]
                        if len(parts) >= 3:
                            try:
                                set_num = int(parts[0])
                                weight = float(parts[1])
                                reps = int(parts[2])
                                rpe = (
                                    float(parts[3])
                                    if len(parts) > 3 and parts[3]
                                    else None
                                )
                                is_warmup = "(warmup)" in line
                                current_exercise.sets.append(
                                    Set(
                                        weight=weight,
                                        reps=reps,
                                        rpe=rpe,
                                        is_warmup=is_warmup,
                                        set_number=set_num,
                                    )
                                )
                            except (ValueError, IndexError):
                                pass

        if current_exercise:
            workout.exercises.append(current_exercise)

        notes_match = re.search(r"## Notes\n(.*)", body, re.DOTALL)
        if notes_match:
            workout.notes = notes_match.group(1).strip()

        return workout

    def list_workout_dates(self) -> list[date]:
        dates = []
        for path in self.config.workouts_path.glob("*.md"):
            try:
                d = date.fromisoformat(path.stem)
                dates.append(d)
            except ValueError:
                pass
        return sorted(dates)

    def save_goal(self, goal: Goal) -> None:
        self.config.goals_path.mkdir(parents=True, exist_ok=True)

        fm = {
            "name": goal.name,
            "target_date": goal.target_date.isoformat(),
            "metric": goal.metric.value,
            "target_value": goal.target_value,
            "current_value": goal.current_value,
            "exercise_name": goal.exercise_name,
            "created_date": goal.created_date.isoformat(),
        }

        body = f"""# {goal.name}

**Target:** {goal.target_value} {goal.metric.value} by {goal.target_date.isoformat()}
**Current:** {goal.current_value}
**Progress:** {goal.progress_pct:.1f}%
**Days Remaining:** {goal.days_remaining}

{goal.notes}
"""

        content = self._write_frontmatter(fm, body)
        self._goal_file(goal).write_text(content)

    def load_goals(self) -> list[Goal]:
        goals = []
        for path in self.config.goals_path.glob("*.md"):
            content = path.read_text()
            fm, body = self._parse_frontmatter(content)
            try:
                goal = Goal(
                    name=fm.get("name", path.stem),
                    target_date=date.fromisoformat(
                        fm.get("target_date", date.today().isoformat())
                    ),
                    metric=GoalMetric(fm.get("metric", "weight")),
                    target_value=fm.get("target_value", 0.0),
                    current_value=fm.get("current_value", 0.0),
                    exercise_name=fm.get("exercise_name"),
                    created_date=date.fromisoformat(
                        fm.get("created_date", date.today().isoformat())
                    ),
                    notes=body.strip(),
                )
                goals.append(goal)
            except (ValueError, KeyError):
                pass
        return sorted(goals, key=lambda g: g.target_date)

    def delete_workout(self, workout_date: date) -> None:
        path = self._workout_file(workout_date)
        if path.exists():
            path.unlink()

    def load_exercise_library(self) -> list[str]:
        path = self.config.gym_path / "Overview.md"
        if not path.exists():
            return []

        content = path.read_text()
        exercises: list[str] = []
        in_exercise_table = False
        for line in content.splitlines():
            if line.startswith("## Current Split") or line.startswith("## Split"):
                in_exercise_table = False
            if line.startswith("### "):
                ex_name = line[4:].strip()
                if ex_name and ex_name not in exercises:
                    exercises.append(ex_name)
            if line.startswith("|") and "Exercise" in line:
                in_exercise_table = True
                continue
            if in_exercise_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2 and parts[1] and not parts[1].startswith("-"):
                    ex_name = parts[1]
                    if ex_name and ex_name not in exercises:
                        exercises.append(ex_name)

        return exercises

    def save_exercise_library(self, exercises: list[str]) -> None:
        path = self.config.gym_path / "Overview.md"
        if not path.exists():
            path.write_text("# Gym — Overview\n\n## Exercise Library\n\n")
        content = path.read_text()
        if "## Exercise Library" not in content:
            content += "\n## Exercise Library\n\n"
            content += "| Exercise |\n|----------|\n"
            for ex in exercises:
                content += f"| {ex} |\n"
            path.write_text(content)
        else:
            lines = content.splitlines()
            in_library = False
            library_start = -1
            library_end = -1
            for i, line in enumerate(lines):
                if line.startswith("## Exercise Library"):
                    in_library = True
                    library_start = i
                    continue
                if in_library and line.startswith("## "):
                    library_end = i
                    break
            if library_start >= 0:
                header = lines[: library_start + 1]
                rest = lines[library_end:] if library_end >= 0 else []
                table = ["| Exercise |", "|----------|"]
                for ex in exercises:
                    table.append(f"| {ex} |")
                path.write_text("\n".join(header + table + rest) + "\n")

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

    def delete_goal(self, goal: Goal) -> None:
        path = self._goal_file(goal)
        if path.exists():
            path.unlink()

    def append_monthly_progress(self, workout: Workout) -> None:
        month_key = workout.date.strftime("%Y-%m")
        progress_file = self.config.gym_path / f"Progress-{month_key}.md"

        if not progress_file.exists():
            progress_file.write_text(
                f"# Progress — {month_key}\n\n| Date | Exercise | Weight | Reps | RPE | Volume |\n|------|----------|--------|------|-----|--------|\n"
            )

        lines = progress_file.read_text().splitlines()
        for ex in workout.exercises:
            for s in ex.working_sets:
                vol = s.volume
                rpe = f"{s.rpe:.1f}" if s.rpe else ""
                lines.append(
                    f"| {workout.date.isoformat()} | {ex.name} | {s.weight} | {s.reps} | {rpe} | {vol:.1f} |"
                )

        progress_file.write_text("\n".join(lines) + "\n")

    def save_ai_note(
        self, title: str, content: str, tags: list[str] | None = None
    ) -> Path:
        """Save an AI-generated note to the vault."""
        import re
        from datetime import datetime

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

        body = f"# {title}\n\n{content}\n"

        if tags:
            body += f"\n---\n*Tags: {', '.join(tags)}*"

        full_content = f"---\n{yaml.dump(fm, sort_keys=False)}---\n\n{body}\n"
        filepath.write_text(full_content)
        return filepath
