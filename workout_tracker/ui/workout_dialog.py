from datetime import date

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.models import Exercise, Workout, WorkoutTemplate
from .exercise_list_widget import ExerciseListWidget
from .theme import FONT_BODY, FONT_DISPLAY

DEFAULT_EXERCISES = [
    "Bench Press",
    "Incline Bench Press",
    "Decline Bench Press",
    "Overhead Press",
    "Arnold Press",
    "Lateral Raises",
    "Front Raises",
    "Tricep Pushdowns",
    "Skull Crushers",
    "Close Grip Bench",
    "Pull-ups",
    "Lat Pulldowns",
    "Barbell Rows",
    "Seated Cable Rows",
    "Face Pulls",
    "Rear Delt Flyes",
    "Bicep Curls",
    "Hammer Curls",
    "Squats",
    "Front Squats",
    "Leg Press",
    "Romanian Deadlifts",
    "Deadlifts",
    "Leg Curls",
    "Leg Extensions",
    "Calf Raises",
    "Hip Thrusts",
    "Glute Bridges",
    "Lunges",
    "Bulgarian Split Squats",
    "Dips",
    "Push-ups",
    "Chin-ups",
    "Shrugs",
    "Farmers Walks",
]

SPLIT_EXERCISES: dict[str, list[str]] = {
    "Push": [
        "Bench Press",
        "Overhead Press",
        "Incline Dumbbell Press",
        "Lateral Raises",
        "Tricep Pushdowns",
        "Skull Crushers",
    ],
    "Pull": [
        "Pull-ups",
        "Barbell Rows",
        "Seated Cable Rows",
        "Face Pulls",
        "Bicep Curls",
        "Hammer Curls",
    ],
    "Legs": [
        "Squats",
        "Romanian Deadlifts",
        "Leg Press",
        "Leg Curls",
        "Leg Extensions",
        "Calf Raises",
    ],
    "Upper": [
        "Bench Press",
        "Overhead Press",
        "Barbell Rows",
        "Pull-ups",
        "Lateral Raises",
        "Bicep Curls",
    ],
    "Lower": [
        "Squats",
        "Deadlifts",
        "Leg Press",
        "Leg Curls",
        "Calf Raises",
    ],
    "Full Body": [
        "Squats",
        "Bench Press",
        "Barbell Rows",
        "Overhead Press",
        "Deadlifts",
    ],
}

SPLIT_OPTIONS = [
    "",
    "Push",
    "Pull",
    "Legs",
    "Upper",
    "Lower",
    "Full Body",
    "Chest",
    "Back",
    "Shoulders",
    "Arms",
]


class WorkoutDialog(QDialog):
    def __init__(
        self,
        workout_date: date,
        existing: Workout | None = None,
        template: WorkoutTemplate | None = None,
        exercise_library: list[str] | None = None,
        units: str = "metric",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._workout_date = workout_date
        self._workout = existing
        self._exercise_library = list(set((exercise_library or []) + DEFAULT_EXERCISES))
        self._units = units
        self._weight_suffix = " kg" if units == "metric" else " lbs"
        self._setup_ui()
        if existing:
            self._load_workout(existing)
        elif template:
            self._load_template(template)

    def _setup_ui(self) -> None:
        self.setWindowTitle(f"Workout - {self._workout_date.isoformat()}")
        self.setMinimumSize(750, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("Log Workout")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        sub_header = QLabel(self._workout_date.strftime("%A, %B %d, %Y"))
        sub_header.setStyleSheet(
            f"font-family: '{FONT_BODY}'; font-size: 12px; color: #a39b8e; margin-top: -4px;"
        )
        layout.addWidget(sub_header)

        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Split:"))
        self._split_combo = QComboBox()
        self._split_combo.addItems(SPLIT_OPTIONS)
        self._split_combo.currentTextChanged.connect(self._on_split_changed)
        info_layout.addWidget(self._split_combo)

        info_layout.addWidget(QLabel("Duration (min):"))
        self._duration_spin = QSpinBox()
        self._duration_spin.setRange(0, 300)
        self._duration_spin.setSuffix(" min")
        self._duration_spin.setSpecialValueText("--")
        info_layout.addWidget(self._duration_spin)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        exercise_group = QGroupBox("Exercises")
        exercise_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1.5px solid #ece8e0;
                border-radius: 10px;
                margin-top: 16px;
                padding: 16px 12px 8px 12px;
                font-family: '{FONT_DISPLAY}';
                font-weight: 600;
                font-size: 11px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                color: #7a7265;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background: #f5f2ec;
                color: #7a7265;
            }}
        """)
        exercise_layout = QVBoxLayout(exercise_group)
        self._exercises_widget = ExerciseListWidget(
            self._exercise_library, self._weight_suffix
        )
        exercise_layout.addWidget(self._exercises_widget)

        add_ex_btn = QPushButton("+ Add Exercise")
        add_ex_btn.clicked.connect(self._exercises_widget.add_exercise)
        exercise_layout.addWidget(add_ex_btn)
        layout.addWidget(exercise_group)

        layout.addWidget(QLabel("Notes:"))
        self._notes_edit = QTextEdit()
        self._notes_edit.setMaximumHeight(80)
        self._notes_edit.setPlaceholderText(
            "How did the workout feel? Any injuries or adjustments?"
        )
        layout.addWidget(self._notes_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Workout")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        # Load Template via Ctrl+L from main window

    def _on_split_changed(self, split: str) -> None:
        if not split:
            return
        if self._workout:
            return
        if self._exercises_widget.get_exercises():
            return

        split_lower = split.lower()
        for key, exercises in SPLIT_EXERCISES.items():
            if key.lower() == split_lower:
                self.setWindowTitle(
                    f"Workout - {self._workout_date.isoformat()} ({split})"
                )
                available = [ex for ex in exercises if ex in self._exercise_library]
                for ex_name in available:
                    self._exercises_widget.add_exercise(
                        Exercise(
                            name=ex_name, order=self._exercises_widget._layout.count()
                        )
                    )
                break

    def _load_workout(self, workout: Workout) -> None:
        if workout.split_day:
            idx = self._split_combo.findText(workout.split_day)
            if idx >= 0:
                self._split_combo.setCurrentIndex(idx)
        if workout.duration_min:
            self._duration_spin.setValue(workout.duration_min)
        self._notes_edit.setText(workout.notes)
        for ex in workout.exercises:
            self._exercises_widget.add_exercise(ex)

    def _load_template(self, template: WorkoutTemplate) -> None:
        if template.split_day:
            idx = self._split_combo.findText(template.split_day)
            if idx >= 0:
                self._split_combo.setCurrentIndex(idx)
        self._notes_edit.setText(template.notes)
        for ex in template.exercises:
            self._exercises_widget.add_exercise(ex)

    def _save(self) -> None:
        exercises = self._exercises_widget.get_exercises()
        if not exercises:
            QMessageBox.warning(
                self, "No Exercises", "Add at least one exercise to save the workout."
            )
            return

        self._workout = Workout(
            date=self._workout_date,
            exercises=exercises,
            split_day=self._split_combo.currentText() or None,
            duration_min=self._duration_spin.value() or None,
            notes=self._notes_edit.toPlainText().strip(),
            completed=True,
        )
        self.accept()

    def get_workout(self) -> Workout | None:
        return self._workout
