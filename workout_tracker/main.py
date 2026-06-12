"""GymBuddy - Workout Tracker."""

import sys

from PyQt6.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("GymBuddy")
    app.setOrganizationName("gymbuddy")

    from .ui.theme import register_fonts
    register_fonts()

    from .ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
