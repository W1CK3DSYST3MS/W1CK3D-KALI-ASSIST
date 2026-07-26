"""netexec builder: -M module system, --lsa/--ntds fix (builder used to only ever
emit --sam), -x/-X mutual exclusion, -L standalone, and share spidering."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("netexec")


def test_module_flag_builds():
    plan = build({"target": "10.0.0.1", "username": "jdoe", "password": "pw", "module": "enum_av"})
    assert "-M" in plan.array_form and "enum_av" in plan.array_form


def test_module_with_options_splits_key_value_pairs():
    plan = build({"target": "10.0.0.1", "module": "lsassy", "module_options": "METHOD=comsvcs SAVE_DIR=/tmp"})
    toks = plan.array_form
    assert toks.index("-M") < toks.index("-o")
    assert "METHOD=comsvcs" in toks and "SAVE_DIR=/tmp" in toks
    assert any("--options" in n for n in plan.notes)


def test_lsa_and_ntds_now_emit_correct_flags():
    # Previously the builder only ever emitted --sam even though the flow's prose
    # talked about --lsa/--ntds too — this is the fix.
    plan = build({"target": "10.0.0.1", "lsa": True})
    assert "--lsa" in plan.array_form
    assert "--sam" not in plan.array_form

    plan2 = build({"target": "10.0.0.1", "ntds": True})
    assert "--ntds" in plan2.array_form
    assert any("Domain Controller" in n for n in plan2.notes)


def test_sam_lsa_ntds_can_combine():
    plan = build({"target": "10.0.0.1", "sam": True, "lsa": True, "ntds": True})
    for flag in ("--sam", "--lsa", "--ntds"):
        assert flag in plan.array_form


def test_exec_command_vs_ps_command_mutually_exclusive():
    plan = build({"target": "10.0.0.1", "exec_command": "whoami"})
    assert "-x" in plan.array_form and "whoami" in plan.array_form

    plan2 = build({"target": "10.0.0.1", "ps_command": "whoami"})
    assert "-X" in plan2.array_form and "whoami" in plan2.array_form

    with pytest.raises(ValueError):
        build({"target": "10.0.0.1", "exec_command": "whoami", "ps_command": "whoami"})


def test_list_modules_is_standalone():
    plan = build({"protocol": "smb", "list_modules": True})
    assert plan.array_form == ["netexec", "smb", "-L"]


def test_list_modules_ignores_credentials():
    plan = build({"protocol": "smb", "list_modules": True, "username": "jdoe", "password": "pw"})
    assert "-u" not in plan.array_form
    assert plan.array_form == ["netexec", "smb", "-L"]


def test_spider_share_and_content():
    plan = build({"target": "10.0.0.1", "spider": "C$", "spider_content": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["--spider", "C$", "--content"]


def test_missing_target_is_noted_not_crashed():
    plan = build({"username": "jdoe"})
    assert any("No target" in n for n in plan.notes)
