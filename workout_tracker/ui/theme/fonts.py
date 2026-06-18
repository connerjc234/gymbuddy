"""Font registration for GymBuddy.

Searches for font files in:
  1. Bundled AppImage path (<AppDir>/usr/share/fonts/gymbuddy/)
  2. PyInstaller bundle path (<exe_root>/fonts/)
  3. Dev path (<project_root>/.fonts/)
  4. User install (~/.fonts/)
"""

import os
import sys

from PyQt6.QtGui import QFontDatabase


def register_fonts() -> None:
    for name in [
        "Oswald-Variable.ttf",
        "SourceSans3-Variable.ttf",
        "PlayfairDisplay-Variable.ttf",
    ]:
        paths: list[str] = [
            # bundled in AppImage: <AppDir>/usr/share/fonts/gymbuddy/<name>
            str(__file__).rsplit("/usr/lib/", 1)[0]
            + "/usr/share/fonts/gymbuddy/"
            + name,
            # PyInstaller: <sys._MEIPASS>/fonts/<name>
            os.path.join(getattr(sys, "_MEIPASS", ""), "fonts", name),
            # dev: <project_root>/.fonts/<name>
            # __file__ is at workout_tracker/ui/theme/fonts.py → go up 4 levels
            str(__file__).rsplit("/", 4)[0] + "/.fonts/" + name,
            # user install: ~/.fonts/<name>
            os.path.expanduser(f"~/.fonts/{name}"),
        ]
        for p in paths:
            if p and os.path.exists(p):
                QFontDatabase.addApplicationFont(p)
                break
