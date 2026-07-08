# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — W1CK3D'S KALI ASSIST (one-file, offline, generate-only).

Build (run from the repo root):
    pyinstaller packaging/w1ck3d-kali-assist.spec --noconfirm

Bundles the runtime content (modules/) + brand assets (fonts, logo) INTO the
binary so the app runs fully offline. Only this built file is ever distributed;
source stays private.
"""

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

# SPECPATH is the directory containing this spec (packaging/), so the project
# root is its parent.
PROJECT = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = [
    (os.path.join(PROJECT, "assets"), "assets"),
    (os.path.join(PROJECT, "modules"), "modules"),
]

# The builder package auto-discovers *_builder.py at runtime (pkgutil). In a
# frozen app those submodules must be explicitly collected or only the ones
# imported by name would be bundled — collect them all so every tool registers.
hiddenimports = collect_submodules("wizard_core.builders")

# Force-collect PySide6 so all Qt modules (QtWidgets/QtCore/QtGui) + plugins are
# bundled. Without this the frozen app can fail with
# "No module named 'PySide6.QtWidgets'".
_qt_datas, _qt_binaries, _qt_hidden = collect_all("PySide6")
datas += _qt_datas
hiddenimports += _qt_hidden

a = Analysis(
    [os.path.join(PROJECT, "wizard_desktop", "app.py")],
    pathex=[PROJECT],
    binaries=_qt_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

# --- Slim the Qt payload -------------------------------------------------- #
# collect_all AND PyInstaller's automatic PySide6 hook both add the full Qt
# stack, including enormous components this app never imports (it uses only
# QtCore/QtGui/QtWidgets). Qt6WebEngineCore alone is ~195 MB. Filter the merged
# TOCs here (after Analysis) so the removals actually stick. KEEP everything
# under the plugins tree (platforms/imageformats — the Linux xcb plugin lives
# there) and the core QtCore/Gui/Widgets/Network/DBus/OpenGL/Svg libraries so
# the GUI, icons and image loading still work on Kali.
_QT_DROP = (
    "webengine", "webchannel", "qt3d", "quick3d", "quick", "qtquick",
    "qml", "qmlmodels", "multimedia", "spatialaudio", "charts",
    "datavisualization", "graphs", "qt6pdf", "pdfquick", "designer",
    "qthelp", "qttest", "sensors", "serialport", "serialbus", "bluetooth",
    "nfc", "positioning", "qt6location", "texttospeech", "remoteobjects",
    "scxml", "qt6sql", "virtualkeyboard", "shadertools",
    "avcodec", "avformat", "avutil", "swscale", "swresample",
    "qtwebengineprocess", "devtools_resources",
)


def _drop(dest: str) -> bool:
    low = dest.replace("\\", "/").lower()
    if "/plugins/" in low:          # never drop platform/imageformat plugins
        return False
    return any(tok in low for tok in _QT_DROP)


_before = len(a.binaries) + len(a.datas)
a.binaries = [e for e in a.binaries if not _drop(e[0])]
a.datas = [e for e in a.datas if not _drop(e[0])]
print(f"[slim] Qt filter removed {_before - len(a.binaries) - len(a.datas)} entries")

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="w1ck3d-kali-assist",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,           # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=os.path.join(PROJECT, "assets", "W1CK3D-SYSTEMS-logo.png"),
)
