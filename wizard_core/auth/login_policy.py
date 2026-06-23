"""Local login + disclaimer gate rules (Blueprint §8.1). UI-agnostic.

This is a LOCAL accountability gate, not network auth (the app is offline). It
enforces: a username, a password meeting a minimal policy, and an explicit
disclaimer acknowledgment. The wizard stays locked until all pass.

Passwords are never stored or logged in plaintext: ``hash_password`` produces a
salted PBKDF2 digest for optional local persistence.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
from dataclasses import dataclass, field

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{3,32}$")
_MIN_PASSWORD_LEN = 8
_PBKDF2_ROUNDS = 200_000

DISCLAIMER_TEXT = (
    "W1CK3D'S KALI ASSIST is a GENERATE-ONLY reference and learning tool. It does "
    "NOT run any commands for you. You are solely responsible for what you run in "
    "your own terminal, and you must only use these techniques on systems you own "
    "or are explicitly authorized to test. Unauthorized access or scanning may be "
    "illegal. Activity is recorded to a local audit log for accountability."
)


@dataclass
class LoginResult:
    ok: bool
    errors: list[str] = field(default_factory=list)


class LoginPolicy:
    """Validates credentials + disclaimer. No I/O, no UI, no network."""

    min_password_len: int = _MIN_PASSWORD_LEN

    def validate(self, username: str, password: str, disclaimer_ack: bool) -> LoginResult:
        errors: list[str] = []
        if not username or not _USERNAME_RE.match(username):
            errors.append(
                "Username must be 3–32 chars: letters, digits, '_', '.', '-'."
            )
        if not password or len(password) < self.min_password_len:
            errors.append(f"Password must be at least {self.min_password_len} characters.")
        if not disclaimer_ack:
            errors.append("You must acknowledge the disclaimer to continue.")
        return LoginResult(ok=not errors, errors=errors)

    # -- optional local credential persistence helpers --------------------- #
    @staticmethod
    def hash_password(password: str, *, salt: bytes | None = None) -> str:
        """Return ``pbkdf2$<rounds>$<salt_hex>$<digest_hex>`` for local storage."""
        salt = salt or os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ROUNDS)
        return f"pbkdf2${_PBKDF2_ROUNDS}${salt.hex()}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, stored: str) -> bool:
        try:
            scheme, rounds_s, salt_hex, digest_hex = stored.split("$")
            if scheme != "pbkdf2":
                return False
            digest = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(rounds_s)
            )
            return hmac.compare_digest(digest.hex(), digest_hex)
        except (ValueError, AttributeError):
            return False
