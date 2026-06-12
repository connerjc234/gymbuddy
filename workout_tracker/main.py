"""GymBuddy - Workout Tracker."""

import sys

from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.theme import register_fonts


def main() -> None:
    register_fonts()

    app = QApplication(sys.argv)
    app.setApplicationName("GymBuddy")
    app.setOrganizationName("gymbuddy")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
