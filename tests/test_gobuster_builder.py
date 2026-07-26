"""gobuster builder: mode-specific target flags, Basic Auth, bucket modes."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("gobuster")


def test_dir_mode_uses_dash_u():
    plan = build({"mode": "dir", "target": "http://site", "wordlist": "w.txt"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["-u", "http://site"]


def test_dns_mode_uses_dash_d():
    plan = build({"mode": "dns", "target": "example.com", "wordlist": "w.txt"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["-d", "example.com"]


def test_tftp_mode_uses_dash_s():
    plan = build({"mode": "tftp", "target": "10.0.0.5", "wordlist": "w.txt"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["-s", "10.0.0.5"]


def test_s3_mode_has_no_target_flag():
    plan = build({"mode": "s3", "target": "should-be-ignored", "wordlist": "w.txt"})
    assert Slot.TARGET_PIVOT not in plan.slot_values or plan.slot_values[Slot.TARGET_PIVOT] == []
    assert any("no target flag" in n for n in plan.notes)


def test_gcs_mode_has_no_target_flag():
    plan = build({"mode": "gcs", "wordlist": "w.txt"})
    assert Slot.TARGET_PIVOT not in plan.slot_values or plan.slot_values[Slot.TARGET_PIVOT] == []


def test_basic_auth_in_dir_mode():
    plan = build({"mode": "dir", "target": "http://site", "wordlist": "w.txt",
                  "username": "admin", "password": "hunter2"})
    assert "-U" in plan.array_form and "admin" in plan.array_form
    assert "-P" in plan.array_form and "hunter2" in plan.array_form


def test_basic_auth_noted_as_unsupported_in_dns_mode():
    plan = build({"mode": "dns", "target": "example.com", "wordlist": "w.txt",
                  "username": "admin", "password": "hunter2"})
    assert "-U" not in plan.array_form
    assert any("Basic Auth" in n for n in plan.notes)


def test_unknown_mode_fails_loudly():
    with pytest.raises(ValueError):
        build({"mode": "smtp", "target": "x", "wordlist": "w.txt"})
