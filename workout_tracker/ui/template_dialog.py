from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.models import WorkoutTemplate
from ..core.storage import VaultStorage


class TemplateDialog(QDialog):
    def __init__(self, storage: VaultStorage, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._storage = storage
        self._selected_template: WorkoutTemplate | None = None
        self._setup_ui()
        self._load_templates()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Workout Templates")
        self.setMinimumSize(500, 450)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Workout Templates")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        sub = QLabel("Load a saved template to quickly start a workout")
        sub.setStyleSheet("color: #7a7265; font-size: 12px; margin-top: -6px;")
        layout.addWidget(sub)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._accept_template)
        layout.addWidget(self._list, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        load_btn = QPushButton("Load Template")
        load_btn.setObjectName("primaryButton")
        load_btn.clicked.connect(self._accept_template)
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(load_btn)
        layout.addLayout(btn_layout)

    def _load_templates(self) -> None:
        self._list.clear()
        for name in self._storage.list_templates():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self._list.addItem(item)
        if self._list.count() == 0:
            item = QListWidgetItem(
                "No saved templates — save a workout as a template first"
            )
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self._list.addItem(item)

    def _accept_template(self) -> None:
        current = self._list.currentItem()
        if not current:
            return
        name = current.data(Qt.ItemDataRole.UserRole)
        if not name:
            return
        self._selected_template = self._storage.load_template(name)
        if self._selected_template:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", f"Could not load template '{name}'")

    def _delete_selected(self) -> None:
        current = self._list.currentItem()
        if not current:
            return
        name = current.data(Qt.ItemDataRole.UserRole)
        if not name:
            return
        confirm = QMessageBox.question(
            self,
            "Delete Template",
            f"Delete template '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._storage.delete_template(name)
            self._load_templates()

    def get_template(self) -> WorkoutTemplate | None:
        return self._selected_template


class SaveTemplateDialog(QDialog):
    def __init__(
        self, template: WorkoutTemplate, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._template = template
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Save as Template")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Save as Template")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        layout.addWidget(QLabel("Template Name:"))
        self._name_input = QLineEdit()
        self._name_input.setText(self._template.name)
        self._name_input.selectAll()
        layout.addWidget(self._name_input)

        info = QLabel(
            f"Will save: {len(self._template.exercises)} exercises, "
            f"{sum(len(e.sets) for e in self._template.exercises)} sets"
        )
        info.setStyleSheet("color: #7a7265; font-size: 12px;")
        layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Template")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _save(self) -> None:
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Enter a template name.")
            return
        self._template.name = name
        self.accept()

    def get_template(self) -> WorkoutTemplate:
        return self._template
