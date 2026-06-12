from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.models import Exercise, Set, Workout

EXERCISE_LIBRARY = [
    "Bench Press", "Incline Bench Press", "Decline Bench Press",
    "Overhead Press", "Arnold Press", "Lateral Raises", "Front Raises",
    "Tricep Pushdowns", "Skull Crushers", "Close Grip Bench",
    "Pull-ups", "Lat Pulldowns", "Barbell Rows", "Seated Cable Rows",
    "Face Pulls", "Rear Delt Flyes", "Bicep Curls", "Hammer Curls",
    "Squats", "Front Squats", "Leg Press", "Romanian Deadlifts",
    "Deadlifts", "Leg Curls", "Leg Extensions", "Calf Raises",
    "Hip Thrusts", "Glute Bridges", "Lunges", "Bulgarian Split Squats",
    "Dips", "Push-ups", "Chin-ups", "Shrugs", "Farmers Walks",
]

SPLIT_OPTIONS = ["", "Push", "Pull", "Legs", "Upper", "Lower",
                 "Full Body", "Chest", "Back", "Shoulders", "Arms"]


class WorkoutDialog(QDialog):
    def __init__(self, workout_date: date, existing: Workout | None = None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workout_date = workout_date
        self._workout = existing
        self._setup_ui()

        if existing:
            self._load_workout(existing)

    def _setup_ui(self) -> None:
        self.setWindowTitle(f"Workout - {self._workout_date.isoformat()}")
        self.setMinimumSize(700, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel(f"Log Workout — {self._workout_date.strftime('%A, %B %d, %Y')}")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Split:"))
        self._split_combo = QComboBox()
        self._split_combo.addItems(SPLIT_OPTIONS)
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
        exercise_layout = QVBoxLayout(exercise_group)
        self._exercises_widget = ExerciseListWidget()
        exercise_layout.addWidget(self._exercises_widget)

        add_ex_btn = QPushButton("+ Add Exercise")
        add_ex_btn.clicked.connect(self._exercises_widget.add_exercise)
        exercise_layout.addWidget(add_ex_btn)
        layout.addWidget(exercise_group)

        layout.addWidget(QLabel("Notes:"))
        self._notes_edit = QTextEdit()
        self._notes_edit.setMaximumHeight(80)
        self._notes_edit.setPlaceholderText("How did the workout feel? Any injuries or adjustments?")
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

    def _save(self) -> None:
        exercises = self._exercises_widget.get_exercises()
        if not exercises:
            QMessageBox.warning(self, "No Exercises",
                                "Add at least one exercise to save the workout.")
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


class ExerciseRow(QWidget):
    def __init__(self, exercise: Exercise | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._exercise = exercise
        self._setup_ui()
        if exercise:
            self._load_exercise(exercise)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        header = QHBoxLayout()
        self._name_combo = QComboBox()
        self._name_combo.setEditable(True)
        self._name_combo.addItems(EXERCISE_LIBRARY)
        self._name_combo.setMinimumWidth(180)
        self._name_combo.currentTextChanged.connect(self._on_name_changed)
        header.addWidget(self._name_combo)

        self._notes_input = QLineEdit()
        self._notes_input.setPlaceholderText("Exercise notes...")
        header.addWidget(self._notes_input, 1)

        self._remove_btn = QPushButton("✕")
        self._remove_btn.setFixedSize(28, 28)
        self._remove_btn.setObjectName("dangerButton")
        header.addWidget(self._remove_btn)
        layout.addLayout(header)

        self._sets_table = QTableWidget(0, 5)
        self._sets_table.setHorizontalHeaderLabels(["Set", "Weight", "Reps", "RPE", "Warmup"])
        self._sets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._sets_table.setColumnWidth(0, 40)
        self._sets_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._sets_table.setColumnWidth(4, 60)
        self._sets_table.verticalHeader().setVisible(False)
        layout.addWidget(self._sets_table)

        set_btn_layout = QHBoxLayout()
        add_set_btn = QPushButton("+ Add Set")
        add_set_btn.clicked.connect(self._add_set_row)
        self._add_warmup_btn = QPushButton("+ Warmup")
        self._add_warmup_btn.clicked.connect(lambda: self._add_set_row(is_warmup=True))
        set_btn_layout.addWidget(add_set_btn)
        set_btn_layout.addWidget(self._add_warmup_btn)
        set_btn_layout.addStretch()
        layout.addLayout(set_btn_layout)

    def _on_name_changed(self, name: str) -> None:
        if name:
            self._name_combo.setStyleSheet("")

    def _add_set_row(self, is_warmup: bool = False) -> None:
        row = self._sets_table.rowCount()
        self._sets_table.insertRow(row)

        set_item = QTableWidgetItem(str(row + 1))
        set_item.setFlags(set_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._sets_table.setItem(row, 0, set_item)

        weight = QDoubleSpinBox()
        weight.setRange(0, 999.5)
        weight.setSingleStep(2.5)
        weight.setDecimals(1)
        weight.setSuffix(" kg")
        weight.setValue(0)
        self._sets_table.setCellWidget(row, 1, weight)

        reps = QSpinBox()
        reps.setRange(0, 100)
        reps.setValue(10)
        self._sets_table.setCellWidget(row, 2, reps)

        rpe = QDoubleSpinBox()
        rpe.setRange(0, 10)
        rpe.setSingleStep(0.5)
        rpe.setDecimals(1)
        rpe.setValue(7)
        self._sets_table.setCellWidget(row, 3, rpe)

        warmup = QCheckBox()
        warmup.setChecked(is_warmup)
        warmup_widget = QWidget()
        warmup_layout = QHBoxLayout(warmup_widget)
        warmup_layout.addWidget(warmup)
        warmup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warmup_layout.setContentsMargins(0, 0, 0, 0)
        self._sets_table.setCellWidget(row, 4, warmup_widget)

        weight.valueChanged.connect(lambda: self._renumber_sets())

    def _renumber_sets(self) -> None:
        for row in range(self._sets_table.rowCount()):
            item = self._sets_table.item(row, 0)
            if item:
                item.setText(str(row + 1))

    def _load_exercise(self, exercise: Exercise) -> None:
        idx = self._name_combo.findText(exercise.name)
        if idx >= 0:
            self._name_combo.setCurrentIndex(idx)
        else:
            self._name_combo.setCurrentText(exercise.name)
        self._notes_input.setText(exercise.notes)

        for s in exercise.sets:
            row = self._sets_table.rowCount()
            self._sets_table.insertRow(row)

            set_item = QTableWidgetItem(str(row + 1))
            set_item.setFlags(set_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._sets_table.setItem(row, 0, set_item)

            weight = QDoubleSpinBox()
            weight.setRange(0, 999.5)
            weight.setSingleStep(2.5)
            weight.setDecimals(1)
            weight.setSuffix(" kg")
            weight.setValue(s.weight)
            self._sets_table.setCellWidget(row, 1, weight)

            reps = QSpinBox()
            reps.setRange(0, 100)
            reps.setValue(s.reps)
            self._sets_table.setCellWidget(row, 2, reps)

            rpe = QDoubleSpinBox()
            rpe.setRange(0, 10)
            rpe.setSingleStep(0.5)
            rpe.setDecimals(1)
            rpe.setValue(s.rpe if s.rpe else 7)
            self._sets_table.setCellWidget(row, 3, rpe)

            warmup = QCheckBox()
            warmup.setChecked(s.is_warmup)
            warmup_widget = QWidget()
            warmup_layout = QHBoxLayout(warmup_widget)
            warmup_layout.addWidget(warmup)
            warmup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            warmup_layout.setContentsMargins(0, 0, 0, 0)
            self._sets_table.setCellWidget(row, 4, warmup_widget)

    def get_exercise(self) -> Exercise | None:
        name = self._name_combo.currentText().strip()
        if not name:
            return None

        sets = []
        for row in range(self._sets_table.rowCount()):
            weight_widget = self._sets_table.cellWidget(row, 1)
            reps_widget = self._sets_table.cellWidget(row, 2)
            rpe_widget = self._sets_table.cellWidget(row, 3)
            warmup_widget = self._sets_table.cellWidget(row, 4)

            if not all([weight_widget, reps_widget, rpe_widget]):
                continue

            weight = weight_widget.value()
            reps = reps_widget.value()
            rpe = rpe_widget.value()
            is_warmup = warmup_widget.findChild(QCheckBox).isChecked()

            if weight == 0 or reps == 0:
                continue

            sets.append(Set(
                weight=weight,
                reps=reps,
                rpe=rpe,
                is_warmup=is_warmup,
                set_number=row + 1,
            ))

        return Exercise(
            name=name,
            sets=sets,
            notes=self._notes_input.text().strip(),
        )


class ExerciseListWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)

    def add_exercise(self, exercise: Exercise | None = None) -> None:
        row = ExerciseRow(exercise)
        row._remove_btn.clicked.connect(lambda: self._remove_exercise(row))
        if self._layout.count() > 0:
            sep = self._layout.itemAt(self._layout.count() - 1)
            if sep and sep.widget():
                sep.widget().deleteLater()
        self._layout.addWidget(row)

    def _remove_exercise(self, row: ExerciseRow) -> None:
        self._layout.removeWidget(row)
        row.deleteLater()

    def get_exercises(self) -> list[Exercise]:
        exercises = []
        for i in range(self._layout.count()):
            widget = self._layout.itemAt(i).widget()
            if isinstance(widget, ExerciseRow):
                ex = widget.get_exercise()
                if ex and ex.sets:
                    exercises.append(ex)
        return exercises
