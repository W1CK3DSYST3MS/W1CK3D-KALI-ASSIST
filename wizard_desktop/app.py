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
from wizard_core.progress import ProgressStore

from wizard_desktop.fonts import load_fonts
from wizard_desktop.resources import modules_dir
from wizard_desktop.theme import build_qss
from wizard_desktop.ui.login_window import LoginWindow
from wizard_desktop.ui.main_window import MainWindow

MODULES_DIR = modules_dir()


def _state_dir() -> Path:
    base = Path.home() / ".w1ck3d-kali-assist"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _audit_path() -> Path:
    return _state_dir() / "activity.audit.jsonl"


def _self_test() -> int:
    """Verify the (possibly bundled) app finds its packaged resources. No GUI."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication(sys.argv)
    app.setStyleSheet(build_qss())
    fams = load_fonts()
    reg = load_modules(MODULES_DIR)
    from wizard_core.builders import get_builder

    assert len(fams) >= 5, f"expected >=5 fonts, got {fams}"
    assert reg.tools and reg.lessons and reg.troubleshooters, "modules missing"

    # Every tool's builder must resolve + run — this catches builders that were
    # not bundled (the pkgutil auto-discovery must survive freezing).
    builder_ids = {f.command_builder_id for t in reg.tools.values() for f in t.flows}
    for bid in sorted(builder_ids):
        get_builder(bid)({})  # raises KeyError if the builder wasn't registered
    plan = get_builder("nmap")({"profile": "standard", "targets": "scanme.nmap.org"})

    print(f"SELF-TEST OK: fonts={len(fams)} tools={len(reg.tools)} "
          f"lessons={len(reg.lessons)} troubleshooters={len(reg.troubleshooters)} "
          f"builders={len(builder_ids)}")
    print(f"  sample build: {plan.bash_preview_string}")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return _self_test()
    app = QApplication(sys.argv)
    app.setApplicationName("W1CK3D'S KALI ASSIST")
    load_fonts()
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
    progress = ProgressStore(_state_dir() / "progress.json")
    win = MainWindow(registry, audit, progress=progress, username=username)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
