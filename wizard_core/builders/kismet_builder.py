"""kismet command builder — wireless (Wi-Fi/Bluetooth) detector & sniffer.

Passively detects networks/devices and logs them; a web UI shows results.
Generate-only. Capture sources are added with -c; runs privileged. Per
`kismet --help`, nearly all flags are just run-time overrides for
kismet.conf — this builder covers the handful worth exposing directly:
-c/--no-ncurses/--log-prefix plus -T/--log-types, -f/--config-file and
--daemonize.
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
    g: list[str] = []      # GLOBAL_OPTIONS (--no-ncurses/--daemonize/-f)
    env: list[str] = []    # ENV_INTERFACE (-c source)
    o: list[str] = []      # OUTPUT_OPTIONS (--log-prefix/--log-types)

    if _truthy(inputs.get("no_ncurses")):
        g.append("--no-ncurses")
    if inputs.get("config_file"):
        g.extend(["-f", str(inputs["config_file"])])
    if _truthy(inputs.get("daemonize")):
        g.append("--daemonize")
    source = inputs.get("source")
    if source:
        env.extend(["-c", str(source)])
    else:
        notes.append("No capture source — add one with -c (e.g. -c wlan0) or in the web UI.")
    if inputs.get("log_types"):
        o.extend(["--log-types", str(inputs["log_types"])])
    if inputs.get("log_prefix"):
        o.extend(["--log-prefix", str(inputs["log_prefix"])])

    elevation = None if _truthy(inputs.get("no_sudo")) else "sudo"
    return assemble("kismet", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ENV_INTERFACE: env,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes, elevation=elevation)
