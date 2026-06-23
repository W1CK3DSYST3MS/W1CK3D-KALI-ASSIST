"""Slot model + fixed-order assembly + shell escaping."""

from wizard_core.builders.common import assemble, shell_escape
from wizard_core.slots import SLOT_ORDER, Slot


def test_slot_order_is_one_to_eight():
    assert [int(s) for s in SLOT_ORDER] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert SLOT_ORDER[0] is Slot.PROGRAM


def test_from_name_roundtrip_and_failure():
    assert Slot.from_name("action_options") is Slot.ACTION_OPTIONS
    assert Slot.from_name("PROGRAM") is Slot.PROGRAM
    try:
        Slot.from_name("bogus")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError on unknown slot")


def test_assemble_respects_fixed_order_regardless_of_input_order():
    # Provide slots out of order; assembly must still be PROGRAM->...->EXTRA.
    plan = assemble(
        "nmap",
        {
            Slot.OUTPUT_OPTIONS: ["-oX", "out.xml"],
            Slot.ACTION_OPTIONS: ["-sV"],
            Slot.TARGET_PIVOT: ["10.0.0.1"],
            Slot.GLOBAL_OPTIONS: ["-T4"],
        },
    )
    assert plan.array_form == ["nmap", "-T4", "10.0.0.1", "-sV", "-oX", "out.xml"]
    assert plan.bash_preview_string == "nmap -T4 10.0.0.1 -sV -oX out.xml"


def test_empty_slots_are_skipped():
    plan = assemble("ls", {Slot.ACTION_OPTIONS: [], Slot.TARGET_PIVOT: ["/etc"]})
    assert plan.array_form == ["ls", "/etc"]


def test_shell_escape_quotes_dangerous_tokens():
    assert shell_escape("simple") == "simple"
    assert shell_escape("two words") == "'two words'"
    # An injection-looking token must be safely single-quoted in the preview.
    assert shell_escape("a; rm -rf /") == "'a; rm -rf /'"


def test_elevation_prefixes_program():
    plan = assemble("nmap", {Slot.ACTION_OPTIONS: ["-O"], Slot.TARGET_PIVOT: ["x"]},
                    elevation="sudo")
    assert plan.array_form[0] == "sudo"
    assert plan.array_form[1] == "nmap"
    assert plan.bash_preview_string.startswith("sudo nmap ")
