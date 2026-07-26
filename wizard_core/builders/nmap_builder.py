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

    Recognised keys (all optional except ``targets``):
      profile, targets, scan_type, ports, top_ports, fast, all_ports,
      service_version, os_detect, aggressive, scripts, script_args,
      timing(0-5), no_dns, skip_host_discovery, verbose, reason,
      output_format(+output_path), input_list, interface, privileged,
      fragment, decoys, spoof_source_ip, source_port, spoof_mac.
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
    if _as_bool(inputs.get("skip_host_discovery")):
        g.append("-Pn")
    if _as_bool(inputs.get("verbose")):
        g.append("-v")
    if _as_bool(inputs.get("reason")):
        g.append("--reason")

    # 3. ACTION_OPTIONS (what the tool does).
    scan_type = inputs.get("scan_type")
    if scan_type:
        a.append(str(scan_type))  # e.g. -sS / -sT / -sU / -sn
    if _as_bool(inputs.get("service_version")):
        a.append("-sV")
    if _as_bool(inputs.get("os_detect")):
        a.append("-O")
    if _as_bool(inputs.get("aggressive")):
        a.append("-A")

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

    scripts = inputs.get("scripts")
    if scripts:
        a.append(f"--script={scripts}")
    script_args = inputs.get("script_args")
    if script_args:
        a.extend(["--script-args", str(script_args)])

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

    # Privilege handling: -sS / -O / -sU need root. Render as `sudo` prefix.
    privileged = _as_bool(inputs.get("privileged"))
    needs_priv = any(t in {"-sS", "-O", "-sU", "-f", "-D", "-S", "--spoof-mac"} for t in a)
    if needs_priv and not privileged:
        notes.append("This scan needs privileges (-sS/-O/-sU). Prefix with sudo, or use -sT.")
    elevation = "sudo" if (privileged or (needs_priv and _as_bool(inputs.get("auto_sudo")))) else None

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: [str(inputs["targets"])] if inputs.get("targets") else [],
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.EXTRA_FILES: extra,
    }
    if not inputs.get("targets"):
        notes.append("No targets supplied — fill the TARGET_PIVOT slot before running.")

    return assemble("nmap", slot_values, notes=notes, elevation=elevation)
