"""responder builder: interface slot placement, sudo elevation, and the new
high-risk flags (-P, -F, -d/-D/--dhcpv6, -e/-6)."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("responder")


def test_iface_lands_in_env_interface_and_sudo_always_on():
    plan = build({"iface": "eth0"})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-I", "eth0"]
    assert plan.bash_preview_string.startswith("sudo responder ")


def test_missing_iface_is_noted_not_crashed():
    plan = build({"analyze": True})
    assert any("No -I" in n for n in plan.notes)
    assert Slot.ENV_INTERFACE not in plan.slot_values


def test_analyze_mode_passive():
    plan = build({"iface": "eth0", "analyze": True, "verbose": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-A", "-v"]


def test_proxy_auth_flag_and_note():
    plan = build({"iface": "eth0", "proxy_auth": True})
    assert "-P" in plan.array_form
    assert any("rogue proxy auth capture" in n for n in plan.notes)


def test_proxy_auth_conflicts_with_wpad():
    with pytest.raises(ValueError):
        build({"iface": "eth0", "wpad": True, "proxy_auth": True})


def test_force_wpad_auth_flag():
    plan = build({"iface": "eth0", "wpad": True, "force_wpad_auth": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-w", "-F"]


def test_dhcp_family_flags_all_warn_about_disruption():
    plan = build({"iface": "eth0", "dhcp": True, "dhcp_dns": True, "dhcpv6": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-d", "-D", "--dhcpv6"]
    assert any("disruptive" in n for n in plan.notes)


def test_dhcp_alone_still_warns():
    plan = build({"iface": "eth0", "dhcp": True})
    assert "-d" in plan.array_form
    assert any("disruptive" in n for n in plan.notes)


def test_no_dhcp_no_warning():
    plan = build({"iface": "eth0", "analyze": True})
    assert not any("disruptive" in n for n in plan.notes)


def test_external_ip_spoofing():
    plan = build({"iface": "eth0", "external_ip": "10.0.0.9", "external_ip6": "fe80::1"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-e", "10.0.0.9", "-6", "fe80::1"]


def test_basic_and_verbose_still_work():
    plan = build({"iface": "eth0", "basic": True, "verbose": True})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-b", "-v"]
