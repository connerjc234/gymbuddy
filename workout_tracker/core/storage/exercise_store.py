"""Exercise library vault storage — read/write the Overview.md exercise table."""

from .base import BaseStore


class ExerciseStore(BaseStore):
    """Read/write exercise library to vault/Gym/Overview.md."""

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
