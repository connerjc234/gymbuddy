"""Obsidian vault storage layer for workout tracker.

Provides entity-specific stores for workouts, goals, templates, supplements,
exercise library, monthly progress, and AI notes.

Backward-compatible VaultStorage facade delegates to all stores.
"""

from datetime import date
from pathlib import Path

from ..config import get_config
from ..models import Goal, Supplement, Workout, WorkoutTemplate
from .ai_store import AIStore
from .exercise_store import ExerciseStore
from .goal_store import GoalStore
from .progress_store import ProgressStore
from .supplement_store import SupplementStore
from .template_store import TemplateStore
from .workout_store import WorkoutStore


class VaultStorage:
    """Backward-compatible facade that delegates to entity-specific stores.

    All public methods from the original monolithic VaultStorage are preserved.
    Internally, each entity type is handled by its own store.
    """

    def __init__(self) -> None:
        config = get_config()
        self.config = config
        self._workouts = WorkoutStore(config)
        self._goals = GoalStore(config)
        self._templates = TemplateStore(config)
        self._supplements = SupplementStore(config)
        self._exercises = ExerciseStore(config)
        self._progress = ProgressStore(config)
        self._ai = AIStore(config)

    # ── Workouts ──

    def save_workout(self, workout: Workout) -> None:
        self._workouts.save_workout(workout)

    def load_workout(self, workout_date: date) -> Workout | None:
        return self._workouts.load_workout(workout_date)

    def list_workout_dates(self) -> list[date]:
        return self._workouts.list_workout_dates()

    def delete_workout(self, workout_date: date) -> None:
        self._workouts.delete_workout(workout_date)

    # ── Goals ──

    def save_goal(self, goal: Goal) -> None:
        self._goals.save_goal(goal)

    def load_goals(self) -> list[Goal]:
        return self._goals.load_goals()

    def delete_goal(self, goal: Goal) -> None:
        self._goals.delete_goal(goal)

    # ── Exercise Library ──

    def load_exercise_library(self) -> list[str]:
        return self._exercises.load_exercise_library()

    def save_exercise_library(self, exercises: list[str]) -> None:
        self._exercises.save_exercise_library(exercises)

    # ── Templates ──

    def save_template(self, template: WorkoutTemplate) -> None:
        self._templates.save_template(template)

    def load_template(self, name: str) -> WorkoutTemplate | None:
        return self._templates.load_template(name)

    def list_templates(self) -> list[str]:
        return self._templates.list_templates()

    def delete_template(self, name: str) -> None:
        self._templates.delete_template(name)

    # ── Supplements ──

    def save_supplement(self, supplement: Supplement) -> None:
        self._supplements.save_supplement(supplement)

    def load_supplements(self) -> list[Supplement]:
        return self._supplements.load_supplements()

    def delete_supplement(self, supplement_id: str) -> None:
        self._supplements.delete_supplement(supplement_id)

    # ── Monthly Progress ──

    def append_monthly_progress(self, workout: Workout) -> None:
        self._progress.append_monthly_progress(workout)

    # ── AI Notes ──

    def save_ai_note(
        self, title: str, content: str, tags: list[str] | None = None
    ) -> Path:
        return self._ai.save_ai_note(title, content, tags)
