"""Individual exercise row with set table for workout dialog."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.models import Exercise, Set


class ExerciseRow(QWidget):
    """A single exercise row with name, notes, and sets table."""

    def __init__(
        self,
        exercise_library: list[str],
        weight_suffix: str = " kg",
        exercise: Exercise | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._exercise_library = exercise_library
        self._weight_suffix = weight_suffix
        self._exercise = exercise
        self._setup_ui()
        if exercise:
            self._load_exercise(exercise)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        header = QHBoxLayout()
        self._name_combo = QComboBox()
        self._name_combo.setEditable(True)
        self._name_combo.addItems(sorted(self._exercise_library))
        self._name_combo.setMinimumWidth(190)
        self._name_combo.currentTextChanged.connect(self._on_name_changed)
        header.addWidget(self._name_combo)

        self._notes_input = QLineEdit()
        self._notes_input.setPlaceholderText("Exercise notes...")
        header.addWidget(self._notes_input, 1)

        self._remove_btn = QPushButton("\u2715")
        self._remove_btn.setFixedSize(28, 28)
        self._remove_btn.setObjectName("dangerButton")
        header.addWidget(self._remove_btn)
        layout.addLayout(header)

        self._sets_table = QTableWidget(0, 5)
        self._sets_table.setHorizontalHeaderLabels(
            ["Set", "Weight", "Reps", "RPE", "Warmup"]
        )
        h_header = self._sets_table.horizontalHeader()
        if h_header:
            h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._sets_table.setColumnWidth(0, 40)
        if h_header:
            h_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._sets_table.setColumnWidth(4, 60)
        v_header = self._sets_table.verticalHeader()
        if v_header:
            v_header.setVisible(False)
        layout.addWidget(self._sets_table)

        set_btn_layout = QHBoxLayout()
        add_set_btn = QPushButton("+ Add Set")
        add_set_btn.clicked.connect(self._add_set_row)
        self._add_warmup_btn = QPushButton("+ Warmup")
        self._add_warmup_btn.clicked.connect(lambda: self._add_set_row(is_warmup=True))
        set_btn_layout.addWidget(add_set_btn)
        set_btn_layout.addWidget(self._add_warmup_btn)
        set_btn_layout.addStretch()
        layout.addLayout(set_btn_layout)

    def _on_name_changed(self, name: str) -> None:
        if name:
            self._name_combo.setStyleSheet("")

    def _add_set_row(self, is_warmup: bool = False) -> None:
        row = self._sets_table.rowCount()
        self._sets_table.insertRow(row)

        set_item = QTableWidgetItem(str(row + 1))
        set_item.setFlags(set_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._sets_table.setItem(row, 0, set_item)

        weight = QDoubleSpinBox()
        weight.setRange(0, 999.5)
        weight.setSingleStep(2.5)
        weight.setDecimals(1)
        weight.setSuffix(self._weight_suffix)
        weight.setValue(0)
        self._sets_table.setCellWidget(row, 1, weight)

        reps = QSpinBox()
        reps.setRange(0, 100)
        reps.setValue(10)
        self._sets_table.setCellWidget(row, 2, reps)

        rpe = QDoubleSpinBox()
        rpe.setRange(0, 10)
        rpe.setSingleStep(0.5)
        rpe.setDecimals(1)
        rpe.setValue(7)
        self._sets_table.setCellWidget(row, 3, rpe)

        warmup = QCheckBox()
        warmup.setChecked(is_warmup)
        warmup_widget = QWidget()
        warmup_layout = QHBoxLayout(warmup_widget)
        warmup_layout.addWidget(warmup)
        warmup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warmup_layout.setContentsMargins(0, 0, 0, 0)
        self._sets_table.setCellWidget(row, 4, warmup_widget)

    def _renumber_sets(self) -> None:
        for row in range(self._sets_table.rowCount()):
            item = self._sets_table.item(row, 0)
            if item:
                item.setText(str(row + 1))

    def _load_exercise(self, exercise: Exercise) -> None:
        idx = self._name_combo.findText(exercise.name)
        if idx >= 0:
            self._name_combo.setCurrentIndex(idx)
        else:
            self._name_combo.setCurrentText(exercise.name)
        self._notes_input.setText(exercise.notes)

        for s in exercise.sets:
            row = self._sets_table.rowCount()
            self._sets_table.insertRow(row)

            set_item = QTableWidgetItem(str(row + 1))
            set_item.setFlags(set_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._sets_table.setItem(row, 0, set_item)

            weight = QDoubleSpinBox()
            weight.setRange(0, 999.5)
            weight.setSingleStep(2.5)
            weight.setDecimals(1)
            weight.setSuffix(self._weight_suffix)
            weight.setValue(s.weight)
            self._sets_table.setCellWidget(row, 1, weight)

            reps = QSpinBox()
            reps.setRange(0, 100)
            reps.setValue(s.reps)
            self._sets_table.setCellWidget(row, 2, reps)

            rpe = QDoubleSpinBox()
            rpe.setRange(0, 10)
            rpe.setSingleStep(0.5)
            rpe.setDecimals(1)
            rpe.setValue(s.rpe if s.rpe else 7)
            self._sets_table.setCellWidget(row, 3, rpe)

            warmup = QCheckBox()
            warmup.setChecked(s.is_warmup)
            warmup_widget = QWidget()
            warmup_layout = QHBoxLayout(warmup_widget)
            warmup_layout.addWidget(warmup)
            warmup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            warmup_layout.setContentsMargins(0, 0, 0, 0)
            self._sets_table.setCellWidget(row, 4, warmup_widget)

    def get_exercise(self) -> Exercise | None:
        name = self._name_combo.currentText().strip()
        if not name:
            return None

        sets = []
        for row in range(self._sets_table.rowCount()):
            weight_widget = self._sets_table.cellWidget(row, 1)
            reps_widget = self._sets_table.cellWidget(row, 2)
            rpe_widget = self._sets_table.cellWidget(row, 3)
            warmup_widget = self._sets_table.cellWidget(row, 4)

            if not all([weight_widget, reps_widget, rpe_widget]):
                continue

            weight = weight_widget.value()
            reps = reps_widget.value()
            rpe = rpe_widget.value()
            warmup_check = warmup_widget.findChild(QCheckBox)
            is_warmup = warmup_check.isChecked() if warmup_check else False

            if weight == 0 or reps == 0:
                continue

            sets.append(
                Set(
                    weight=weight,
                    reps=reps,
                    rpe=rpe,
                    is_warmup=is_warmup,
                    set_number=row + 1,
                )
            )

        return Exercise(
            name=name,
            sets=sets,
            notes=self._notes_input.text().strip(),
        )
