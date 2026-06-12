from datetime import date
from typing import Literal, cast

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..core.calculator import consistency_streak
from ..core.config import get_config, save_config
from ..core.models import Goal, Workout
from ..core.storage import VaultStorage
from .calendar_widget import CalendarWidget
from .exercise_dialog import ExerciseLibraryDialog
from .goal_dialog import GoalDialog
from .progress_chart import ProgressChartWidget
from .theme import get_stylesheet
from .workout_dialog import WorkoutDialog


class GoalCard(QFrame):
    editRequested = pyqtSignal(Goal)
    deleteRequested = pyqtSignal(Goal)

    def __init__(self, goal: Goal, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._goal = goal
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            GoalCard {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
            GoalCard:hover {
                border-color: #585b70;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        header = QHBoxLayout()
        name_label = QLabel(self._goal.name)
        name_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #cdd6f4;")
        header.addWidget(name_label, 1)

        days = self._goal.days_remaining
        if days < 0:
            days_label = QLabel(f"Overdue by {abs(days)}d")
            days_label.setStyleSheet("color: #f38ba8; font-weight: 600;")
        elif days <= 7:
            days_label = QLabel(f"{days}d left")
            days_label.setStyleSheet("color: #fab387; font-weight: 600;")
        else:
            days_label = QLabel(f"{days}d left")
            days_label.setStyleSheet("color: #a6adc8;")
        header.addWidget(days_label)
        layout.addLayout(header)

        target_text = f"Target: {self._goal.target_value:.0f} {self._goal.metric.value}"
        if self._goal.exercise_name:
            target_text += f" ({self._goal.exercise_name})"
        target_label = QLabel(target_text)
        target_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(target_label)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(self._goal.progress_pct))
        progress_bar.setFormat(f"{self._goal.progress_pct:.0f}%")
        if self._goal.is_complete:
            progress_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #a6e3a1; }
            """)
        elif self._goal.is_overdue:
            progress_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #f38ba8; }
            """)
        layout.addWidget(progress_bar)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(60, 24)
        edit_btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        edit_btn.clicked.connect(lambda: self.editRequested.emit(self._goal))
        delete_btn = QPushButton("Del")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setFixedSize(52, 24)
        delete_btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        delete_btn.clicked.connect(lambda: self.deleteRequested.emit(self._goal))
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)


