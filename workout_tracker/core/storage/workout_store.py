"""Workout vault storage — markdown read/write for workout logs."""

import re
from datetime import date
from pathlib import Path

from ..models import Exercise, Set, Workout
from .base import BaseStore


class WorkoutStore(BaseStore):
    """Read/write workout markdown files in vault/Workouts/."""

    def _workout_file(self, workout_date: date) -> Path:
        return self.config.workouts_path / f"{workout_date.isoformat()}.md"

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

    def delete_workout(self, workout_date: date) -> None:
        path = self._workout_file(workout_date)
        if path.exists():
            path.unlink()
