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


def test_extra_scan_techniques():
    for stype in ["-sA", "-sW", "-sM", "-sN", "-sF", "-sX", "-sO", "-sY", "-sZ", "-sL"]:
        plan = build({"targets": "x", "scan_type": stype})
        assert stype in plan.array_form


def test_idle_zombie_scan():
    plan = build({"targets": "x", "idle_zombie": "zombie.example.com:80"})
    assert "-sI" in plan.array_form and "zombie.example.com:80" in plan.array_form
    assert any("privileges" in n for n in plan.notes)


def test_ping_probe_types():
    plan = build({
        "targets": "x", "ping_syn": "22,80", "ping_ack": "80",
        "ping_udp": "53", "ping_echo": True, "ping_timestamp": True,
        "ping_netmask": True, "ping_protocol": "1,6,17",
    })
    assert "-PS22,80" in plan.array_form
    assert "-PA80" in plan.array_form
    assert "-PU53" in plan.array_form
    assert "-PE" in plan.array_form
    assert "-PP" in plan.array_form
    assert "-PM" in plan.array_form
    assert "-PO1,6,17" in plan.array_form


def test_ipv6_and_resolve_all_and_traceroute():
    plan = build({"targets": "x", "ipv6": True, "resolve_all": True, "traceroute": True})
    assert "-6" in plan.array_form
    assert "-R" in plan.array_form
    assert "--traceroute" in plan.array_form


def test_target_spec_exclude_and_random():
    plan = build({"targets": "10.0.0.0/24", "exclude": "10.0.0.1,10.0.0.2"})
    assert "--exclude" in plan.array_form and "10.0.0.1,10.0.0.2" in plan.array_form

    plan2 = build({"random_targets": 100})
    assert "-iR" in plan2.array_form and "100" in plan2.array_form
    assert not any("No targets" in n for n in plan2.notes)


def test_performance_tuning_flags():
    plan = build({
        "targets": "x", "min_rate": 300, "max_rate": 1000,
        "host_timeout": "30m", "max_retries": 2,
        "scan_delay": "1s", "max_scan_delay": "5s",
    })
    assert "--min-rate" in plan.array_form and "300" in plan.array_form
    assert "--max-rate" in plan.array_form and "1000" in plan.array_form
    assert "--host-timeout" in plan.array_form and "30m" in plan.array_form
    assert "--max-retries" in plan.array_form and "2" in plan.array_form
    assert "--scan-delay" in plan.array_form and "1s" in plan.array_form
    assert "--max-scan-delay" in plan.array_form and "5s" in plan.array_form


def test_evasion_extras_data_ttl_badsum_proxies():
    plan = build({
        "targets": "x", "proxies": "http://127.0.0.1:8080",
        "data_string": "hello", "data_length": 25,
        "ttl": 64, "badsum": True, "ip_options": "R",
    })
    assert "--proxies" in plan.array_form and "http://127.0.0.1:8080" in plan.array_form
    assert "--data-string" in plan.array_form and "hello" in plan.array_form
    assert "--data-length" in plan.array_form and "25" in plan.array_form
    assert "--ttl" in plan.array_form and "64" in plan.array_form
    assert "--badsum" in plan.array_form
    assert "--ip-options" in plan.array_form and "R" in plan.array_form


def test_script_scan_extras():
    plan = build({"targets": "x", "script_default": True})
    assert "-sC" in plan.array_form

    plan2 = build({"targets": "x", "scripts": "vuln", "script_default": True})
    assert "-sC" not in plan2.array_form
    assert "--script=vuln" in plan2.array_form

    plan3 = build({"script_updatedb": True})
    assert "--script-updatedb" in plan3.array_form
    assert any("doesn't scan anything" in n for n in plan3.notes)


def test_version_intensity_and_light_and_osscan():
    plan = build({"targets": "x", "version_intensity": 9})
    assert "--version-intensity" in plan.array_form and "9" in plan.array_form

    plan2 = build({"targets": "x", "version_light": True})
    assert "--version-light" in plan2.array_form

    plan3 = build({"targets": "x", "osscan_limit": True, "osscan_guess": True})
    assert "--osscan-limit" in plan3.array_form
    assert "--osscan-guess" in plan3.array_form


def test_debug_open_packet_trace_resume():
    plan = build({
        "targets": "x", "debug": True, "show_open_only": True,
        "packet_trace": True, "iflist": True, "append_output": True,
        "resume": "scan.gnmap",
    })
    assert "-d" in plan.array_form
    assert "--open" in plan.array_form
    assert "--packet-trace" in plan.array_form
    assert "--iflist" in plan.array_form
    assert "--append-output" in plan.array_form
    assert "--resume" in plan.array_form and "scan.gnmap" in plan.array_form
