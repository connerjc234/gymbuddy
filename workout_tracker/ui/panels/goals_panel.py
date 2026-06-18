"""Goals display panel with goal cards."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...core.models import Goal
from ..theme import FONT_DISPLAY


class GoalCard(QFrame):
    """Card showing a single goal's progress."""

    editRequested = pyqtSignal(object)  # Goal
    deleteRequested = pyqtSignal(object)  # Goal

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


class GoalsPanel(QWidget):
    """Scrollable list of goal cards."""

    edit_requested = pyqtSignal(object)  # Goal
    delete_requested = pyqtSignal(object)  # Goal

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        header = QLabel("Active Goals")
        header.setObjectName("subsectionLabel")
        layout.addWidget(header)

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
        layout.addWidget(self._goals_scroll, 1)

    # ── Public API ──

    def set_goals(self, goals: list[Goal]) -> None:
        """Render goal cards from the provided list."""
        self._clear_layout(self._goals_container_layout)

        if not goals:
            placeholder = QLabel("No goals yet. Set one to track progress!")
            placeholder.setStyleSheet("color: #a39b8e; padding: 12px; font-size: 12px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._goals_container_layout.addWidget(placeholder)
        else:
            active = [g for g in goals if not g.is_complete]
            active.sort(key=lambda g: g.target_date)
            for goal in active[:5]:
                card = GoalCard(goal)
                card.editRequested.connect(self.edit_requested.emit)
                card.deleteRequested.connect(self.delete_requested.emit)
                self._goals_container_layout.addWidget(card)

        self._goals_container_layout.addStretch()

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
