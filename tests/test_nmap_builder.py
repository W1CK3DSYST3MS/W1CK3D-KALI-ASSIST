"""nmap builder: profiles, slot placement, privilege handling, output."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("nmap")


def test_standard_profile_prefills_slots():
    plan = build({"profile": "standard", "targets": "192.168.1.10"})
    # Profile sets -T4 (global) + -sV --top-ports 1000 (action).
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-T4"]
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-sV", "--top-ports", "1000"]
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["192.168.1.10"]


def test_targets_always_in_target_pivot_not_action():
    plan = build({"targets": "10.0.0.0/24", "scan_type": "-sT", "ports": "22,80"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["10.0.0.0/24"]
    # ports flag stays in ACTION, never drifts next to targets
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-sT", "-p", "22,80"]
    # full ordered preview
    assert plan.bash_preview_string == "nmap 10.0.0.0/24 -sT -p 22,80"


def test_unknown_profile_fails_loudly():
    with pytest.raises(ValueError):
        build({"profile": "ludicrous", "targets": "x"})


def test_privileged_scan_warns_when_not_elevated():
    plan = build({"targets": "x", "scan_type": "-sS"})
    assert any("needs privileges" in n for n in plan.notes)
    assert not plan.bash_preview_string.startswith("sudo")


def test_privileged_flag_adds_sudo():
    plan = build({"targets": "x", "os_detect": True, "privileged": True})
    assert plan.bash_preview_string.startswith("sudo nmap ")
    assert "-O" in plan.array_form


def test_output_all_formats():
    plan = build({"targets": "x", "service_version": True,
                  "output_format": "all", "output_path": "./out/scan"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-oA", "./out/scan"]


def test_port_selection_precedence_explicit_ports_win():
    plan = build({"targets": "x", "ports": "443", "fast": True, "top_ports": 100})
    assert "-p" in plan.array_form and "443" in plan.array_form
    assert "-F" not in plan.array_form
    assert "--top-ports" not in plan.array_form


def test_missing_targets_is_noted_not_crashed():
    plan = build({"profile": "quick"})
    assert any("No targets" in n for n in plan.notes)
    assert Slot.TARGET_PIVOT not in plan.slot_values


def test_evasion_flags_build_correctly():
    plan = build({
        "targets": "x", "fragment": True, "decoys": "RND:5",
        "source_port": 53, "spoof_mac": "0",
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "-f", "-D", "RND:5", "-g", "53", "--spoof-mac", "0",
    ]
    # these all need raw-socket privileges, same as -sS/-O/-sU
    assert any("needs privileges" in n for n in plan.notes)


def test_spoof_source_ip_warns_about_interface_and_pn():
    plan = build({"targets": "x", "spoof_source_ip": "10.0.0.99"})
    assert "-S" in plan.array_form and "10.0.0.99" in plan.array_form
    assert any("-e <interface>" in n for n in plan.notes)
