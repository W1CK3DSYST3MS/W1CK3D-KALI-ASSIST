"""photon builder: URL slot placement, crawl tuning, and the new content-gap flags
(--keys, --dns, --clone, -e/--export)."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("photon")


def test_url_lands_in_env_interface():
    plan = build({"url": "https://example.com"})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-u", "https://example.com"]


def test_missing_url_is_noted_not_crashed():
    plan = build({"depth": 2})
    assert any("No URL" in n for n in plan.notes)
    assert Slot.ENV_INTERFACE not in plan.slot_values


def test_depth_threads_delay_wayback():
    plan = build({"url": "https://x", "depth": 3, "threads": 10, "delay": "1", "wayback": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-l", "3", "-t", "10", "-d", "1", "--wayback"]


def test_keys_flag_warns_to_verify_manually():
    plan = build({"url": "https://x", "keys": True})
    assert "--keys" in plan.array_form
    assert any("verify" in n for n in plan.notes)


def test_dns_flag_no_special_note():
    plan = build({"url": "https://x", "dns": True})
    assert "--dns" in plan.array_form


def test_clone_flag_warns_about_disk_space():
    plan = build({"url": "https://x", "clone": True})
    assert "--clone" in plan.array_form
    assert any("disk space" in n for n in plan.notes)


def test_export_format_valid_values():
    plan = build({"url": "https://x", "export": "json"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-e", "json"]

    plan = build({"url": "https://x", "export": "csv", "output": "~/out"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-o", "~/out", "-e", "csv"]


def test_export_unknown_format_fails_loudly():
    with pytest.raises(ValueError):
        build({"url": "https://x", "export": "xml"})


def test_full_crawl_all_new_flags_combined():
    plan = build({
        "url": "https://example.com", "depth": 2, "keys": True, "dns": True,
        "clone": True, "export": "json", "output": "~/photon_out",
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-l", "2", "--keys", "--dns", "--clone"]
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-o", "~/photon_out", "-e", "json"]
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-u", "https://example.com"]
