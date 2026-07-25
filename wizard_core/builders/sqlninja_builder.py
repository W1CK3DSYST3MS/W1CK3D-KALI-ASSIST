"""sqlninja command builder — MSSQL injection to OS-level access.

Unlike most tools here, sqlninja doesn't take a target URL/IP on the command
line at all — everything about the target (the vulnerable HTTP request, the
injection marker) lives in a config file (-f), authored ahead of time.
Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("sqlninja")
def build_sqlninja(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-m/-p/-w/-v)
    extra: list[str] = []  # EXTRA_FILES (-f)

    mode = inputs.get("mode")
    if mode:
        a.extend(["-m", str(mode)])
    else:
        notes.append("No -m — sqlninja requires a mode (t=test is the safe first choice).")

    if inputs.get("password"):
        a.extend(["-p", str(inputs["password"])])
    if inputs.get("wordlist"):
        a.extend(["-w", str(inputs["wordlist"])])
    if _truthy(inputs.get("verbose")):
        a.append("-v")

    conf = inputs.get("conf_file") or "sqlninja.conf"
    extra.extend(["-f", str(conf)])

    return assemble(
        "sqlninja",
        {
            Slot.ACTION_OPTIONS: a,
            Slot.EXTRA_FILES: extra,
        },
        notes=notes,
    )
