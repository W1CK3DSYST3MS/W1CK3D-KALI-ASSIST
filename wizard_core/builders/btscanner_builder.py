"""btscanner command builder — interactive Bluetooth device scanner (ncurses).

Discovers nearby discoverable Bluetooth devices and reads their info. Generate-only.
The tool itself is an interactive TUI; the command mainly selects the adapter/output.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("btscanner")
def build_btscanner(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    o: list[str] = []     # OUTPUT_OPTIONS

    # btscanner is primarily an interactive ncurses tool: you launch it, then use
    # in-app keys (i = inquiry scan) to discover devices. It writes device dumps
    # to an output directory (-o); the adapter is prepared beforehand with
    # hciconfig/rfkill, not a btscanner flag. Keep the command honest and minimal.
    if inputs.get("output_dir"):
        o.extend(["-o", str(inputs["output_dir"])])
    else:
        notes.append("btscanner is interactive: launch it, press 'i' to run an inquiry scan. -o saves device dumps to a directory.")

    return assemble("btscanner", {Slot.OUTPUT_OPTIONS: o}, notes=notes)
