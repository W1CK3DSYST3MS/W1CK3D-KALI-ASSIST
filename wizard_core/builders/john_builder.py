"""John the Ripper command builder (Module 05 spec).

Shape: john [mode/options] [--format=…] <hashfile>. The hash file is POSITIONAL
and goes last; mode/format flags precede it. Cracked results land in the pot file
automatically — --show reads them back. Generate-only (offline cracking).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("john")
def build_john(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []

    # Standalone forms.
    if inputs.get("list"):
        return assemble("john", {Slot.GLOBAL_OPTIONS: [f"--list={inputs['list']}"]})
    if _truthy(inputs.get("restore")):
        name = inputs.get("restore")
        flag = f"--restore={name}" if isinstance(name, str) and name not in ("True", "true") else "--restore"
        return assemble("john", {Slot.GLOBAL_OPTIONS: [flag]},
                        notes=["Resumes a previously aborted john session."])

    g: list[str] = []   # GLOBAL_OPTIONS
    a: list[str] = []   # ACTION_OPTIONS (mode flags, before positional hashfile)
    pos: list[str] = []  # POSITIONAL_ARGS (hashfile last)

    profile = str(inputs.get("profile") or "")
    if profile == "wordlist":
        a.extend(["--wordlist=" + str(inputs.get("wordlist") or _DEFAULT_WORDLIST), "--rules"])
        notes.append("Profile 'wordlist' set --wordlist + --rules.")
    elif profile == "brute":
        a.append("--incremental")
        notes.append("Profile 'brute' set --incremental (slow; short/odd hashes only).")
    elif profile == "targeted":
        if not inputs.get("format"):
            notes.append("Profile 'targeted' needs --format=<name> (set the hash type).")
        a.append("--wordlist=" + str(inputs.get("wordlist") or _DEFAULT_WORDLIST))
        notes.append("Profile 'targeted' set --wordlist; supply --format.")
    elif profile and profile != "auto":
        raise ValueError(f"Unknown john profile {profile!r}. Valid: auto, wordlist, targeted, brute.")

    # GLOBAL
    if inputs.get("format"):
        g.append(f"--format={inputs['format']}")
    if inputs.get("session"):
        g.append(f"--session={inputs['session']}")
    if inputs.get("fork"):
        g.append(f"--fork={int(inputs['fork'])}")
    if inputs.get("pot"):
        g.append(f"--pot={inputs['pot']}")

    # ACTION modes (avoid duplicating profile-set flags)
    if _truthy(inputs.get("single")):
        a.append("--single")
    if inputs.get("wordlist") and not any(t.startswith("--wordlist=") for t in a):
        a.append(f"--wordlist={inputs['wordlist']}")
    if _truthy(inputs.get("rules")) and "--rules" not in a:
        # allow a named ruleset, e.g. rules="Jumbo"
        a.append("--rules" if inputs.get("rules") is True or str(inputs.get("rules")).lower() in {"true", "1", "yes"}
                 else f"--rules={inputs['rules']}")
    if inputs.get("incremental") and not any(t.startswith("--incremental") for t in a):
        inc = inputs.get("incremental")
        a.append("--incremental" if inc is True or str(inc).lower() in {"true", "1", "yes"}
                 else f"--incremental={inc}")
    if _truthy(inputs.get("show")):
        a.append("--show")

    # POSITIONAL hashfile (last)
    if inputs.get("hashfile"):
        pos.append(str(inputs["hashfile"]))
    else:
        notes.append("No hash file — supply the file of hashes to crack.")

    return assemble("john", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ACTION_OPTIONS: a,
        Slot.POSITIONAL_ARGS: pos,
    }, notes=notes)
