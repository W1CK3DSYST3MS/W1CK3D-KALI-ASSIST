"""gvm command builder — Greenbone Vulnerability Management (OpenVAS) control.

Starts/stops and sets up the GVM services (the scanner you then use via its web UI).
Generate-only. Each action maps to a distinct gvm-* binary; most need root.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from .common import assemble, register_builder

_ACTIONS = {
    "start": "gvm-start",
    "stop": "gvm-stop",
    "check-setup": "gvm-check-setup",
    "setup": "gvm-setup",
    "feed-update": "gvm-feed-update",
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("gvm")
def build_gvm(inputs: Mapping[str, object]) -> CommandPlan:
    action = str(inputs.get("action") or "start")
    program = _ACTIONS.get(action)
    if program is None:
        raise ValueError(f"Unknown gvm action {action!r}. Valid: {', '.join(_ACTIONS)}")
    elevation = None if _truthy(inputs.get("no_sudo")) else "sudo"
    return assemble(program, {}, elevation=elevation,
                    notes=[f"gvm action '{action}' -> {program}."])
