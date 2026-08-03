"""hashcat command builder (Module 06 spec).

Shape: hashcat -m <type> -a <attack> [options] <hashfile> <wordlist|mask>. The
hash file and the wordlist/mask are POSITIONAL and come last, in that order.
-m (hash mode) is the #1 thing users get wrong — the module makes it explicit.
Combinator mode (-a 1) is the one attack that needs TWO positional wordlists
(dictionary1 dictionary2) instead of one wordlist/mask — handled separately so
the ordering stays correct. Generate-only (offline cracking).

2026-07-26: extended to cover hashcat's FULL `--help` surface (v7.1.2) — the
earlier pass only compared against a first-audit "major gaps" list, not the
tool's actual --help output section by section (Options, Attack modes, Hash
modes, Built-in charsets, Outfile formats, Debug modes). Mode 9 (Association)
is intentionally NOT offered — niche/rare real-world use.

Recognised keys (all optional except hash_mode/hashfile+wordlist|mask):
  profile, benchmark, benchmark_all, identify, list_devices, hash_info,
  hash_mode, attack_mode, rules, rule_left, rule_right, generate_rules,
  custom_charset, custom_charset2, custom_charset3, custom_charset4,
  hex_charset, hex_salt, hex_wordlist, increment, increment_min,
  increment_max, markov_disable, loopback, username, show, left,
  potfile_disable, potfile_path, remove, remove_timer, workload, optimized,
  session, force, output, outfile_format, separator, device,
  opencl_device_type, stdout, keyspace, total_candidates, speed_only,
  progress_only, skip, limit, runtime, quiet, restore, restore_file_path,
  debug_mode, debug_file, keep_guessing, hashfile, wordlist, wordlist2
  (combinator only), mask.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
# attack modes: 0 straight, 1 combinator, 3 mask, 6 hybrid wl+mask, 7 hybrid mask+wl
# (mode 9 "Association" deliberately not offered here — niche.)
_PROFILES: dict[str, dict[str, object]] = {
    "wordlist": {"attack": "0", "wordlist": _DEFAULT_WORDLIST},
    "wordlist_rules": {"attack": "0", "wordlist": _DEFAULT_WORDLIST,
                       "rules": "/usr/share/hashcat/rules/best64.rule"},
    "mask": {"attack": "3"},
    "combinator": {"attack": "1"},
    "benchmark": {"benchmark": True},
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


def _bare_or_named(flag: str, val: object) -> str:
    """--flag alone for a boolean-ish truthy value, --flag=val for a real value."""
    if val is True or str(val).lower() in {"true", "1", "yes"}:
        return flag
    return f"{flag}={val}"


@register_builder("hashcat")
def build_hashcat(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []

    profile = str(inputs.get("profile") or "")
    preset: dict[str, object] = {}
    if profile:
        preset = _PROFILES.get(profile, {})
        if not preset and profile not in _PROFILES:
            raise ValueError(f"Unknown hashcat profile {profile!r}. Valid: {', '.join(_PROFILES)}")
        notes.append(f"Profile '{profile}' pre-filled attack/options.")

    # Standalone forms — these ignore attack setup entirely.
    if _truthy(inputs.get("benchmark")) or preset.get("benchmark"):
        a0 = ["-b"]
        if _truthy(inputs.get("benchmark_all")):
            a0.append("--benchmark-all")
        return assemble("hashcat", {Slot.ACTION_OPTIONS: a0},
                        notes=["Benchmarks your hardware speed."])
    if _truthy(inputs.get("identify")):
        pos = [str(inputs["hashfile"])] if inputs.get("hashfile") else []
        return assemble("hashcat", {Slot.ACTION_OPTIONS: ["--identify"], Slot.POSITIONAL_ARGS: pos})
    if _truthy(inputs.get("list_devices")):
        return assemble("hashcat", {Slot.ENV_INTERFACE: ["-I"]})
    if _truthy(inputs.get("hash_info")):
        hi: list[str] = []
        if inputs.get("hash_mode") not in (None, ""):
            hi.extend(["-m", str(inputs["hash_mode"])])
        hi.append("-H")
        return assemble("hashcat", {Slot.ACTION_OPTIONS: hi},
                        notes=["-H prints details about the hash-mode(s) instead of cracking "
                               "anything — set Hash mode (-m) to see one specific mode, or "
                               "leave it blank to see the full list."])
    if _truthy(inputs.get("restore")):
        rg: list[str] = []
        if inputs.get("session"):
            rg.append(f"--session={inputs['session']}")
        else:
            notes.append("--restore usually needs --session=<name> matching the interrupted "
                         "run — without it hashcat assumes the default session name.")
        rg.append("--restore")
        if inputs.get("restore_file_path"):
            rg.append(f"--restore-file-path={inputs['restore_file_path']}")
        return assemble("hashcat", {Slot.GLOBAL_OPTIONS: rg},
                        notes=notes + ["Resumes a previously interrupted hashcat session."])

    g: list[str] = []   # GLOBAL_OPTIONS
    a: list[str] = []   # ACTION_OPTIONS (-m -a -r etc., before positionals)
    o: list[str] = []   # OUTPUT_OPTIONS
    env: list[str] = []  # ENV_INTERFACE
    pos: list[str] = []  # POSITIONAL_ARGS (hashfile then wordlist/mask)

    # ACTION: hash mode (-m) is critical.
    if inputs.get("hash_mode") not in (None, ""):
        a.extend(["-m", str(inputs["hash_mode"])])
    else:
        notes.append("No -m hash mode set — hashcat needs the exact hash-type number or it never cracks.")
    attack = inputs.get("attack_mode")
    if attack in (None, "") and preset.get("attack"):
        attack = preset["attack"]
    if attack not in (None, ""):
        a.extend(["-a", str(attack)])

    rules = inputs.get("rules") or preset.get("rules")
    if rules:
        a.extend(["-r", str(rules)])
    if inputs.get("rule_left"):
        a.extend(["-j", str(inputs["rule_left"])])
        notes.append("-j applies one rule to every word from the LEFT list (dictionary1).")
    if inputs.get("rule_right"):
        a.extend(["-k", str(inputs["rule_right"])])
        notes.append("-k applies one rule to every word from the RIGHT list (dictionary2).")
    if inputs.get("generate_rules"):
        a.extend(["-g", str(int(inputs["generate_rules"]))])
        notes.append("-g generates that many RANDOM rules instead of using a -r rule file — "
                     "an alternative source of mangling, not normally combined with -r.")

    # Custom charset DEFINITIONS (-1..-4) — defines what ?1/?2/?3/?4 mean in a
    # mask, as distinct from just referencing them.
    for key, flag in (("custom_charset", "-1"), ("custom_charset2", "-2"),
                       ("custom_charset3", "-3"), ("custom_charset4", "-4")):
        val = inputs.get(key)
        if val:
            a.extend([flag, str(val)])

    # Hex-encoded inputs — the charset/salt/wordlist bytes are given in hex,
    # not plain text (binary or non-UTF8 candidate bytes).
    if _truthy(inputs.get("hex_charset")):
        a.append("--hex-charset")
    if _truthy(inputs.get("hex_salt")):
        a.append("--hex-salt")
    if _truthy(inputs.get("hex_wordlist")):
        a.append("--hex-wordlist")

    if _truthy(inputs.get("increment")):
        a.append("--increment")
    if inputs.get("increment_min") not in (None, ""):
        a.extend(["--increment-min", str(int(inputs["increment_min"]))])
    if inputs.get("increment_max") not in (None, ""):
        a.extend(["--increment-max", str(int(inputs["increment_max"]))])
    if _truthy(inputs.get("markov_disable")):
        a.append("--markov-disable")
    if _truthy(inputs.get("loopback")):
        a.append("--loopback")

    if _truthy(inputs.get("username")):
        a.append("--username")
    if _truthy(inputs.get("show")):
        a.append("--show")
    if _truthy(inputs.get("left")):
        a.append("--left")
    if _truthy(inputs.get("potfile_disable")):
        a.append("--potfile-disable")
    if inputs.get("potfile_path"):
        a.extend(["--potfile-path", str(inputs["potfile_path"])])
    if _truthy(inputs.get("remove")):
        a.append("--remove")
    if inputs.get("remove_timer") not in (None, ""):
        a.extend(["--remove-timer", str(int(inputs["remove_timer"]))])
        if "--remove" not in a:
            notes.append("--remove-timer only matters alongside --remove (enable it too).")
    if _truthy(inputs.get("keep_guessing")):
        a.append("--keep-guessing")

    # Debug modes (rule-debugging, DEBUG MODES section of --help) — logs how
    # each rule transformed each word; only meaningful alongside -r/-g.
    if inputs.get("debug_mode") not in (None, ""):
        a.extend(["--debug-mode", str(int(inputs["debug_mode"]))])
        if not (rules or inputs.get("generate_rules")):
            notes.append("--debug-mode only produces output when rules are actually active (-r or -g).")
    if inputs.get("debug_file"):
        a.extend(["--debug-file", str(inputs["debug_file"])])

    # Preview / estimate — see candidates or keyspace size WITHOUT cracking.
    stdout_mode = _truthy(inputs.get("stdout"))
    if stdout_mode:
        a.append("--stdout")
    if _truthy(inputs.get("keyspace")):
        a.append("--keyspace")
    if _truthy(inputs.get("total_candidates")):
        a.append("--total-candidates")
    if _truthy(inputs.get("speed_only")):
        a.append("--speed-only")
    if _truthy(inputs.get("progress_only")):
        a.append("--progress-only")

    if inputs.get("quiet"):
        g.append("--quiet")
    if inputs.get("runtime") not in (None, ""):
        g.extend(["--runtime", str(int(inputs["runtime"]))])
    if inputs.get("skip") not in (None, ""):
        g.extend(["-s", str(int(inputs["skip"]))])
    if inputs.get("limit") not in (None, ""):
        g.extend(["-l", str(int(inputs["limit"]))])

    # GLOBAL tuning
    if inputs.get("workload"):
        g.extend(["-w", str(inputs["workload"])])
    if _truthy(inputs.get("optimized")):
        g.append("-O")
        notes.append("-O is faster but caps the maximum password length.")
    if inputs.get("session"):
        g.append(f"--session={inputs['session']}")
    if _truthy(inputs.get("force")):
        g.append("--force")
        notes.append("--force bypasses warnings but can give WRONG results — not recommended.")

    # OUTPUT
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])
    if inputs.get("outfile_format"):
        o.extend(["--outfile-format", str(inputs["outfile_format"])])
    if inputs.get("separator"):
        o.extend(["-p", str(inputs["separator"])])

    # ENV / device
    if inputs.get("device"):
        env.extend(["-d", str(inputs["device"])])
    if inputs.get("opencl_device_type"):
        env.extend(["-D", str(inputs["opencl_device_type"])])

    # POSITIONAL: hashfile then wordlist/mask — except combinator (-a 1), which
    # takes TWO wordlists (dictionary1 dictionary2), not a wordlist+mask pair.
    # --stdout mode is the one case that needs NO hash file at all (it only
    # generates/prints candidates, never loads or compares a hash).
    if inputs.get("hashfile"):
        pos.append(str(inputs["hashfile"]))
    elif not stdout_mode:
        notes.append("No hash file — supply the file of hashes to crack.")

    if str(attack) == "1":
        wordlist1 = inputs.get("wordlist") or preset.get("wordlist")
        wordlist2 = inputs.get("wordlist2")
        if wordlist1:
            pos.append(str(wordlist1))
        else:
            notes.append("Combinator attack (-a 1) needs a first wordlist (dictionary1).")
        if wordlist2:
            pos.append(str(wordlist2))
        else:
            notes.append(
                "Combinator attack (-a 1) needs a SECOND wordlist (dictionary2) — every word "
                "from the first is paired with every word from the second."
            )
    else:
        target = inputs.get("wordlist") or inputs.get("mask") or preset.get("wordlist")
        if target:
            pos.append(str(target))
        elif str(attack) == "3":
            notes.append("Mask attack (-a 3) needs a mask, e.g. ?u?l?l?l?l?d?d?d.")
        elif str(attack) == "0":
            notes.append("Wordlist attack (-a 0) needs a wordlist path.")

    return assemble("hashcat", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.POSITIONAL_ARGS: pos,
    }, notes=notes)
