"""Main window — header + Lessons / Tools / Troubleshooter sections.

Each section is a list -> detail stack. Tools honor the authorization gate;
lessons and troubleshooters run through the shared adaptive StepperView.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from wizard_core.audit import AuditLogger
from wizard_core.loader import Registry
from wizard_core.progress import ProgressStore
from wizard_core.stepper import StepperSession

from ..settings import get_text_scale, set_text_scale
from ..theme import build_qss
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
        # Wrap in a scroll area so tall content (walk-through steps with several
        # cards) scrolls instead of squashing into an unreadable panel.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(widget)
        self._detail_slot.addWidget(scroll)
        self.stack.setCurrentIndex(1)


class MainWindow(QMainWindow):
    def __init__(self, registry: Registry, audit: AuditLogger, *,
                 progress: "ProgressStore | None" = None, username: str = "local") -> None:
        super().__init__()
        self._reg = registry
        self._audit = audit
        self._progress = progress
        self._user = username
        self.setWindowTitle("W1CK3D'S KALI ASSIST")
        self._build()
        self._apply_default_geometry()

    def _apply_default_geometry(self) -> None:
        """Open at a size that fits common laptop screens (incl. 1366x768),
        clamped to the available desktop, and centred."""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.resize(1120, 720)
            return
        avail = screen.availableGeometry()
        w = min(1120, avail.width() - 40)
        h = min(720, avail.height() - 60)
        self.resize(w, h)
        self.setMinimumSize(min(880, w), min(560, h))
        frame = self.frameGeometry()
        frame.moveCenter(avail.center())
        self.move(frame.topLeft())

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

        # Accessibility: text-size control (persisted).  Text size  [ − ] 100% [ + ]
        self._scale = get_text_scale()
        tsize = QLabel("  Text size")
        tsize.setObjectName("Muted")
        header.addWidget(tsize)
        smaller = QPushButton("−")
        smaller.setObjectName("Compact")
        smaller.setToolTip("Smaller text")
        smaller.clicked.connect(lambda: self._bump_text_scale(-0.1))
        header.addWidget(smaller)
        # The percentage read-out doubles as a reset button (click to return to 100%).
        self._scale_readout = QPushButton(self._scale_pct())
        self._scale_readout.setObjectName("Compact")
        self._scale_readout.setToolTip("Current text size — click to reset to 100%")
        self._scale_readout.clicked.connect(lambda: self._set_text_scale(1.0))
        header.addWidget(self._scale_readout)
        bigger = QPushButton("+")
        bigger.setObjectName("Compact")
        bigger.setToolTip("Larger text")
        bigger.clicked.connect(lambda: self._bump_text_scale(0.1))
        header.addWidget(bigger)
        # Fixed size + explicit minimum widths so a crowded header can never
        # shrink these below their text (that was clipping "A−" to "half an A").
        for b in (smaller, self._scale_readout, bigger):
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._tsize_minus = smaller
        self._tsize_plus = bigger
        self._size_text_controls()
        root.addLayout(header)

        tabs = QTabWidget()
        tabs.addTab(self._lessons_tab(), "LESSONS")
        tabs.addTab(self._tools_tab(), "TOOLS")
        tabs.addTab(self._troubleshooter_tab(), "TROUBLESHOOTER")
        root.addWidget(tabs)

    # -- Accessibility: text size ------------------------------------------ #
    def _scale_pct(self) -> str:
        return f"{round(self._scale * 100)}%"

    def _size_text_controls(self) -> None:
        """Pin control widths to the current scale so labels never clip.

        setFixedWidth is the strongest width constraint (min == max), so a
        crowded header can't compress these and clip their labels.
        """
        s = self._scale
        self._tsize_minus.setFixedWidth(round(40 * s))
        self._tsize_plus.setFixedWidth(round(40 * s))
        self._scale_readout.setFixedWidth(round(80 * s))

    def _bump_text_scale(self, delta: float) -> None:
        self._set_text_scale(self._scale + delta)

    def _set_text_scale(self, scale: float) -> None:
        self._scale = max(0.8, min(2.2, round(scale, 2)))
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(build_qss(self._scale))
        self._scale_readout.setText(self._scale_pct())
        self._size_text_controls()
        set_text_scale(self._scale)

    # -- Lessons ----------------------------------------------------------- #
    def _lessons_tab(self) -> QWidget:
        sec = _Section("Lessons — fundamentals")
        hint = QLabel("Your progress is saved — pick a lesson to resume where you left off.")
        hint.setObjectName("Muted")
        sec.chooser_layout.addWidget(hint)
        self._lessons_list = QListWidget()
        self._refresh_lessons_list()
        self._lessons_list.itemClicked.connect(
            lambda it: self._open_lesson(sec, it.data(Qt.UserRole)))
        sec.chooser_layout.addWidget(self._lessons_list)
        return sec

    def _lesson_label(self, lesson) -> str:
        step_ids = [s.step_id for s in lesson.steps]
        if not self._progress:
            return lesson.title
        done, total = self._progress.counts(lesson.lesson_id, step_ids)
        if done == 0:
            badge = "· not started"
        elif done >= total:
            badge = "· ✓ complete"
        else:
            badge = f"· {done}/{total} — resume"
        return f"{lesson.title}   {badge}"

    # Suggested learning order; anything not listed sorts after, alphabetically.
    _LESSON_ORDER = [
        "lesson.setup_and_securing",
        "lesson.shell_grammar",
        "lesson.files_navigation",
        "lesson.permissions",
        "lesson.viewing_editing",
        "lesson.pipes_redirection",
        "lesson.text_processing",
        "lesson.processes",
        "lesson.packages",
        "lesson.bash_environment",
        "lesson.users_groups",
        "lesson.archives_transfer",
        "lesson.networking",
        "lesson.wordlists",
    ]

    def _ordered_lessons(self) -> list:
        order = {lid: i for i, lid in enumerate(self._LESSON_ORDER)}
        return sorted(
            self._reg.lessons.values(),
            key=lambda le: (order.get(le.lesson_id, len(order)), le.title),
        )

    def _refresh_lessons_list(self) -> None:
        self._lessons_list.clear()
        for lesson in self._ordered_lessons():
            it = QListWidgetItem(self._lesson_label(lesson))
            it.setData(Qt.UserRole, lesson.lesson_id)
            self._lessons_list.addItem(it)

    def _open_lesson(self, sec: _Section, lesson_id: str) -> None:
        lesson = self._reg.lessons[lesson_id]
        self._audit.selected("lesson", lesson_id)
        self._reg.glossary.reset_seen()
        step_ids = [s.step_id for s in lesson.steps]
        start = 0
        if self._progress:
            r = self._progress.resume_index(lesson_id, step_ids)
            start = r if r < len(step_ids) else 0  # completed -> allow a fresh run

        def _milestone(sid: str, res: str) -> None:
            self._audit.step_milestone(lesson_id, sid, res)
            if res == "yes" and self._progress:
                self._progress.mark_complete(lesson_id, sid)
                self._refresh_lessons_list()

        session = StepperSession(lesson.steps, flow_title=lesson.title, start_index=start)
        view = StepperView(session, glossary=self._reg.glossary, on_milestone=_milestone)
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
