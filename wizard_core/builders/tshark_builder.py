"""tshark command builder (Module 09 spec).

Shape: tshark [global] -i <iface> | -r <file> [filters] [output]. The source is
EXACTLY ONE of -i (live) or -r (file) — the builder refuses both. Teaches the
capture-filter (-f, BPF) vs display-filter (-Y, Wireshark) distinction by keeping
them separate. Also covers ring-buffer file rotation (-b), autostop conditions
beyond packet count (-a filesize/files/duration), and Decode-As (-d). Generate-
only; capture is privacy-sensitive.

Recognised keys (all optional except a source): list_interfaces, source_iface,
read_file, no_resolve, quiet, count, duration, autostop_filesize, autostop_files,
capture_filter, display_filter, decode_as, stats, fields, csv_header, write,
ring_filesize, ring_files, snaplen, no_promiscuous.
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

    # Autostop conditions beyond packet count/duration — each -a is a separate
    # "stop the whole capture when..." condition (any one of them ends the run).
    # Not to be confused with -b (ring buffer), which rotates files forever.
    if inputs.get("autostop_filesize") not in (None, ""):
        g.extend(["-a", f"filesize:{int(inputs['autostop_filesize'])}"])
    if inputs.get("autostop_files") not in (None, ""):
        g.extend(["-a", f"files:{int(inputs['autostop_files'])}"])

    # ACTION: capture filter (BPF) vs display filter (Wireshark)
    if inputs.get("capture_filter"):
        if read_file:
            notes.append("Capture filter (-f) only applies to live capture; use -Y on a read file.")
        a.extend(["-f", str(inputs["capture_filter"])])
    if inputs.get("display_filter"):
        a.extend(["-Y", str(inputs["display_filter"])])
    if inputs.get("decode_as"):
        a.extend(["-d", str(inputs["decode_as"])])
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

    # Ring buffer / file rotation — keeps a bounded window of recent traffic
    # instead of one ever-growing file. Needs -w (a base filename to rotate).
    ring_filesize = inputs.get("ring_filesize")
    ring_files = inputs.get("ring_files")
    if ring_filesize not in (None, ""):
        o.extend(["-b", f"filesize:{int(ring_filesize)}"])
    if ring_files not in (None, ""):
        o.extend(["-b", f"files:{int(ring_files)}"])
    if (ring_filesize or ring_files) and not inputs.get("write"):
        notes.append(
            "-b (ring buffer) rotates the file named by -w — set Write to file, or -b has "
            "nothing to rotate."
        )

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
