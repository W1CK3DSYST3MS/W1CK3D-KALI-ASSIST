"""aircrack-ng suite builder (Module 07 spec).

A workflow across four binaries (airmon-ng / airodump-ng / aireplay-ng /
aircrack-ng). The builder dispatches on ``binary``; each still follows the slot
model. Capture/monitor steps run privileged (sudo); cracking does not.
Generate-only — the most legally sensitive module (active steps are double-gated
in the UI).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_BINARIES = {"airmon-ng", "airodump-ng", "aireplay-ng", "aircrack-ng"}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("aircrack-ng")
def build_aircrack(inputs: Mapping[str, object]) -> CommandPlan:
    binary = str(inputs.get("binary") or "aircrack-ng")
    if binary not in _BINARIES:
        raise ValueError(f"Unknown aircrack-ng binary {binary!r}. Valid: {', '.join(sorted(_BINARIES))}")
    notes: list[str] = []

    if binary == "airmon-ng":
        return _airmon(inputs, notes)
    if binary == "airodump-ng":
        return _airodump(inputs, notes)
    if binary == "aireplay-ng":
        return _aireplay(inputs, notes)
    return _aircrack(inputs, notes)


def _airmon(inputs: Mapping[str, object], notes: list[str]) -> CommandPlan:
    action = str(inputs.get("action") or "start")  # start | stop | check
    sub = [action]
    pos: list[str] = []
    if action == "check" and _truthy(inputs.get("kill")):
        sub.append("kill")
        notes.append("check kill stops NetworkManager — you lose normal Wi-Fi/internet until you restart it.")
    iface = inputs.get("iface") or inputs.get("ifacemon")
    if iface:
        pos.append(str(iface))
    elif action in ("start", "stop"):
        notes.append("No interface — supply the adapter (e.g. wlan0) / monitor iface (wlan0mon).")
    return assemble("airmon-ng", {Slot.POSITIONAL_ARGS: pos}, notes=notes,
                    elevation="sudo", subcommand=sub)


def _airodump(inputs: Mapping[str, object], notes: list[str]) -> CommandPlan:
    a: list[str] = []
    o: list[str] = []
    pos: list[str] = []
    if inputs.get("channel"):
        a.extend(["-c", str(inputs["channel"])])
    if inputs.get("bssid"):
        a.extend(["--bssid", str(inputs["bssid"])])
    if inputs.get("write_prefix"):
        o.extend(["-w", str(inputs["write_prefix"])])
    if inputs.get("ifacemon"):
        pos.append(str(inputs["ifacemon"]))
    else:
        notes.append("No monitor interface — supply e.g. wlan0mon.")
    return assemble("airodump-ng", {
        Slot.ACTION_OPTIONS: a, Slot.OUTPUT_OPTIONS: o, Slot.POSITIONAL_ARGS: pos,
    }, notes=notes, elevation="sudo")


def _aireplay(inputs: Mapping[str, object], notes: list[str]) -> CommandPlan:
    a: list[str] = []
    pos: list[str] = []
    count = inputs.get("deauth_count")
    a.extend(["--deauth", str(count if count not in (None, "") else 5)])
    if inputs.get("bssid"):
        a.extend(["-a", str(inputs["bssid"])])
    if inputs.get("client"):
        a.extend(["-c", str(inputs["client"])])
    else:
        notes.append("No client (-c) — broadcast deauth is louder; target one client when possible.")
    if inputs.get("ifacemon"):
        pos.append(str(inputs["ifacemon"]))
    else:
        notes.append("No monitor interface — supply e.g. wlan0mon.")
    notes.append("ACTIVE: a deauth kicks a real device off the network — your own network / authorized lab only.")
    return assemble("aireplay-ng", {
        Slot.ACTION_OPTIONS: a, Slot.POSITIONAL_ARGS: pos,
    }, notes=notes, elevation="sudo")


def _aircrack(inputs: Mapping[str, object], notes: list[str]) -> CommandPlan:
    a: list[str] = []
    pos: list[str] = []
    if inputs.get("wordlist"):
        a.extend(["-w", str(inputs["wordlist"])])
    else:
        notes.append("No wordlist (-w) — aircrack-ng needs one to test the passphrase.")
    if inputs.get("bssid"):
        a.extend(["-b", str(inputs["bssid"])])
    if inputs.get("capture"):
        pos.append(str(inputs["capture"]))
    else:
        notes.append("No capture file — supply the .cap containing the handshake.")
    return assemble("aircrack-ng", {
        Slot.ACTION_OPTIONS: a, Slot.POSITIONAL_ARGS: pos,
    }, notes=notes)
