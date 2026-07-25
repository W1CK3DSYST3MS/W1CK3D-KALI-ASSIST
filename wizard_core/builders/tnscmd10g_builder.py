"""tnscmd10g command builder — raw Oracle TNS listener prober.

Usage is ``tnscmd10g [command] -h host [options]``: the command (version/
status/ping) must come immediately after the program name, before any flags
— its simple hand-rolled arg parser expects that position, unlike getopt-style
tools where flag order doesn't matter. Modelled the same way as gobuster's/
netexec's subcommand (rendered right after PROGRAM, ahead of every slot).
--rawcmd replaces the preset command entirely. Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


@register_builder("tnscmd10g")
def build_tnscmd10g(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-h/-p/--rawcmd)

    rawcmd = inputs.get("rawcmd")
    command = inputs.get("command")
    subcommand: list[str] = []
    if rawcmd:
        a.extend(["--rawcmd", str(rawcmd)])
        if command:
            notes.append("Both a preset command and --rawcmd were given — --rawcmd takes over; the preset is ignored.")
    elif command:
        subcommand.append(str(command))

    host = inputs.get("host")
    if host:
        a.extend(["-h", str(host)])
    else:
        notes.append("No target — tnscmd10g needs -h <host>.")

    if inputs.get("port"):
        a.extend(["-p", str(inputs["port"])])

    return assemble(
        "tnscmd10g",
        {Slot.ACTION_OPTIONS: a},
        notes=notes,
        subcommand=subcommand,
    )
