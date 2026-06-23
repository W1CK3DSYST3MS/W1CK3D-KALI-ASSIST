"""Main window — header + Lessons / Tools / Troubleshooter sections.

Each section is a list -> detail stack. Tools honor the authorization gate;
lessons and troubleshooters run through the shared adaptive StepperView.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from wizard_core.audit import AuditLogger
from wizard_core.loader import Registry
from wizard_core.stepper import StepperSession

from .stepper_view import StepperView
from .tool_page import ToolPage


class _Section(QWidget):
    """A list (page 0) -> active detail (page 1) with a Back bar."""

    def __init__(self, title: str) -> None:
        super().__init__()
        self._v = QVBoxLayout(self)
        self._v.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self._v.addWidget(self.stack)

        self._chooser = QWidget()
        self.chooser_layout = QVBoxLayout(self._chooser)
        self.chooser_layout.setContentsMargins(4, 4, 4, 4)
        head = QLabel(title)
        head.setObjectName("H1")
        self.chooser_layout.addWidget(head)
        self.stack.addWidget(self._chooser)

        self._detail_host = QWidget()
        self._detail_layout = QVBoxLayout(self._detail_host)
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        bar = QHBoxLayout()
        back = QPushButton("← Back")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        bar.addWidget(back)
        bar.addStretch(1)
        self._detail_layout.addLayout(bar)
        self._detail_slot = QStackedWidget()
        self._detail_layout.addWidget(self._detail_slot)
        self.stack.addWidget(self._detail_host)

    def show_detail(self, widget: QWidget) -> None:
        while self._detail_slot.count():
            w = self._detail_slot.widget(0)
            self._detail_slot.removeWidget(w)
            w.deleteLater()
        self._detail_slot.addWidget(widget)
        self.stack.setCurrentIndex(1)


class MainWindow(QMainWindow):
    def __init__(self, registry: Registry, audit: AuditLogger, *, username: str = "local") -> None:
        super().__init__()
        self._reg = registry
        self._audit = audit
        self._user = username
        self.setWindowTitle("W1CK3D'S KALI ASSIST")
        self.resize(1180, 760)
        self._build()

    def _build(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 16)
        root.setSpacing(12)
        self.setCentralWidget(central)

        # Header
        header = QHBoxLayout()
        word = QLabel("W1CK3D'S KALI ASSIST")
        word.setObjectName("Wordmark")
        header.addWidget(word)
        header.addStretch(1)
        badge = QLabel("GENERATE-ONLY · NOTHING IS EXECUTED")
        badge.setObjectName("Subwordmark")
        header.addWidget(badge)
        user = QLabel(f"  {self._user}")
        user.setObjectName("Muted")
        header.addWidget(user)
        root.addLayout(header)

        tabs = QTabWidget()
        tabs.addTab(self._lessons_tab(), "LESSONS")
        tabs.addTab(self._tools_tab(), "TOOLS")
        tabs.addTab(self._troubleshooter_tab(), "TROUBLESHOOTER")
        root.addWidget(tabs)

    # -- Lessons ----------------------------------------------------------- #
    def _lessons_tab(self) -> QWidget:
        sec = _Section("Lessons — fundamentals")
        lst = QListWidget()
        for lesson in self._reg.lessons.values():
            it = QListWidgetItem(lesson.title)
            it.setData(Qt.UserRole, lesson.lesson_id)
            lst.addItem(it)
        lst.itemActivated.connect(lambda it: self._open_lesson(sec, it.data(Qt.UserRole)))
        lst.itemClicked.connect(lambda it: self._open_lesson(sec, it.data(Qt.UserRole)))
        sec.chooser_layout.addWidget(lst)
        return sec

    def _open_lesson(self, sec: _Section, lesson_id: str) -> None:
        lesson = self._reg.lessons[lesson_id]
        self._audit.selected("lesson", lesson_id)
        self._reg.glossary.reset_seen()
        session = StepperSession(lesson.steps, flow_title=lesson.title)
        view = StepperView(
            session,
            glossary=self._reg.glossary,
            on_milestone=lambda sid, res: self._audit.step_milestone(lesson_id, sid, res),
        )
        sec.show_detail(view)

    # -- Tools ------------------------------------------------------------- #
    def _tools_tab(self) -> QWidget:
        sec = _Section("Tools — by category")
        lst = QListWidget()
        for tool in self._reg.tools.values():
            cats = ", ".join(tool.categories)
            it = QListWidgetItem(f"{tool.display_name}   ·   {cats}")
            it.setData(Qt.UserRole, tool.tool_id)
            lst.addItem(it)
        lst.itemClicked.connect(lambda it: self._open_tool(sec, it.data(Qt.UserRole)))
        sec.chooser_layout.addWidget(lst)
        return sec

    def _open_tool(self, sec: _Section, tool_id: str) -> None:
        tool = self._reg.tools[tool_id]
        self._audit.selected("tool", tool_id)
        page = ToolPage(
            tool,
            on_preview=lambda tid, flow: self._audit.command_preview(tool=tid, flow=flow or ""),
            on_auth_ack=lambda tid: self._audit.authorization_ack(tid),
            on_walk_flow=lambda flow_id: self._walk_tool_flow(sec, tool_id, flow_id),
        )
        sec.show_detail(page)

    def _walk_tool_flow(self, sec: _Section, tool_id: str, flow_id: str) -> None:
        tool = self._reg.tools[tool_id]
        flow = next(f for f in tool.flows if f.flow_id == flow_id)
        if not flow.steps:
            return
        self._reg.glossary.reset_seen()
        session = StepperSession(flow.steps, flow_title=flow.title)
        view = StepperView(
            session,
            glossary=self._reg.glossary,
            on_milestone=lambda sid, res: self._audit.step_milestone(flow_id, sid, res),
        )
        sec.show_detail(view)

    # -- Troubleshooter ---------------------------------------------------- #
    def _troubleshooter_tab(self) -> QWidget:
        sec = _Section("Troubleshooter — start here")
        search = QLineEdit()
        search.setPlaceholderText("Describe the problem or paste an error…")
        sec.chooser_layout.addWidget(search)
        lst = QListWidget()
        self._fill_symptoms(lst, self._reg.all_symptoms())
        search.textChanged.connect(
            lambda q: self._fill_symptoms(
                lst, self._reg.search_symptoms(q) if q.strip() else self._reg.all_symptoms()
            )
        )
        lst.itemClicked.connect(lambda it: self._open_symptom(sec, it.data(Qt.UserRole)))
        sec.chooser_layout.addWidget(lst)
        return sec

    @staticmethod
    def _fill_symptoms(lst: QListWidget, matches) -> None:
        lst.clear()
        for m in matches:
            it = QListWidgetItem(m.label)
            it.setData(Qt.UserRole, (m.troubleshooter_id, m.symptom_id))
            lst.addItem(it)

    def _open_symptom(self, sec: _Section, key: tuple[str, str]) -> None:
        ts_id, sym_id = key
        ts = self._reg.troubleshooters[ts_id]
        symptom = next(s for s in ts.symptoms if s.symptom_id == sym_id)
        self._audit.selected("symptom", sym_id)

        host = QWidget()
        v = QVBoxLayout(host)
        v.setContentsMargins(0, 0, 0, 0)

        if symptom.diagnosis:
            self._reg.glossary.reset_seen()
            session = StepperSession(
                symptom.diagnosis, flow_title=ts.title, context={"symptom": symptom.label}
            )
            view = StepperView(
                session,
                glossary=self._reg.glossary,
                resources=ts.external_resources,
                on_milestone=lambda sid, res: self._audit.step_milestone(ts_id, sid, res),
            )
            v.addWidget(view)
        else:
            head = QLabel(symptom.label)
            head.setObjectName("H1")
            v.addWidget(head)

        # tiered fixes panel
        fixes = QFrame()
        fixes.setObjectName("Card")
        fl = QVBoxLayout(fixes)
        fl.setContentsMargins(14, 12, 14, 12)
        fh = QLabel("FIXES (by tier)")
        fh.setObjectName("H2")
        fl.addWidget(fh)
        for fx in symptom.fixes:
            warn = "   ⚠ DESTRUCTIVE" if fx.destructive else ""
            line = QLabel(f"[{fx.tier}] {fx.title}{warn}")
            line.setObjectName("Muted")
            cmd = QLabel(fx.command)
            cmd.setObjectName("Mono")
            cmd.setWordWrap(True)
            cmd.setTextInteractionFlags(Qt.TextSelectableByMouse)
            fl.addWidget(line)
            fl.addWidget(cmd)
            if fx.destructive and fx.recovery:
                rec = QLabel(f"Recovery: {fx.recovery}")
                rec.setObjectName("Faint")
                rec.setWordWrap(True)
                fl.addWidget(rec)
        v.addWidget(fixes)

        sec.show_detail(host)
