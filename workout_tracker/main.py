"""Workout Tracker - Entry point."""

import sys

from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Workout Tracker")
    app.setOrganizationName("workout-tracker")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
