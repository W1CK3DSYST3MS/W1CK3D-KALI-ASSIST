"""heartleech command builder — Heartbleed (CVE-2014-0160) scanner/exploiter.

Tests a TLS service for Heartbleed and can dump leaked memory. Generate-only.
Exploitation tool -> the module is authorization-gated. hostname is POSITIONAL.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("heartleech")
def build_heartleech(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (port / scan / autopwn)
    o: list[str] = []      # OUTPUT_OPTIONS (--dump)
    pos: list[str] = []    # POSITIONAL_ARGS (hostname)

    if inputs.get("port"):
        a.extend(["--port", str(int(inputs["port"]))])
    if _truthy(inputs.get("scan")):
        a.append("--scan")
    if _truthy(inputs.get("autopwn")):
        a.append("--autopwn")
    if inputs.get("dump"):
        o.extend(["--dump", str(inputs["dump"])])

    target = inputs.get("target")
    if target:
        pos.append(str(target))
    else:
        notes.append("No target — supply the hostname/IP of the TLS service to test.")

    return assemble("heartleech", {
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.POSITIONAL_ARGS: pos,
    }, notes=notes)
