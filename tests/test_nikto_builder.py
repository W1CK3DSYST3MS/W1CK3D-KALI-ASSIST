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
