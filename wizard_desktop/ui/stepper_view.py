"""Adaptive stepper widget (Blueprint §4) — renders one StepperSession.

Shows instruction + what/why/where + the command to try + the "Did it work?
Yes/No" gate. No -> walks alternatives (cause/fix/check, destructive warnings).
Exhausted -> renders the Unresolved Issue Log + curated links. Generate-only.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from wizard_core.glossary import Glossary
from wizard_core.models import ExternalResource
from wizard_core.stepper import StepperSession, StepperState


class StepperView(QWidget):
    """Drives a StepperSession. Optional callbacks for milestones + audit."""

    def __init__(
        self,
        session: StepperSession,
        *,
        glossary: Glossary | None = None,
        resources: list[ExternalResource] | None = None,
        on_milestone: Callable[[str, str], None] | None = None,
        on_finished: Callable[[StepperState], None] | None = None,
    ) -> None:
        super().__init__()
        self._s = session
        self._glossary = glossary
        self._resources = resources or []
        self._on_milestone = on_milestone
        self._on_finished = on_finished
        self._build()
        self._render()

    def _build(self) -> None:
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(12)

        self._progress = QLabel("")
        self._progress.setObjectName("Muted")
        self._root.addWidget(self._progress)

        self._title = QLabel("")
        self._title.setObjectName("H1")
        self._title.setWordWrap(True)
        self._root.addWidget(self._title)

        self._explain = QFrame()
        self._explain.setObjectName("Card")
        ex = QVBoxLayout(self._explain)
        ex.setContentsMargins(14, 12, 14, 12)
        self._what = self._wrapped(ex, "What")
        self._why = self._wrapped(ex, "Why")
        self._where = self._wrapped(ex, "Where")
        self._root.addWidget(self._explain)

        self._alt = QFrame()
        self._alt.setObjectName("Warning")
        al = QVBoxLayout(self._alt)
        al.setContentsMargins(14, 12, 14, 12)
        self._alt_head = QLabel("")
        self._alt_head.setObjectName("H2")
        al.addWidget(self._alt_head)
        self._alt_cause = self._wrapped(al, "Likely cause")
        self._alt_fix = self._wrapped(al, "Try this")
        self._alt_check = self._wrapped(al, "Check")
        self._root.addWidget(self._alt)

        self._try_label = QLabel("Run this in your own terminal:")
        self._try_label.setObjectName("Muted")
        self._root.addWidget(self._try_label)
        self._try = QLabel("")
        self._try.setObjectName("Mono")
        self._try.setWordWrap(True)
        self._try.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._root.addWidget(self._try)

        self._success = QLabel("")
        self._success.setObjectName("Muted")
        self._success.setWordWrap(True)
        self._root.addWidget(self._success)

        self._glossary_box = QLabel("")
        self._glossary_box.setObjectName("Faint")
        self._glossary_box.setWordWrap(True)
        self._root.addWidget(self._glossary_box)

        # Yes/No gate
        gate = QHBoxLayout()
        self._gate_label = QLabel("Did it work?")
        self._gate_label.setObjectName("H2")
        gate.addWidget(self._gate_label)
        gate.addStretch(1)
        self._no = QPushButton("NO")
        self._no.setObjectName("No")
        self._no.clicked.connect(self._answer_no)
        self._yes = QPushButton("YES")
        self._yes.setObjectName("Yes")
        self._yes.clicked.connect(self._answer_yes)
        gate.addWidget(self._no)
        gate.addWidget(self._yes)
        self._gate_host = QWidget()
        self._gate_host.setLayout(gate)
        self._root.addWidget(self._gate_host)

        # Final panel (complete or exhausted)
        self._final = QTextEdit()
        self._final.setObjectName("Mono")
        self._final.setReadOnly(True)
        self._final.hide()
        self._root.addWidget(self._final)
        self._root.addStretch(1)

    @staticmethod
    def _wrapped(layout: QVBoxLayout, caption: str) -> QLabel:
        cap = QLabel(caption.upper())
        cap.setObjectName("Faint")
        body = QLabel("")
        body.setObjectName("Body")
        body.setWordWrap(True)
        layout.addWidget(cap)
        layout.addWidget(body)
        return body

    # -- rendering --------------------------------------------------------- #
    def _render(self) -> None:
        if self._s.is_done():
            self._render_final()
            return
        v = self._s.current()
        self._progress.setText(f"STEP {v.index + 1} / {v.total}")
        self._title.setText(v.title)
        self._what.setText(v.what)
        self._why.setText(v.why)
        self._where.setText(v.where or "—")
        self._try.setText(v.try_this or "(no command for this step)")
        self._success.setText(f"Success looks like: {v.success_criteria}" if v.success_criteria else "")

        if v.on_alternative:
            self._alt.show()
            head = f"ALTERNATIVE {v.alternative_index + 1} / {v.alternative_total}"
            if v.destructive:
                head += "   ⚠ DESTRUCTIVE"
            self._alt_head.setText(head)
            self._alt_cause.setText(v.cause)
            fix = v.fix
            if v.destructive and v.recovery:
                fix += f"\n\nRecovery: {v.recovery}"
            self._alt_fix.setText(fix)
            self._alt_check.setText(v.check or "—")
            self._alt.setObjectName("Critical" if v.destructive else "Warning")
            self._alt.style().unpolish(self._alt)
            self._alt.style().polish(self._alt)
        else:
            self._alt.hide()

        # glossary first-use surfacing
        if self._glossary and v.glossary_refs:
            defs = []
            for term in v.glossary_refs:
                d = self._glossary.first_use(term)
                if d:
                    defs.append(f"{term}: {d}")
            self._glossary_box.setText("\n".join(defs))
            self._glossary_box.setVisible(bool(defs))
        else:
            self._glossary_box.hide()

    def _render_final(self) -> None:
        for w in (self._explain, self._alt, self._try, self._try_label,
                  self._success, self._gate_host, self._glossary_box):
            w.hide()
        self._final.show()
        if self._s.state is StepperState.COMPLETE:
            self._progress.setText("COMPLETE")
            self._title.setText("✔ Done — you completed this flow.")
            self._final.setPlainText(
                "Every step verified. You can revisit any step from the menu, "
                "or move on to the next module."
            )
        else:
            self._progress.setText("UNRESOLVED")
            self._title.setText("Authored fixes exhausted — here is your Issue Log.")
            log = self._s.issue_log().to_text()
            links = "\n".join(
                f"  - {r.title} {r.url}{(' — ' + r.note) if r.note else ''}"
                for r in self._resources
            )
            self._final.setPlainText(
                log + "\n\nCURATED TRUSTED LINKS (search yourself — no live help):\n" + links
            )
        if self._on_finished:
            self._on_finished(self._s.state)

    # -- gate -------------------------------------------------------------- #
    def _answer_yes(self) -> None:
        v = self._s.current()
        if self._on_milestone:
            self._on_milestone(v.step_id, "yes")
        self._s.answer_yes()
        self._render()

    def _answer_no(self) -> None:
        v = self._s.current()
        if self._on_milestone:
            self._on_milestone(v.step_id, "no")
        self._s.answer_no()
        self._render()
