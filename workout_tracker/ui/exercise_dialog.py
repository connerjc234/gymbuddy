from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ExerciseLibraryDialog(QDialog):
    def __init__(self, exercises: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._exercises = sorted(set(exercises))
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Exercise Library")
        self.setMinimumSize(400, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QLabel("Exercise Library")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        add_layout = QHBoxLayout()
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("New exercise name...")
        add_layout.addWidget(self._name_input, 1)
        add_btn = QPushButton("Add")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self._add_exercise)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        self._list = QListWidget()
        self._list.addItems(self._exercises)
        layout.addWidget(self._list, 1)

        remove_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setObjectName("dangerButton")
        remove_btn.clicked.connect(self._remove_selected)
        remove_layout.addWidget(remove_btn)
        remove_layout.addStretch()
        layout.addLayout(remove_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Library")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _add_exercise(self) -> None:
        name = self._name_input.text().strip()
        if not name:
            return
        items = [self._list.item(i).text() for i in range(self._list.count())]
        if name not in items:
            self._list.addItem(name)
            self._name_input.clear()
            self._name_input.setFocus()

    def _remove_selected(self) -> None:
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))

    def _save(self) -> None:
        self._exercises = [self._list.item(i).text() for i in range(self._list.count())]
        self.accept()

    def get_exercises(self) -> list[str]:
        return sorted(self._exercises)
