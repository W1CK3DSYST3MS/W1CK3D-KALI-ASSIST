"""exiftool command builder — reads embedded file metadata (GPS/device/dates).

Generate-only, and inherently read-only for this app's guided flows (no
write/-TAG=VALUE support here). Note: -json accepts an optional =FILE suffix
to write directly (``-json=out.json``) rather than needing shell redirection,
which the builder can't emit safely (tokens are shell-escaped individually).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("exiftool")
def build_exiftool(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-r/-gps:all/-common/-json)
    pos: list[str] = []    # POSITIONAL_ARGS (file or folder)

    if _truthy(inputs.get("recurse")):
        a.append("-r")
    if _truthy(inputs.get("gps_only")):
        a.append("-gps:all")
    if _truthy(inputs.get("common_only")) and not _truthy(inputs.get("gps_only")):
        a.append("-common")

    output = inputs.get("output")
    if _truthy(inputs.get("json")):
        a.append(f"-json={output}" if output else "-json")
    elif output:
        notes.append("A file was given but -json wasn't checked — exiftool's plain-text "
                      "output has no direct write-to-file flag here; redirect it yourself "
                      "with '> file' when you run the command.")

    target = inputs.get("target")
    if target:
        pos.append(str(target))
    else:
        notes.append("No file/folder — exiftool needs one.")

    return assemble(
        "exiftool",
        {
            Slot.ACTION_OPTIONS: a,
            Slot.POSITIONAL_ARGS: pos,
        },
        notes=notes,
    )
