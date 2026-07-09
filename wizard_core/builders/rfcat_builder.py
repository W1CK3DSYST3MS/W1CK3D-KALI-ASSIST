"""rfcat command builder — sub-GHz RF transceiver research tool (e.g. YARD Stick One).

Opens an interactive Python REPL to receive/transmit sub-GHz RF. Generate-only.
Transmitting is heavily regulated — the module carries an authorization gate.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("rfcat")
def build_rfcat(inputs: Mapping[str, object]) -> CommandPlan:
    a: list[str] = []
    # -r launches the interactive research shell (the usual entry point).
    if inputs.get("interactive") is None or _truthy(inputs.get("interactive")):
        a.append("-r")
    if inputs.get("index") not in (None, ""):
        a.extend(["-i", str(int(inputs["index"]))])
    return assemble("rfcat", {Slot.ACTION_OPTIONS: a})
