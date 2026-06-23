"""Resource path resolution for both source checkout and PyInstaller bundle.

PyInstaller unpacks bundled data to ``sys._MEIPASS``. All access to assets/ and
modules/ goes through here so the app finds them in either layout.
"""

from __future__ import annotations

import sys
from pathlib import Path


def base_path() -> Path:
    """Repo root in a source checkout, or the unpack dir in a bundle."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return Path(__file__).resolve().parents[1]


def assets_dir() -> Path:
    return base_path() / "assets"


def modules_dir() -> Path:
    return base_path() / "modules"
