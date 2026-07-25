"""Headless GUI smoke test (offscreen).

Constructs the themed login + main window, drives each section programmatically
(lesson stepper, tool build, troubleshooter symptom) and asserts no exceptions.
Proves the PySide6 layer wires to the engine. Run:

    QT_QPA_PLATFORM=offscreen python -m tools.gui_smoke
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication  # noqa: E402

from wizard_core.audit import AuditLogger  # noqa: E402
from wizard_core.auth import LoginPolicy  # noqa: E402
from wizard_core.loader import load_modules  # noqa: E402

from wizard_desktop.theme import build_qss  # noqa: E402
from wizard_desktop.ui.login_window import LoginWindow  # noqa: E402
from wizard_desktop.ui.main_window import MainWindow  # noqa: E402

MODULES = Path(__file__).resolve().parents[1] / "modules"


def main() -> int:
    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(build_qss())
    print("theme applied:", len(build_qss()), "chars QSS")

    # Login gate validates correctly.
    login = LoginWindow(LoginPolicy())
    assert not login._policy.validate("x", "y", False).ok
    assert login._policy.validate("hunter", "correcthorse", True).ok
    print("login gate: OK")

    registry = load_modules(MODULES)
    audit = AuditLogger(Path(tempfile.gettempdir()) / "w1ck3d_gui_smoke.audit.jsonl", user="hunter")
    win = MainWindow(registry, audit, username="hunter")
    win.show()
    print("main window built:", win.windowTitle())

    # Drive each section's open path (no real display needed).
    lessons = win._lessons_tab()  # noqa: SLF001 (smoke test pokes internals)
    win._open_lesson(lessons, "lesson.shell_grammar")
    print("lesson opened + stepper rendered: OK")

    # Drive the step-review nav directly: answer step 1, look back at it with
    # Previous, confirm the gate is hidden while reviewing, then Next back to live.
    from wizard_core.stepper import StepperSession
    from wizard_desktop.ui.stepper_view import StepperView

    lesson = registry.lessons["lesson.shell_grammar"]
    assert len(lesson.steps) >= 2, "smoke test needs a lesson with 2+ steps"
    session = StepperSession(lesson.steps, flow_title=lesson.title)
    view = StepperView(session, glossary=registry.glossary)
    first_step_id = session.current().step_id
    view._answer_yes()  # noqa: SLF001
    assert session.current().step_id != first_step_id
    view._go_previous()  # noqa: SLF001
    # isHidden() reflects our own show()/hide() calls directly, unlike isVisible()
    # (which also depends on this standalone widget's never-shown top-level window).
    assert view._review_pos == 0 and view._gate_host.isHidden()
    assert view._title.text() == lesson.steps[0].title
    view._go_next()  # noqa: SLF001
    assert view._review_pos is None and not view._gate_host.isHidden()
    assert view._title.text() == session.current().title
    print("step review nav (Previous/Next): OK")

    # Regression: the completion screen used to show a hardcoded generic
    # message no matter what, silently dropping any flow_goal pointer to a
    # related flow (this shipped broken once already - sherlock's "now what"
    # pointer never actually reached the screen the user lands on after
    # finishing). Drive a flow to completion for real and check the ACTUAL
    # rendered completion text, not just the pre-completion step.
    sherlock = registry.tools["sherlock"]
    guided = next(f for f in sherlock.flows if f.flow_id == "guided")
    assert guided.goal, "sherlock's guided flow should have a goal to test with"
    s2 = StepperSession(guided.steps, flow_title=guided.title, flow_goal=guided.goal)
    for _ in guided.steps:
        s2.answer_yes()
    assert s2.is_done()
    view2 = StepperView(s2, glossary=registry.glossary)
    assert guided.goal in view2._final.toPlainText()  # noqa: SLF001
    print("flow_goal reaches the actual completion screen: OK")

    tools = win._tools_tab()
    win._open_tool(tools, "nmap")
    # Build a command directly, force-authorized to skip the modal dialog.
    from wizard_desktop.ui.tool_page import ToolPage

    tp = ToolPage(registry.tools["nmap"])
    tp._authorized = True
    # Fill the dynamic quick-build form: set required fields to sample values.
    from PySide6.QtWidgets import QComboBox, QLineEdit

    for fid, (fs, w) in tp._fields.items():
        if not fs.required:
            continue
        if isinstance(w, QLineEdit):
            w.setText("scanme.nmap.org")
        elif isinstance(w, QComboBox) and w.currentData() is None:
            w.setCurrentIndex(w.count() - 1)
    tp._build_command()
    assert tp._preview._plan is not None
    print("tool page built command:", tp._preview._plan.bash_preview_string)

    ts = win._troubleshooter_tab()
    win._open_symptom(ts, ("troubleshoot.networking", "no_internet"))
    print("troubleshooter symptom opened: OK")

    app.processEvents()
    print("\nGUI SMOKE PASSED — no command executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
