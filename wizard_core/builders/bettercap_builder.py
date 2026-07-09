"""bettercap command builder — network attack/MITM framework.

Very powerful (ARP/DNS spoofing, sniffing, MITM). Runs privileged. Generate-only.
-iface selects the interface; -eval runs interactive-console commands on start;
-caplet loads a script. The module carries an authorization gate for a reason.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("bettercap")
def build_bettercap(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    g: list[str] = []      # GLOBAL_OPTIONS
    env: list[str] = []    # ENV_INTERFACE (-iface)
    a: list[str] = []      # ACTION_OPTIONS (-eval)
    extra: list[str] = []  # EXTRA_FILES (-caplet)

    iface = inputs.get("iface")
    if iface:
        env.extend(["-iface", str(iface)])
    else:
        notes.append("No -iface — bettercap picks a default interface; set one to be explicit.")

    if _truthy(inputs.get("silent")):
        g.append("-silent")
    if _truthy(inputs.get("no_colors")):
        g.append("-no-colors")

    if inputs.get("caplet"):
        extra.extend(["-caplet", str(inputs["caplet"])])
    if inputs.get("eval"):
        a.extend(["-eval", str(inputs["eval"])])

    # bettercap needs root for raw sockets / spoofing.
    elevation = None if _truthy(inputs.get("no_sudo")) else "sudo"

    return assemble(
        "bettercap",
        {
            Slot.GLOBAL_OPTIONS: g,
            Slot.ENV_INTERFACE: env,
            Slot.ACTION_OPTIONS: a,
            Slot.EXTRA_FILES: extra,
        },
        notes=notes,
        elevation=elevation,
    )
