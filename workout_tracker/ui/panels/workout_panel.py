"""Workout display panel with summary card, chart, and actions."""

from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...core.models import Goal, Workout
from ..progress_chart import ProgressChartWidget
from ..theme import FONT_DISPLAY


class WorkoutSummaryCard(QFrame):
    """Card showing a single workout's summary details."""

    def __init__(self, workout: Workout, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workout = workout
        self.setObjectName("workoutCard")
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet("""
            QFrame#workoutCard {
                background-color: #ffffff;
                border: 1.5px solid #ece8e0;
                border-radius: 12px;
                padding: 16px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        header = QHBoxLayout()
        date_label = QLabel(self._workout.date.strftime("%A, %b %d"))
        date_label.setStyleSheet(
            f"font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 15px; color: #1a1612; letter-spacing: 0.3px; text-transform: uppercase;"
        )
        header.addWidget(date_label, 1)

        if self._workout.split_day:
            split_label = QLabel(self._workout.split_day)
            split_label.setStyleSheet(f"""
                font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 11px;
                background-color: #f5f2ec; color: #7a7265;
                padding: 3px 10px; border-radius: 4px;
                letter-spacing: 0.3px; text-transform: uppercase;
            """)
            header.addWidget(split_label)

        if self._workout.duration_min:
            dur_label = QLabel(f"{self._workout.duration_min}")
            dur_label.setStyleSheet(
                f"font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 13px; color: #7a7265;"
            )
            dur_unit = QLabel("min")
            dur_unit.setStyleSheet("color: #a39b8e; font-size: 10px; margin-left: 2px;")
            header.addWidget(dur_label)
            header.addWidget(dur_unit)

        layout.addLayout(header)

        vol = self._workout.total_volume
        vol_label = QLabel(
            f"{vol:,.0f} kg total  \u00b7  {self._workout.total_sets} working sets  \u00b7  {self._workout.exercise_count} exercises"
        )
        vol_label.setStyleSheet("color: #7a7265; font-size: 12px;")
        layout.addWidget(vol_label)

        if self._workout.notes:
            notes_label = QLabel(
                f"\u201c{self._workout.notes[:80]}{'...' if len(self._workout.notes) > 80 else ''}\u201d"
            )
            notes_label.setStyleSheet(
                "color: #a39b8e; font-size: 11px; font-style: italic; padding-top: 2px;"
            )
            layout.addWidget(notes_label)


class WorkoutPanel(QWidget):
    """Right-side panel showing selected day's workout with chart."""

    edit_requested = pyqtSignal(date)
    delete_requested = pyqtSignal(date)
    save_as_template_requested = pyqtSignal(object)  # Workout

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._today_header = QLabel()
        self._today_header.setObjectName("headerLabel")
        layout.addWidget(self._today_header)

        self._workout_scroll = QScrollArea()
        self._workout_scroll.setWidgetResizable(True)
        self._workout_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._workout_container = QWidget()
        self._workout_container.setStyleSheet("background: transparent;")
        self._workout_container_layout = QVBoxLayout(self._workout_container)
        self._workout_container_layout.setSpacing(8)
        self._workout_container_layout.setContentsMargins(0, 0, 0, 0)
        self._workout_scroll.setWidget(self._workout_container)
        layout.addWidget(self._workout_scroll, 3)

        self._chart = ProgressChartWidget()
        layout.addWidget(self._chart, 2)

    # ── Public API ──

    def show_workout(self, selected_date: date, workout: Workout | None) -> None:
        """Render the workout card and actions for a given date."""
        from datetime import date

        is_today = selected_date == date.today()
        prefix = "" if not is_today else "\u25cf  "
        self._today_header.setText(f"{prefix}{selected_date.strftime('%A, %B %d, %Y')}")

        self._clear_layout(self._workout_container_layout)

        if workout:
            card = WorkoutSummaryCard(workout)
            self._workout_container_layout.addWidget(card)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(6)
            edit_btn = QPushButton("Edit Workout")
            edit_btn.clicked.connect(
                lambda checked, d=selected_date: self.edit_requested.emit(d)
            )
            btn_row.addWidget(edit_btn)

            template_btn = QPushButton("Save as Template")
            template_btn.setObjectName("goalButton")
            template_btn.clicked.connect(
                lambda checked, w=workout: self.save_as_template_requested.emit(w)
            )
            btn_row.addWidget(template_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("dangerButton")
            delete_btn.clicked.connect(
                lambda checked, d=selected_date: self.delete_requested.emit(d)
            )
            btn_row.addWidget(delete_btn)
            btn_row.addStretch()
            self._workout_container_layout.addLayout(btn_row)

            ex_label = QLabel()
            ex_lines = []
            for ex in workout.exercises:
                working = [s for s in ex.sets if not s.is_warmup]
                if working:
                    best = f"{working[-1].weight}\u00d7{working[-1].reps}"
                    line = f"  \u2022  {ex.name}  \u2014  {best}"
                    if len(working) > 1:
                        line += f"  ({len(working)} sets)"
                    ex_lines.append(line)
            ex_label.setText("\n".join(ex_lines))
            ex_label.setStyleSheet(
                "color: #7a7265; font-size: 12px; padding: 8px 0 0 0;"
            )
            self._workout_container_layout.addWidget(ex_label)
        else:
            placeholder = QLabel("No workout logged for this day.")
            placeholder.setStyleSheet("color: #a39b8e; padding: 24px; font-size: 13px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._workout_container_layout.addWidget(placeholder)

            log_btn = QPushButton("Log Workout")
            log_btn.setObjectName("primaryButton")
            log_btn.clicked.connect(
                lambda checked, d=selected_date: self.edit_requested.emit(d)
            )
            self._workout_container_layout.addWidget(log_btn)

        self._workout_container_layout.addStretch()

    def set_chart_data(self, workouts: list[Workout], goals: list[Goal]) -> None:
        self._chart.set_data(workouts, goals)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
