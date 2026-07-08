"""Tool page — a per-tool quick-build form on the left, live preview on the right.

The form is rendered dynamically from the tool's ``quick_build`` spec (field
list authored in each tool.yaml), and the collected inputs are fed to that
tool's registered builder (generate-only). Honors the tool's authorization_gate
before showing any built command. "Walk this flow" opens the adaptive stepper.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wizard_core.builders import assemble, get_builder
from wizard_core.models import FieldSchema, ToolSpec

from .auth_gate import confirm_authorization
from .command_preview import CommandPreview

_NONE_LABEL = "(none)"


class ToolPage(QWidget):
    def __init__(
        self,
        tool: ToolSpec,
        *,
        on_preview: Callable[[str, str], None] | None = None,
        on_auth_ack: Callable[[str], None] | None = None,
        on_walk_flow: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()
        self._tool = tool
        self._on_preview = on_preview
        self._on_auth_ack = on_auth_ack
        self._on_walk_flow = on_walk_flow
        self._authorized = not tool.authorization_gate
        # field_id -> (FieldSchema, widget)
        self._fields: dict[str, tuple[FieldSchema, QWidget]] = {}
        self._build()

    # ------------------------------------------------------------------ build
    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setSpacing(16)

        left = QFrame()
        left.setObjectName("Card")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(16, 14, 16, 14)
        lv.setSpacing(10)

        title = QLabel(self._tool.display_name)
        title.setObjectName("H1")
        lv.addWidget(title)
        one = QLabel(self._tool.one_liner)
        one.setObjectName("Muted")
        one.setWordWrap(True)
        lv.addWidget(one)

        if self._tool.authorization_gate:
            gate = QFrame()
            gate.setObjectName("Critical")
            gl = QVBoxLayout(gate)
            gl.setContentsMargins(12, 10, 12, 10)
            gh = QLabel("AUTHORIZATION GATE")
            gh.setObjectName("H2")
            gl.addWidget(gh)
            gt = QLabel(self._tool.authorization_text)
            gt.setObjectName("Body")
            gt.setWordWrap(True)
            gl.addWidget(gt)
            lv.addWidget(gate)

        # --- Choose a task -------------------------------------------------- #
        pick = QLabel("Choose what you want to do:")
        pick.setObjectName("H2")
        lv.addWidget(pick)
        self._flow = QComboBox()
        for f in self._tool.flows:
            self._flow.addItem(f.title, f.flow_id)
        self._flow.currentIndexChanged.connect(self._on_flow_changed)
        lv.addWidget(self._flow)

        # Short description of the selected task (its goal).
        self._flow_goal = QLabel("")
        self._flow_goal.setObjectName("Muted")
        self._flow_goal.setWordWrap(True)
        lv.addWidget(self._flow_goal)

        # --- PRIMARY: the guided walk-through (the teaching path) ----------- #
        walk = QPushButton("▶  Walk me through it — step by step")
        walk.setObjectName("Primary")
        walk.clicked.connect(self._walk)
        lv.addWidget(walk)
        walk_hint = QLabel(
            "New here? This explains every step: what to type, how to find the "
            "info you need, and what each part of the command does."
        )
        walk_hint.setObjectName("Faint")
        walk_hint.setWordWrap(True)
        lv.addWidget(walk_hint)

        # --- SECONDARY: quick build for people who know the flags ----------- #
        qb = self._tool.quick_build
        if qb and qb.fields:
            sep = QLabel("— or, if you already know the flags, quick-build a command —")
            sep.setObjectName("Faint")
            sep.setWordWrap(True)
            lv.addWidget(sep)

            form = QFormLayout()
            for fs in qb.fields:
                widget = self._make_widget(fs)
                self._fields[fs.field_id] = (fs, widget)
                form.addRow(fs.label, widget)
            lv.addLayout(form)

            build = QPushButton("Quick-build command")
            build.clicked.connect(self._build_command)
            lv.addWidget(build)

        lv.addStretch(1)
        self._on_flow_changed()  # seed the goal text

        self._preview = CommandPreview()
        root.addWidget(left, 2)
        root.addWidget(self._preview, 3)

    def _make_widget(self, fs: FieldSchema) -> QWidget:
        if fs.type == "bool":
            cb = QCheckBox()
            cb.setChecked(bool(fs.default))
            if fs.help:
                cb.setToolTip(fs.help)
            return cb
        if fs.type == "choice":
            combo = QComboBox()
            if not fs.required:
                combo.addItem(_NONE_LABEL, None)
            for c in fs.choices:
                combo.addItem(c, c)
            if fs.default is not None:
                idx = combo.findData(fs.default)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            if fs.help:
                combo.setToolTip(fs.help)
            return combo
        # string / int / path / list / range -> line edit
        line = QLineEdit()
        if fs.default not in (None, ""):
            line.setText(str(fs.default))
        if fs.placeholder:
            line.setPlaceholderText(fs.placeholder)
        if fs.help:
            line.setToolTip(fs.help)
        return line

    # -------------------------------------------------------------- authorize
    def _ensure_authorized(self) -> bool:
        if self._authorized:
            return True
        ok = confirm_authorization(self, self._tool.display_name, self._tool.authorization_text)
        if ok:
            self._authorized = True
            if self._on_auth_ack:
                self._on_auth_ack(self._tool.tool_id)
        return ok

    def _selected_flow(self):
        flow_id = self._flow.currentData()
        for f in self._tool.flows:
            if f.flow_id == flow_id:
                return f
        return self._tool.flows[0]

    def _on_flow_changed(self, *_) -> None:
        flow = self._selected_flow()
        self._flow_goal.setText(flow.goal or "")

    # ----------------------------------------------------------------- inputs
    def _collect_inputs(self) -> dict[str, object]:
        inputs: dict[str, object] = {}
        for field_id, (fs, widget) in self._fields.items():
            if isinstance(widget, QCheckBox):
                if widget.isChecked():
                    inputs[field_id] = True
            elif isinstance(widget, QComboBox):
                val = widget.currentData()
                if val is not None:
                    inputs[field_id] = val
            else:  # QLineEdit
                text = widget.text().strip()
                if text:
                    inputs[field_id] = text
        return inputs

    def _build_command(self) -> None:
        if not self._ensure_authorized():
            return
        flow = self._selected_flow()
        qb = self._tool.quick_build
        builder_id = qb.builder if qb else flow.command_builder_id
        inputs = self._collect_inputs()
        try:
            plan = get_builder(builder_id)(inputs)
        except Exception as exc:  # builder validation (fail-loudly) -> show, don't crash
            plan = assemble(self._tool.tool_id, {}, notes=[
                f"Could not build from the quick form: {exc}",
                "Use 'Walk this flow (adaptive stepper)' for guided, correct commands.",
            ])
        self._preview.set_plan(plan)
        if self._on_preview:
            self._on_preview(self._tool.tool_id, flow.flow_id)

    def _walk(self) -> None:
        if not self._ensure_authorized():
            return
        if self._on_walk_flow:
            self._on_walk_flow(self._flow.currentData())
