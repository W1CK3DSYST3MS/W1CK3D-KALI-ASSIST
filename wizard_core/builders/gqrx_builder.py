"""gqrx command builder — SDR (software-defined radio) receiver GUI.

Receive-only spectrum/audio from an SDR device. Generate-only. gqrx is a GUI app;
its CLI only selects a config, lists devices, or edits/resets the config — there
is NO command-line device-select flag. The device is always chosen in the GUI's
Configure I/O Devices dialog (optionally remembered in a config file via -c).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("gqrx")
def build_gqrx(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    g: list[str] = []      # GLOBAL_OPTIONS (edit/reset/list)
    extra: list[str] = []  # EXTRA_FILES (config)

    if _truthy(inputs.get("list_devices")):
        return assemble("gqrx", {Slot.GLOBAL_OPTIONS: ["-l"]},
                        notes=["Lists SDR devices gqrx can see."])
    if _truthy(inputs.get("edit")):
        g.append("-e")
    if _truthy(inputs.get("reset")):
        g.append("-r")
    if inputs.get("config"):
        extra.extend(["-c", str(inputs["config"])])

    return assemble("gqrx", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.EXTRA_FILES: extra,
    }, notes=notes)
