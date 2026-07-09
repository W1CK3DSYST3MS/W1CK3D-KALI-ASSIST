"""blueranger command builder — locate a Bluetooth device by link quality.

A bash script that uses l2ping to raise link quality and estimate proximity to a
target device. Generate-only. Positional args: <hci interface> <target MAC>.
Runs privileged (l2ping needs root).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("blueranger")
def build_blueranger(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    pos: list[str] = []

    iface = str(inputs.get("iface") or "hci0")
    pos.append(iface)

    bdaddr = inputs.get("bdaddr")
    if bdaddr:
        pos.append(str(bdaddr))
    else:
        notes.append("No target MAC — supply the Bluetooth address (BD_ADDR) to locate.")

    elevation = None if _truthy(inputs.get("no_sudo")) else "sudo"

    return assemble(
        "blueranger",
        {Slot.POSITIONAL_ARGS: pos},
        notes=notes,
        elevation=elevation,
    )
