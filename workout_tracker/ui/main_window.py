from datetime import date
from typing import Literal, cast

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from ..core.calculator import consistency_streak
from ..core.config import get_config, save_config
from ..core.dbus_service import DBusService
from ..core.models import Exercise, Goal, Set, Supplement, Workout, WorkoutTemplate
from ..core.storage import VaultStorage
from .ai_chat_dialog import AIChatDialog
from .exercise_dialog import ExerciseLibraryDialog
from .goal_dialog import GoalDialog
from .panels.goals_panel import GoalsPanel
from .panels.sidebar_panel import SidebarPanel
from .panels.workout_panel import WorkoutPanel
from .supplement_dialog import SupplementDialog
from .template_dialog import SaveTemplateDialog, TemplateDialog
from .theme import ACCENT_TERRACOTTA, get_stylesheet
from .workout_dialog import WorkoutDialog


def _create_tray_icon() -> QIcon:
    pixmap = QPixmap(22, 22)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(ACCENT_TERRACOTTA))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 18, 18, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Oswald", int(pixmap.height() * 0.45)))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "G")
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._config = get_config()
        self._storage = VaultStorage()
        self._workouts: list[Workout] = []
        self._goals: list[Goal] = []
        self._exercise_library: list[str] = []
        self._supplements: list[Supplement] = []

        self._setup_ui()
        self._setup_menu()
        self._load_data()
        self._init_dbus()
        self._init_notifications()

    def _setup_ui(self) -> None:
        self.setWindowTitle("GymBuddy")
        self.setMinimumSize(1050, 720)
        self.setStyleSheet(get_stylesheet())

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(20)

        # ── SIDEBAR ──
        self._sidebar = SidebarPanel()
        self._sidebar.date_selected.connect(self._on_date_selected)
        self._sidebar.new_workout_requested.connect(lambda: self._log_workout())
        self._sidebar.new_goal_requested.connect(self._new_goal)
        self._sidebar.supplements_requested.connect(self._manage_supplements)
        self._sidebar.settings_requested.connect(self._show_settings)
        main_layout.addWidget(self._sidebar)

        # ── RIGHT PANEL ──
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        self._workout_panel = WorkoutPanel()
        self._workout_panel.edit_requested.connect(self._log_workout)
        self._workout_panel.delete_requested.connect(self._delete_workout)
        self._workout_panel.save_as_template_requested.connect(self._save_as_template)
        right_layout.addWidget(self._workout_panel, 3)

        self._goals_panel = GoalsPanel()
        self._goals_panel.edit_requested.connect(self._edit_goal)
        self._goals_panel.delete_requested.connect(self._delete_goal)
        right_layout.addWidget(self._goals_panel, 1)

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
        ai_chat_action = QAction("AI Coach...", self)
        ai_chat_action.setShortcut(QKeySequence("Ctrl+I"))
        ai_chat_action.triggered.connect(self._open_ai_chat)
        workout_menu.addAction(ai_chat_action)

        workout_menu.addSeparator()
        delete_action = QAction("Delete Selected", self)
        delete_action.setShortcut(QKeySequence("Ctrl+D"))
        delete_action.triggered.connect(
            lambda: self._delete_workout(self._sidebar.selected_date)
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

        supp_menu = menubar.addMenu("Supplements")
        manage_supp_action = QAction("Manage Supplements...", self)
        manage_supp_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        manage_supp_action.triggered.connect(self._manage_supplements)
        supp_menu.addAction(manage_supp_action)

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
        self._supplements = self._storage.load_supplements()

        self._sidebar.set_workout_dates(list(workout_dates))
        self._sidebar.set_goal_dates([g.target_date for g in self._goals])

        self._refresh_stats()
        self._refresh_goals()
        self._refresh_workout()
        self._workout_panel.set_chart_data(self._workouts, self._goals)

    def _refresh_stats(self) -> None:
        streak = consistency_streak(self._workouts)
        total_vol = sum(w.total_volume for w in self._workouts)
        self._sidebar.set_stats(streak, len(self._workouts), total_vol)

    def _refresh_workout(self) -> None:
        selected = self._sidebar.selected_date
        existing = next((w for w in self._workouts if w.date == selected), None)
        self._workout_panel.show_workout(selected, existing)

    def _refresh_goals(self) -> None:
        self._goals_panel.set_goals(self._goals)

    def _on_date_selected(self, d: date) -> None:
        self._refresh_workout()

    def _delete_workout(self, d: date | object) -> None:
        if not isinstance(d, date):
            return
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
            self._sidebar.set_workout_dates(self._storage.list_workout_dates())
            self._refresh_stats()
            self._refresh_workout()
            self._workout_panel.set_chart_data(self._workouts, self._goals)
            self._status_bar.showMessage(f"Deleted {d.isoformat()}", 5000)

    def _log_workout(self, d: date | None = None) -> None:
        if d is None:
            d = self._sidebar.selected_date
        if not isinstance(d, date):
            return
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
                self._sidebar.set_workout_dates(self._storage.list_workout_dates())
                self._refresh_stats()
                self._refresh_workout()
                self._workout_panel.set_chart_data(self._workouts, self._goals)
                self._status_bar.showMessage(f"Saved {d.isoformat()}", 5000)

    def _new_goal(self) -> None:
        dialog = GoalDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            goal = dialog.get_goal()
            if goal:
                self._storage.save_goal(goal)
                self._goals.append(goal)
                self._sidebar.set_goal_dates([g.target_date for g in self._goals])
                self._refresh_goals()
                self._workout_panel.set_chart_data(self._workouts, self._goals)
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
                self._refresh_goals()
                self._workout_panel.set_chart_data(self._workouts, self._goals)
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
            self._refresh_goals()
            self._workout_panel.set_chart_data(self._workouts, self._goals)
            self._status_bar.showMessage(f"Deleted: {goal.name}", 5000)

    def _load_template(self) -> None:
        dialog = TemplateDialog(self._storage, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template = dialog.get_template()
            if template:
                selected = self._sidebar.selected_date
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
                        self._sidebar.set_workout_dates(
                            self._storage.list_workout_dates()
                        )
                        self._refresh_stats()
                        self._refresh_workout()
                        self._workout_panel.set_chart_data(self._workouts, self._goals)
                        self._status_bar.showMessage(
                            f"Loaded template: {template.name}", 5000
                        )

    def _save_as_template(self, workout: Workout) -> None:
        template = WorkoutTemplate(
            name=f"{workout.split_day or 'Workout'} \u2014 {workout.date.strftime('%b %d')}",
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

    def _open_ai_chat(self) -> None:
        config = get_config()
        if not config.ai_enabled:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "AI Not Enabled",
                "Enable AI in Settings to use the coach.",
            )
            return
        dialog = AIChatDialog(self._workouts, self._goals, parent=self)
        dialog.exec()

    def _go_to_today(self) -> None:
        self._sidebar.go_to_today()

    def _init_dbus(self) -> None:
        self._dbus = DBusService(self._supplements, self)

    def _manage_supplements(self) -> None:
        dialog = SupplementDialog(self._supplements, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_list = dialog.get_supplements()
            new_ids = {s.supplement_id for s in new_list}
            for s in self._supplements:
                if s.supplement_id not in new_ids:
                    self._storage.delete_supplement(s.supplement_id)
            self._supplements = new_list
            for s in self._supplements:
                self._storage.save_supplement(s)
            self._dbus.supplements = self._supplements
            self._status_bar.showMessage(
                f"{len(self._supplements)} supplements saved", 5000
            )

    def _init_notifications(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon = _create_tray_icon()
        self._tray_icon = QSystemTrayIcon(icon, self)
        self._tray_icon.setToolTip("GymBuddy")
        self._tray_icon.show()
        self._check_supplements()
        self._notification_timer = QTimer(self)
        self._notification_timer.setInterval(300_000)
        self._notification_timer.timeout.connect(self._check_supplements)
        self._notification_timer.start()

    def _check_supplements(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        due = [
            s
            for s in self._supplements
            if s.enabled and s.is_due_today and not s.is_taken_today
        ]
        if due:
            names = "\n".join(f"  \u2022 {s.name} ({s.dosage})" for s in due)
            self._tray_icon.showMessage(
                "Supplement Reminder",
                f"Time to take:\n{names}",
                QSystemTrayIcon.MessageIcon.Information,
                10000,
            )

    def _show_settings(self) -> None:
        from PyQt6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDialogButtonBox,
            QFormLayout,
            QLineEdit,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(480)

        layout = QFormLayout(dialog)

        vault_path = QLineEdit(self._config.vault_path)
        vault_path.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(80)

        def _browse_vault() -> None:
            path = QFileDialog.getExistingDirectory(
                dialog, "Select Obsidian Vault", self._config.vault_path
            )
            if path:
                vault_path.setText(path)

        browse_btn.clicked.connect(_browse_vault)

        vault_layout = QHBoxLayout()
        vault_layout.addWidget(vault_path, 1)
        vault_layout.addWidget(browse_btn)
        vault_widget = QWidget()
        vault_widget.setLayout(vault_layout)
        layout.addRow("Vault Path:", vault_widget)

        units = QComboBox()
        units.addItems(["metric", "imperial"])
        units.setCurrentText(self._config.units)
        layout.addRow("Units:", units)

        split = QLineEdit(self._config.default_split)
        layout.addRow("Default Split:", split)

        layout.addRow(QLabel(""))  # spacer

        ai_enabled = QCheckBox("Enable AI Coach")
        ai_enabled.setChecked(self._config.ai_enabled)
        layout.addRow(ai_enabled)

        ai_provider = QComboBox()
        ai_provider.addItems(["openai", "ollama", "local"])
        ai_provider.setCurrentText(self._config.ai_provider)
        ai_provider.setEnabled(self._config.ai_enabled)
        layout.addRow("Provider:", ai_provider)

        ai_base_url = QLineEdit(self._config.ai_base_url)
        ai_base_url.setPlaceholderText("https://api.openai.com/v1")
        ai_base_url.setEnabled(self._config.ai_enabled)
        layout.addRow("Base URL:", ai_base_url)

        ai_model = QLineEdit(self._config.ai_model)
        ai_model.setPlaceholderText("gpt-4o-mini")
        ai_model.setEnabled(self._config.ai_enabled)
        layout.addRow("Model:", ai_model)

        ai_api_key = QLineEdit(self._config.ai_api_key)
        ai_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai_api_key.setPlaceholderText("API key (or leave blank for Ollama)")
        ai_api_key.setEnabled(self._config.ai_enabled)
        layout.addRow("API Key:", ai_key := ai_api_key)

        ai_notes_folder = QLineEdit(self._config.ai_notes_folder)
        ai_notes_folder.setPlaceholderText("AI-Notes")
        ai_notes_folder.setEnabled(self._config.ai_enabled)
        layout.addRow("Notes Folder:", ai_notes_folder)

        def _toggle_ai_fields(checked: bool) -> None:
            ai_provider.setEnabled(checked)
            ai_base_url.setEnabled(checked)
            ai_model.setEnabled(checked)
            ai_key.setEnabled(checked)
            ai_notes_folder.setEnabled(checked)

        ai_enabled.toggled.connect(_toggle_ai_fields)

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
            self._config.ai_enabled = ai_enabled.isChecked()
            self._config.ai_provider = cast(
                Literal["openai", "ollama", "local"],
                ai_provider.currentText(),
            )
            self._config.ai_base_url = ai_base_url.text()
            self._config.ai_model = ai_model.text()
            self._config.ai_api_key = ai_api_key.text()
            self._config.ai_notes_folder = ai_notes_folder.text()
            save_config(self._config)
            self._storage = VaultStorage()
            self._load_data()
            self._status_bar.showMessage("Settings saved", 5000)
