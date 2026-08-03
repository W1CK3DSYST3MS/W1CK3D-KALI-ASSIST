"""John the Ripper command builder (Module 05 spec).

Shape: john [mode/options] [--format=…] <hashfile>. The hash file is POSITIONAL
and goes last; mode/format flags precede it. Cracked results land in the pot file
automatically — --show reads them back. Generate-only (offline cracking).

2026-07-26: extended to cover john's FULL `--help` surface (jumbo build
1.9.0-jumbo-1) — the earlier pass only compared against a first-audit "major
gaps" list, not the tool's actual --help output. `unshadow`/`unafs`/`undrop`
and the *2john helpers are SEPARATE binaries (not `john` itself, confirmed via
`dpkg -L john` — they're symlinks to the john binary that switch mode on
argv[0]), so they're taught as their own commands in the `prepare` flow rather
than built by this function.

Recognised keys (all optional except ``hashfile``): profile, hashfile, format,
session, fork, pot, single, wordlist, rules, rules_name, rules_stack,
incremental, show, list, restore, mask, prince, loopback, markov, min_length,
max_length, config, encoding, users, shells, field_separator_char, node,
max_candidates, max_run_time, status, make_charset, stdout, keep_guessing,
test, test_full. Verified against the installed jumbo build (``john --help``,
1.9.0-jumbo-1) — the bundled ``man john`` page is a stale non-jumbo doc and
disagrees with several of these.
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
    if inputs.get("test_full") not in (None, ""):
        return assemble("john", {Slot.GLOBAL_OPTIONS: [f"--test-full={inputs['test_full']}"]},
                        notes=["Runs john's more thorough self-tests/benchmark for every "
                               "format; ignores hash file and attack-mode settings."])
    if _truthy(inputs.get("test")):
        val = inputs.get("test")
        flag = "--test" if val is True or str(val).lower() in {"true", "1", "yes"} else f"--test={val}"
        return assemble("john", {Slot.GLOBAL_OPTIONS: [flag]},
                        notes=["Benchmarks john's cracking speed per hash type; ignores hash file."])

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

    # GLOBAL — run-wide behaviour, input interpretation, and which
    # accounts/candidates are in scope (same grouping as --format below).
    if inputs.get("format"):
        g.append(f"--format={inputs['format']}")
    if inputs.get("session"):
        g.append(f"--session={inputs['session']}")
    if inputs.get("fork"):
        g.append(f"--fork={int(inputs['fork'])}")
    if inputs.get("pot"):
        g.append(f"--pot={inputs['pot']}")
    if inputs.get("config"):
        g.append(f"--config={inputs['config']}")
    if inputs.get("encoding"):
        g.append(f"--encoding={inputs['encoding']}")
    if inputs.get("min_length") not in (None, ""):
        g.append(f"--min-length={int(inputs['min_length'])}")
    if inputs.get("max_length") not in (None, ""):
        g.append(f"--max-length={int(inputs['max_length'])}")
    if inputs.get("users"):
        g.append(f"--users={inputs['users']}")
    if inputs.get("shells"):
        g.append(f"--shells={inputs['shells']}")
    if inputs.get("field_separator_char"):
        g.append(f"--field-separator-char={inputs['field_separator_char']}")
    if inputs.get("node"):
        g.append(f"--node={inputs['node']}")
    if inputs.get("max_candidates") not in (None, ""):
        g.append(f"--max-candidates={int(inputs['max_candidates'])}")
    if inputs.get("max_run_time") not in (None, ""):
        g.append(f"--max-run-time={int(inputs['max_run_time'])}")
    if inputs.get("status"):
        val = inputs.get("status")
        g.append("--status" if val is True or str(val).lower() in {"true", "1", "yes"} else f"--status={val}")

    # ACTION modes (avoid duplicating profile-set flags)
    if _truthy(inputs.get("single")):
        a.append("--single")
    if inputs.get("wordlist") and not any(t.startswith("--wordlist=") for t in a):
        a.append(f"--wordlist={inputs['wordlist']}")
    rules_val = inputs.get("rules_name") or inputs.get("rules")
    if rules_val and not any(t.startswith("--rules") for t in a):
        # allow a named ruleset, e.g. rules_name="Jumbo" / "KoreLogic", or a bare bool toggle
        a.append("--rules" if rules_val is True or str(rules_val).lower() in {"true", "1", "yes"}
                 else f"--rules={rules_val}")
    if inputs.get("rules_stack"):
        a.append(f"--rules-stack={inputs['rules_stack']}")
        notes.append("--rules-stack applies on TOP of the rules already selected above (or to "
                     "modes that don't normally support rules) — it doesn't replace them.")
    if inputs.get("incremental") and not any(t.startswith("--incremental") for t in a):
        inc = inputs.get("incremental")
        a.append("--incremental" if inc is True or str(inc).lower() in {"true", "1", "yes"}
                 else f"--incremental={inc}")

    # Mask mode (spec gap fix): hashcat-style placeholder pattern, e.g.
    # --mask='?d?d?d?d?d?d?d?d' for an 8-digit PIN. ?d=digit ?l=lower ?u=upper ?s=symbol.
    if inputs.get("mask"):
        a.append(f"--mask={inputs['mask']}")

    if inputs.get("make_charset"):
        a.append(f"--make-charset={inputs['make_charset']}")
        notes.append("--make-charset builds a custom incremental charset FROM a wordlist's "
                     "letter-frequency statistics — it doesn't crack anything; needs a "
                     "--wordlist source and no hash file.")

    # Lower-priority modes (PRINCE / loopback / Markov) — same bare-flag-or-named-value
    # shape as --incremental above.
    for key, flag in (("prince", "--prince"), ("loopback", "--loopback"), ("markov", "--markov")):
        val = inputs.get(key)
        if val:
            a.append(flag if val is True or str(val).lower() in {"true", "1", "yes"} else f"{flag}={val}")

    # Preview candidates without cracking — like hashcat's --stdout, needs no
    # hash file at all, just a candidate-generating mode (wordlist/mask/etc.).
    stdout_mode = _truthy(inputs.get("stdout"))
    if stdout_mode:
        val = inputs.get("stdout")
        a.append("--stdout" if val is True or str(val).lower() in {"true", "1", "yes"} else f"--stdout={val}")

    if _truthy(inputs.get("keep_guessing")):
        a.append("--keep-guessing")

    if _truthy(inputs.get("show")):
        a.append("--show")

    # POSITIONAL hashfile (last) — not required for --stdout or --make-charset,
    # both of which generate/derive candidates rather than crack a hash file.
    if inputs.get("hashfile"):
        pos.append(str(inputs["hashfile"]))
    elif not stdout_mode and not inputs.get("make_charset"):
        notes.append("No hash file — supply the file of hashes to crack.")

    return assemble("john", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ACTION_OPTIONS: a,
        Slot.POSITIONAL_ARGS: pos,
    }, notes=notes)
