"""dirbuster command builder — OWASP web content brute-forcer (Java GUI).

Primarily a GUI; supports a headless (-H) mode with -u url / -l wordlist / -r report,
plus the scan-tuning flags -t/-s/-g/-R/-v (per `dirbuster -h`). Generate-only. Bare
`dirbuster` launches the GUI.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("dirbuster")
def build_dirbuster(inputs: Mapping[str, object]) -> CommandPlan:
    g: list[str] = []      # GLOBAL_OPTIONS (-H headless, -v verbose)
    env: list[str] = []    # ENV_INTERFACE (-u url)
    a: list[str] = []      # ACTION_OPTIONS (-e extensions, -t/-s/-g/-R)
    o: list[str] = []      # OUTPUT_OPTIONS (-r report)
    extra: list[str] = []  # EXTRA_FILES (-l wordlist)

    if _truthy(inputs.get("headless")):
        g.append("-H")
    if _truthy(inputs.get("verbose")):
        g.append("-v")
    if inputs.get("url"):
        env.extend(["-u", str(inputs["url"])])
    if inputs.get("extensions"):
        a.extend(["-e", str(inputs["extensions"])])
    threads = inputs.get("threads")
    if threads:
        a.extend(["-t", str(int(threads))])
    if inputs.get("start_point"):
        a.extend(["-s", str(inputs["start_point"])])
    if _truthy(inputs.get("get_only")):
        a.append("-g")
    if _truthy(inputs.get("non_recursive")):
        a.append("-R")
    if inputs.get("report"):
        o.extend(["-r", str(inputs["report"])])
    if inputs.get("wordlist"):
        extra.extend(["-l", str(inputs["wordlist"])])

    return assemble("dirbuster", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ENV_INTERFACE: env,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.EXTRA_FILES: extra,
    })
