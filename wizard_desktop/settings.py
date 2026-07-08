"""Tiny persistent UI settings (accessibility text scale, etc.).

Stored as JSON in the per-user state dir. Best-effort: any read/write error
falls back to defaults so the app always starts.
"""

from __future__ import annotations

import json
from pathlib import Path

_DEFAULTS: dict[str, object] = {
    "text_scale": 1.0,  # accessibility text-size multiplier (0.9–2.0 in the UI)
}


def _path() -> Path:
    base = Path.home() / ".w1ck3d-kali-assist"
    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.json"


def load_settings() -> dict:
    try:
        data = json.loads(_path().read_text(encoding="utf-8"))
        return {**_DEFAULTS, **(data if isinstance(data, dict) else {})}
    except Exception:
        return dict(_DEFAULTS)


def save_settings(settings: dict) -> None:
    try:
        _path().write_text(json.dumps(settings, indent=2), encoding="utf-8")
    except Exception:
        pass  # settings are a convenience, never fatal


def get_text_scale() -> float:
    try:
        return float(load_settings().get("text_scale", 1.0))
    except (TypeError, ValueError):
        return 1.0


def set_text_scale(scale: float) -> None:
    s = load_settings()
    s["text_scale"] = round(float(scale), 2)
    save_settings(s)
