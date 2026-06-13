"""GymBuddy - Workout Tracker."""

import sys

from PyQt6.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("GymBuddy")
    app.setOrganizationName("gymbuddy")

    from .core.ai_client import set_ai_client
    from .core.config import get_config

    config = get_config()
    if config.ai_enabled and config.ai_provider in ("openai", "ollama", "local"):
        from .core.openai_client import OpenAICompatibleClient

        set_ai_client(OpenAICompatibleClient())

    from .ui.theme import register_fonts

    register_fonts()

    from .ui.main_window import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
