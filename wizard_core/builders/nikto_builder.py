"""nikto command builder (Module 11 spec).

Target is always `-h` (never a bare argument). Generate-only. nikto is noisy by
design — the module's authorization gate and pacing flags reflect that.

2026-07-26: extended to cover nikto's FULL `-H` help surface (the earlier pass
only covered the "major gaps" a first, shallower audit had flagged — see
docs/DEPTH-AUDIT.md). Newly recognised: nocheck/ask (update-check control),
dbcheck/version_info (standalone diagnostics, like list_plugins), display_options
(merges with verbose into one -Display value), ignore_code/ignore_string
(-404code/-404string false-positive filtering), followredirects/nocookies/
nointeractive/nolookup/noslash/no404 (request/response behaviour toggles),
ip_version (-ipv4/-ipv6), useragent, add_header (-Add-header), cgidirs
(-Cgidirs), platform (-Platform), root (-root), userdbs (-Userdbs), config
(-config), option_override (-Option).

Recognised keys (all optional except ``host``): profile, host, port, ssl, nossl,
ip_version, tuning, vhost, evasion, plugins, mutate, mutate_options, output,
format, save, timeout, pause, maxtime, verbose, display_options, nocheck, ask,
dbcheck, version_info, check6, nolookup, nointeractive, nocookies, noslash,
no404, followredirects, useragent, add_header, ignore_code, ignore_string,
cgidirs, platform, root, userdbs, option_override, config, proxy, auth_id,
rsacert, key, update, list_plugins. Verified against the installed build
(``nikto -H``, Nikto 2.6.0).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_PROFILES: dict[str, dict[str, list[str]]] = {
    "quick": {"action": []},
    "https": {"action": ["-ssl", "-p", "443"]},
    "tuned": {"action": ["-Tuning", "1234"]},
    "reported": {"action": [], "output": ["-o", "report.html", "-Format", "htm"]},
}
_FORMATS = {"htm", "csv", "xml", "json", "txt", "sql"}
_IP_VERSION_FLAG = {"ipv4": "-ipv4", "ipv6": "-ipv6"}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("nikto")
def build_nikto(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []

    # Maintenance commands stand alone.
    if _truthy(inputs.get("update")):
        # This nikto build has NO -update flag (confirmed against installed --help).
        # It only auto-checks CIRT.net for a newer nikto version on startup (toggle
        # with -nocheck/-ask); the DB/plugins themselves ship in the Kali package and
        # are refreshed via apt, not a nikto command line switch.
        notes.append(
            "nikto has no -update flag. It silently checks for a newer nikto version "
            "on every run (toggle with -nocheck/-ask). To refresh the vulnerability "
            "database/plugins on Kali, run: sudo apt update && sudo apt install "
            "--only-upgrade nikto."
        )
    if _truthy(inputs.get("dbcheck")):
        # -dbcheck only verifies the plugin/db files parse — it doesn't scan anything.
        return assemble("nikto", {Slot.ACTION_OPTIONS: ["-dbcheck"]})
    if _truthy(inputs.get("version_info")):
        # -Version prints plugin/database versions and exits — no scan, no target.
        return assemble("nikto", {Slot.ACTION_OPTIONS: ["-Version"]})
    if _truthy(inputs.get("list_plugins")):
        return assemble("nikto", {Slot.ACTION_OPTIONS: ["-list-plugins"]})

    g: list[str] = []
    a: list[str] = []
    o: list[str] = []
    env: list[str] = []
    extra: list[str] = []

    profile = inputs.get("profile")
    if profile:
        preset = _PROFILES.get(str(profile))
        if preset is None:
            raise ValueError(f"Unknown nikto profile {profile!r}. Valid: {', '.join(_PROFILES)}")
        a.extend(preset.get("action", []))
        o.extend(preset.get("output", []))
        notes.append(f"Profile '{profile}' pre-filled options.")

    # GLOBAL
    # -Display takes a combined string of sub-flags (1/2/3/4/D/E/P/S/V); the
    # simple "verbose" checkbox is just a shortcut for V, merged in here so both
    # can be used together without emitting -Display twice.
    if _truthy(inputs.get("verbose")) or inputs.get("display_options"):
        disp_chars: list[str] = []
        seen: set[str] = set()
        if _truthy(inputs.get("verbose")):
            disp_chars.append("V")
            seen.add("V")
        if inputs.get("display_options"):
            for ch in str(inputs["display_options"]):
                if ch.strip() and ch not in seen:
                    disp_chars.append(ch)
                    seen.add(ch)
        g.extend(["-Display", "".join(disp_chars)])
    if inputs.get("timeout"):
        g.extend(["-timeout", str(int(inputs["timeout"]))])
    if inputs.get("pause"):
        g.extend(["-Pause", str(inputs["pause"])])
    if inputs.get("maxtime"):
        g.extend(["-maxtime", str(inputs["maxtime"])])
    if _truthy(inputs.get("nocheck")):
        g.append("-nocheck")
    if inputs.get("ask"):
        g.extend(["-ask", str(inputs["ask"])])
    if _truthy(inputs.get("check6")):
        g.append("-check6")
    if _truthy(inputs.get("nolookup")):
        g.append("-nolookup")
    if _truthy(inputs.get("nointeractive")):
        g.append("-nointeractive")
    if _truthy(inputs.get("nocookies")):
        g.append("-nocookies")
    if _truthy(inputs.get("noslash")):
        g.append("-noslash")
    if _truthy(inputs.get("no404")):
        g.append("-no404")
    if _truthy(inputs.get("followredirects")):
        g.append("-followredirects")
    ip_version = inputs.get("ip_version")
    if ip_version:
        flag = _IP_VERSION_FLAG.get(str(ip_version))
        if flag is None:
            raise ValueError(f"Unknown nikto ip_version {ip_version!r}. Valid: {', '.join(_IP_VERSION_FLAG)}")
        g.append(flag)
    if inputs.get("useragent"):
        g.extend(["-useragent", str(inputs["useragent"])])
    if inputs.get("add_header"):
        g.extend(["-Add-header", str(inputs["add_header"])])
    if inputs.get("ignore_code"):
        g.extend(["-404code", str(inputs["ignore_code"])])
    if inputs.get("ignore_string"):
        g.extend(["-404string", str(inputs["ignore_string"])])
    if inputs.get("config"):
        g.extend(["-config", str(inputs["config"])])
    if inputs.get("option_override"):
        g.extend(["-Option", str(inputs["option_override"])])

    # TARGET — always -h. A hosts file (.txt) is still -h but conceptually an EXTRA file.
    host = inputs.get("host")
    target_tokens: list[str] = []
    if not host:
        notes.append("No host — supply a target with -h.")
    elif str(host).endswith(".txt"):
        extra.extend(["-h", str(host)])
    else:
        target_tokens = ["-h", str(host)]

    # ACTION
    if inputs.get("port"):
        a.extend(["-p", str(inputs["port"])])
    if _truthy(inputs.get("ssl")) and "-ssl" not in a:
        a.append("-ssl")
    if _truthy(inputs.get("nossl")):
        a.append("-nossl")
    if inputs.get("tuning"):
        a.extend(["-Tuning", str(inputs["tuning"])])
    if inputs.get("vhost"):
        a.extend(["-vhost", str(inputs["vhost"])])
    if inputs.get("evasion"):
        a.extend(["-evasion", str(inputs["evasion"])])
    if inputs.get("plugins"):
        a.extend(["-Plugins", str(inputs["plugins"])])
    if inputs.get("cgidirs"):
        a.extend(["-Cgidirs", str(inputs["cgidirs"])])
    if inputs.get("platform"):
        a.extend(["-Platform", str(inputs["platform"])])
    if inputs.get("root"):
        a.extend(["-root", str(inputs["root"])])
    if inputs.get("userdbs"):
        a.extend(["-Userdbs", str(inputs["userdbs"])])

    # Deeper enumeration (spec gap fix): -mutate makes nikto actively GUESS extra
    # files/usernames/directories instead of only checking its built-in signatures.
    # Sub-options on this installed build (nikto -H): 1,2,3,4,6 — there is no 5.
    if inputs.get("mutate"):
        a.extend(["-mutate", str(inputs["mutate"])])
    if inputs.get("mutate_options"):
        a.extend(["-mutate-options", str(inputs["mutate_options"])])

    # OUTPUT
    if inputs.get("output"):
        fmt = str(inputs.get("format") or "").strip()
        if fmt and fmt not in _FORMATS:
            raise ValueError(f"Unknown nikto format {fmt!r}. Valid: {', '.join(sorted(_FORMATS))}")
        o.extend(["-o", str(inputs["output"])])
        if fmt:
            o.extend(["-Format", fmt])
    if inputs.get("save"):
        val = inputs.get("save")
        o.extend(["-Save", "." if val is True or str(val).lower() in {"true", "1", "yes"} else str(val)])

    # ENV / proxy / auth / client-certificate auth
    if inputs.get("proxy"):
        env.extend(["-useproxy", str(inputs["proxy"])])
    if inputs.get("auth_id"):
        env.extend(["-id", str(inputs["auth_id"])])
    if inputs.get("rsacert"):
        env.extend(["-RSAcert", str(inputs["rsacert"])])
    if inputs.get("key"):
        env.extend(["-key", str(inputs["key"])])

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: target_tokens,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.EXTRA_FILES: extra,
    }
    return assemble("nikto", slot_values, notes=notes)
