from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..core.models import Goal, Workout
from .theme import FONT_BODY, FONT_DISPLAY


class ProgressChart(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workouts: list[Workout] = []
        self._goals: list[Goal] = []
        self._min_height = 180
        self.setMinimumHeight(self._min_height)
        self.setStyleSheet("background: transparent;")

    def set_data(self, workouts: list[Workout], goals: list[Goal]) -> None:
        self._workouts = workouts
        self._goals = goals
        self.update()

    def paintEvent(self, event: object) -> None:
        if not self._workouts:
            painter = QPainter(self)
            painter.setPen(QColor("#a39b8e"))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "No workout data yet"
            )
            painter.end()
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin_left = 48
        margin_right = 16
        margin_top = 24
        margin_bottom = 28
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        workouts = sorted(self._workouts, key=lambda wo: wo.date)
        dates = [wo.date for wo in workouts]
        volumes = [wo.total_volume for wo in workouts]

        if not volumes or max(volumes) == 0:
            painter.end()
            return

        max_vol = max(volumes) * 1.15
        bar_count = len(dates)

        # Horizontal grid lines
        num_grid = 3
        for i in range(num_grid + 1):
            y = margin_top + chart_h - (chart_h * i / num_grid)
            painter.setPen(QPen(QColor("#ece8e0"), 1))
            painter.drawLine(QPointF(margin_left, y), QPointF(w - margin_right, y))

            val = max_vol * i / num_grid
            painter.setPen(QColor("#a39b8e"))
            font = painter.font()
            font.setFamilies([FONT_DISPLAY])
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(
                QRectF(0, y - 8, margin_left - 6, 16),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                f"{val:.0f}",
            )

        # Bars
        if bar_count == 1:
            bar_w = chart_w * 0.5
        else:
            bar_w = min(chart_w / bar_count * 0.55, 32)

        for i, (d, vol) in enumerate(zip(dates, volumes)):
            x = (
                margin_left
                + (chart_w / bar_count) * i
                + (chart_w / bar_count - bar_w) / 2
            )
            bar_h = (vol / max_vol) * chart_h
            y = margin_top + chart_h - bar_h

            color = QColor("#d64550")
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 3, 3)

            # Date label
            painter.setPen(QColor("#7a7265"))
            font = painter.font()
            font.setFamilies([FONT_BODY])
            font.setPointSize(7)
            painter.setFont(font)
            rect = QRectF(x - 12, margin_top + chart_h + 4, bar_w + 24, 16)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, d.strftime("%m/%d"))

        # Goal line
        for goal in self._goals:
            if goal.metric.value not in ("weight", "volume"):
                continue
            goal_y = margin_top + chart_h - (goal.target_value / max_vol) * chart_h
            painter.setPen(QPen(QColor("#c4a35a"), 1.5, Qt.PenStyle.DashLine))
            painter.drawLine(
                QPointF(margin_left, goal_y), QPointF(w - margin_right, goal_y)
            )

            painter.setPen(QColor("#c4a35a"))
            font = painter.font()
            font.setFamilies([FONT_BODY])
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(
                QRectF(w - margin_right - 80, goal_y - 16, 80, 16),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                f"goal {goal.target_value:.0f}",
            )

        # Axis labels
        painter.setPen(QColor("#a39b8e"))
        font = painter.font()
        font.setFamilies([FONT_DISPLAY])
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(
            QRectF(margin_left + 4, 4, 120, 16), Qt.AlignmentFlag.AlignLeft, "VOLUME"
        )

        painter.end()


class ProgressChartWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Progress")
        header.setObjectName("subsectionLabel")
        layout.addWidget(header)

        self._chart = ProgressChart()
        layout.addWidget(self._chart, 1)

    def set_data(self, workouts: list[Workout], goals: list[Goal]) -> None:
        self._chart.set_data(workouts, goals)
