DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 13px;
}

QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
}

QMenuBar::item:selected {
    background-color: #45475a;
}

QMenu {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
}

QMenu::item:selected {
    background-color: #45475a;
}

QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #585b70;
    border-color: #6c7086;
}

QPushButton:pressed {
    background-color: #313244;
}

QPushButton:disabled {
    background-color: #313244;
    color: #6c7086;
}

QPushButton#primaryButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #74c7ec;
}

QPushButton#dangerButton {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #eba0ac;
}

QPushButton#goalButton {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: none;
}

QPushButton#goalButton:hover {
    background-color: #94e2d5;
}

QLabel {
    color: #cdd6f4;
    background-color: transparent;
}

QLabel#headerLabel {
    font-size: 20px;
    font-weight: 700;
    color: #cba6f7;
}

QLabel#subsectionLabel {
    font-size: 15px;
    font-weight: 600;
    color: #89b4fa;
}

QLabel#goalValue {
    font-size: 28px;
    font-weight: 700;
    color: #a6e3a1;
}

QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #89b4fa;
}

QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 13px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #89b4fa;
}

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QComboBox:focus {
    border-color: #89b4fa;
}

QComboBox::drop-down {
    border: none;
    background: transparent;
}

QComboBox QAbstractItemView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    selection-background-color: #45475a;
}

QTextEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
    font-size: 13px;
}

QTextEdit:focus {
    border-color: #89b4fa;
}

QTableWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    gridline-color: #313244;
}

QTableWidget::item {
    padding: 4px 8px;
}

QTableWidget::item:selected {
    background-color: #45475a;
}

QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    border: none;
    border-bottom: 1px solid #313244;
    padding: 6px;
    font-weight: 600;
}

QScrollBar:vertical {
    background: #181825;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #181825;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QTabWidget::pane {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    border: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-weight: 600;
}

QTabBar::tab:hover {
    background-color: #313244;
}

QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 4px;
    height: 12px;
    text-align: center;
    color: #cdd6f4;
}

QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 4px;
}

QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #89b4fa;
}

QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #585b70;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QDateEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
}

QDateEdit:focus {
    border-color: #89b4fa;
}

QCalendarWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QCalendarWidget QToolButton {
    color: #cdd6f4;
    background-color: #313244;
    border: none;
    border-radius: 4px;
    padding: 4px 12px;
}

QCalendarWidget QToolButton:hover {
    background-color: #45475a;
}

QCalendarWidget QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: none;
}
"""

LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #f5f5f5;
    color: #1e1e2e;
}

QWidget {
    background-color: #f5f5f5;
    color: #1e1e2e;
}
"""


def get_stylesheet(theme: str = "dark") -> str:
    if theme == "light":
        return LIGHT_STYLESHEET
    return DARK_STYLESHEET
