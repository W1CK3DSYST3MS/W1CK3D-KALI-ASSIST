"""kismet builder: capture source, logging, and startup-override flags."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("kismet")


def test_source_and_defaults_to_sudo():
    plan = build({"source": "wlan0"})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-c", "wlan0"]
    assert plan.bash_preview_string.startswith("sudo kismet")


def test_no_sudo_drops_elevation():
    plan = build({"source": "wlan0", "no_sudo": True})
    assert not plan.bash_preview_string.startswith("sudo")


def test_no_source_notes_missing():
    plan = build({})
    assert any("No capture source" in n for n in plan.notes)


def test_log_types_and_config_file_and_daemonize():
    plan = build({
        "source": "wlan0", "log_types": "kismet,pcapng",
        "config_file": "/etc/kismet/custom.conf", "daemonize": True,
    })
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["--log-types", "kismet,pcapng"]
    assert "-f" in plan.array_form and "/etc/kismet/custom.conf" in plan.array_form
    assert "--daemonize" in plan.array_form


def test_log_prefix():
    plan = build({"source": "wlan0", "log_prefix": "~/kismet-logs"})
    assert "--log-prefix" in plan.array_form and "~/kismet-logs" in plan.array_form
