"""theHarvester command builder — company/domain OSINT (emails, subdomains, hosts).

Generate-only. -c/-t actively touch DNS and check for takeovers, so the
authorization gate covers that, not just passive source queries.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("theharvester")
def build_theharvester(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-d/-b/-l/-c/-r/-t)
    o: list[str] = []      # OUTPUT_OPTIONS (-f)

    domain = inputs.get("domain")
    if domain:
        a.extend(["-d", str(domain)])
    else:
        notes.append("No domain — theHarvester needs -d <domain>.")

    sources = inputs.get("sources")
    if sources:
        a.extend(["-b", str(sources)])
    else:
        notes.append("No -b source — theHarvester requires at least one (e.g. crtsh, no API key needed).")

    if inputs.get("limit"):
        a.extend(["-l", str(inputs["limit"])])
    if _truthy(inputs.get("dns_brute")):
        a.append("-c")
    if _truthy(inputs.get("dns_resolve")):
        a.append("-r")
    if _truthy(inputs.get("take_over")):
        a.append("-t")

    if inputs.get("filename"):
        o.extend(["-f", str(inputs["filename"])])

    return assemble(
        "theHarvester",
        {
            Slot.ACTION_OPTIONS: a,
            Slot.OUTPUT_OPTIONS: o,
        },
        notes=notes,
    )
