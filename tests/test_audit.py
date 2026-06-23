"""Audit log: writes JSONL, never logs secrets."""

import json

from wizard_core.audit import AuditLogger, redact


def test_redact_strips_secret_keys():
    out = redact({"username": "kali", "password": "hunter2", "nested": {"token": "abc"}})
    assert out["username"] == "kali"
    assert out["password"] == "[REDACTED]"
    assert out["nested"]["token"] == "[REDACTED]"


def test_redact_masks_secret_in_text():
    out = redact("connecting with password=hunter2 now")
    assert "hunter2" not in out
    assert "[REDACTED]" in out


def test_logger_writes_jsonl_without_secrets(tmp_path):
    log = AuditLogger(tmp_path / "a.audit.jsonl", user="tester")
    log.login("tester")
    log.command_preview(tool="nmap", flow="portscan")
    rec = log.log("wifi_attempt", ssid="HomeNet", password="should-not-appear")

    assert rec["password"] == "[REDACTED]"
    lines = (tmp_path / "a.audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    first = json.loads(lines[0])
    assert first["event"] == "login" and first["user"] == "tester"
    assert "should-not-appear" not in (tmp_path / "a.audit.jsonl").read_text(encoding="utf-8")
