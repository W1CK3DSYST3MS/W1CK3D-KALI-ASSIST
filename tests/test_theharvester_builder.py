"""theHarvester builder: core search flags plus the Shodan/screenshot/API-scan additions."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("theharvester")


def test_basic_search_builds_d_and_b():
    plan = build({"domain": "example-corp.com", "sources": "crtsh"})
    assert plan.bash_preview_string == "theHarvester -d example-corp.com -b crtsh"


def test_shodan_flag_adds_dash_s_and_warns_about_api_key():
    plan = build({"domain": "example-corp.com", "sources": "crtsh", "shodan": True})
    assert "-s" in plan.slot_values[Slot.ACTION_OPTIONS]
    assert any("Shodan API key" in n for n in plan.notes)


def test_no_shodan_flag_means_no_dash_s_or_note():
    plan = build({"domain": "example-corp.com", "sources": "crtsh"})
    assert "-s" not in plan.array_form
    assert not any("Shodan API key" in n for n in plan.notes)


def test_api_scan_with_wordlist():
    plan = build({"domain": "example-corp.com", "sources": "crtsh",
                  "api_scan": True, "api_wordlist": "endpoints.txt"})
    a = plan.slot_values[Slot.ACTION_OPTIONS]
    assert "-a" in a
    assert a[a.index("-a") + 1:a.index("-a") + 3] == ["-w", "endpoints.txt"] or ("-w" in a and "endpoints.txt" in a)


def test_api_scan_without_wordlist_omits_dash_w():
    plan = build({"domain": "example-corp.com", "sources": "crtsh", "api_scan": True})
    assert "-a" in plan.array_form
    assert "-w" not in plan.array_form


def test_screenshot_dir_is_output_option():
    plan = build({"domain": "example-corp.com", "sources": "crtsh", "screenshot_dir": "./shots"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["--screenshot", "./shots"]


def test_missing_domain_is_noted_not_crashed():
    plan = build({"sources": "crtsh"})
    assert any("No domain" in n for n in plan.notes)
