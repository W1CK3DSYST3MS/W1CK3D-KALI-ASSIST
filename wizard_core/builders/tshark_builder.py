"""tshark command builder (Module 09 spec).

Shape: tshark [global] -i <iface> | -r <file> [filters] [output]. The source is
EXACTLY ONE of -i (live) or -r (file) — the builder refuses both. Teaches the
capture-filter (-f, BPF) vs display-filter (-Y, Wireshark) vs read-filter (-R,
requires -2 two-pass) three-way distinction by keeping them separate. Also
covers ring-buffer file rotation (-b), autostop conditions beyond packet count
(-a filesize/files/duration), and Decode-As (-d). Generate-only; capture is
privacy-sensitive.

2026-07-26: extended to cover tshark's FULL `--help`/`man tshark` surface (an
earlier pass only covered a "major gaps" list, not the exhaustive option set —
see docs/DEPTH-AUDIT.md). Recognised keys (all optional except a source):
list_interfaces, list_link_types, source_iface, read_file, no_resolve, quiet,
quiet_errors_only, count, duration, autostop_filesize, autostop_files,
capture_filter, display_filter, read_filter, two_pass, name_resolve_flags,
decode_as, stats, fields, csv_header, output_type, protocol_filter,
protocol_filter_top, timestamp_format, seconds_format, verbose_tree,
detail_protocols, hex_dump, hexdump_opts, print_even_writing, color_output,
only_protocols, enable_protocol, disable_protocol, write, ring_filesize,
ring_files, ring_duration, output_format, save_network_addrs, export_objects,
snaplen, no_promiscuous, monitor_mode, buffer_size.
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

    # Standalone: list link-layer types for one interface, then exit.
    if _truthy(inputs.get("list_link_types")):
        iface = inputs.get("source_iface")
        if not iface:
            raise ValueError("list_link_types (-L) needs an interface — set Capture interface.")
        return assemble("tshark", {
            Slot.TARGET_PIVOT: ["-i", str(iface)],
            Slot.ENV_INTERFACE: ["-L"],
        }, notes=["Lists link-layer types tshark can use on this interface, then exits."])

    g: list[str] = []   # GLOBAL_OPTIONS
    a: list[str] = []   # ACTION_OPTIONS (filters / fields / stats / display tweaks)
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
    if _truthy(inputs.get("quiet_errors_only")):
        g.append("-Q")
    if _truthy(inputs.get("two_pass")):
        g.append("-2")
    if inputs.get("name_resolve_flags"):
        g.extend(["-N", str(inputs["name_resolve_flags"])])
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

    # ACTION: capture filter (BPF) vs display filter (Wireshark) vs read filter
    # (Wireshark syntax too, but applied during a second pass — needs -2).
    if inputs.get("capture_filter"):
        if read_file:
            notes.append("Capture filter (-f) only applies to live capture; use -Y on a read file.")
        a.extend(["-f", str(inputs["capture_filter"])])
    if inputs.get("display_filter"):
        a.extend(["-Y", str(inputs["display_filter"])])
    read_filter = inputs.get("read_filter")
    if read_filter:
        a.extend(["-R", str(read_filter)])
        if "-2" not in g:
            g.append("-2")
            notes.append("Added -2 (two-pass analysis) — -R only works during a second pass.")
    if inputs.get("decode_as"):
        a.extend(["-d", str(inputs["decode_as"])])
    if inputs.get("stats"):
        a.extend(["-z", str(inputs["stats"])])
        if "-q" not in g:
            g.append("-q")  # stats want quiet mode
            notes.append("Added -q (stats are printed with -q -z).")

    # Field extraction (CSV-style) vs a plain -T <type> (json/pdml/ek/...).
    fields = inputs.get("fields")
    output_type = inputs.get("output_type")
    if fields:
        field_list = fields if isinstance(fields, (list, tuple)) else str(fields).split(",")
        a.append("-T")
        a.append("fields")
        for f in field_list:
            a.extend(["-e", str(f).strip()])
        if _truthy(inputs.get("csv_header")):
            o.extend(["-E", "header=y", "-E", "separator=,"])
        if output_type and str(output_type) != "fields":
            notes.append("Extract fields (-e) already sets -T fields — Output type is ignored while fields are set.")
    elif output_type and str(output_type) != "text":
        a.extend(["-T", str(output_type)])

    # -j/-J protocol filters only make sense alongside -T ek|pdml|json.
    _EK_LIKE = {"ek", "pdml", "json"}
    protocol_filter = inputs.get("protocol_filter")
    protocol_filter_top = inputs.get("protocol_filter_top")
    if protocol_filter:
        a.extend(["-j", str(protocol_filter)])
        if not fields and str(output_type or "") not in _EK_LIKE:
            notes.append("-j only takes effect with Output type set to ek, pdml or json.")
    if protocol_filter_top:
        a.extend(["-J", str(protocol_filter_top)])
        if not fields and str(output_type or "") not in _EK_LIKE:
            notes.append("-J only takes effect with Output type set to ek, pdml or json.")

    if inputs.get("timestamp_format"):
        a.extend(["-t", str(inputs["timestamp_format"])])
    if inputs.get("seconds_format"):
        a.extend(["-u", str(inputs["seconds_format"])])

    # Packet-detail display: full protocol tree (-V), narrow it to protocols
    # (-O), hex+ASCII dump (-x [--hexdump opts]), force printing while writing
    # to a file (-P), and GUI-style colored terminal output (--color).
    if _truthy(inputs.get("verbose_tree")):
        a.append("-V")
    detail_protocols = inputs.get("detail_protocols")
    if detail_protocols:
        a.extend(["-O", str(detail_protocols)])
        if not _truthy(inputs.get("verbose_tree")):
            notes.append("-O narrows packet DETAIL output — it's normally used together with -V (Full protocol tree).")
    hexdump_opts = inputs.get("hexdump_opts")
    if _truthy(inputs.get("hex_dump")) or hexdump_opts:
        if "-x" not in a:
            a.append("-x")
        if hexdump_opts:
            a.extend(["--hexdump", str(hexdump_opts)])
    if _truthy(inputs.get("print_even_writing")):
        a.append("-P")
        if not inputs.get("write"):
            notes.append("-P (print while writing) has no extra effect without Save capture to file (-w) — tshark already prints when not writing.")
    if _truthy(inputs.get("color_output")):
        a.append("--color")

    # Dissection control — narrow/disable which protocols tshark even parses.
    if inputs.get("only_protocols"):
        a.extend(["--only-protocols", str(inputs["only_protocols"])])
    if inputs.get("enable_protocol"):
        a.extend(["--enable-protocol", str(inputs["enable_protocol"])])
    if inputs.get("disable_protocol"):
        a.extend(["--disable-protocol", str(inputs["disable_protocol"])])

    # OUTPUT
    if inputs.get("write"):
        o.extend(["-w", str(inputs["write"])])

    # Ring buffer / file rotation — keeps a bounded window of recent traffic
    # instead of one ever-growing file. Needs -w (a base filename to rotate).
    ring_filesize = inputs.get("ring_filesize")
    ring_files = inputs.get("ring_files")
    ring_duration = inputs.get("ring_duration")
    if ring_filesize not in (None, ""):
        o.extend(["-b", f"filesize:{int(ring_filesize)}"])
    if ring_duration not in (None, ""):
        o.extend(["-b", f"duration:{int(ring_duration)}"])
    if ring_files not in (None, ""):
        o.extend(["-b", f"files:{int(ring_files)}"])
    if (ring_filesize or ring_files or ring_duration) and not inputs.get("write"):
        notes.append(
            "-b (ring buffer) rotates the file named by -w — set Write to file, or -b has "
            "nothing to rotate."
        )

    output_format = inputs.get("output_format")
    if output_format:
        o.extend(["-F", str(output_format)])
    if _truthy(inputs.get("save_network_addrs")):
        o.extend(["-W", "n"])
    export_objects = inputs.get("export_objects")
    if export_objects:
        o.extend(["--export-objects", str(export_objects)])

    # ENV / capture setup
    if inputs.get("snaplen"):
        env.extend(["-s", str(int(inputs["snaplen"]))])
    if _truthy(inputs.get("no_promiscuous")):
        env.append("-p")
    if _truthy(inputs.get("monitor_mode")):
        env.append("-I")
    if inputs.get("buffer_size"):
        env.extend(["-B", str(int(inputs["buffer_size"]))])

    return assemble("tshark", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: src,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
    }, notes=notes)
