"""netexec command builder — network execution / AD testing swiss-army knife.

netexec <protocol> <target> [options]. The protocol is a subcommand, the
target(s) are positional (TARGET_PIVOT), everything else — credentials,
enumeration flags, execution — is ACTION_OPTIONS. Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("netexec")
def build_netexec(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    t: list[str] = []      # TARGET_PIVOT
    a: list[str] = []      # ACTION_OPTIONS

    protocol = str(inputs.get("protocol") or "smb")

    target = inputs.get("target")
    if target:
        t.append(str(target))
    else:
        notes.append("No target — netexec needs an IP/CIDR/hostname/file of targets.")

    if inputs.get("username"):
        a.extend(["-u", str(inputs["username"])])
    if inputs.get("password"):
        a.extend(["-p", str(inputs["password"])])
    if inputs.get("hash"):
        a.extend(["-H", str(inputs["hash"])])
    if inputs.get("domain"):
        a.extend(["-d", str(inputs["domain"])])
    if _truthy(inputs.get("local_auth")):
        a.append("--local-auth")
    if _truthy(inputs.get("shares")):
        a.append("--shares")
    if _truthy(inputs.get("sam")):
        a.append("--sam")
    if inputs.get("exec_command"):
        a.extend(["-x", str(inputs["exec_command"])])

    return assemble(
        "netexec",
        {
            Slot.TARGET_PIVOT: t,
            Slot.ACTION_OPTIONS: a,
        },
        notes=notes,
        subcommand=[protocol],
    )
