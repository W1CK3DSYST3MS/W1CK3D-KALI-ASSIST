"""Application entrypoint.

Boots Qt, applies the W1CK3D theme, runs the login + disclaimer gate, loads the
modules into the engine registry, then opens the main window. Generate-only.

Run:  python -m wizard_desktop.app
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from a source checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication

from wizard_core.audit import AuditLogger
from wizard_core.loader import load_modules

from wizard_desktop.theme import build_qss
from wizard_desktop.ui.login_window import LoginWindow
from wizard_desktop.ui.main_window import MainWindow

_REPO = Path(__file__).resolve().parents[1]
MODULES_DIR = _REPO / "modules"


def _audit_path() -> Path:
    base = Path.home() / ".w1ck3d-kali-assist"
    base.mkdir(parents=True, exist_ok=True)
    return base / "activity.audit.jsonl"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("W1CK3D'S KALI ASSIST")
    app.setStyleSheet(build_qss())

    # 1. Login + disclaimer gate.
    login = LoginWindow()
    if login.exec() != LoginWindow.Accepted:
        return 0
    username = login.username

    audit = AuditLogger(_audit_path(), user=username)
    audit.login(username)

    # 2. Load modules into the engine registry.
    registry = load_modules(MODULES_DIR)

    # 3. Main window.
    win = MainWindow(registry, audit, username=username)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
