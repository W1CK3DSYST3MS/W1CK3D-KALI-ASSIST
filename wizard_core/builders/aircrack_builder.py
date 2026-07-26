"""aircrack-ng suite builder (Module 07 spec).

A workflow across four binaries (airmon-ng / airodump-ng / aireplay-ng /
aircrack-ng). The builder dispatches on ``binary``; each still follows the slot
model. Capture/monitor steps run privileged (sudo); cracking does not.
Generate-only — the most legally sensitive module (active steps are double-gated
in the UI).

aireplay-ng dispatches further on ``attack_mode`` (deauth / fakeauth /
arpreplay — see `aireplay-ng --help`, "Attack modes"): deauth (-0) kicks a
client to force a reconnect; fakeauth (-1) does an open-system association
with the AP without the real password, often required before the AP accepts
other injected packets; arpreplay (-3) replays a captured ARP packet to
generate IVs fast for legacy WEP cracking.
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


_AIREPLAY_MODES = {"deauth", "fakeauth", "arpreplay"}


def _aireplay(inputs: Mapping[str, object], notes: list[str]) -> CommandPlan:
    a: list[str] = []
    pos: list[str] = []
    attack_mode = str(inputs.get("attack_mode") or "deauth")
    if attack_mode not in _AIREPLAY_MODES:
        raise ValueError(
            f"Unknown aireplay-ng attack_mode {attack_mode!r}. Valid: {', '.join(sorted(_AIREPLAY_MODES))}"
        )

    if attack_mode == "deauth":
        count = inputs.get("deauth_count")
        a.extend(["--deauth", str(count if count not in (None, "") else 5)])
        if inputs.get("bssid"):
            a.extend(["-a", str(inputs["bssid"])])
        if inputs.get("client"):
            a.extend(["-c", str(inputs["client"])])
        else:
            notes.append("No client (-c) — broadcast deauth is louder; target one client when possible.")
        notes.append("ACTIVE: a deauth kicks a real device off the network — your own network / authorized lab only.")
    elif attack_mode == "fakeauth":
        # --fakeauth <delay>: open-system association with the AP, no real password needed.
        # Often a prerequisite before the AP accepts OTHER injected packets (e.g. arpreplay).
        delay = inputs.get("fakeauth_delay")
        a.extend(["--fakeauth", str(delay if delay not in (None, "") else 0)])
        if inputs.get("bssid"):
            a.extend(["-a", str(inputs["bssid"])])
        else:
            notes.append("No AP (-a) — fake auth needs the target access point's BSSID.")
        if inputs.get("essid"):
            a.extend(["-e", str(inputs["essid"])])
        if inputs.get("source_mac"):
            a.extend(["-h", str(inputs["source_mac"])])
        else:
            notes.append("No source MAC (-h) — set one and reuse the SAME MAC for arpreplay, so the AP recognizes it as already associated.")
        notes.append("ACTIVE: associates your adapter with the AP at the 802.11 layer — your own network / authorized lab only.")
    else:  # arpreplay
        a.append("--arpreplay")
        if inputs.get("bssid"):
            a.extend(["-b", str(inputs["bssid"])])
        else:
            notes.append("No AP (-b) — ARP replay needs the target access point's BSSID to filter captured packets.")
        if inputs.get("source_mac"):
            a.extend(["-h", str(inputs["source_mac"])])
        else:
            notes.append("No source MAC (-h) — should match a MAC already fake-authed with the AP, or replays will be rejected.")
        notes.append(
            "ACTIVE: floods the AP with a captured ARP packet to generate WEP IVs fast — your own "
            "network / authorized lab only, and only useful against legacy WEP."
        )

    if inputs.get("ifacemon"):
        pos.append(str(inputs["ifacemon"]))
    else:
        notes.append("No monitor interface — supply e.g. wlan0mon.")
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
