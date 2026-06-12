from datetime import date
from typing import Literal, cast

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
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
from ..core.models import Exercise, Goal, Set, Workout, WorkoutTemplate
from ..core.storage import VaultStorage
from .calendar_widget import CalendarWidget
from .exercise_dialog import ExerciseLibraryDialog
from .goal_dialog import GoalDialog
from .progress_chart import ProgressChartWidget
from .template_dialog import SaveTemplateDialog, TemplateDialog
from .theme import FONT_DISPLAY, get_stylesheet
from .workout_dialog import WorkoutDialog


class GoalCard(QFrame):
    editRequested = pyqtSignal(Goal)
    deleteRequested = pyqtSignal(Goal)

    def __init__(self, goal: Goal, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._goal = goal
        self.setObjectName("goalCard")
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet("""
            QFrame#goalCard {
                background-color: #ffffff;
                border: 1.5px solid #ece8e0;
                border-radius: 10px;
                padding: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        name_label = QLabel(self._goal.name)
        name_label.setStyleSheet(
            f"font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 14px; color: #1a1612; letter-spacing: 0.3px;"
        )
        header.addWidget(name_label, 1)

        days = self._goal.days_remaining
        if days < 0:
            days_label = QLabel(f"Overdue {abs(days)}d")
            days_label.setStyleSheet(
                "color: #d64550; font-weight: 600; font-size: 11px; font-family: '{FONT_DISPLAY}';"
            )
        elif days <= 7:
            days_label = QLabel(f"{days}d left")
            days_label.setStyleSheet(
                "color: #c4a35a; font-weight: 600; font-size: 11px; font-family: '{FONT_DISPLAY}';"
            )
        else:
            days_label = QLabel(f"{days}d left")
            days_label.setStyleSheet(
                "color: #a39b8e; font-size: 11px; font-family: '{FONT_DISPLAY}';"
            )
        header.addWidget(days_label)
        layout.addLayout(header)

        target_text = f"Target: {self._goal.target_value:.0f} {self._goal.metric.value}"
        if self._goal.exercise_name:
            target_text += f" \u00b7 {self._goal.exercise_name}"
        target_label = QLabel(target_text)
        target_label.setStyleSheet("color: #7a7265; font-size: 12px;")
        layout.addWidget(target_label)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(self._goal.progress_pct))
        progress_bar.setFormat(f"{self._goal.progress_pct:.0f}%")
        if self._goal.is_complete:
            progress_bar.setStyleSheet("""
                QProgressBar { background: #ece8e0; border: none; border-radius: 4px; height: 6px; }
                QProgressBar::chunk { background: #4a7c5b; border-radius: 4px; }
            """)
        elif self._goal.is_overdue:
            progress_bar.setStyleSheet("""
                QProgressBar { background: #ece8e0; border: none; border-radius: 4px; height: 6px; }
                QProgressBar::chunk { background: #d64550; border-radius: 4px; }
            """)
        else:
            progress_bar.setStyleSheet("""
                QProgressBar { background: #ece8e0; border: none; border-radius: 4px; height: 6px; }
                QProgressBar::chunk { background: #c4a35a; border-radius: 4px; }
            """)
        layout.addWidget(progress_bar)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(52, 24)
        edit_btn.setStyleSheet(
            "font-size: 11px; padding: 2px 8px; color: #7a7265; border: 1px solid #e3ddd4; border-radius: 4px;"
        )
        edit_btn.clicked.connect(lambda: self.editRequested.emit(self._goal))
        delete_btn = QPushButton("Del")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setFixedSize(44, 24)
        delete_btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        delete_btn.clicked.connect(lambda: self.deleteRequested.emit(self._goal))
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)


class WorkoutSummaryCard(QFrame):
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


class StatCard(QFrame):
    def __init__(self, value: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: #ffffff;
                border: 1.5px solid #ece8e0;
                border-radius: 10px;
                padding: 12px 16px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        val_label = QLabel(value)
        val_label.setStyleSheet(
            f"font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 20px; color: #1a1612; letter-spacing: 0.3px;"
        )
        layout.addWidget(val_label)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            "color: #a39b8e; font-size: 10px; letter-spacing: 0.5px; text-transform: uppercase; padding-top: 2px;"
        )
        layout.addWidget(lbl)


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
        self.setWindowTitle("GymBuddy")
        self.setMinimumSize(1050, 720)
        self.setStyleSheet(get_stylesheet())

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(20)

        # ── LEFT PANEL ──
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        brand = QLabel("GymBuddy")
        brand.setStyleSheet(
            f"font-family: '{FONT_DISPLAY}'; font-weight: 700; font-size: 26px; letter-spacing: 1px; text-transform: uppercase; color: #1a1612; padding: 4px 0;"
        )
        left_layout.addWidget(brand)

        self._calendar = CalendarWidget()
        self._calendar.dateSelected.connect(self._on_date_selected)
        left_layout.addWidget(self._calendar)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)
        self._streak_card = StatCard("—", "streak")
        stats_row.addWidget(self._streak_card)
        self._total_card = StatCard("—", "workouts")
        stats_row.addWidget(self._total_card)
        self._vol_card = StatCard("—", "volume")
        stats_row.addWidget(self._vol_card)
        left_layout.addLayout(stats_row)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(6)
        new_workout_btn = QPushButton("+ New Workout")
        new_workout_btn.setObjectName("primaryButton")
        new_workout_btn.clicked.connect(self._log_workout)
        btn_layout.addWidget(new_workout_btn)
        new_goal_btn = QPushButton("+ New Goal")
        new_goal_btn.setObjectName("goalButton")
        new_goal_btn.clicked.connect(self._new_goal)
        btn_layout.addWidget(new_goal_btn)
        left_layout.addLayout(btn_layout)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # ── RIGHT PANEL ──
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        self._today_header = QLabel()
        self._today_header.setObjectName("headerLabel")
        right_layout.addWidget(self._today_header)

        self._workout_scroll = QScrollArea()
        self._workout_scroll.setWidgetResizable(True)
        self._workout_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._workout_container = QWidget()
        self._workout_container.setStyleSheet("background: transparent;")
        self._workout_container_layout = QVBoxLayout(self._workout_container)
        self._workout_container_layout.setSpacing(8)
        self._workout_container_layout.setContentsMargins(0, 0, 0, 0)
        self._workout_scroll.setWidget(self._workout_container)
        right_layout.addWidget(self._workout_scroll, 3)

        self._chart = ProgressChartWidget()
        right_layout.addWidget(self._chart, 2)

        goals_header = QLabel("Active Goals")
        goals_header.setObjectName("subsectionLabel")
        right_layout.addWidget(goals_header)

        self._goals_scroll = QScrollArea()
        self._goals_scroll.setWidgetResizable(True)
        self._goals_scroll.setMaximumHeight(220)
        self._goals_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._goals_container = QWidget()
        self._goals_container.setStyleSheet("background: transparent;")
        self._goals_container_layout = QVBoxLayout(self._goals_container)
        self._goals_container_layout.setSpacing(6)
        self._goals_container_layout.setContentsMargins(0, 0, 0, 0)
        self._goals_scroll.setWidget(self._goals_container)
        right_layout.addWidget(self._goals_scroll, 1)

        main_layout.addWidget(right_panel, 1)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("GymBuddy")
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
        library_action = QAction("Exercise Library...", self)
        library_action.triggered.connect(self._manage_exercise_library)
        workout_menu.addAction(library_action)

        workout_menu.addSeparator()
        load_template_action = QAction("Load Template...", self)
        load_template_action.setShortcut(QKeySequence("Ctrl+L"))
        load_template_action.triggered.connect(self._load_template)
        workout_menu.addAction(load_template_action)

        workout_menu.addSeparator()
        delete_action = QAction("Delete Selected", self)
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
        self._streak_card.findChildren(QLabel)[0].setText(f"{streak}")
        self._total_card.findChildren(QLabel)[0].setText(f"{len(self._workouts)}")
        self._vol_card.findChildren(QLabel)[0].setText(f"{total_vol:,.0f}")

    def _update_workout_panel(self) -> None:
        selected = self._calendar.selected_date
        is_today = selected == date.today()
        prefix = "" if not is_today else "\u25cf  "
        self._today_header.setText(f"{prefix}{selected.strftime('%A, %B %d, %Y')}")

        self._clear_layout(self._workout_container_layout)

        existing = next((w for w in self._workouts if w.date == selected), None)

        if existing:
            card = WorkoutSummaryCard(existing)
            self._workout_container_layout.addWidget(card)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(6)
            edit_btn = QPushButton("Edit Workout")
            edit_btn.clicked.connect(lambda: self._log_workout(selected))
            btn_row.addWidget(edit_btn)

            template_btn = QPushButton("Save as Template")
            template_btn.setObjectName("goalButton")
            template_btn.clicked.connect(lambda: self._save_as_template(existing))
            btn_row.addWidget(template_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("dangerButton")
            delete_btn.clicked.connect(lambda: self._delete_workout(selected))
            btn_row.addWidget(delete_btn)
            btn_row.addStretch()
            self._workout_container_layout.addLayout(btn_row)

            ex_label = QLabel()
            ex_lines = []
            for ex in existing.exercises:
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
            log_btn.clicked.connect(lambda: self._log_workout(selected))
            self._workout_container_layout.addWidget(log_btn)

        self._workout_container_layout.addStretch()

    def _update_goals_panel(self) -> None:
        self._clear_layout(self._goals_container_layout)

        if not self._goals:
            placeholder = QLabel("No goals yet. Set one to track progress!")
            placeholder.setStyleSheet("color: #a39b8e; padding: 12px; font-size: 12px;")
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

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
            self._status_bar.showMessage(f"Deleted {d.isoformat()}", 5000)

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
                if existing:
                    self._workouts.remove(existing)
                self._workouts.append(workout)
                self._workouts.sort(key=lambda w: w.date)
                self._calendar.set_workout_dates(self._storage.list_workout_dates())
                self._update_stats()
                self._update_workout_panel()
                self._chart.set_data(self._workouts, self._goals)
                self._status_bar.showMessage(f"Saved {d.isoformat()}", 5000)

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
                self._status_bar.showMessage(f"Goal set: {goal.name}", 5000)

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
                self._status_bar.showMessage(f"Updated: {updated.name}", 5000)

    def _delete_goal(self, goal: Goal) -> None:
        confirm = QMessageBox.question(
            self,
            "Delete Goal",
            f"Delete '{goal.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._storage.delete_goal(goal)
            self._goals.remove(goal)
            self._update_goals_panel()
            self._chart.set_data(self._workouts, self._goals)
            self._status_bar.showMessage(f"Deleted: {goal.name}", 5000)

    def _load_template(self) -> None:
        dialog = TemplateDialog(self._storage, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template = dialog.get_template()
            if template:
                selected = self._calendar.selected_date
                existing = next((w for w in self._workouts if w.date == selected), None)
                w_dialog = WorkoutDialog(
                    selected,
                    existing=existing,
                    template=template,
                    exercise_library=self._exercise_library,
                    units=self._config.units,
                    parent=self,
                )
                if w_dialog.exec() == QDialog.DialogCode.Accepted:
                    workout = w_dialog.get_workout()
                    if workout:
                        self._storage.save_workout(workout)
                        self._storage.append_monthly_progress(workout)
                        if existing:
                            self._workouts.remove(existing)
                        self._workouts.append(workout)
                        self._workouts.sort(key=lambda w: w.date)
                        self._calendar.set_workout_dates(
                            self._storage.list_workout_dates()
                        )
                        self._update_stats()
                        self._update_workout_panel()
                        self._chart.set_data(self._workouts, self._goals)
                        self._status_bar.showMessage(
                            f"Loaded template: {template.name}", 5000
                        )

    def _save_as_template(self, workout: Workout) -> None:
        template = WorkoutTemplate(
            name=f"{workout.split_day or 'Workout'} — {workout.date.strftime('%b %d')}",
            exercises=[
                Exercise(
                    name=e.name,
                    order=i,
                    sets=[
                        Set(
                            weight=0,
                            reps=s.reps,
                            rpe=7.0,
                            is_warmup=s.is_warmup,
                            set_number=j + 1,
                        )
                        for j, s in enumerate(e.sets)
                    ],
                )
                for i, e in enumerate(workout.exercises)
            ],
            split_day=workout.split_day,
            notes=workout.notes,
        )
        dialog = SaveTemplateDialog(template, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_template()
            self._storage.save_template(updated)
            self._status_bar.showMessage(f"Template saved: {updated.name}", 5000)

    def _manage_exercise_library(self) -> None:
        dialog = ExerciseLibraryDialog(self._exercise_library, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._exercise_library = dialog.get_exercises()
            self._storage.save_exercise_library(self._exercise_library)
            self._status_bar.showMessage(
                f"{len(self._exercise_library)} exercises saved", 5000
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
                Literal["metric", "imperial"], units.currentText()
            )
            self._config.default_split = split.text()
            save_config(self._config)
            self._storage = VaultStorage()
            self._load_data()
            self._status_bar.showMessage("Settings saved", 5000)
