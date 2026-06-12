from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.models import Goal, GoalMetric


class GoalDialog(QDialog):
    def __init__(
        self, existing: Goal | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._goal = existing
        self._setup_ui()

        if existing:
            self._load_goal(existing)

    def _setup_ui(self) -> None:
        self.setWindowTitle("New Goal" if not self._goal else "Edit Goal")
        self.setMinimumSize(450, 350)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("New Goal" if not self._goal else "Edit Goal")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        layout.addWidget(QLabel("Goal Name:"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("e.g., Bench 225x5, Bodyweight 180")
        layout.addWidget(self._name_input)

        metric_layout = QHBoxLayout()
        metric_layout.addWidget(QLabel("Metric:"))
        self._metric_combo = QComboBox()
        for m in GoalMetric:
            self._metric_combo.addItem(m.value)
        self._metric_combo.currentTextChanged.connect(self._on_metric_changed)
        metric_layout.addWidget(self._metric_combo)

        metric_layout.addWidget(QLabel("Exercise (optional):"))
        self._exercise_input = QLineEdit()
        self._exercise_input.setPlaceholderText("e.g., Bench Press")
        metric_layout.addWidget(self._exercise_input, 1)
        layout.addLayout(metric_layout)

        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Target Value:"))
        self._target_spin = QDoubleSpinBox()
        self._target_spin.setRange(0, 10000)
        self._target_spin.setDecimals(1)
        self._target_spin.setSingleStep(2.5)
        self._target_spin.setSuffix(" kg")
        self._target_spin.setValue(100)
        value_layout.addWidget(self._target_spin)

        value_layout.addWidget(QLabel("Current Value:"))
        self._current_spin = QDoubleSpinBox()
        self._current_spin.setRange(0, 10000)
        self._current_spin.setDecimals(1)
        self._current_spin.setSingleStep(2.5)
        self._current_spin.setSuffix(" kg")
        value_layout.addWidget(self._current_spin)
        layout.addLayout(value_layout)

        layout.addWidget(QLabel("Target Date:"))
        self._date_input = QDateEdit()
        self._date_input.setDate(QDate(2026, 8, 15))  # Summer goal deadline
        self._date_input.setCalendarPopup(True)
        self._date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self._date_input)

        layout.addWidget(QLabel("Notes:"))
        self._notes_edit = QTextEdit()
        self._notes_edit.setMaximumHeight(80)
        self._notes_edit.setPlaceholderText("Any notes about this goal...")
        layout.addWidget(self._notes_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Goal")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _load_goal(self, goal: Goal) -> None:
        self._name_input.setText(goal.name)
        idx = self._metric_combo.findText(goal.metric.value)
        if idx >= 0:
            self._metric_combo.setCurrentIndex(idx)
        if goal.exercise_name:
            self._exercise_input.setText(goal.exercise_name)
        self._target_spin.setValue(goal.target_value)
        self._current_spin.setValue(goal.current_value)
        self._date_input.setDate(
            QDate(goal.target_date.year, goal.target_date.month, goal.target_date.day)
        )
        self._notes_edit.setText(goal.notes)

    def _on_metric_changed(self, metric: str) -> None:
        suffix_map = {
            "weight": " kg",
            "reps": " reps",
            "volume": " kg",
            "bodyweight": " kg",
            "consistency": " days",
        }
        suffix = suffix_map.get(metric, "")
        self._target_spin.setSuffix(suffix)
        self._current_spin.setSuffix(suffix)

    def _save(self) -> None:
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Enter a name for your goal.")
            return

        metric = GoalMetric(self._metric_combo.currentText())
        qdate = self._date_input.date()

        self._goal = Goal(
            name=name,
            target_date=date(qdate.year(), qdate.month(), qdate.day()),
            metric=metric,
            target_value=self._target_spin.value(),
            current_value=self._current_spin.value(),
            exercise_name=self._exercise_input.text().strip() or None,
            notes=self._notes_edit.toPlainText().strip(),
        )
        self.accept()

    def get_goal(self) -> Goal | None:
        return self._goal
