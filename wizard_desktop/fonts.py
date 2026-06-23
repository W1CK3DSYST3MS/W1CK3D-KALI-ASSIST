"""Register the bundled brand fonts with Qt at startup.

Loads every .ttf under assets/fonts/ via QFontDatabase so the theme's font
stacks (Black Ops One / Orbitron / Chakra Petch / JetBrains Mono / Share Tech
Mono) resolve even on systems without them installed. Works from a source
checkout and from a PyInstaller bundle (sys._MEIPASS).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFontDatabase

from .resources import assets_dir


def fonts_dir() -> Path:
    """Locate assets/fonts/ in both source and PyInstaller-bundled layouts."""
    return assets_dir() / "fonts"


def load_fonts() -> list[str]:
    """Register all bundled .ttf files. Returns the loaded family names."""
    families: list[str] = []
    d = fonts_dir()
    if not d.is_dir():
        return families
    for ttf in sorted(d.glob("*.ttf")):
        font_id = QFontDatabase.addApplicationFont(str(ttf))
        if font_id != -1:
            families.extend(QFontDatabase.applicationFontFamilies(font_id))
    return families
