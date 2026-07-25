"""responder command builder — LLMNR/NBT-NS/mDNS poisoner + rogue auth servers.

Poisons name resolution for the WHOLE network segment it's run on, not a single
target — there is no target host, only an interface. Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("responder")
def build_responder(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    env: list[str] = []    # ENV_INTERFACE (-I)
    a: list[str] = []      # ACTION_OPTIONS

    iface = inputs.get("iface")
    if iface:
        env.extend(["-I", str(iface)])
    else:
        notes.append("No -I — Responder requires an interface; pick one with `ip a`.")

    if _truthy(inputs.get("analyze")):
        a.append("-A")
    if _truthy(inputs.get("verbose")):
        a.append("-v")
    if _truthy(inputs.get("basic")):
        a.append("-b")
    if _truthy(inputs.get("wpad")):
        a.append("-w")

    return assemble(
        "responder",
        {
            Slot.ENV_INTERFACE: env,
            Slot.ACTION_OPTIONS: a,
        },
        notes=notes,
        elevation="sudo",
    )
