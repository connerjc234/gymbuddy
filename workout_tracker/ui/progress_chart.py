
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..core.models import Goal, Workout


class ProgressChart(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workouts: list[Workout] = []
        self._goals: list[Goal] = []
        self._min_height = 200
        self.setMinimumHeight(self._min_height)

    def set_data(self, workouts: list[Workout], goals: list[Goal]) -> None:
        self._workouts = workouts
        self._goals = goals
        self.update()

    def paintEvent(self, event: object) -> None:
        if not self._workouts:
            painter = QPainter(self)
            painter.setPen(QColor("#6c7086"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "No workout data yet")
            painter.end()
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 50
        chart_w = w - 2 * margin
        chart_h = h - 2 * margin

        # sort by date
        workouts = sorted(self._workouts, key=lambda wo: wo.date)
        dates = [wo.date for wo in workouts]
        volumes = [wo.total_volume for wo in workouts]

        if not volumes:
            painter.end()
            return

        max_vol = max(volumes) * 1.1
        if max_vol == 0:
            painter.end()
            return

        # draw grid lines
        painter.setPen(QPen(QColor("#313244"), 1))
        num_grid = 4
        for i in range(num_grid + 1):
            y = margin + chart_h - (chart_h * i / num_grid)
            painter.drawLine(QPointF(margin, y), QPointF(w - margin, y))

            val = max_vol * i / num_grid
            painter.setPen(QColor("#a6adc8"))
            painter.drawText(QRectF(0, y - 8, margin - 8, 16),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             f"{val:.0f}")
            painter.setPen(QPen(QColor("#313244"), 1))

        # draw volume bars
        bar_count = len(dates)
        if bar_count == 1:
            bar_w = chart_w * 0.6
        else:
            bar_w = min(chart_w / bar_count * 0.7, 40)

        for i, (d, vol) in enumerate(zip(dates, volumes)):
            x = margin + (chart_w / max(bar_count, 1)) * i + (chart_w / max(bar_count, 1) - bar_w) / 2
            bar_h = (vol / max_vol) * chart_h
            y = margin + chart_h - bar_h

            color = QColor("#89b4fa")
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 3, 3)

            # date label
            painter.setPen(QColor("#a6adc8"))
            font = painter.font()
            font.setPointSize(7)
            painter.setFont(font)
            rect = QRectF(x - 15, margin + chart_h + 4, bar_w + 30, 16)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter,
                             d.strftime("%m/%d"))

        # draw goal line if there are goals
        for goal in self._goals:
            if goal.metric.value not in ("weight", "volume"):
                continue
            if not goal.target_date:
                continue

            goal_y = margin + chart_h - (goal.target_value / max_vol) * chart_h
            painter.setPen(QPen(QColor("#a6e3a1"), 2, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(margin, goal_y), QPointF(w - margin, goal_y))

            painter.setPen(QColor("#a6e3a1"))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(QRectF(w - margin - 100, goal_y - 16, 100, 16),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                             f"Goal: {goal.target_value:.0f}")

        # labels
        painter.setPen(QColor("#a6adc8"))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(QRectF(margin + 8, 8, 200, 20),
                         Qt.AlignmentFlag.AlignLeft,
                         "Volume (kg)")
        painter.drawText(QRectF(margin, margin + chart_h, chart_w, 20),
                         Qt.AlignmentFlag.AlignCenter,
                         "Date")

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
