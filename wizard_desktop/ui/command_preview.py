"""Command-preview pane — the 3 synchronized slot views (Blueprint §3.3).

Skeleton (shape) · Filled (real values) · Why (per-slot explanation). Mono fonts
throughout. Display only — nothing here is ever executed.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QGuiApplication

from wizard_core.models import CommandPlan
from wizard_core.slots import Slot


class CommandPreview(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Card")
        self._plan: CommandPlan | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(8)

        title = QLabel("COMMAND PREVIEW")
        title.setObjectName("H2")
        root.addWidget(title)

        self._skeleton = QLabel("—")
        self._skeleton.setObjectName("Skeleton")
        self._skeleton.setWordWrap(True)
        root.addWidget(self._label("Skeleton"))
        root.addWidget(self._skeleton)

        self._filled = QLabel("—")
        self._filled.setObjectName("Mono")
        self._filled.setWordWrap(True)
        self._filled.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self._label("Filled (copy this into YOUR terminal)"))
        root.addWidget(self._filled)

        root.addWidget(self._label("Slots — why each part is where it is"))
        self._slot_grid = QGridLayout()
        self._slot_grid.setColumnStretch(2, 1)
        grid_host = QWidget()
        grid_host.setLayout(self._slot_grid)
        root.addWidget(grid_host)

        self._notes = QLabel("")
        self._notes.setObjectName("Muted")
        self._notes.setWordWrap(True)
        root.addWidget(self._notes)

        copy = QPushButton("Copy command")
        copy.clicked.connect(self._copy)
        root.addWidget(copy)
        root.addStretch(1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lab = QLabel(text)
        lab.setObjectName("Muted")
        return lab

    def set_plan(self, plan: CommandPlan) -> None:
        self._plan = plan
        self._skeleton.setText(plan.skeleton or "—")
        self._filled.setText(plan.bash_preview_string or "—")
        # rebuild slot grid
        while self._slot_grid.count():
            item = self._slot_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for r, (slot, toks) in enumerate(plan.slot_values.items()):
            num = QLabel(str(slot.value))
            num.setObjectName("Faint")
            name = QLabel(slot.label)
            name.setObjectName("H2")
            val = QLabel(" ".join(toks))
            val.setObjectName("Mono")
            val.setWordWrap(True)
            self._slot_grid.addWidget(num, r, 0)
            self._slot_grid.addWidget(name, r, 1)
            self._slot_grid.addWidget(val, r, 2)
        self._notes.setText("\n".join(f"• {n}" for n in plan.notes))

    def _copy(self) -> None:
        if self._plan:
            QGuiApplication.clipboard().setText(self._plan.bash_preview_string)
