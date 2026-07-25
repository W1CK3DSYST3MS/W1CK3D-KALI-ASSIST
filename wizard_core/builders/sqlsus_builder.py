"""sqlsus command builder — MySQL injection to an interactive shell.

Two shapes: ``sqlsus -g <file>`` generates a config template (the file is the
argument to -g, not a separate positional); ``sqlsus <file> [-e 'cmd']``
launches the interactive session (or runs one command and exits with -e).
Generate-only — building the command never actually launches the interactive
session from here.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("sqlsus")
def build_sqlsus(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-g/-e)
    pos: list[str] = []    # POSITIONAL_ARGS (config file, launch/execute mode)

    conf = inputs.get("conf_file")
    if not conf:
        notes.append("No config file — sqlsus needs one, either to generate (-g) or to launch.")

    if _truthy(inputs.get("genconf")):
        if conf:
            a.extend(["-g", str(conf)])
    else:
        if conf:
            pos.append(str(conf))
        if inputs.get("execute"):
            a.extend(["-e", str(inputs["execute"])])

    return assemble(
        "sqlsus",
        {
            Slot.ACTION_OPTIONS: a,
            Slot.POSITIONAL_ARGS: pos,
        },
        notes=notes,
    )
