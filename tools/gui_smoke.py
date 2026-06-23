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

    tools = win._tools_tab()
    win._open_tool(tools, "nmap")
    # Build a command directly, force-authorized to skip the modal dialog.
    from wizard_desktop.ui.tool_page import ToolPage

    tp = ToolPage(registry.tools["nmap"])
    tp._authorized = True
    tp._targets.setText("scanme.nmap.org")
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
