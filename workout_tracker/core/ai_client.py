"""AI client interface for future AI integration."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .models import Exercise, Goal, Set, Workout


@dataclass
class AIWorkoutPlan:
    exercises: list[Exercise]
    notes: str = ""


class AIClient(ABC):
    @abstractmethod
    def generate_workout(
        self,
        goal: Goal,
        history: list[Workout],
        split_day: str,
        available_equipment: list[str]
    ) -> AIWorkoutPlan:
        """Generate a workout based on goal and history."""

    @abstractmethod
    def analyze_progress(
        self,
        goal: Goal,
        history: list[Workout]
    ) -> str:
        """Analyze progress toward goal and provide insights."""

    @abstractmethod
    def suggest_deload(self, history: list[Workout]) -> bool:
        """Suggest if a deload week is needed."""

    @abstractmethod
    def adjust_program(
        self,
        current_split: str,
        goals: list[Goal],
        history: list[Workout]
    ) -> str:
        """Suggest program adjustments."""


class MockAIClient(AIClient):
    """Rule-based fallback when AI is not configured."""

    def generate_workout(
        self,
        goal: Goal,
        history: list[Workout],
        split_day: str,
        available_equipment: list[str]
    ) -> AIWorkoutPlan:
        exercises = self._default_exercises_for_split(split_day, available_equipment)
        return AIWorkoutPlan(exercises=exercises, notes="Generated from template")

    def analyze_progress(self, goal: Goal, history: list[Workout]) -> str:
        if not history:
            return "No workout history yet. Start logging to get AI insights!"
        return f"Progress: {goal.progress_pct:.1f}% toward {goal.name}. {goal.days_remaining} days remaining."

    def suggest_deload(self, history: list[Workout]) -> bool:
        if len(history) < 4:
            return False
        recent = history[-4:]
        avg_rpe = self._avg_rpe(recent)
        return avg_rpe > 8.5

    def adjust_program(
        self,
        current_split: str,
        goals: list[Goal],
        history: list[Workout]
    ) -> str:
        return f"Current split: {current_split}. Consider adding volume for lagging goals."

    def _default_exercises_for_split(self, split: str, equipment: list[str]) -> list[Exercise]:
        templates = {
            "Push": [
                ("Bench Press", 3, 8, 0),
                ("Overhead Press", 3, 10, 0),
                ("Incline Dumbbell Press", 3, 12, 0),
                ("Lateral Raises", 3, 15, 0),
                ("Tricep Pushdowns", 3, 12, 0),
            ],
            "Pull": [
                ("Pull-ups", 3, 8, 0),
                ("Barbell Rows", 3, 10, 0),
                ("Face Pulls", 3, 15, 0),
                ("Bicep Curls", 3, 12, 0),
                ("Rear Delt Flyes", 3, 15, 0),
            ],
            "Legs": [
                ("Squats", 3, 8, 0),
                ("Romanian Deadlifts", 3, 10, 0),
                ("Leg Press", 3, 12, 0),
                ("Leg Curls", 3, 12, 0),
                ("Calf Raises", 4, 15, 0),
            ],
        }
        exercises = []
        for i, (name, sets, reps, _) in enumerate(templates.get(split, [])):
            ex = Exercise(name=name, order=i)
            for s in range(sets):
                ex.sets.append(Set(weight=0, reps=reps, set_number=s + 1))
            exercises.append(ex)
        return exercises

    def _avg_rpe(self, workouts: list[Workout]) -> float:
        rpes = []
        for w in workouts:
            for ex in w.exercises:
                for s in ex.working_sets:
                    if s.rpe:
                        rpes.append(s.rpe)
        return sum(rpes) / len(rpes) if rpes else 0.0


_ai_client: AIClient | None = None


def get_ai_client() -> AIClient:
    global _ai_client
    if _ai_client is None:
        _ai_client = MockAIClient()
    return _ai_client


def set_ai_client(client: AIClient) -> None:
    global _ai_client
    _ai_client = client
