"""Sidebar panel with calendar, stat cards, and action buttons."""

from datetime import date

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..calendar_widget import CalendarWidget
from ..theme import FONT_DISPLAY


class StatCard(QFrame):
    """Compact stat display card with a large value and small label."""

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

        self._value_label = QLabel(value)
        self._value_label.setStyleSheet(
            f"font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 20px; color: #1a1612; letter-spacing: 0.3px;"
        )
        layout.addWidget(self._value_label)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            "color: #a39b8e; font-size: 10px; letter-spacing: 0.5px; text-transform: uppercase; padding-top: 2px;"
        )
        layout.addWidget(lbl)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)


class SidebarPanel(QWidget):
    """Left sidebar: brand, calendar, stat cards, action buttons."""

    date_selected = pyqtSignal(date)
    new_workout_requested = pyqtSignal()
    new_goal_requested = pyqtSignal()
    supplements_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMaximumWidth(300)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        brand = QLabel("GymBuddy")
        brand.setStyleSheet(
            f"font-family: '{FONT_DISPLAY}'; font-weight: 700; font-size: 26px; letter-spacing: 1px; text-transform: uppercase; color: #1a1612; padding: 4px 0;"
        )
        layout.addWidget(brand)

        self._calendar = CalendarWidget()
        self._calendar.dateSelected.connect(self.date_selected.emit)
        layout.addWidget(self._calendar)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)
        self._streak_card = StatCard("\u2014", "streak")
        stats_row.addWidget(self._streak_card)
        self._total_card = StatCard("\u2014", "workouts")
        stats_row.addWidget(self._total_card)
        self._vol_card = StatCard("\u2014", "volume")
        stats_row.addWidget(self._vol_card)
        layout.addLayout(stats_row)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(6)
        new_workout_btn = QPushButton("+ New Workout")
        new_workout_btn.setObjectName("primaryButton")
        new_workout_btn.clicked.connect(self.new_workout_requested)
        btn_layout.addWidget(new_workout_btn)
        new_goal_btn = QPushButton("+ New Goal")
        new_goal_btn.setObjectName("goalButton")
        new_goal_btn.clicked.connect(self.new_goal_requested)
        btn_layout.addWidget(new_goal_btn)
        supp_btn = QPushButton("Supplements")
        supp_btn.clicked.connect(self.supplements_requested)
        btn_layout.addWidget(supp_btn)
        settings_btn = QPushButton("\u2699 Settings")
        settings_btn.setObjectName("secondaryButton")
        settings_btn.clicked.connect(self.settings_requested)
        btn_layout.addWidget(settings_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

    # ── Public API ──

    @property
    def calendar(self) -> CalendarWidget:
        return self._calendar

    @property
    def selected_date(self) -> date:
        return self._calendar.selected_date

    def set_workout_dates(self, dates: list[date]) -> None:
        self._calendar.set_workout_dates(dates)

    def set_goal_dates(self, dates: list[date]) -> None:
        self._calendar.set_goal_dates(dates)

    def set_stats(self, streak: int, total: int, volume: float) -> None:
        self._streak_card.set_value(str(streak))
        self._total_card.set_value(str(total))
        self._vol_card.set_value(f"{volume:,.0f}")

    def go_to_today(self) -> None:
        from datetime import date

        self._calendar.go_to_date(date.today())
