"""hashcat command builder (Module 06 spec).

Shape: hashcat -m <type> -a <attack> [options] <hashfile> <wordlist|mask>. The
hash file and the wordlist/mask are POSITIONAL and come last, in that order.
-m (hash mode) is the #1 thing users get wrong — the module makes it explicit.
Generate-only (offline cracking).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
# attack modes: 0 straight, 1 combinator, 3 mask, 6 hybrid wl+mask, 7 hybrid mask+wl
_PROFILES: dict[str, dict[str, object]] = {
    "wordlist": {"attack": "0", "wordlist": _DEFAULT_WORDLIST},
    "wordlist_rules": {"attack": "0", "wordlist": _DEFAULT_WORDLIST,
                       "rules": "/usr/share/hashcat/rules/best64.rule"},
    "mask": {"attack": "3"},
    "benchmark": {"benchmark": True},
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("hashcat")
def build_hashcat(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []

    profile = str(inputs.get("profile") or "")
    preset: dict[str, object] = {}
    if profile:
        preset = _PROFILES.get(profile, {})
        if not preset and profile not in _PROFILES:
            raise ValueError(f"Unknown hashcat profile {profile!r}. Valid: {', '.join(_PROFILES)}")
        notes.append(f"Profile '{profile}' pre-filled attack/options.")

    # Standalone forms.
    if _truthy(inputs.get("benchmark")) or preset.get("benchmark"):
        return assemble("hashcat", {Slot.ACTION_OPTIONS: ["-b"]},
                        notes=["Benchmarks your hardware speed."])
    if _truthy(inputs.get("identify")):
        pos = [str(inputs["hashfile"])] if inputs.get("hashfile") else []
        return assemble("hashcat", {Slot.ACTION_OPTIONS: ["--identify"], Slot.POSITIONAL_ARGS: pos})
    if _truthy(inputs.get("list_devices")):
        return assemble("hashcat", {Slot.ENV_INTERFACE: ["-I"]})

    g: list[str] = []   # GLOBAL_OPTIONS
    a: list[str] = []   # ACTION_OPTIONS (-m -a -r etc., before positionals)
    o: list[str] = []   # OUTPUT_OPTIONS
    env: list[str] = []  # ENV_INTERFACE (device)
    pos: list[str] = []  # POSITIONAL_ARGS (hashfile then wordlist/mask)

    # ACTION: hash mode (-m) is critical.
    if inputs.get("hash_mode") not in (None, ""):
        a.extend(["-m", str(inputs["hash_mode"])])
    else:
        notes.append("No -m hash mode set — hashcat needs the exact hash-type number or it never cracks.")
    attack = inputs.get("attack_mode")
    if attack in (None, "") and preset.get("attack"):
        attack = preset["attack"]
    if attack not in (None, ""):
        a.extend(["-a", str(attack)])

    rules = inputs.get("rules") or preset.get("rules")
    if rules:
        a.extend(["-r", str(rules)])
    if inputs.get("custom_charset"):
        a.extend(["-1", str(inputs["custom_charset"])])
    if _truthy(inputs.get("increment")):
        a.append("--increment")
    if _truthy(inputs.get("username")):
        a.append("--username")
    if _truthy(inputs.get("show")):
        a.append("--show")
    if _truthy(inputs.get("potfile_disable")):
        a.append("--potfile-disable")

    # GLOBAL tuning
    if inputs.get("workload"):
        g.extend(["-w", str(inputs["workload"])])
    if _truthy(inputs.get("optimized")):
        g.append("-O")
        notes.append("-O is faster but caps the maximum password length.")
    if inputs.get("session"):
        g.append(f"--session={inputs['session']}")
    if _truthy(inputs.get("force")):
        g.append("--force")
        notes.append("--force bypasses warnings but can give WRONG results — not recommended.")

    # OUTPUT
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])

    # ENV / device
    if inputs.get("device"):
        env.extend(["-d", str(inputs["device"])])

    # POSITIONAL: hashfile then wordlist/mask
    if inputs.get("hashfile"):
        pos.append(str(inputs["hashfile"]))
    else:
        notes.append("No hash file — supply the file of hashes to crack.")
    target = inputs.get("wordlist") or inputs.get("mask") or preset.get("wordlist")
    if target:
        pos.append(str(target))
    elif str(attack) == "3":
        notes.append("Mask attack (-a 3) needs a mask, e.g. ?u?l?l?l?l?d?d?d.")
    elif str(attack) == "0":
        notes.append("Wordlist attack (-a 0) needs a wordlist path.")

    return assemble("hashcat", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.POSITIONAL_ARGS: pos,
    }, notes=notes)
