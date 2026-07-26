"""hydra builder: credential sources, -x bruteforce generation, -S, -m, positional order."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("hydra")


def test_resume_is_standalone():
    plan = build({"resume": True, "target": "x", "service": "ssh"})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-R"]
    assert Slot.POSITIONAL_ARGS not in plan.slot_values


def test_target_and_service_are_positional_last():
    plan = build({"target": "192.168.1.10", "service": "ssh", "login": "admin", "password": "hunter2"})
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["192.168.1.10", "ssh"]
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-l", "admin", "-p", "hunter2"]
    assert plan.bash_preview_string == "hydra -l admin -p hunter2 192.168.1.10 ssh"


def test_bruteforce_generation_uses_dash_x():
    plan = build({"target": "x", "service": "ssh", "login": "admin", "bruteforce": "4:6:a1"})
    assert "-x" in plan.array_form and "4:6:a1" in plan.array_form
    assert "-p" not in plan.array_form and "-P" not in plan.array_form
    assert any("implies -u" in n for n in plan.notes)


def test_bruteforce_overrides_password_list_with_a_note():
    plan = build({"target": "x", "service": "ssh", "bruteforce": "4:4:1", "password_list": "rockyou.txt"})
    assert "-x" in plan.array_form
    assert "-P" not in plan.array_form
    assert any("replaces -p/-P/-C" in n for n in plan.notes)


def test_ssl_flag_adds_dash_S_with_note():
    plan = build({"target": "x", "service": "ftp", "ssl": True})
    assert "-S" in plan.slot_values[Slot.GLOBAL_OPTIONS]
    assert any("explicit SSL/TLS" in n for n in plan.notes)


def test_module_opts_adds_dash_m():
    plan = build({"target": "x", "service": "oracle-sid", "module_opts": "SID=xe"})
    assert "-m" in plan.array_form and "SID=xe" in plan.array_form


def test_combo_file_used_when_no_bruteforce():
    plan = build({"target": "x", "service": "ssh", "combo": "combos.txt"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-C", "combos.txt"]


def test_http_form_service_needs_form_string():
    plan = build({"target": "x", "service": "http-post-form"})
    assert any("form" in n.lower() for n in plan.notes)


def test_http_form_service_appends_form_string_positional():
    plan = build({
        "target": "x", "service": "http-post-form",
        "http_form": "/login.php:user=^USER^&pass=^PASS^:F=Invalid",
    })
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == [
        "x", "http-post-form", "/login.php:user=^USER^&pass=^PASS^:F=Invalid",
    ]


def test_targets_file_replaces_single_target():
    plan = build({"targets_file": "targets.txt", "service": "ssh", "login": "admin", "password": "x"})
    assert "-M" in plan.slot_values[Slot.ACTION_OPTIONS]
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["ssh"]


def test_output_and_output_format():
    plan = build({"target": "x", "service": "ssh", "output": "hits.txt", "output_format": "json"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-o", "hits.txt", "-b", "json"]


def test_unknown_profile_fails_loudly():
    with pytest.raises(ValueError):
        build({"profile": "ludicrous", "target": "x", "service": "ssh"})
