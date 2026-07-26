"""john builder: mask mode, and the form-gap fields (session/fork/pot/list/restore/
single/incremental/show), plus the lower-priority PRINCE/loopback/Markov modes."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("john")


def test_mask_mode_builds_flag():
    plan = build({"format": "raw-md5", "mask": "?d?d?d?d?d?d?d?d", "hashfile": "pin.hash"})
    assert "--mask=?d?d?d?d?d?d?d?d" in plan.array_form
    assert plan.array_form[-1] == "pin.hash"


def test_mask_combines_with_format_and_hashfile_in_order():
    plan = build({"format": "raw-md5", "mask": "?u?l?l?l?d?d", "hashfile": "h.txt"})
    assert plan.array_form == ["john", "--format=raw-md5", "--mask=?u?l?l?l?d?d", "h.txt"]


def test_single_and_show_flags():
    plan = build({"single": True, "hashfile": "h.txt"})
    assert "--single" in plan.slot_values[Slot.ACTION_OPTIONS]

    plan2 = build({"show": True, "hashfile": "h.txt"})
    assert "--show" in plan2.slot_values[Slot.ACTION_OPTIONS]


def test_incremental_bare_flag():
    plan = build({"incremental": True, "hashfile": "h.txt"})
    assert "--incremental" in plan.array_form


def test_session_fork_pot_land_in_global_options():
    plan = build({"session": "crackA", "fork": 4, "pot": "custom.pot", "hashfile": "h.txt"})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["--session=crackA", "--fork=4", "--pot=custom.pot"]


def test_list_capability_is_standalone_and_ignores_hashfile():
    plan = build({"list": "formats", "hashfile": "h.txt"})
    assert plan.array_form == ["john", "--list=formats"]


def test_restore_bare_flag_when_boolean():
    plan = build({"restore": True})
    assert plan.array_form == ["john", "--restore"]
    assert any("Resumes" in n for n in plan.notes)


def test_restore_named_session_when_string():
    plan = build({"restore": "crackA"})
    assert plan.array_form == ["john", "--restore=crackA"]


def test_prince_loopback_markov_bare_flags():
    plan = build({"prince": True, "hashfile": "h.txt"})
    assert "--prince" in plan.array_form

    plan2 = build({"loopback": True, "hashfile": "h.txt"})
    assert "--loopback" in plan2.array_form

    plan3 = build({"markov": True, "hashfile": "h.txt"})
    assert "--markov" in plan3.array_form


def test_prince_named_file_value():
    plan = build({"prince": "custom.dict", "hashfile": "h.txt"})
    assert "--prince=custom.dict" in plan.array_form


def test_missing_hashfile_is_noted_not_crashed():
    plan = build({"mask": "?d?d?d?d"})
    assert any("No hash file" in n for n in plan.notes)
