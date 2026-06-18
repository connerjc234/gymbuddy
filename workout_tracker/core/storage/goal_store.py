"""Goal vault storage — markdown read/write for goals."""

import re
from datetime import date
from pathlib import Path

from ..models import Goal, GoalMetric
from .base import BaseStore


class GoalStore(BaseStore):
    """Read/write goal markdown files in vault/Goals/."""

    def _goal_file(self, goal: Goal) -> Path:
        safe_name = re.sub(r"[^\w\-]", "-", goal.name.lower())
        return self.config.goals_path / f"{goal.target_date.isoformat()}-{safe_name}.md"

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

    def delete_goal(self, goal: Goal) -> None:
        path = self._goal_file(goal)
        if path.exists():
            path.unlink()
