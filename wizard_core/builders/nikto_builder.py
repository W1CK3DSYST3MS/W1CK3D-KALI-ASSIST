"""nikto command builder (Module 11 spec).

Target is always `-h` (never a bare argument). Generate-only. nikto is noisy by
design — the module's authorization gate and pacing flags reflect that.
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
_FORMATS = {"htm", "csv", "xml", "json", "txt"}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("nikto")
def build_nikto(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []

    # Maintenance commands stand alone.
    if _truthy(inputs.get("update")):
        return assemble("nikto", {Slot.ACTION_OPTIONS: ["-update"]},
                        notes=["Refreshes the nikto vulnerability database/plugins."])
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
    if _truthy(inputs.get("verbose")):
        g.extend(["-Display", "V"])
    if inputs.get("timeout"):
        g.extend(["-timeout", str(int(inputs["timeout"]))])
    if inputs.get("pause"):
        g.extend(["-Pause", str(inputs["pause"])])
    if inputs.get("maxtime"):
        g.extend(["-maxtime", str(inputs["maxtime"])])

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

    # OUTPUT
    if inputs.get("output"):
        fmt = str(inputs.get("format") or "").strip()
        if fmt and fmt not in _FORMATS:
            raise ValueError(f"Unknown nikto format {fmt!r}. Valid: {', '.join(sorted(_FORMATS))}")
        o.extend(["-o", str(inputs["output"])])
        if fmt:
            o.extend(["-Format", fmt])

    # ENV / proxy / auth
    if inputs.get("proxy"):
        env.extend(["-useproxy", str(inputs["proxy"])])
    if inputs.get("auth_id"):
        env.extend(["-id", str(inputs["auth_id"])])

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: target_tokens,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.EXTRA_FILES: extra,
    }
    return assemble("nikto", slot_values, notes=notes)
