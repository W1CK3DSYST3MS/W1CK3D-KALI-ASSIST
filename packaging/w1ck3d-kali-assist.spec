# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — W1CK3D'S KALI ASSIST (one-file, offline, generate-only).

Build (run from the repo root):
    pyinstaller packaging/w1ck3d-kali-assist.spec --noconfirm

Bundles the runtime content (modules/) + brand assets (fonts, logo) INTO the
binary so the app runs fully offline. Only this built file is ever distributed;
source stays private.
"""

import os

# SPECPATH is the directory containing this spec (packaging/), so the project
# root is its parent.
PROJECT = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = [
    (os.path.join(PROJECT, "assets"), "assets"),
    (os.path.join(PROJECT, "modules"), "modules"),
]

hiddenimports = [
    # Builders self-register on import; make sure the analyzer keeps them.
    "wizard_core.builders.nmap_builder",
]

a = Analysis(
    [os.path.join(PROJECT, "wizard_desktop", "app.py")],
    pathex=[PROJECT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
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
