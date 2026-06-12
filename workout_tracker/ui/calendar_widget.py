from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


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

        nav = QHBoxLayout()
        self._prev_btn = QPushButton("◀")
        self._prev_btn.setFixedWidth(36)
        self._prev_btn.clicked.connect(self._prev_month)

        self._month_label = QLabel()
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._month_label.setStyleSheet("font-size: 14px; font-weight: 600;")

        self._next_btn = QPushButton("▶")
        self._next_btn.setFixedWidth(36)
        self._next_btn.clicked.connect(self._next_month)

        nav.addWidget(self._prev_btn)
        nav.addWidget(self._month_label, 1)
        nav.addWidget(self._next_btn)
        layout.addLayout(nav)

        self._grid = QGridLayout()
        self._grid.setSpacing(2)
        layout.addLayout(self._grid)

        self._update_calendar()

    def _update_calendar(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._month_label.setText(self._current_date.strftime("%B %Y"))

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                "font-size: 11px; color: #a6adc8; font-weight: 600; padding: 2px;"
            )
            self._grid.addWidget(label, 0, i)

        first_day = date(self._current_date.year, self._current_date.month, 1)
        last_day = date(
            self._current_date.year + 1
            if self._current_date.month == 12
            else self._current_date.year,
            self._current_date.month % 12 + 1,
            1,
        )
        from datetime import timedelta

        last_day -= timedelta(days=1)

        start_col = (first_day.weekday()) % 7
        row = 1
        col = start_col

        for day_num in range(1, last_day.day + 1):
            d = date(self._current_date.year, self._current_date.month, day_num)
            btn = DayButton(str(day_num), d)
            btn.setFixedSize(36, 32)
            btn.setStyleSheet(self._day_style(d))

            btn.clicked.connect(lambda checked, dt=d: self._on_day_clicked(dt))
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

        bg = "#313244"
        if is_selected:
            bg = "#89b4fa"
        elif is_today:
            bg = "#45475a"

        border = "none"
        if has_goal and has_workout:
            border = "2px solid #a6e3a1"
        elif has_goal:
            border = "2px solid #f9e2af"
        elif has_workout:
            border = "2px solid #89b4fa"

        color = "#cdd6f4"
        if is_selected:
            color = "#1e1e2e"

        return f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: {border};
                border-radius: 4px;
                font-size: 12px;
                font-weight: {"700" if is_today or is_selected else "400"};
            }}
            QPushButton:hover {{
                background-color: #585b70;
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
