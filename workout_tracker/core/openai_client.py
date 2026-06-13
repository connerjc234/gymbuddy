"""OpenAI-compatible client for AI integration."""

from openai import OpenAI

from .ai_client import AIClient, AIWorkoutPlan
from .config import get_config
from .models import Exercise, Goal, Set, Workout


class OpenAICompatibleClient(AIClient):
    def __init__(self) -> None:
        config = get_config()
        self._client = OpenAI(
            base_url=config.ai_base_url,
            api_key=config.ai_api_key or "ollama",
        )
        self._model = config.ai_model

    def generate_workout(
        self,
        goal: Goal,
        history: list[Workout],
        split_day: str,
        available_equipment: list[str],
    ) -> AIWorkoutPlan:
        prompt = self._build_workout_prompt(
            goal, history, split_day, available_equipment
        )
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strength training coach. Return JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        return self._parse_workout_response(response.choices[0].message.content or "")

    def analyze_progress(self, goal: Goal, history: list[Workout]) -> str:
        prompt = self._build_analysis_prompt(goal, history)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strength training coach. Be concise and actionable.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=800,
        )
        return response.choices[0].message.content or "No analysis available."

    def suggest_deload(self, history: list[Workout]) -> bool:
        if len(history) < 4:
            return False
        prompt = f"Recent 4 workouts: {self._summarize_workouts(history[-4:])}\n\nSuggest deload? Answer 'yes' or 'no' only."
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10,
        )
        return "yes" in (response.choices[0].message.content or "").lower()

    def adjust_program(
        self, current_split: str, goals: list[Goal], history: list[Workout]
    ) -> str:
        prompt = self._build_adjustment_prompt(current_split, goals, history)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strength training coach. Be concise.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=600,
        )
        return response.choices[0].message.content or "No suggestion available."

    def chat(self, message: str, history: list[Workout], goals: list[Goal]) -> str:
        """General chat with workout context."""
        context = self._build_chat_context(history, goals)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message},
            ],
            temperature=0.5,
            max_tokens=1000,
        )
        return response.choices[0].message.content or "No response."

    def _build_workout_prompt(
        self, goal: Goal, history: list[Workout], split_day: str, equipment: list[str]
    ) -> str:
        recent = history[-5:] if history else []
        return f"""
Goal: {goal.name} — {goal.metric.value} {goal.target_value} {f"({goal.exercise_name})" if goal.exercise_name else ""}
Deadline: {goal.target_date}
Split day: {split_day}
Equipment: {", ".join(equipment) if equipment else "full gym"}
Recent workouts: {self._summarize_workouts(recent)}

Generate a {split_day} workout as JSON:
{{
  "exercises": [
    {{"name": "Exercise", "sets": [{{"weight": 0, "reps": 8, "set_number": 1, "is_warmup": false}}]}}
  ],
  "notes": "Brief coaching note"
}}
"""

    def _build_analysis_prompt(self, goal: Goal, history: list[Workout]) -> str:
        if not history:
            return f"Goal: {goal.name} (target: {goal.target_value} {goal.metric.value} by {goal.target_date}). No history yet. Give starter advice."
        relevant = [
            w
            for w in history
            if goal.exercise_name is None
            or any(e.name == goal.exercise_name for e in w.exercises)
        ]
        return f"""
Goal: {goal.name} — {goal.metric.value} {goal.target_value} by {goal.target_date}
Progress: {goal.progress_pct:.1f}% | Days left: {goal.days_remaining}
Relevant workouts: {self._summarize_workouts(relevant[-10:])}

Analyze progress and give 3 actionable recommendations.
"""

    def _build_adjustment_prompt(
        self, current_split: str, goals: list[Goal], history: list[Workout]
    ) -> str:
        return f"""
Current split: {current_split}
Goals: {", ".join(f"{g.name} ({g.progress_pct:.0f}%)" for g in goals)}
Recent volume: {sum(w.total_volume for w in history[-4:]) if history else 0:.0f}kg over {len(history[-4:])} sessions

Suggest program adjustments (split changes, volume, frequency, exercise selection).
"""

    def _build_chat_context(self, history: list[Workout], goals: list[Goal]) -> str:
        return f"""You are a strength training coach for GymBuddy.
User stats: {len(history)} workouts logged, {len(goals)} active goals.
Recent: {self._summarize_workouts(history[-3:]) if history else "none"}
Goals: {", ".join(f"{g.name} ({g.progress_pct:.0f}%)" for g in goals) if goals else "none"}
Answer workout/training questions concisely. No markdown unless asked."""

    def _summarize_workouts(self, workouts: list[Workout]) -> str:
        if not workouts:
            return "none"
        lines = []
        for w in workouts:
            exs = "; ".join(
                f"{e.name}: {', '.join(f'{s.weight}x{s.reps}@{s.rpe}' for s in e.working_sets)}"
                for e in w.exercises
            )
            lines.append(f"{w.date} ({w.split_day}): {exs}")
        return " | ".join(lines)

    def _parse_workout_response(self, content: str) -> AIWorkoutPlan:
        import json

        try:
            data = json.loads(content)
            exercises = []
            for i, ex_data in enumerate(data.get("exercises", [])):
                ex = Exercise(name=ex_data["name"], order=i)
                for s_data in ex_data.get("sets", []):
                    ex.sets.append(
                        Set(
                            weight=s_data.get("weight", 0),
                            reps=s_data.get("reps", 8),
                            rpe=s_data.get("rpe"),
                            is_warmup=s_data.get("is_warmup", False),
                            set_number=s_data.get("set_number", len(ex.sets) + 1),
                        )
                    )
                exercises.append(ex)
            return AIWorkoutPlan(exercises=exercises, notes=data.get("notes", ""))
        except Exception:
            from datetime import date

            from .ai_client import MockAIClient
            from .models import GoalMetric

            return MockAIClient().generate_workout(
                Goal(
                    name="",
                    target_value=0,
                    metric=GoalMetric.WEIGHT,
                    target_date=date.today(),
                ),
                [],
                "Push",
                [],
            )
