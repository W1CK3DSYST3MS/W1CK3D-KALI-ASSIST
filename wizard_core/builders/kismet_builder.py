"""kismet command builder — wireless (Wi-Fi/Bluetooth) detector & sniffer.

Passively detects networks/devices and logs them; a web UI shows results.
Generate-only. Capture sources are added with -c; runs privileged.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("kismet")
def build_kismet(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    g: list[str] = []      # GLOBAL_OPTIONS (--no-ncurses)
    env: list[str] = []    # ENV_INTERFACE (-c source)
    o: list[str] = []      # OUTPUT_OPTIONS (--log-prefix)

    if _truthy(inputs.get("no_ncurses")):
        g.append("--no-ncurses")
    source = inputs.get("source")
    if source:
        env.extend(["-c", str(source)])
    else:
        notes.append("No capture source — add one with -c (e.g. -c wlan0) or in the web UI.")
    if inputs.get("log_prefix"):
        o.extend(["--log-prefix", str(inputs["log_prefix"])])

    elevation = None if _truthy(inputs.get("no_sudo")) else "sudo"
    return assemble("kismet", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ENV_INTERFACE: env,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes, elevation=elevation)
