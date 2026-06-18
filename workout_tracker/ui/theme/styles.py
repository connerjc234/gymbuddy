"""Stylesheet for the GymBuddy warm editorial theme."""

from .colors import FONT_BODY, FONT_DISPLAY

# ── Root styles ──

ROOT = """
QMainWindow, QDialog, QWidget {
    background-color: #f5f2ec;
    color: #1a1612;
    font-family: 'Source Sans 3', 'Cantarell', sans-serif;
    font-size: 13px;
}
"""


def h1(size: int = 22) -> str:
    return f"""
    font-family: '{FONT_DISPLAY}';
    font-weight: 700;
    font-size: {size}px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #1a1612;
    """


def h2(size: int = 15) -> str:
    return f"""
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
    font-size: {size}px;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    color: #1a1612;
    """


def body_small() -> str:
    return """
    font-family: 'Source Sans 3', sans-serif;
    font-size: 12px;
    color: #7a7265;
    """


def body_compact() -> str:
    return """
    font-family: 'Source Sans 3', sans-serif;
    font-size: 12px;
    color: #7a7265;
    """


# ── Full stylesheet ──

STYLESHEET = f"""
{ROOT}

/* ── BUTTONS ── */
QPushButton {{
    background-color: transparent;
    color: #1a1612;
    border: 1.5px solid #e3ddd4;
    border-radius: 8px;
    padding: 7px 18px;
    font-family: '{FONT_BODY}';
    font-size: 13px;
    font-weight: 600;
}}

QPushButton:hover {{
    border-color: #c9c0b4;
    background-color: #ece8e0;
}}

QPushButton:pressed {{
    background-color: #e3ddd4;
}}

QPushButton:disabled {{
    color: #c9c0b4;
    border-color: #ece8e0;
}}

QPushButton#primaryButton {{
    background-color: #d64550;
    color: #ffffff;
    border: none;
    font-weight: 700;
    font-family: '{FONT_BODY}';
    font-size: 13px;
    padding: 8px 22px;
}}

QPushButton#primaryButton:hover {{
    background-color: #b73842;
}}

QPushButton#primaryButton:pressed {{
    background-color: #a32e38;
}}

QPushButton#dangerButton {{
    color: #d64550;
    border-color: #f0c8c8;
}}

QPushButton#dangerButton:hover {{
    background-color: #fce8e8;
    border-color: #d64550;
}}

QPushButton#goalButton {{
    color: #4a7c5b;
    border-color: #c8dfd0;
}}

QPushButton#goalButton:hover {{
    background-color: #edf5ef;
    border-color: #4a7c5b;
}}

QPushButton#secondaryButton {{
    color: #7a7265;
    border-color: #e3ddd4;
    font-weight: 600;
}}

QPushButton#secondaryButton:hover {{
    background-color: #ece8e0;
    border-color: #c9c0b4;
}}

/* ── LABELS ── */
QLabel {{
    background: transparent;
    color: #1a1612;
    font-family: '{FONT_BODY}';
}}

QLabel#headerLabel {{
    font-family: '{FONT_DISPLAY}';
    font-weight: 700;
    font-size: 22px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #1a1612;
}}

QLabel#subsectionLabel {{
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
    font-size: 15px;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    color: #7a7265;
}}

QLabel#goalValue {{
    font-family: '{FONT_DISPLAY}';
    font-weight: 700;
    font-size: 28px;
    color: #4a7c5b;
}}

QLabel#statValue {{
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
    font-size: 18px;
    color: #1a1612;
}}

QLabel#statLabel {{
    font-family: '{FONT_BODY}';
    font-size: 11px;
    color: #a39b8e;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── INPUTS ── */
QLineEdit, QTextEdit {{
    background-color: #ffffff;
    color: #1a1612;
    border: 1.5px solid #e3ddd4;
    border-radius: 8px;
    padding: 8px 12px;
    font-family: '{FONT_BODY}';
    font-size: 13px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: #d64550;
    background-color: #ffffff;
}}

QLineEdit::placeholder, QTextEdit::placeholder {{
    color: #c9c0b4;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: #ffffff;
    color: #1a1612;
    border: 1.5px solid #e3ddd4;
    border-radius: 8px;
    padding: 6px 10px;
    font-family: '{FONT_BODY}';
    font-size: 13px;
    font-weight: 600;
    min-height: 22px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #d64550;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    border: none;
    background: transparent;
    width: 0;
}}

QComboBox {{
    background-color: #ffffff;
    color: #1a1612;
    border: 1.5px solid #e3ddd4;
    border-radius: 8px;
    padding: 8px 12px;
    font-family: '{FONT_BODY}';
    font-size: 13px;
    min-width: 100px;
}}

QComboBox:focus {{
    border-color: #d64550;
}}

QComboBox::drop-down {{
    border: none;
    background: transparent;
    width: 28px;
}}

QComboBox::down-arrow {{
    width: 0;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #1a1612;
    border: 1.5px solid #e3ddd4;
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #fce8e8;
    selection-color: #1a1612;
    outline: none;
}}

/* ── TABLES ── */
QTableWidget {{
    background-color: #ffffff;
    color: #1a1612;
    border: 1.5px solid #ece8e0;
    border-radius: 8px;
    gridline-color: #f0ede6;
    font-family: '{FONT_BODY}';
    font-size: 13px;
}}

QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid #f0ede6;
}}

QTableWidget::item:selected {{
    background-color: #fce8e8;
    color: #1a1612;
}}

QHeaderView::section {{
    background-color: #f5f2ec;
    color: #7a7265;
    border: none;
    border-bottom: 1.5px solid #e3ddd4;
    padding: 8px 10px;
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── SCROLLBARS ── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #d9d3c8;
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: #c9c0b4;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
}}

QScrollBar::handle:horizontal {{
    background: #d9d3c8;
    border-radius: 3px;
    min-width: 30px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── TABS ── */
QTabWidget::pane {{
    background-color: #ffffff;
    border: 1.5px solid #ece8e0;
    border-radius: 8px;
    border-top-left-radius: 0;
}}

QTabBar::tab {{
    background-color: transparent;
    color: #a39b8e;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 18px;
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}}

QTabBar::tab:selected {{
    color: #d64550;
    border-bottom-color: #d64550;
}}

QTabBar::tab:hover {{
    color: #1a1612;
}}

/* ── PROGRESS BAR ── */
QProgressBar {{
    background-color: #ece8e0;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background-color: #d64550;
    border-radius: 4px;
}}

/* ── GROUP BOX ── */
QGroupBox {{
    border: none;
    border-top: 1.5px solid #e3ddd4;
    margin-top: 16px;
    padding-top: 14px;
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    color: #7a7265;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px 0 0;
    color: #7a7265;
}}

/* ── CHECKBOX ── */
QCheckBox {{
    spacing: 8px;
    font-family: '{FONT_BODY}';
    font-size: 12px;
    color: #1a1612;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid #d9d3c8;
    border-radius: 4px;
    background-color: #ffffff;
}}

QCheckBox::indicator:checked {{
    background-color: #d64550;
    border-color: #d64550;
}}

/* ── CALENDAR ── */
QCalendarWidget {{
    background-color: transparent;
    color: #1a1612;
}}

QCalendarWidget QToolButton {{
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
    font-size: 13px;
    color: #1a1612;
    background: transparent;
    border: none;
    padding: 4px 12px;
    text-transform: uppercase;
}}

QCalendarWidget QToolButton:hover {{
    color: #d64550;
}}

QCalendarWidget QSpinBox {{
    background: transparent;
    border: none;
    font-family: '{FONT_DISPLAY}';
    font-weight: 600;
}}

/* ── SCROLL AREA ── */
QScrollArea {{
    border: none;
    background: transparent;
}}

/* ── STATUSBAR ── */
QStatusBar {{
    background: #ece8e0;
    color: #7a7265;
    font-size: 11px;
    border-top: 1px solid #e3ddd4;
}}

/* ── MENUBAR ── */
QMenuBar {{
    background: #ffffff;
    color: #1a1612;
    border-bottom: 1px solid #ece8e0;
    padding: 2px 8px;
    font-family: '{FONT_BODY}';
    font-size: 12px;
}}

QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background: #f5f2ec;
}}

QMenu {{
    background: #ffffff;
    color: #1a1612;
    border: 1px solid #e3ddd4;
    border-radius: 8px;
    padding: 6px;
}}

QMenu::item {{
    padding: 6px 28px 6px 14px;
    border-radius: 4px;
    font-family: '{FONT_BODY}';
    font-size: 12px;
}}

QMenu::item:selected {{
    background: #f5f2ec;
    color: #1a1612;
}}

QMenu::separator {{
    height: 1px;
    background: #ece8e0;
    margin: 4px 8px;
}}

/* ── LIST WIDGET ── */
QListWidget {{
    background-color: #ffffff;
    border: 1.5px solid #ece8e0;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 8px 12px;
    border-radius: 6px;
    font-family: '{FONT_BODY}';
    font-size: 13px;
}}

QListWidget::item:selected {{
    background-color: #fce8e8;
    color: #1a1612;
}}

QListWidget::item:hover {{
    background-color: #f5f2ec;
}}

/* ── SPLITTER ── */
QSplitter::handle {{
    background: #ece8e0;
    width: 1px;
}}
"""

CARD_STYLE = """
    QFrame#workoutCard, QFrame#goalCard {
        background-color: #ffffff;
        border: 1.5px solid #ece8e0;
        border-radius: 12px;
        padding: 16px;
    }
    QFrame#workoutCard:hover, QFrame#goalCard:hover {
        border-color: #d9d3c8;
    }
"""

STAT_CARD = """
    QFrame#statCard {
        background-color: #ffffff;
        border: 1.5px solid #ece8e0;
        border-radius: 10px;
        padding: 12px 16px;
    }
"""


def get_stylesheet(theme: str = "warm") -> str:
    return STYLESHEET
