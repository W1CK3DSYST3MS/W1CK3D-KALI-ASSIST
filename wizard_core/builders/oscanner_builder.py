"""oscanner command builder — Oracle default-account scanner.

-s (single target) and -f (host-list file) are mutually exclusive per oscanner's
own usage; -r (report file) is required. Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("oscanner")
def build_oscanner(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-s/-f/-P)
    o: list[str] = []      # OUTPUT_OPTIONS (-r)

    target = inputs.get("target")
    host_file = inputs.get("host_file")
    if target and host_file:
        notes.append("Both a target and a host-list file were given — oscanner takes only one; -s is used here.")
        host_file = None
    if target:
        a.extend(["-s", str(target)])
    elif host_file:
        a.extend(["-f", str(host_file)])
    else:
        notes.append("No target — oscanner needs -s <host> or -f <hostlist>.")

    if inputs.get("port"):
        a.extend(["-P", str(inputs["port"])])
    if _truthy(inputs.get("verbose")):
        a.append("-v")

    report = inputs.get("report") or "oscanner-report.txt"
    o.extend(["-r", str(report)])

    return assemble(
        "oscanner",
        {
            Slot.ACTION_OPTIONS: a,
            Slot.OUTPUT_OPTIONS: o,
        },
        notes=notes,
    )
