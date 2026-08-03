"""nikto builder: -mutate deeper enumeration, -Save session, client-cert auth,
and the form-gap fields (timeout/pause/maxtime/tuning/vhost/evasion/plugins/…)."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("nikto")


def test_mutate_flag_builds():
    plan = build({"host": "http://t", "mutate": "3"})
    assert "-mutate" in plan.array_form and "3" in plan.array_form


def test_mutate_options_pairs_with_mutate_6():
    plan = build({"host": "http://t", "mutate": "6", "mutate_options": "dirs.txt"})
    toks = plan.array_form
    assert toks.index("-mutate") < toks.index("-mutate-options")
    assert "dirs.txt" in toks


def test_save_bare_true_uses_dot():
    plan = build({"host": "http://t", "save": True})
    assert "-Save" in plan.array_form
    assert plan.array_form[plan.array_form.index("-Save") + 1] == "."


def test_save_named_directory():
    plan = build({"host": "http://t", "save": "./session1"})
    assert "-Save" in plan.array_form and "./session1" in plan.array_form


def test_client_cert_auth():
    plan = build({"host": "http://t", "rsacert": "client.pem", "key": "client.key"})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-RSAcert", "client.pem", "-key", "client.key"]


def test_global_pacing_fields():
    plan = build({"host": "http://t", "timeout": 10, "pause": 2, "maxtime": "5m"})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-timeout", "10", "-Pause", "2", "-maxtime", "5m"]


def test_tuning_vhost_evasion_plugins():
    plan = build({"host": "http://t", "tuning": "1234", "vhost": "admin.site.local",
                  "evasion": "1", "plugins": "@@ALL"})
    toks = plan.array_form
    assert "-Tuning" in toks and "1234" in toks
    assert "-vhost" in toks and "admin.site.local" in toks
    assert "-evasion" in toks and "1" in toks
    assert "-Plugins" in toks and "@@ALL" in toks


def test_nossl_and_verbose_and_list_plugins():
    plan = build({"host": "http://t", "nossl": True, "verbose": True})
    assert "-nossl" in plan.array_form
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-Display", "V"]

    plan2 = build({"list_plugins": True})
    assert plan2.array_form == ["nikto", "-list-plugins"]


def test_proxy_and_auth_id():
    plan = build({"host": "http://t", "proxy": "http://127.0.0.1:8080", "auth_id": "user:pass"})
    assert plan.slot_values[Slot.ENV_INTERFACE] == ["-useproxy", "http://127.0.0.1:8080", "-id", "user:pass"]


# --- 2026-07-26 full -H sweep: standalone diagnostics ---

def test_dbcheck_is_standalone():
    plan = build({"dbcheck": True, "host": "http://t"})
    assert plan.array_form == ["nikto", "-dbcheck"]


def test_version_info_is_standalone():
    plan = build({"version_info": True})
    assert plan.array_form == ["nikto", "-Version"]


def test_dbcheck_takes_priority_over_version_and_list_plugins():
    plan = build({"dbcheck": True, "version_info": True, "list_plugins": True})
    assert plan.array_form == ["nikto", "-dbcheck"]


# --- update-check control ---

def test_nocheck_and_ask():
    plan = build({"host": "http://t", "nocheck": True, "ask": "auto"})
    assert plan.slot_values[Slot.GLOBAL_OPTIONS] == ["-nocheck", "-ask", "auto"]


# --- -Display merges verbose + display_options into one token ---

def test_display_options_merges_with_verbose_no_duplicate():
    plan = build({"host": "http://t", "verbose": True, "display_options": "12V"})
    toks = plan.array_form
    assert toks.index("-Display") >= 0
    disp_value = toks[toks.index("-Display") + 1]
    assert disp_value == "V12"  # V from verbose first, then new chars, no dupe V


def test_display_options_without_verbose():
    plan = build({"host": "http://t", "display_options": "124DEPSV"})
    toks = plan.array_form
    assert toks[toks.index("-Display") + 1] == "124DEPSV"


# --- request/response behaviour toggles ---

def test_behaviour_toggle_flags():
    plan = build({
        "host": "http://t", "nolookup": True, "nointeractive": True,
        "nocookies": True, "noslash": True, "no404": True, "followredirects": True,
        "check6": True,
    })
    for flag in ("-nolookup", "-nointeractive", "-nocookies", "-noslash",
                 "-no404", "-followredirects", "-check6"):
        assert flag in plan.array_form


# --- IP version, user-agent, custom header, 404 filtering ---

def test_ip_version_flags():
    plan = build({"host": "http://t", "ip_version": "ipv4"})
    assert "-ipv4" in plan.array_form

    plan2 = build({"host": "http://t", "ip_version": "ipv6"})
    assert "-ipv6" in plan2.array_form


def test_unknown_ip_version_fails_loudly():
    with pytest.raises(ValueError):
        build({"host": "http://t", "ip_version": "ipv5"})


def test_useragent_and_add_header():
    plan = build({"host": "http://t", "useragent": "Mozilla/5.0 custom",
                  "add_header": "X-Forwarded-For: 127.0.0.1"})
    assert "-useragent" in plan.array_form and "Mozilla/5.0 custom" in plan.array_form
    assert "-Add-header" in plan.array_form and "X-Forwarded-For: 127.0.0.1" in plan.array_form


def test_ignore_code_and_string():
    plan = build({"host": "http://t", "ignore_code": "302,301", "ignore_string": "not found"})
    assert "-404code" in plan.array_form and "302,301" in plan.array_form
    assert "-404string" in plan.array_form and "not found" in plan.array_form


# --- config / Option override ---

def test_config_and_option_override():
    plan = build({"host": "http://t", "config": "/etc/nikto/nikto.conf",
                  "option_override": "USERAGENT=test"})
    assert "-config" in plan.array_form and "/etc/nikto/nikto.conf" in plan.array_form
    assert "-Option" in plan.array_form and "USERAGENT=test" in plan.array_form


# --- scan-scope flags: -Cgidirs/-Platform/-root/-Userdbs ---

def test_cgidirs_platform_root_userdbs():
    plan = build({"host": "http://t", "cgidirs": "/cgi/ /cgi-a/",
                  "platform": "win", "root": "/app", "userdbs": "tests"})
    toks = plan.array_form
    assert "-Cgidirs" in toks and "/cgi/ /cgi-a/" in toks
    assert "-Platform" in toks and "win" in toks
    assert "-root" in toks and "/app" in toks
    assert "-Userdbs" in toks and "tests" in toks
