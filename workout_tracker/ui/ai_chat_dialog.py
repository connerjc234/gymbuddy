"""AI Chat dialog for GymBuddy."""

from datetime import datetime

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..core.ai_client import get_ai_client
from ..core.models import Goal, Workout
from ..core.storage import VaultStorage
from .theme import (
    ACCENT_GOLD,
    ACCENT_TERRACOTTA,
    ACCENT_TERRACOTTA_HOVER,
    BG_CARD,
    BG_WARM,
    BORDER_LIGHT,
    FONT_BODY,
    FONT_DISPLAY,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class ChatMessage(QWidget):
    def __init__(self, text: str, is_user: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bubble.setFont(QFont(FONT_BODY, 11))
        if is_user:
            bubble.setStyleSheet(f"""
                background-color: {ACCENT_TERRACOTTA};
                color: #ffffff;
                border: 1.5px solid {ACCENT_TERRACOTTA};
                border-radius: 12px;
                padding: 10px 14px;
            """)
        else:
            bubble.setStyleSheet(f"""
                background-color: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER_LIGHT};
                border-radius: 12px;
                padding: 10px 14px;
            """)
        bubble.setMaximumWidth(500)

        if is_user:
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            layout.addWidget(bubble)
            layout.addStretch()


class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, message: str, history: list[Workout], goals: list[Goal]) -> None:
        super().__init__()
        self._message = message
        self._history = history
        self._goals = goals

    def run(self) -> None:
        try:
            client = get_ai_client()
            if hasattr(client, "chat"):
                response = client.chat(self._message, self._history, self._goals)
            else:
                response = "AI chat not available with current provider."
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class AIChatDialog(QDialog):
    def __init__(
        self, history: list[Workout], goals: list[Goal], parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._history = history
        self._goals = goals
        self._worker: AIWorker | None = None
        self._last_ai_response: str | None = None
        self._storage = VaultStorage()

        self.setWindowTitle("GymBuddy AI Coach")
        self.setMinimumSize(520, 600)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG_WARM}; }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: transparent; width: 8px; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {ACCENT_GOLD}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {ACCENT_GOLD}; }}
        """)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("AI Coach")
        header.setStyleSheet(f"""
            font-family: '{FONT_DISPLAY}'; font-weight: 700; font-size: 20px;
            color: {TEXT_PRIMARY}; letter-spacing: 0.5px; text-transform: uppercase;
        """)
        layout.addWidget(header)

        subtitle = QLabel(
            "Ask about training, programming, form, nutrition, or anything fitness-related."
        )
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(subtitle)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(self._scroll.Shape.NoFrame)
        self._chat_container = QWidget()
        self._chat_container.setStyleSheet("background: transparent;")
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(0, 0, 0, 0)
        self._chat_layout.setSpacing(8)
        self._chat_layout.addStretch()
        self._scroll.setWidget(self._chat_container)
        layout.addWidget(self._scroll, 1)

        self._add_message(
            "Welcome! I have context on your workouts and goals. How can I help?",
            is_user=False,
        )

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask me anything...")
        self._input.setFont(QFont(FONT_BODY, 12))
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_CARD};
                border: 1.5px solid {BORDER_LIGHT};
                border-radius: 8px;
                padding: 10px 14px;
                color: {TEXT_PRIMARY};
                font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT_TERRACOTTA}; }}
        """)
        self._input.returnPressed.connect(self._send_message)
        input_row.addWidget(self._input, 1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setObjectName("primaryButton")
        self._send_btn.setFixedWidth(80)
        self._send_btn.setStyleSheet(f"""
            QPushButton#primaryButton {{
                background-color: {ACCENT_TERRACOTTA}; color: #ffffff;
                border: none; border-radius: 8px; padding: 10px;
                font-weight: 600; font-size: 12px;
            }}
            QPushButton#primaryButton:hover {{ background-color: {ACCENT_TERRACOTTA_HOVER}; }}
            QPushButton#primaryButton:disabled {{ background-color: {ACCENT_TERRACOTTA}80; }}
        """)
        self._send_btn.clicked.connect(self._send_message)
        input_row.addWidget(self._send_btn)

        self._save_note_btn = QPushButton("💾 Save Note")
        self._save_note_btn.setObjectName("secondaryButton")
        self._save_note_btn.setFixedWidth(110)
        self._save_note_btn.setEnabled(False)
        self._save_note_btn.setStyleSheet(f"""
            QPushButton#secondaryButton {{
                color: {TEXT_MUTED};
                border: 1.5px solid {BORDER_LIGHT};
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {BG_CARD};
                border-color: {ACCENT_GOLD};
                color: {TEXT_PRIMARY};
            }}
            QPushButton#secondaryButton:disabled {{
                color: #c9c0b4;
                border-color: #ece8e0;
            }}
        """)
        self._save_note_btn.clicked.connect(self._save_note)
        input_row.addWidget(self._save_note_btn)

        layout.addLayout(input_row)

    def _add_message(self, text: str, is_user: bool) -> None:
        self._chat_layout.insertWidget(
            self._chat_layout.count() - 1, ChatMessage(text, is_user)
        )
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def _send_message(self) -> None:
        text = self._input.text().strip()
        if not text:
            return

        self._add_message(text, is_user=True)
        self._input.clear()
        self._send_btn.setEnabled(False)
        self._send_btn.setText("...")

        self._worker = AIWorker(text, self._history, self._goals)
        self._worker.finished.connect(self._on_response)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_response(self, response: str) -> None:
        self._add_message(response, is_user=False)
        self._last_ai_response = response
        self._save_note_btn.setEnabled(True)
        self._send_btn.setEnabled(True)
        self._send_btn.setText("Send")
        self._worker = None

    def _on_error(self, error: str) -> None:
        self._add_message(f"Error: {error}", is_user=False)
        self._send_btn.setEnabled(True)
        self._send_btn.setText("Send")
        self._worker = None

    def _save_note(self) -> None:
        if not self._last_ai_response:
            return

        from PyQt6.QtWidgets import (
            QDialog,
            QDialogButtonBox,
            QLabel,
            QLineEdit,
            QVBoxLayout,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Save AI Note")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(f"QDialog {{ background-color: {BG_WARM}; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Enter a title for this note:"))

        title_input = QLineEdit()
        title_input.setPlaceholderText(
            "e.g., Deload Week Advice, Programming Tips, etc."
        )
        title_input.setFont(QFont(FONT_BODY, 12))
        title_input.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_CARD};
                border: 1.5px solid {BORDER_LIGHT};
                border-radius: 8px;
                padding: 10px 14px;
                color: {TEXT_PRIMARY};
            }}
            QLineEdit:focus {{ border-color: {ACCENT_TERRACOTTA}; }}
        """)
        layout.addWidget(title_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        buttons.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                border: 1.5px solid {BORDER_LIGHT};
                border-radius: 6px;
                padding: 8px 16px;
                color: {TEXT_PRIMARY};
            }}
            QPushButton:hover {{ border-color: {ACCENT_TERRACOTTA}; }}
        """)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = title_input.text().strip()
            if not title:
                title = f"AI Note {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            try:
                path = self._storage.save_ai_note(title, self._last_ai_response)
                QMessageBox.information(
                    self,
                    "Note Saved",
                    f"Saved to {path.relative_to(self._storage.config.gym_path)}",
                )
                self._save_note_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save note: {e}")
