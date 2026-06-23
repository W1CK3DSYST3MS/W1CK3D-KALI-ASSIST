"""gobuster command builder (Module 10 spec).

gobuster's first argument is a MODE (dir/dns/vhost/fuzz) — a subcommand that must
come right after the program. The mode decides the target flag: -u for dir/vhost/
fuzz, -d for dns. Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_MODES = {"dir", "dns", "vhost", "fuzz"}
# Profiles map to (mode, global tokens, action tokens).
_PROFILES: dict[str, dict[str, object]] = {
    "quick_dir": {"mode": "dir", "global": ["-t", "40"], "action": []},
    "dir_files": {"mode": "dir", "global": ["-t", "40"], "action": ["-x", "php,html,txt,bak"]},
    "subdomains": {"mode": "dns", "global": ["-t", "40"], "action": []},
    "vhosts": {"mode": "vhost", "global": [], "action": ["--append-domain"]},
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("gobuster")
def build_gobuster(inputs: Mapping[str, object]) -> CommandPlan:
    g: list[str] = []
    a: list[str] = []
    o: list[str] = []
    env: list[str] = []
    extra: list[str] = []
    notes: list[str] = []

    mode = inputs.get("mode")
    profile = inputs.get("profile")
    if profile:
        preset = _PROFILES.get(str(profile))
        if preset is None:
            raise ValueError(f"Unknown gobuster profile {profile!r}. Valid: {', '.join(_PROFILES)}")
        mode = mode or preset["mode"]
        g.extend(list(preset["global"]))
        a.extend(list(preset["action"]))
        notes.append(f"Profile '{profile}' set mode '{mode}' and pre-filled options.")
    mode = str(mode or "dir")
    if mode not in _MODES:
        raise ValueError(f"Unknown gobuster mode {mode!r}. Valid: {', '.join(sorted(_MODES))}")

    # GLOBAL
    if inputs.get("threads"):
        g.extend(["-t", str(int(inputs["threads"]))])
    if _truthy(inputs.get("skip_tls")):
        g.append("-k")
    if _truthy(inputs.get("quiet")):
        g.append("-q")

    # TARGET — correct flag per mode.
    target: list[str] = []
    tgt = inputs.get("target")
    if tgt:
        flag = "-d" if mode == "dns" else "-u"
        target = [flag, str(tgt)]
    else:
        notes.append("No target — supply a URL (dir/vhost) or domain (dns).")

    # ACTION
    if inputs.get("wordlist"):
        extra.extend(["-w", str(inputs["wordlist"])])
    else:
        notes.append("No wordlist (-w) — gobuster needs one to run.")
    if inputs.get("extensions"):
        a.extend(["-x", str(inputs["extensions"])])
    # status filters: blacklist (-b) OR whitelist (-s), never both.
    if inputs.get("status_blacklist") and inputs.get("status_whitelist"):
        raise ValueError("Set EITHER status_blacklist (-b) OR status_whitelist (-s), not both.")
    if inputs.get("status_blacklist"):
        a.extend(["-b", str(inputs["status_blacklist"])])
    if inputs.get("status_whitelist"):
        a.extend(["-s", str(inputs["status_whitelist"])])
    if inputs.get("exclude_length"):
        a.extend(["--exclude-length", str(inputs["exclude_length"])])
    if mode != "dns" and _truthy(inputs.get("follow_redirects")):
        a.append("-r")  # in dns mode -r is the resolver, handled below
    if mode == "vhost" and _truthy(inputs.get("append_domain")) and "--append-domain" not in a:
        a.append("--append-domain")
    if inputs.get("cookie"):
        a.extend(["-c", str(inputs["cookie"])])
    if inputs.get("header"):
        a.extend(["-H", str(inputs["header"])])
    if inputs.get("user_agent"):
        a.extend(["-a", str(inputs["user_agent"])])
    if mode == "dns" and _truthy(inputs.get("show_ips")):
        a.append("-i")
    if mode == "dns" and inputs.get("resolver"):
        a.extend(["-r", str(inputs["resolver"])])

    # OUTPUT
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])

    # ENV / proxy
    if inputs.get("proxy"):
        env.extend(["--proxy", str(inputs["proxy"])])

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: target,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.EXTRA_FILES: extra,
    }
    return assemble("gobuster", slot_values, notes=notes, subcommand=[mode])
