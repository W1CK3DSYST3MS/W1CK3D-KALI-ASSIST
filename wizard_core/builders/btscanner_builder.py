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
    a: list[str] = []   # ACTION_OPTIONS

    # Per the man page, btscanner's ONLY options are --help, --cfg <file> and
    # --no-reset; it is an interactive ncurses tool. Device dumps are written to
    # the 'device_path' configured in btscanner.conf, NOT via a command-line flag.
    if _truthy(inputs.get("no_reset")):
        a.append("--no-reset")
    if inputs.get("config"):
        a.extend(["--cfg", str(inputs["config"])])
    if not a:
        notes.append("btscanner is interactive: launch it, press 'i' for an inquiry scan. "
                     "Device dumps go to the 'device_path' set in its config file (btscanner.conf).")

    return assemble("btscanner", {Slot.ACTION_OPTIONS: a}, notes=notes)