class WorkoutSummaryCard(QFrame):
    def __init__(self, workout: Workout, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workout = workout
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            WorkoutSummaryCard {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 10px;
                margin: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        header = QHBoxLayout()
        date_label = QLabel(self._workout.date.strftime("%A, %b %d"))
        date_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #89b4fa;")
        header.addWidget(date_label, 1)

        if self._workout.split_day:
            split_label = QLabel(self._workout.split_day)
            split_label.setStyleSheet("""
                background-color: #45475a;
                color: #cdd6f4;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
            """)
            header.addWidget(split_label)

        if self._workout.duration_min:
            dur_label = QLabel(f"{self._workout.duration_min}min")
            dur_label.setStyleSheet("color: #a6adc8; font-size: 11px;")
            header.addWidget(dur_label)

        layout.addLayout(header)

        vol = self._workout.total_volume
        vol_label = QLabel(
            f"Volume: {vol:.0f} kg · {self._workout.total_sets} sets · {self._workout.exercise_count} exercises"
        )
        vol_label.setStyleSheet("color: #a6adc8; font-size: 11px;")
        layout.addWidget(vol_label)

        if self._workout.notes:
            notes_label = QLabel(
                self._workout.notes[:80]
                + ("..." if len(self._workout.notes) > 80 else "")
            )
            notes_label.setStyleSheet(
                "color: #6c7086; font-size: 11px; font-style: italic;"
            )
            layout.addWidget(notes_label)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._config = get_config()
        self._storage = VaultStorage()
        self._workouts: list[Workout] = []
        self._goals: list[Goal] = []
        self._exercise_library: list[str] = []

        self._setup_ui()
        self._setup_menu()
        self._load_data()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Workout Tracker")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(get_stylesheet(self._config.theme))

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(12)

        left_panel = QWidget()
        left_panel.setMaximumWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self._calendar = CalendarWidget()
        self._calendar.dateSelected.connect(self._on_date_selected)
        left_layout.addWidget(self._calendar)

        stats_group = QGroupBox("Stats")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(4)
        self._streak_label = QLabel("Streak: —")
        self._streak_label.setStyleSheet("font-size: 11px;")
        stats_layout.addWidget(self._streak_label)
        self._total_workouts_label = QLabel("Total Workouts: —")
        self._total_workouts_label.setStyleSheet("font-size: 11px;")
        stats_layout.addWidget(self._total_workouts_label)
        self._total_volume_label = QLabel("Total Volume: —")
        self._total_volume_label.setStyleSheet("font-size: 11px;")
        stats_layout.addWidget(self._total_volume_label)
        left_layout.addWidget(stats_group)

        btn_layout = QVBoxLayout()
        new_workout_btn = QPushButton("+ Log Today's Workout")
        new_workout_btn.setObjectName("primaryButton")
        new_workout_btn.clicked.connect(self._log_workout)
        new_goal_btn = QPushButton("+ Set New Goal")
        new_goal_btn.setObjectName("goalButton")
        new_goal_btn.clicked.connect(self._new_goal)
        btn_layout.addWidget(new_workout_btn)
        btn_layout.addWidget(new_goal_btn)
        left_layout.addLayout(btn_layout)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self._today_header = QLabel()
        self._today_header.setObjectName("headerLabel")
        right_layout.addWidget(self._today_header)

        self._workout_scroll = QScrollArea()
        self._workout_scroll.setWidgetResizable(True)
        self._workout_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._workout_container = QWidget()
        self._workout_container_layout = QVBoxLayout(self._workout_container)
        self._workout_container_layout.setSpacing(6)
        self._workout_scroll.setWidget(self._workout_container)
        right_layout.addWidget(self._workout_scroll, 3)

        self._chart = ProgressChartWidget()
        right_layout.addWidget(self._chart, 2)

        goals_header = QLabel("Active Goals")
        goals_header.setObjectName("subsectionLabel")
        right_layout.addWidget(goals_header)

        self._goals_scroll = QScrollArea()
        self._goals_scroll.setWidgetResizable(True)
        self._goals_scroll.setMaximumHeight(200)
        self._goals_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._goals_container = QWidget()
        self._goals_container_layout = QVBoxLayout(self._goals_container)
        self._goals_container_layout.setSpacing(6)
        self._goals_scroll.setWidget(self._goals_container)
        right_layout.addWidget(self._goals_scroll, 1)

        main_layout.addWidget(right_panel, 1)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        workout_menu = menubar.addMenu("Workout")
        log_action = QAction("Log Workout...", self)
        log_action.setShortcut(QKeySequence("Ctrl+N"))
        log_action.triggered.connect(lambda: self._log_workout(date.today()))
        workout_menu.addAction(log_action)

        library_action = QAction("Manage Exercise Library...", self)
        library_action.triggered.connect(self._manage_exercise_library)
        workout_menu.addAction(library_action)

        workout_menu.addSeparator()
        delete_action = QAction("Delete Selected Workout", self)
        delete_action.setShortcut(QKeySequence("Ctrl+D"))
        delete_action.triggered.connect(
            lambda: self._delete_workout(self._calendar.selected_date)
        )
        workout_menu.addAction(delete_action)

        view_menu = menubar.addMenu("View")
        today_action = QAction("Go to Today", self)
        today_action.setShortcut(QKeySequence("Ctrl+T"))
        today_action.triggered.connect(self._go_to_today)
        view_menu.addAction(today_action)

        goals_menu = menubar.addMenu("Goals")
        new_goal_action = QAction("New Goal...", self)
        new_goal_action.setShortcut(QKeySequence("Ctrl+G"))
        new_goal_action.triggered.connect(self._new_goal)
        goals_menu.addAction(new_goal_action)

    def _load_data(self) -> None:
        workout_dates = self._storage.list_workout_dates()
        self._workouts = []
        for d in reversed(workout_dates):
            w = self._storage.load_workout(d)
            if w:
                self._workouts.append(w)
        self._workouts.reverse()

        self._goals = self._storage.load_goals()
        self._exercise_library = self._storage.load_exercise_library()

        self._calendar.set_workout_dates(list(workout_dates))
        self._calendar.set_goal_dates([g.target_date for g in self._goals])

        self._update_stats()
        self._update_goals_panel()
        self._update_workout_panel()
        self._chart.set_data(self._workouts, self._goals)

    def _update_stats(self) -> None:
        streak = consistency_streak(self._workouts)
        total_vol = sum(w.total_volume for w in self._workouts)
        self._streak_label.setText(f"Streak: {streak} day{'s' if streak != 1 else ''}")
        self._total_workouts_label.setText(f"Total Workouts: {len(self._workouts)}")
        self._total_volume_label.setText(f"Total Volume: {total_vol:,.0f} kg")

    def _update_workout_panel(self) -> None:
        selected = self._calendar.selected_date
        self._today_header.setText(f"📋 {selected.strftime('%A, %B %d, %Y')}")

        while self._workout_container_layout.count():
            item = self._workout_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        existing = next((w for w in self._workouts if w.date == selected), None)

        if existing:
            card = WorkoutSummaryCard(existing)
            self._workout_container_layout.addWidget(card)

            btn_row = QHBoxLayout()
            edit_btn = QPushButton("Edit Workout")
            edit_btn.clicked.connect(lambda: self._log_workout(selected))
            btn_row.addWidget(edit_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("dangerButton")
            delete_btn.clicked.connect(lambda: self._delete_workout(selected))
            btn_row.addWidget(delete_btn)

            btn_row.addStretch()
            self._workout_container_layout.addLayout(btn_row)

            ex_label = QLabel()
            ex_text = "<b>Exercises:</b><br>"
            for ex in existing.exercises:
                working = [s for s in ex.sets if not s.is_warmup]
                if working:
                    best = f"{working[-1].weight}×{working[-1].reps}"
                    ex_text += f"&nbsp;&nbsp;• {ex.name} — {best}"
                    if len(working) > 1:
                        ex_text += f" ({len(working)} sets)"
                    ex_text += "<br>"
            ex_label.setText(ex_text)
            ex_label.setStyleSheet("color: #a6adc8; font-size: 12px; padding: 4px 8px;")
            ex_label.setTextFormat(Qt.TextFormat.RichText)
            self._workout_container_layout.addWidget(ex_label)
        else:
            placeholder = QLabel("No workout logged for this day.")
            placeholder.setStyleSheet("color: #6c7086; padding: 20px; font-size: 13px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._workout_container_layout.addWidget(placeholder)

            log_btn = QPushButton("Log Workout")
            log_btn.setObjectName("primaryButton")
            log_btn.clicked.connect(lambda: self._log_workout(selected))
            self._workout_container_layout.addWidget(log_btn)

        self._workout_container_layout.addStretch()

    def _update_goals_panel(self) -> None:
        while self._goals_container_layout.count():
            item = self._goals_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._goals:
            placeholder = QLabel("No goals set. Click '+ Set New Goal' to start!")
            placeholder.setStyleSheet("color: #6c7086; padding: 10px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._goals_container_layout.addWidget(placeholder)
        else:
            active = [g for g in self._goals if not g.is_complete]
            active.sort(key=lambda g: g.target_date)
            for goal in active[:5]:
                card = GoalCard(goal)
                card.editRequested.connect(self._edit_goal)
                card.deleteRequested.connect(self._delete_goal)
                self._goals_container_layout.addWidget(card)

        self._goals_container_layout.addStretch()

    def _on_date_selected(self, d: date) -> None:
        self._update_workout_panel()

    def _delete_workout(self, d: date) -> None:
        existing = next((w for w in self._workouts if w.date == d), None)
        if not existing:
            return
        confirm = QMessageBox.question(
            self,
            "Delete Workout",
            f"Delete workout for {d.isoformat()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._storage.delete_workout(d)
            self._workouts.remove(existing)
            self._calendar.set_workout_dates(self._storage.list_workout_dates())
            self._update_stats()
            self._update_workout_panel()
            self._chart.set_data(self._workouts, self._goals)
            self._status_bar.showMessage(f"Workout deleted for {d.isoformat()}", 5000)

    def _log_workout(self, d: date | None = None) -> None:
        if d is None:
            d = self._calendar.selected_date

        existing = next((w for w in self._workouts if w.date == d), None)
        dialog = WorkoutDialog(
            d,
            existing=existing,
            exercise_library=self._exercise_library,
            units=self._config.units,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            workout = dialog.get_workout()
            if workout:
                self._storage.save_workout(workout)
                self._storage.append_monthly_progress(workout)

                # Update in-memory list
                if existing:
                    self._workouts.remove(existing)
                self._workouts.append(workout)
                self._workouts.sort(key=lambda w: w.date)

                self._calendar.set_workout_dates(self._storage.list_workout_dates())
                self._update_stats()
                self._update_workout_panel()
                self._chart.set_data(self._workouts, self._goals)

                self._status_bar.showMessage(f"Workout saved for {d.isoformat()}", 5000)

    def _new_goal(self) -> None:
        dialog = GoalDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            goal = dialog.get_goal()
            if goal:
                self._storage.save_goal(goal)
                self._goals.append(goal)

                self._calendar.set_goal_dates([g.target_date for g in self._goals])
                self._update_goals_panel()
                self._chart.set_data(self._workouts, self._goals)

                self._status_bar.showMessage(f"Goal '{goal.name}' saved!", 5000)

    def _edit_goal(self, goal: Goal) -> None:
        dialog = GoalDialog(existing=goal, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_goal()
            if updated:
                self._storage.delete_goal(goal)
                self._storage.save_goal(updated)
                self._goals.remove(goal)
                self._goals.append(updated)

                self._update_goals_panel()
                self._chart.set_data(self._workouts, self._goals)
                self._status_bar.showMessage(f"Goal updated: {updated.name}", 5000)

    def _delete_goal(self, goal: Goal) -> None:
        confirm = QMessageBox.question(
            self,
            "Delete Goal",
            f"Delete goal '{goal.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._storage.delete_goal(goal)
            self._goals.remove(goal)
            self._update_goals_panel()
            self._chart.set_data(self._workouts, self._goals)
            self._status_bar.showMessage(f"Goal deleted: {goal.name}", 5000)

    def _manage_exercise_library(self) -> None:
        dialog = ExerciseLibraryDialog(self._exercise_library, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._exercise_library = dialog.get_exercises()
            self._storage.save_exercise_library(self._exercise_library)
            self._status_bar.showMessage(
                f"Exercise library saved ({len(self._exercise_library)} exercises)",
                5000,
            )

    def _go_to_today(self) -> None:
        self._calendar.go_to_date(date.today())

    def _show_settings(self) -> None:
        from PyQt6.QtWidgets import (
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QFormLayout,
            QLineEdit,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(400)

        layout = QFormLayout(dialog)

        vault_path = QLineEdit(self._config.vault_path)
        layout.addRow("Vault Path:", vault_path)

        units = QComboBox()
        units.addItems(["metric", "imperial"])
        units.setCurrentText(self._config.units)
        layout.addRow("Units:", units)

        split = QLineEdit(self._config.default_split)
        layout.addRow("Default Split:", split)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._config.vault_path = vault_path.text()
            self._config.units = cast(
                "Literal['metric', 'imperial']", units.currentText()
            )
            self._config.default_split = split.text()
            save_config(self._config)
            self._storage = VaultStorage()
            self._load_data()
            self._status_bar.showMessage("Settings saved", 5000)
