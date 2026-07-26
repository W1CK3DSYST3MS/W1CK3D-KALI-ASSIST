"""exiftool builder: read-mode flags plus the new strip-metadata write mode."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("exiftool")


def test_plain_read_default():
    plan = build({"target": "photo.jpg", "common_only": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-common"]
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["photo.jpg"]


def test_gps_only_read():
    plan = build({"target": "photo.jpg", "gps_only": True, "common_only": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-gps:all"]


def test_strip_all_uses_all_equals():
    plan = build({"target": "photo.jpg", "strip_all": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-all="]
    assert any("deletes ALL metadata" in n for n in plan.notes)


def test_strip_gps_uses_gps_all_equals():
    plan = build({"target": "photo.jpg", "strip_gps": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-gps:all="]


def test_strip_all_wins_over_strip_gps():
    plan = build({"target": "photo.jpg", "strip_all": True, "strip_gps": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-all="]


def test_overwrite_original_only_applies_in_strip_mode():
    plan = build({"target": "photo.jpg", "strip_all": True, "overwrite_original": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-overwrite_original", "-all="]


def test_read_flags_ignored_and_noted_when_stripping():
    plan = build({"target": "photo.jpg", "strip_all": True, "json": True, "common_only": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-all="]
    assert any("ignored while stripping" in n for n in plan.notes)


def test_recurse_still_applies_in_strip_mode():
    plan = build({"target": "./photos/", "strip_all": True, "recurse": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-r", "-all="]
