from datetime import date, timedelta

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .theme import FONT_DISPLAY


class CalendarWidget(QWidget):
    dateSelected = pyqtSignal(date)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workout_dates: set[date] = set()
        self._goal_dates: set[date] = set()
        self._current_date = date.today()
        self._selected_date = date.today()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Navigation
        nav = QHBoxLayout()
        self._prev_btn = QPushButton("\u25c0")
        self._prev_btn.setFixedSize(32, 30)
        self._prev_btn.setStyleSheet(
            "font-size: 14px; border: none; color: #7a7265; background: transparent;"
        )
        self._prev_btn.clicked.connect(self._prev_month)

        self._month_label = QLabel()
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._month_label.setStyleSheet(
            f"font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 15px; letter-spacing: 0.5px; text-transform: uppercase; color: #1a1612; padding: 4px 0;"
        )
        nav.addWidget(self._prev_btn)
        nav.addWidget(self._month_label, 1)
        self._next_btn = QPushButton("\u25b6")
        self._next_btn.setFixedSize(32, 30)
        self._next_btn.setStyleSheet(
            "font-size: 14px; border: none; color: #7a7265; background: transparent;"
        )
        self._next_btn.clicked.connect(self._next_month)
        nav.addWidget(self._next_btn)
        layout.addLayout(nav)

        self._grid = QGridLayout()
        self._grid.setSpacing(2)
        layout.addLayout(self._grid)
        self._update_calendar()

    def _update_calendar(self) -> None:
        self._clear_grid()

        self._month_label.setText(self._current_date.strftime("%B %Y"))

        days = ["M", "T", "W", "T", "F", "S", "S"]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                f"font-family: '{FONT_DISPLAY}'; font-weight: 600; font-size: 10px; color: #a39b8e; letter-spacing: 0.5px; text-transform: uppercase; padding: 2px;"
            )
            self._grid.addWidget(label, 0, i)

        first_day = date(self._current_date.year, self._current_date.month, 1)
        if self._current_date.month == 12:
            last_day = date(self._current_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(
                self._current_date.year, self._current_date.month + 1, 1
            ) - timedelta(days=1)

        start_col = first_day.weekday()  # Monday=0
        row = 1
        col = start_col

        for day_num in range(1, last_day.day + 1):
            d = date(self._current_date.year, self._current_date.month, day_num)
            btn = DayButton(str(day_num), d)
            btn.setFixedSize(36, 32)
            btn.setStyleSheet(self._day_style(d))

            btn.clicked.connect(lambda checked=False, dt=d: self._on_day_clicked(dt))
            self._grid.addWidget(btn, row, col)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def _day_style(self, d: date) -> str:
        is_today = d == date.today()
        is_selected = d == self._selected_date
        has_workout = d in self._workout_dates
        has_goal = d in self._goal_dates

        if is_selected:
            bg = "#d64550"
            color = "#ffffff"
            border = "none"
        elif is_today:
            bg = "#ffffff"
            color = "#1a1612"
            border = "1.5px solid #d64550"
        else:
            bg = "transparent"
            color = "#7a7265"
            border = "1.5px solid transparent"

        if has_workout and has_goal:
            border = "1.5px solid #c4a35a"
        elif has_goal:
            border = "1.5px solid #c4a35a"
        elif has_workout and not is_selected:
            border = "1.5px solid #d9d3c8"

        fw = "600" if (is_today or is_selected) else "400"

        return f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: {border};
                border-radius: 6px;
                font-family: '{FONT_DISPLAY}';
                font-size: 12px;
                font-weight: {fw};
            }}
            QPushButton:hover {{
                background-color: #ece8e0;
                color: #1a1612;
            }}
        """

    def _on_day_clicked(self, d: date) -> None:
        self._selected_date = d
        self._update_calendar()
        self.dateSelected.emit(d)

    def _prev_month(self) -> None:
        year = self._current_date.year
        month = self._current_date.month - 1
        if month < 1:
            month = 12
            year -= 1
        self._current_date = date(year, month, 1)
        self._update_calendar()

    def _next_month(self) -> None:
        year = self._current_date.year
        month = self._current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        self._current_date = date(year, month, 1)
        self._update_calendar()

    def _clear_grid(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_workout_dates(self, dates: list[date]) -> None:
        self._workout_dates = set(dates)
        self._update_calendar()

    def set_goal_dates(self, goals: list[date]) -> None:
        self._goal_dates = set(goals)
        self._update_calendar()

    @property
    def selected_date(self) -> date:
        return self._selected_date

    def go_to_date(self, d: date) -> None:
        self._current_date = date(d.year, d.month, 1)
        self._selected_date = d
        self._update_calendar()


class DayButton(QPushButton):
    def __init__(
        self, text: str, day_date: date, parent: QWidget | None = None
    ) -> None:
        super().__init__(text, parent)
        self.day_date = day_date
