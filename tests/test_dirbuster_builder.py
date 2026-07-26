"""dirbuster builder: headless mode + scan-tuning flags (-t/-s/-g/-R/-v)."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("dirbuster")


def test_bare_launch_has_no_flags():
    plan = build({})
    assert plan.bash_preview_string == "dirbuster"


def test_headless_basic_flow_unaffected():
    plan = build({"headless": True, "url": "http://target/", "wordlist": "wl.txt", "report": "r.txt"})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-H"]
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-u", "http://target/"]
    assert plan.slot_values[Slot.EXTRA_FILES] == ["-l", "wl.txt"]
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-r", "r.txt"]


def test_threads_start_point_get_only_non_recursive():
    plan = build({
        "headless": True, "url": "http://target/",
        "threads": 50, "start_point": "/admin/",
        "get_only": True, "non_recursive": True,
    })
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "-t", "50", "-s", "/admin/", "-g", "-R",
    ]


def test_verbose_is_global_option():
    plan = build({"headless": True, "verbose": True})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-H", "-v"]


def test_extensions_and_threads_both_in_action_options():
    plan = build({"headless": True, "extensions": "php,txt", "threads": 20})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-e", "php,txt", "-t", "20"]
