"""tshark command builder (Module 09 spec).

Shape: tshark [global] -i <iface> | -r <file> [filters] [output]. The source is
EXACTLY ONE of -i (live) or -r (file) — the builder refuses both. Teaches the
capture-filter (-f, BPF) vs display-filter (-Y, Wireshark) distinction by keeping
them separate. Generate-only; capture is privacy-sensitive.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("tshark")
def build_tshark(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []

    # Standalone: list interfaces.
    if _truthy(inputs.get("list_interfaces")):
        return assemble("tshark", {Slot.ENV_INTERFACE: ["-D"]},
                        notes=["Lists capture interfaces by number and name."])

    g: list[str] = []   # GLOBAL_OPTIONS
    a: list[str] = []   # ACTION_OPTIONS (filters / fields / stats)
    o: list[str] = []   # OUTPUT_OPTIONS
    env: list[str] = []  # ENV_INTERFACE
    src: list[str] = []  # TARGET_PIVOT (-i or -r)

    # SOURCE — exactly one of live (-i) or read (-r).
    iface = inputs.get("source_iface")
    read_file = inputs.get("read_file")
    if iface and read_file:
        raise ValueError("Set EITHER source_iface (-i, live) OR read_file (-r, file), not both.")
    if iface:
        src = ["-i", str(iface)]
    elif read_file:
        src = ["-r", str(read_file)]
    else:
        notes.append("No source — supply a live interface (-i) or a pcap to read (-r).")

    # GLOBAL
    if _truthy(inputs.get("no_resolve")):
        g.append("-n")
    if _truthy(inputs.get("quiet")):
        g.append("-q")
    if inputs.get("count") not in (None, ""):
        g.extend(["-c", str(int(inputs["count"]))])
    if inputs.get("duration") not in (None, ""):
        g.extend(["-a", f"duration:{int(inputs['duration'])}"])

    # ACTION: capture filter (BPF) vs display filter (Wireshark)
    if inputs.get("capture_filter"):
        if read_file:
            notes.append("Capture filter (-f) only applies to live capture; use -Y on a read file.")
        a.extend(["-f", str(inputs["capture_filter"])])
    if inputs.get("display_filter"):
        a.extend(["-Y", str(inputs["display_filter"])])
    if inputs.get("stats"):
        a.extend(["-z", str(inputs["stats"])])
        if "-q" not in g:
            g.append("-q")  # stats want quiet mode
            notes.append("Added -q (stats are printed with -q -z).")

    # Field extraction (CSV-style)
    fields = inputs.get("fields")
    if fields:
        field_list = fields if isinstance(fields, (list, tuple)) else str(fields).split(",")
        a.append("-T")
        a.append("fields")
        for f in field_list:
            a.extend(["-e", str(f).strip()])
        if _truthy(inputs.get("csv_header")):
            o.extend(["-E", "header=y", "-E", "separator=,"])

    # OUTPUT
    if inputs.get("write"):
        o.extend(["-w", str(inputs["write"])])

    # ENV / capture setup
    if inputs.get("snaplen"):
        env.extend(["-s", str(int(inputs["snaplen"]))])
    if _truthy(inputs.get("no_promiscuous")):
        env.append("-p")

    return assemble("tshark", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: src,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
    }, notes=notes)
