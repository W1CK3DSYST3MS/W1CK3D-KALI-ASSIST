"""Tool page — profile + inputs on the left, live command preview on the right.

Builds commands via the engine's registered builder (generate-only). Honors the
tool's authorization_gate before showing any built command. A "Walk this flow"
button opens the adaptive stepper for the selected flow.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
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
from wizard_core.models import ToolSpec

from .auth_gate import confirm_authorization
from .command_preview import CommandPreview

# Builder-input presets per profile are inside the builder; here we only collect
# the simple on-ramp fields (profile + targets + output) plus a couple toggles.
_NMAP_PROFILES = ["quick", "standard", "thorough", "quiet"]


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
        self._build()

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setSpacing(16)

        # left: controls
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

        form = QFormLayout()
        self._flow = QComboBox()
        for f in self._tool.flows:
            self._flow.addItem(f.title, f.flow_id)
        form.addRow("Flow", self._flow)

        self._profile = QComboBox()
        self._profile.addItem("(none)", None)
        # Profiles are tool-specific; only nmap's simple form is wired into BUILD.
        # Other tools are built via "Walk this flow" until per-tool forms land (M4).
        if self._tool.tool_id == "nmap":
            for p in _NMAP_PROFILES:
                self._profile.addItem(p, p)
            self._profile.setCurrentText("standard")
        form.addRow("Profile", self._profile)

        self._targets = QLineEdit()
        self._targets.setPlaceholderText("scanme.nmap.org  or  192.168.1.0/24")
        form.addRow("Targets", self._targets)

        self._ports = QLineEdit()
        self._ports.setPlaceholderText("22,80,443  (optional)")
        form.addRow("Ports", self._ports)

        self._out = QLineEdit()
        self._out.setPlaceholderText("./out/scan  (optional)")
        form.addRow("Output base", self._out)
        lv.addLayout(form)

        build = QPushButton("BUILD COMMAND")
        build.setObjectName("Primary")
        build.clicked.connect(self._build_command)
        lv.addWidget(build)

        walk = QPushButton("Walk this flow (adaptive stepper)")
        walk.clicked.connect(self._walk)
        lv.addWidget(walk)
        lv.addStretch(1)

        # right: preview
        self._preview = CommandPreview()

        root.addWidget(left, 2)
        root.addWidget(self._preview, 3)

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

    def _build_command(self) -> None:
        if not self._ensure_authorized():
            return
        flow = self._selected_flow()
        target = self._targets.text().strip()
        out = self._out.text().strip()
        # The simple form is nmap-shaped; pass the target under the common keys other
        # builders read (each ignores keys it doesn't use). Full per-tool forms: M4.
        inputs: dict[str, object] = {
            "profile": self._profile.currentData(),
            "targets": target, "target": target, "url": target, "host": target,
            "output_format": "all" if out else None,
            "output_path": out or None,
            "output": out or None,
        }
        if self._ports.text().strip():
            inputs["ports"] = self._ports.text().strip()
        try:
            plan = get_builder(flow.command_builder_id)(inputs)
        except Exception as exc:  # builder validation (fail-loudly) -> show, don't crash
            plan = assemble(self._tool.tool_id, {}, notes=[
                f"Could not build from the simple form: {exc}",
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
