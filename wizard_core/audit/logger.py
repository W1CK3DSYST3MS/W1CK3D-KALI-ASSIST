"""On-device audit log (Blueprint §8.3).

A local accountability trail in JSON Lines. This is the project's safety model:
accountability over censorship. NEVER logs secrets (passwords, tokens, keys).

Events are small dicts: timestamp, user, category/tool/flow, step milestones,
"command preview generated". Nothing is sent anywhere — append-only local file.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Keys whose values must never be written, even if a caller passes them.
_SECRET_KEYS = {
    "password", "passwd", "pass", "secret", "token", "api_key", "apikey",
    "key", "private_key", "passphrase", "credential", "credentials", "auth",
    "wifi_password", "psk",
}

# Patterns that look like secrets embedded in free text -> masked.
_SECRET_PATTERNS = [
    re.compile(r"(password|passwd|psk|token|secret|api[_-]?key)\s*[:=]\s*\S+", re.I),
]


def redact(value: Any) -> Any:
    """Recursively strip secret-keyed fields and mask secret-looking substrings."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if str(k).lower() in _SECRET_KEYS:
                out[k] = "[REDACTED]"
            else:
                out[k] = redact(v)
        return out
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    if isinstance(value, str):
        masked = value
        for pat in _SECRET_PATTERNS:
            masked = pat.sub(lambda m: m.group(0).split(m.group(1))[0] + m.group(1) + "=[REDACTED]", masked)
        return masked
    return value


class AuditLogger:
    """Append-only JSONL audit logger. Pass a file path (created on first write)."""

    def __init__(self, path: str | Path, *, user: str = "local") -> None:
        self._path = Path(path)
        self._user = user

    @property
    def path(self) -> Path:
        return self._path

    def log(self, event: str, **fields: Any) -> dict[str, Any]:
        """Write one audit record. Returns the record actually written (redacted)."""
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "user": self._user,
            "event": event,
            **redact(fields),
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    # Convenience wrappers for the common events (Blueprint §8.3).
    def login(self, username: str) -> dict[str, Any]:
        return self.log("login", username=username)

    def selected(self, kind: str, ident: str) -> dict[str, Any]:
        return self.log("selected", kind=kind, id=ident)

    def step_milestone(self, flow: str, step_id: str, result: str) -> dict[str, Any]:
        return self.log("step_milestone", flow=flow, step_id=step_id, result=result)

    def command_preview(self, tool: str, flow: str) -> dict[str, Any]:
        # Note: we log THAT a preview was generated, not the target string.
        return self.log("command_preview_generated", tool=tool, flow=flow)

    def authorization_ack(self, tool: str) -> dict[str, Any]:
        return self.log("authorization_acknowledged", tool=tool)
