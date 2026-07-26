"""nmap command builder (Module 02 spec).

Drives every nmap flow (discovery, portscan, service/version, OS, UDP, NSE,
timing/stealth, output, full) from one validated-inputs dict. Targets are
*positional* in nmap, so they always occupy TARGET_PIVOT and scan/output flags
never drift into that position (spec §3 builder note).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

# Profile presets (spec §4) -> tokens that pre-fill the hard slots (2 + 4).
# Each entry: GLOBAL_OPTIONS tokens, ACTION_OPTIONS tokens.
_PROFILES: dict[str, dict[str, list[str]]] = {
    "quick": {"global": ["-T4"], "action": ["-F"]},
    "standard": {"global": ["-T4"], "action": ["-sV", "--top-ports", "1000"]},
    "thorough": {"global": ["-T4"], "action": ["-sV", "-O", "-p-"]},
    "quiet": {"global": ["-T2", "-Pn"], "action": ["-sS"]},
}

_OUTPUT_FLAG = {"normal": "-oN", "xml": "-oX", "grep": "-oG", "all": "-oA"}


def _as_bool(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("nmap")
def build_nmap(inputs: Mapping[str, object]) -> CommandPlan:
    """Build an nmap CommandPlan from validated inputs.

    2026-07-26: extended to cover nmap's FULL `--help` surface (previous pass
    only covered the "major gaps" a first audit flagged, which itself wasn't
    exhaustive — see docs/DEPTH-AUDIT.md). Recognised keys (all optional
    except ``targets``):
      profile, targets, scan_type, ports, top_ports, fast, all_ports,
      service_version, os_detect, aggressive, scripts, script_args,
      timing(0-5), no_dns, skip_host_discovery, verbose, reason,
      output_format(+output_path), input_list, interface, privileged,
      fragment, decoys, spoof_source_ip, source_port, spoof_mac,
      exclude, exclude_file, random_targets, resolve_all, dns_servers,
      system_dns, traceroute, ping_syn, ping_ack, ping_udp, ping_sctp,
      ping_echo, ping_timestamp, ping_netmask, ping_protocol,
      idle_zombie, scan_flags, ftp_bounce, exclude_ports,
      sequential_ports, version_intensity, version_light, version_trace,
      script_default, script_args_file, script_trace, script_updatedb,
      script_help, osscan_limit, osscan_guess, min_rate, max_rate,
      host_timeout, max_retries, scan_delay, max_scan_delay, proxies,
      data_payload, data_string, data_length, ip_options, ttl, badsum,
      debug, show_open_only, packet_trace, iflist, append_output, resume,
      ipv6, assume_privileged, assume_unprivileged.
    """
    g: list[str] = []   # GLOBAL_OPTIONS
    a: list[str] = []   # ACTION_OPTIONS
    o: list[str] = []   # OUTPUT_OPTIONS
    env: list[str] = []  # ENV_INTERFACE
    extra: list[str] = []  # EXTRA_FILES
    notes: list[str] = []

    # 1. Profile presets first (the simple on-ramp), then explicit fields override/add.
    profile = inputs.get("profile")
    if profile:
        preset = _PROFILES.get(str(profile))
        if preset is None:
            raise ValueError(
                f"Unknown nmap profile {profile!r}. Valid: {', '.join(_PROFILES)}"
            )
        g.extend(preset["global"])
        a.extend(preset["action"])
        notes.append(f"Profile '{profile}' pre-filled global + action slots.")

    # 2. GLOBAL_OPTIONS (run-wide behaviour).
    timing = inputs.get("timing")
    if timing is not None and timing != "":
        g.append(f"-T{int(timing)}")
    if _as_bool(inputs.get("no_dns")):
        g.append("-n")
    if _as_bool(inputs.get("resolve_all")):
        g.append("-R")
    if _as_bool(inputs.get("skip_host_discovery")):
        g.append("-Pn")
    if _as_bool(inputs.get("verbose")):
        g.append("-v")
    if _as_bool(inputs.get("reason")):
        g.append("--reason")
    if _as_bool(inputs.get("ipv6")):
        g.append("-6")
    dns_servers = inputs.get("dns_servers")
    if dns_servers:
        g.extend(["--dns-servers", str(dns_servers)])
    if _as_bool(inputs.get("system_dns")):
        g.append("--system-dns")
    if _as_bool(inputs.get("traceroute")):
        g.append("--traceroute")
    if _as_bool(inputs.get("debug")):
        g.append("-d")
    if _as_bool(inputs.get("show_open_only")):
        g.append("--open")
    if _as_bool(inputs.get("packet_trace")):
        g.append("--packet-trace")
    if _as_bool(inputs.get("iflist")):
        g.append("--iflist")
    if _as_bool(inputs.get("append_output")):
        g.append("--append-output")
    resume = inputs.get("resume")
    if resume:
        g.extend(["--resume", str(resume)])
    if _as_bool(inputs.get("assume_privileged")):
        g.append("--privileged")
    if _as_bool(inputs.get("assume_unprivileged")):
        g.append("--unprivileged")

    # Host-discovery probe selection (HOST DISCOVERY section of --help) — these
    # pick WHICH probes decide "is it up", used when the default is blocked.
    for key, flag in (("ping_syn", "-PS"), ("ping_ack", "-PA"),
                       ("ping_udp", "-PU"), ("ping_sctp", "-PY")):
        val = inputs.get(key)
        if val:
            a.append(f"{flag}{val}")
    if _as_bool(inputs.get("ping_echo")):
        a.append("-PE")
    if _as_bool(inputs.get("ping_timestamp")):
        a.append("-PP")
    if _as_bool(inputs.get("ping_netmask")):
        a.append("-PM")
    ping_protocol = inputs.get("ping_protocol")
    if ping_protocol:
        a.append(f"-PO{ping_protocol}")

    # 3. ACTION_OPTIONS (what the tool does).
    scan_type = inputs.get("scan_type")
    if scan_type:
        a.append(str(scan_type))  # e.g. -sS / -sT / -sU / -sn / -sL / -sA / -sN ...
    idle_zombie = inputs.get("idle_zombie")
    if idle_zombie:
        a.extend(["-sI", str(idle_zombie)])
    scan_flags = inputs.get("scan_flags")
    if scan_flags:
        a.extend(["--scanflags", str(scan_flags)])
    ftp_bounce = inputs.get("ftp_bounce")
    if ftp_bounce:
        a.extend(["-b", str(ftp_bounce)])
        notes.append("-b (FTP bounce scan) is a legacy technique that only works against "
                     "long-obsolete, misconfigured FTP servers — included for completeness.")
    if _as_bool(inputs.get("service_version")):
        a.append("-sV")
    if _as_bool(inputs.get("os_detect")):
        a.append("-O")
    if _as_bool(inputs.get("aggressive")):
        a.append("-A")

    version_intensity = inputs.get("version_intensity")
    if version_intensity not in (None, ""):
        a.extend(["--version-intensity", str(int(version_intensity))])
    elif _as_bool(inputs.get("version_light")):
        a.append("--version-light")
    if _as_bool(inputs.get("version_trace")):
        a.append("--version-trace")

    if _as_bool(inputs.get("osscan_limit")):
        a.append("--osscan-limit")
    if _as_bool(inputs.get("osscan_guess")):
        a.append("--osscan-guess")

    # Port selection (mutually-exclusive forms; explicit ports win).
    ports = inputs.get("ports")
    top_ports = inputs.get("top_ports")
    if ports:
        a.extend(["-p", str(ports)])
    elif _as_bool(inputs.get("all_ports")):
        a.append("-p-")
    elif top_ports:
        a.extend(["--top-ports", str(int(top_ports))])
    elif _as_bool(inputs.get("fast")):
        a.append("-F")
    exclude_ports = inputs.get("exclude_ports")
    if exclude_ports:
        a.extend(["--exclude-ports", str(exclude_ports)])
    if _as_bool(inputs.get("sequential_ports")):
        a.append("-r")

    if _as_bool(inputs.get("script_default")) and not inputs.get("scripts"):
        a.append("-sC")
    scripts = inputs.get("scripts")
    if scripts:
        a.append(f"--script={scripts}")
    script_args = inputs.get("script_args")
    if script_args:
        a.extend(["--script-args", str(script_args)])
    script_args_file = inputs.get("script_args_file")
    if script_args_file:
        a.extend(["--script-args-file", str(script_args_file)])
    if _as_bool(inputs.get("script_trace")):
        a.append("--script-trace")
    if _as_bool(inputs.get("script_updatedb")):
        a.append("--script-updatedb")
        notes.append("--script-updatedb only refreshes the NSE script database — it doesn't "
                     "scan anything, a target isn't needed for this run.")
    script_help = inputs.get("script_help")
    if script_help:
        a.extend(["--script-help", str(script_help)])
        notes.append("--script-help only prints documentation for the named script(s) — it "
                     "doesn't scan anything, a target isn't needed for this run.")

    # Firewall/IDS evasion + spoofing (real nmap flags — see `nmap --help` under
    # "FIREWALL/IDS EVASION AND SPOOFING"). These change what a target/IDS SEES,
    # they don't change what nmap itself does.
    if _as_bool(inputs.get("fragment")):
        a.append("-f")
    decoys = inputs.get("decoys")
    if decoys:
        a.extend(["-D", str(decoys)])
    source_port = inputs.get("source_port")
    if source_port:
        a.extend(["-g", str(int(source_port))])
    spoof_mac = inputs.get("spoof_mac")
    if spoof_mac:
        a.extend(["--spoof-mac", str(spoof_mac)])
    spoof_source_ip = inputs.get("spoof_source_ip")
    if spoof_source_ip:
        a.extend(["-S", str(spoof_source_ip)])
        notes.append(
            "-S (spoof source IP) needs -e <interface> and usually -Pn too, since replies "
            "won't come back to you — set the Interface field, and consider Skip host "
            "discovery."
        )
    proxies = inputs.get("proxies")
    if proxies:
        a.extend(["--proxies", str(proxies)])
    data_payload = inputs.get("data_payload")
    if data_payload:
        a.extend(["--data", str(data_payload)])
    data_string = inputs.get("data_string")
    if data_string:
        a.extend(["--data-string", str(data_string)])
    data_length = inputs.get("data_length")
    if data_length:
        a.extend(["--data-length", str(int(data_length))])
    ip_options = inputs.get("ip_options")
    if ip_options:
        a.extend(["--ip-options", str(ip_options)])
    ttl = inputs.get("ttl")
    if ttl not in (None, ""):
        a.extend(["--ttl", str(int(ttl))])
    if _as_bool(inputs.get("badsum")):
        a.append("--badsum")

    # Timing & performance (TIMING AND PERFORMANCE section of --help).
    min_rate = inputs.get("min_rate")
    if min_rate:
        a.extend(["--min-rate", str(int(min_rate))])
    max_rate = inputs.get("max_rate")
    if max_rate:
        a.extend(["--max-rate", str(int(max_rate))])
    host_timeout = inputs.get("host_timeout")
    if host_timeout:
        a.extend(["--host-timeout", str(host_timeout)])
    max_retries = inputs.get("max_retries")
    if max_retries not in (None, ""):
        a.extend(["--max-retries", str(int(max_retries))])
    scan_delay = inputs.get("scan_delay")
    if scan_delay:
        a.extend(["--scan-delay", str(scan_delay)])
    max_scan_delay = inputs.get("max_scan_delay")
    if max_scan_delay:
        a.extend(["--max-scan-delay", str(max_scan_delay)])

    # 4. OUTPUT_OPTIONS.
    out_fmt = inputs.get("output_format")
    out_path = inputs.get("output_path")
    if out_fmt:
        flag = _OUTPUT_FLAG.get(str(out_fmt))
        if flag is None:
            raise ValueError(
                f"Unknown output_format {out_fmt!r}. Valid: {', '.join(_OUTPUT_FLAG)}"
            )
        o.extend([flag, str(out_path or "./out/scan")])

    # 7. ENV_INTERFACE.
    interface = inputs.get("interface")
    if interface:
        env.extend(["-e", str(interface)])

    # 8. EXTRA_FILES.
    input_list = inputs.get("input_list")
    if input_list:
        extra.extend(["-iL", str(input_list)])
    exclude = inputs.get("exclude")
    if exclude:
        extra.extend(["--exclude", str(exclude)])
    exclude_file = inputs.get("exclude_file")
    if exclude_file:
        extra.extend(["--excludefile", str(exclude_file)])
    random_targets = inputs.get("random_targets")
    if random_targets:
        extra.extend(["-iR", str(int(random_targets))])

    # Privilege handling: most raw-packet scan/probe types need root.
    privileged = _as_bool(inputs.get("privileged"))
    _PRIV_TOKENS = {
        "-sS", "-O", "-sU", "-f", "-D", "-S", "--spoof-mac",
        "-sA", "-sW", "-sM", "-sN", "-sF", "-sX", "-sO", "-sY", "-sZ",
        "-sI", "--traceroute",
    }
    needs_priv = (
        any(t in _PRIV_TOKENS for t in a)
        or any(t.startswith(("-PS", "-PA", "-PU", "-PY", "-PE", "-PP", "-PM", "-PO")) for t in a)
    )
    if needs_priv and not privileged:
        notes.append("This scan needs privileges (raw-packet scan/probe type). Prefix with "
                     "sudo, or switch to -sT / a TCP-connect-based ping type.")
    elevation = "sudo" if (privileged or (needs_priv and _as_bool(inputs.get("auto_sudo")))) else None

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: [str(inputs["targets"])] if inputs.get("targets") else [],
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.EXTRA_FILES: extra,
    }
    if not inputs.get("targets") and not random_targets:
        notes.append("No targets supplied — fill the TARGET_PIVOT slot before running.")

    return assemble("nmap", slot_values, notes=notes, elevation=elevation)
