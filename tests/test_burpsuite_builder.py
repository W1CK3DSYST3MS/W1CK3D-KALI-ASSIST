"""burpsuite builder: startup flags render into GLOBAL_OPTIONS in the right order."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("burpsuite")


def test_no_inputs_gives_empty_global_options():
    plan = build({})
    assert Slot.GLOBAL_OPTIONS not in plan.slot_values
    assert plan.bash_preview_string == "burpsuite"


def test_use_defaults_and_disable_extensions():
    plan = build({"use_defaults": True, "disable_extensions": True})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == [
        "--use-defaults", "--disable-extensions",
    ]


def test_data_dir_and_auto_repair_with_project_file():
    plan = build({
        "project_file": "~/engagement.burp",
        "data_dir": "~/burp-data",
        "auto_repair": True,
    })
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == [
        "--project-file=~/engagement.burp",
        "--data-dir=~/burp-data",
        "--auto-repair",
    ]


def test_all_flags_together_preserve_order():
    plan = build({
        "use_defaults": True,
        "disable_extensions": True,
        "project_file": "p.burp",
        "config_file": "c.json",
        "data_dir": "d",
        "auto_repair": True,
    })
    assert plan.array_form == [
        "burpsuite",
        "--use-defaults", "--disable-extensions",
        "--project-file=p.burp", "--config-file=c.json",
        "--data-dir=d", "--auto-repair",
    ]
