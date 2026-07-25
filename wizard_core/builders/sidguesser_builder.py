"""sidguesser command builder — Oracle SID brute-forcer.

The installed binary is ``sidguess`` (package name is ``sidguesser``).
Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


@register_builder("sidguesser")
def build_sidguesser(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-i/-d/-p/-m)
    o: list[str] = []      # OUTPUT_OPTIONS (-r)

    target = inputs.get("target")
    if target:
        a.extend(["-i", str(target)])
    else:
        notes.append("No target — sidguess needs -i <ip>.")

    dictionary = inputs.get("dictionary")
    if dictionary:
        a.extend(["-d", str(dictionary)])
    else:
        notes.append("No wordlist — sidguess needs -d <dictionary>.")

    if inputs.get("port"):
        a.extend(["-p", str(inputs["port"])])
    mode = inputs.get("mode")
    if mode:
        a.extend(["-m", str(mode)])

    if inputs.get("report"):
        o.extend(["-r", str(inputs["report"])])

    return assemble(
        "sidguess",
        {
            Slot.ACTION_OPTIONS: a,
            Slot.OUTPUT_OPTIONS: o,
        },
        notes=notes,
    )
