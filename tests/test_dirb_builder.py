"""dirb builder: target/wordlist positional order, auth, proxy, throttle, output."""

import pytest

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("dirb")


def test_url_and_wordlist_order_in_target_pivot():
    plan = build({"url": "http://target/", "wordlist": "/usr/share/dirb/wordlists/big.txt"})
    assert plan.slot_values[Slot.TARGET_PIVOT] == ["http://target/", "/usr/share/dirb/wordlists/big.txt"]


def test_missing_url_is_noted_not_crashed():
    plan = build({})
    assert any("No URL" in n for n in plan.notes)
    assert Slot.TARGET_PIVOT not in plan.slot_values


def test_extensions_cookie_agent_flags():
    plan = build({"url": "http://target/", "extensions": ".php,.bak",
                  "cookie": "PHPSESSID=abc", "agent": "Mozilla/5.0"})
    assert plan.slot_values[Slot.ACTION_OPTIONS] == [
        "-X", ".php,.bak", "-c", "PHPSESSID=abc", "-a", "Mozilla/5.0",
    ]


def test_http_basic_auth_flag():
    plan = build({"url": "http://target/admin/", "http_auth": "admin:password123"})
    assert "-u" in plan.array_form and "admin:password123" in plan.array_form


def test_custom_header_flag():
    plan = build({"url": "http://target/", "header": "Authorization: Bearer TOKEN"})
    assert "-H" in plan.array_form and "Authorization: Bearer TOKEN" in plan.array_form


def test_proxy_flag():
    plan = build({"url": "http://target/", "proxy": "127.0.0.1:8080"})
    assert "-p" in plan.array_form and "127.0.0.1:8080" in plan.array_form


def test_proxy_auth_without_proxy_warns():
    plan = build({"url": "http://target/", "proxy_auth": "proxyuser:proxypass"})
    assert "-P" in plan.array_form and "proxyuser:proxypass" in plan.array_form
    assert any("-p (Proxy)" in n for n in plan.notes)


def test_proxy_and_proxy_auth_together_no_warning():
    plan = build({"url": "http://target/", "proxy": "proxy.corp.local:3128",
                  "proxy_auth": "proxyuser:proxypass"})
    assert "-p" in plan.array_form and "-P" in plan.array_form
    assert not any("-p (Proxy)" in n for n in plan.notes)


def test_delay_ms_flag():
    plan = build({"url": "http://target/", "delay_ms": 200})
    assert "-z" in plan.array_form and "200" in plan.array_form


def test_silent_and_no_recursion_flags():
    plan = build({"url": "http://target/", "silent": True, "no_recursion": True})
    assert "-S" in plan.array_form
    assert "-r" in plan.array_form


def test_output_flag():
    plan = build({"url": "http://target/", "output": "~/dirb.txt"})
    assert plan.slot_values[Slot.OUTPUT_OPTIONS] == ["-o", "~/dirb.txt"]


def test_full_command_preview_order():
    plan = build({"url": "http://target/", "wordlist": "big.txt", "proxy": "127.0.0.1:8080",
                  "delay_ms": 200, "output": "out.txt"})
    assert plan.bash_preview_string == (
        "dirb http://target/ big.txt -p 127.0.0.1:8080 -z 200 -o out.txt"
    )
