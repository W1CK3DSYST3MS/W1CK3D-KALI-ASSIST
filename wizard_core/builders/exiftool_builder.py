"""exiftool command builder — reads embedded file metadata (GPS/device/dates).

Generate-only. Primarily read-only, but also supports the common defensive/
privacy use case of STRIPPING metadata before sharing a file (``-all=`` /
``-gps:all=``, per `man exiftool` "WRITING EXAMPLES" and the -TAG=[VALUE]
assignment syntax) — that's a real, intentional write operation, gated behind
its own fields and kept mutually exclusive with the read-mode flags so a
single build never mixes "show me the tags" with "delete the tags". Note:
-json accepts an optional =FILE suffix to write directly (``-json=out.json``)
rather than needing shell redirection, which the builder can't emit safely
(tokens are shell-escaped individually).
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
    a: list[str] = []      # ACTION_OPTIONS (-r/-gps:all/-common/-json/-all=/-gps:all=)
    pos: list[str] = []    # POSITIONAL_ARGS (file or folder)

    if _truthy(inputs.get("recurse")):
        a.append("-r")

    strip_all = _truthy(inputs.get("strip_all"))
    strip_gps = _truthy(inputs.get("strip_gps"))
    if strip_all or strip_gps:
        # Write mode: strip metadata. Mutually exclusive with the read-only flags below.
        if _truthy(inputs.get("overwrite_original")):
            a.append("-overwrite_original")
        if strip_all:
            a.append("-all=")
            notes.append(
                "-all= deletes ALL metadata from the file (a real write, not just a display "
                "option). By default exiftool keeps the untouched original as <file>_original "
                "— tick Overwrite original only once you're sure you don't need that backup."
            )
        else:
            a.append("-gps:all=")
            notes.append(
                "-gps:all= deletes only the GPS tags, leaving other metadata (camera, dates) "
                "intact. By default exiftool keeps the untouched original as <file>_original "
                "— tick Overwrite original only once you're sure you don't need that backup."
            )
        if _truthy(inputs.get("gps_only")) or _truthy(inputs.get("common_only")) or _truthy(inputs.get("json")):
            notes.append(
                "Read-only display flags (GPS only / Common only / JSON) are ignored while "
                "stripping metadata — this is a write operation, pick one mode at a time."
            )
    else:
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
