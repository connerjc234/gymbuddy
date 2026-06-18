"""Monthly progress vault storage — append workout data to monthly summary."""

from ..models import Workout
from .base import BaseStore


class ProgressStore(BaseStore):
    """Append workout sets to monthly progress markdown."""

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
