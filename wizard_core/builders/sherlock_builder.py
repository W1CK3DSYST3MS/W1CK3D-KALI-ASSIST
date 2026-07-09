"""sherlock command builder — OSINT username hunter across social networks.

Passive: it queries public profile URLs. Generate-only. Usernames are POSITIONAL;
options select sites, output format, and routing.
"""

from __future__ import annotations

import re
from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


def _as_list(v: object) -> list[str]:
    if isinstance(v, (list, tuple)):
        return [str(x) for x in v if str(x).strip()]
    return [p for p in re.split(r"[,\s]+", str(v)) if p]


@register_builder("sherlock")
def build_sherlock(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []   # ACTION_OPTIONS
    o: list[str] = []   # OUTPUT_OPTIONS
    env: list[str] = []  # ENV_INTERFACE (tor/proxy)
    pos: list[str] = []  # POSITIONAL_ARGS (usernames)

    if inputs.get("timeout"):
        a.extend(["--timeout", str(int(inputs["timeout"]))])
    for site in _as_list(inputs.get("sites") or ""):
        a.extend(["--site", site])
    if _truthy(inputs.get("print_found")):
        a.append("--print-found")
    if _truthy(inputs.get("nsfw")):
        a.append("--nsfw")

    if _truthy(inputs.get("csv")):
        o.append("--csv")
    if inputs.get("output"):
        o.extend(["--output", str(inputs["output"])])
    if inputs.get("folder_output"):
        o.extend(["--folderoutput", str(inputs["folder_output"])])

    if _truthy(inputs.get("tor")):
        env.append("--tor")
    if inputs.get("proxy"):
        env.extend(["--proxy", str(inputs["proxy"])])

    usernames = _as_list(inputs.get("username") or "")
    if usernames:
        pos.extend(usernames)
    else:
        notes.append("No username — supply at least one username to search for.")

    return assemble(
        "sherlock",
        {
            Slot.ACTION_OPTIONS: a,
            Slot.OUTPUT_OPTIONS: o,
            Slot.ENV_INTERFACE: env,
            Slot.POSITIONAL_ARGS: pos,
        },
        notes=notes,
    )
