"""Container widget for a list of ExerciseRow widgets."""

from PyQt6.QtWidgets import QVBoxLayout, QWidget

from ..core.models import Exercise
from .exercise_row import ExerciseRow


class ExerciseListWidget(QWidget):
    """Vertical list of ExerciseRow widgets, each representing one exercise."""

    def __init__(
        self,
        exercise_library: list[str],
        weight_suffix: str = " kg",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._exercise_library = exercise_library
        self._weight_suffix = weight_suffix
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)

    def add_exercise(self, exercise: Exercise | None = None) -> None:
        row = ExerciseRow(
            self._exercise_library, self._weight_suffix, exercise=exercise
        )
        row._remove_btn.clicked.connect(lambda: self._remove_exercise(row))
        self._layout.addWidget(row)

    def _remove_exercise(self, row: ExerciseRow) -> None:
        self._layout.removeWidget(row)
        row.deleteLater()

    def get_exercises(self) -> list[Exercise]:
        exercises = []
        for i in range(self._layout.count()):
            item = self._layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if isinstance(widget, ExerciseRow):
                ex = widget.get_exercise()
                if ex and ex.sets:
                    exercises.append(ex)
        return exercises
