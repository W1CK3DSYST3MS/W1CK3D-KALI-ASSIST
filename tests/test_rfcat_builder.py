"""rfcat builder: research shell vs. standalone spectrum-analyzer mode."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("rfcat")


def test_default_launches_research_shell():
    plan = build({"interactive": True})
    assert plan.bash_preview_string == "rfcat -r"


def test_index_flag_applies_in_shell_mode():
    plan = build({"interactive": True, "index": 1})
    assert plan.array_form == ["rfcat", "-r", "-i", "1"]


def test_specan_mode_builds_f_c_n_flags():
    plan = build({"specan": True, "centfreq": "433920000", "chan_spacing": "250000", "spec_channels": 104})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "-s", "-f", "433920000", "-c", "250000", "-n", "104",
    ]
    assert plan.bash_preview_string == "rfcat -s -f 433920000 -c 250000 -n 104"


def test_specan_with_no_extra_params_is_just_dash_s():
    plan = build({"specan": True})
    assert plan.array_form == ["rfcat", "-s"]


def test_specan_overrides_research_shell_and_notes_it():
    plan = build({"specan": True, "interactive": True, "centfreq": "433920000"})
    # rfcat's own CLI checks -s before -r, so -s wins and -r must not appear.
    assert "-r" not in plan.array_form
    assert "-s" in plan.array_form
    assert any("checks -s first" in n for n in plan.notes)


def test_specan_notes_display_requirement():
    plan = build({"specan": True})
    assert any("graphical window" in n for n in plan.notes)
