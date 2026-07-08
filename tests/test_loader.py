"""Module loader: validates manifests, loads content, aggregates the T00 router."""

from pathlib import Path

import pytest

from wizard_core.loader import ModuleError, api_satisfied, load_modules

MODULES = Path(__file__).resolve().parents[1] / "modules"


def test_api_satisfied():
    assert api_satisfied(">=1.0")
    assert api_satisfied(">=1.0", "1.0")
    assert not api_satisfied(">=2.0", "1.0")
    assert api_satisfied("==1.0", "1.0")


def test_loads_all_three_module_types():
    reg = load_modules(MODULES)
    assert "fundamentals.shell_grammar" in reg.modules
    assert "tool.nmap" in reg.modules
    assert "troubleshoot.networking" in reg.modules
    assert "troubleshoot.index" in reg.modules
    # content registered
    assert "lesson.shell_grammar" in reg.lessons
    assert "nmap" in reg.tools
    assert "troubleshoot.networking" in reg.troubleshooters


def test_nmap_tool_has_flows_and_auth_gate():
    reg = load_modules(MODULES)
    tool = reg.tools["nmap"]
    assert tool.authorization_gate is True
    assert len(tool.flows) >= 9
    # includes the beginner walk-through plus the capability reference flows
    assert {f.flow_id for f in tool.flows} >= {"guided", "discovery", "portscan", "full"}


def test_glossary_merged_across_modules():
    reg = load_modules(MODULES)
    assert "slot" in reg.glossary          # from shell_grammar
    assert "syn_scan" in reg.glossary      # from nmap
    assert "rfkill" in reg.glossary        # from networking


def test_router_symptom_search_is_deterministic():
    reg = load_modules(MODULES)
    matches = reg.search_symptoms("no internet")
    assert matches
    assert matches[0].symptom_id == "no_internet"
    assert matches[0].troubleshooter_id == "troubleshoot.networking"
    # DNS query routes to dns_fail
    dns = reg.search_symptoms("websites won't resolve by name dns")
    assert any(m.symptom_id == "dns_fail" for m in dns)


def test_categories_index():
    reg = load_modules(MODULES)
    assert "reconnaissance" in reg.categories()
    assert "nmap" in reg.categories()["reconnaissance"]


def test_bad_manifest_fails_loudly(tmp_path):
    bad = tmp_path / "broken"
    bad.mkdir()
    (bad / "manifest.yaml").write_text("module_id: x\n", encoding="utf-8")  # missing required fields
    with pytest.raises(ModuleError):
        load_modules(tmp_path)
