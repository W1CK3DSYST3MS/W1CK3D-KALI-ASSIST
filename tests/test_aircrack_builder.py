"""aircrack-ng suite builder: binary dispatch, airmon actions, airodump capture
file, and aireplay-ng attack modes (deauth / fakeauth / arpreplay)."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("aircrack-ng")


def test_airmon_start_uses_subcommand_and_sudo():
    plan = build({"binary": "airmon-ng", "action": "start", "iface": "wlan0"})
    assert plan.array_form == ["sudo", "airmon-ng", "start", "wlan0"]


def test_airmon_check_kill():
    plan = build({"binary": "airmon-ng", "action": "check", "kill": True})
    assert plan.array_form == ["sudo", "airmon-ng", "check", "kill"]
    assert any("lose normal Wi-Fi" in n for n in plan.notes)


def test_airmon_check_without_kill_has_no_kill_token():
    plan = build({"binary": "airmon-ng", "action": "check"})
    assert "kill" not in plan.array_form


def test_airodump_write_prefix_saves_capture():
    plan = build({"binary": "airodump-ng", "channel": 6, "bssid": "AA:BB:CC:DD:EE:FF",
                  "write_prefix": "~/capture", "ifacemon": "wlan0mon"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-w", "~/capture"]
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-c", "6", "--bssid", "AA:BB:CC:DD:EE:FF"]


def test_aireplay_default_mode_is_deauth():
    plan = build({"binary": "aireplay-ng", "bssid": "AA:BB:CC:DD:EE:FF",
                  "client": "99:88:77:66:55:44", "deauth_count": 5, "ifacemon": "wlan0mon"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "--deauth", "5", "-a", "AA:BB:CC:DD:EE:FF", "-c", "99:88:77:66:55:44",
    ]
    assert any("kicks a real device off" in n for n in plan.notes)


def test_aireplay_fakeauth_mode():
    plan = build({
        "binary": "aireplay-ng", "attack_mode": "fakeauth",
        "bssid": "AA:BB:CC:DD:EE:FF", "essid": "MyHomeWiFi",
        "source_mac": "00:11:22:33:44:55", "fakeauth_delay": 0,
        "ifacemon": "wlan0mon",
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "--fakeauth", "0", "-a", "AA:BB:CC:DD:EE:FF", "-e", "MyHomeWiFi",
        "-h", "00:11:22:33:44:55",
    ]
    assert any("associates your adapter" in n for n in plan.notes)


def test_aireplay_fakeauth_defaults_delay_to_zero():
    plan = build({"binary": "aireplay-ng", "attack_mode": "fakeauth",
                  "bssid": "AA:BB:CC:DD:EE:FF", "ifacemon": "wlan0mon"})
    assert plan.slot_values[Slot.ACTION_OPTIONS][:2] == ["--fakeauth", "0"]


def test_aireplay_arpreplay_mode():
    plan = build({
        "binary": "aireplay-ng", "attack_mode": "arpreplay",
        "bssid": "AA:BB:CC:DD:EE:FF", "source_mac": "00:11:22:33:44:55",
        "ifacemon": "wlan0mon",
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "--arpreplay", "-b", "AA:BB:CC:DD:EE:FF", "-h", "00:11:22:33:44:55",
    ]
    assert any("legacy WEP" in n for n in plan.notes)


def test_aireplay_arpreplay_missing_source_mac_warns():
    plan = build({"binary": "aireplay-ng", "attack_mode": "arpreplay",
                  "bssid": "AA:BB:CC:DD:EE:FF", "ifacemon": "wlan0mon"})
    assert any("No source MAC" in n for n in plan.notes)


def test_aireplay_unknown_attack_mode_fails_loudly():
    with pytest.raises(ValueError):
        build({"binary": "aireplay-ng", "attack_mode": "chopchop", "ifacemon": "wlan0mon"})


def test_aircrack_wordlist_bssid_capture():
    plan = build({"binary": "aircrack-ng", "wordlist": "/usr/share/wordlists/rockyou.txt",
                  "bssid": "AA:BB:CC:DD:EE:FF", "capture": "capture-01.cap"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "-w", "/usr/share/wordlists/rockyou.txt", "-b", "AA:BB:CC:DD:EE:FF",
    ]
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["capture-01.cap"]
    # cracking runs unprivileged — no sudo prefix
    assert not plan.bash_preview_string.startswith("sudo")


def test_unknown_binary_fails_loudly():
    with pytest.raises(ValueError):
        build({"binary": "airbase-ng"})
