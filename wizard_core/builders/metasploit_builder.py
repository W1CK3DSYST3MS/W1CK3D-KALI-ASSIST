"""Metasploit builders (Module 08 spec): msfvenom + msfconsole.

- ``msfvenom`` is a real CLI tool — the 8-slot model applies directly.
- ``msfconsole`` flows follow the console grammar (select -> inspect -> configure
  -> verify -> run -> interact); we render them into a single non-interactive
  ``msfconsole -q -x "cmd; cmd; …"`` one-liner.

Generate-only. Offensive framework — the UI gates it behind a red authorization step.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("msfvenom")
def build_msfvenom(inputs: Mapping[str, object]) -> CommandPlan:
    """Build a msfvenom CommandPlan from validated inputs.

    Recognised keys (all optional except ``payload``):
      payload, lhost, lport, options(dict or "KEY=VAL,KEY2=VAL2" string),
      arch, platform, encoder, iterations, badchars, template, keep,
      encrypt, format, outfile, list (shortcut: overrides everything else).
    """
    notes: list[str] = []

    if inputs.get("list"):
        return assemble("msfvenom", {Slot.ACTION_OPTIONS: ["--list", str(inputs["list"])]},
                        notes=["Lists payloads/formats/encoders."])

    a: list[str] = []   # -p + datastore + shaping (kept in canonical order within the slot)
    o: list[str] = []   # -f / -o

    if inputs.get("payload"):
        a.extend(["-p", str(inputs["payload"])])
    else:
        notes.append("No payload (-p) — e.g. windows/x64/meterpreter/reverse_tcp.")

    # Datastore KEY=VAL (LHOST/LPORT and any extras) right after -p.
    if inputs.get("lhost"):
        a.append(f"LHOST={inputs['lhost']}")
    if inputs.get("lport"):
        a.append(f"LPORT={inputs['lport']}")
    extra_opts = inputs.get("options")
    if isinstance(extra_opts, Mapping):
        for k, v in extra_opts.items():
            a.append(f"{k}={v}")
    elif isinstance(extra_opts, str) and extra_opts.strip():
        # Quick-build form has no dict widget — accept "KEY=VAL,KEY2=VAL2" too.
        for pair in extra_opts.split(","):
            pair = pair.strip()
            if pair:
                a.append(pair)

    # Shaping (honesty: encoders are not reliable AV evasion).
    if inputs.get("arch"):
        a.extend(["-a", str(inputs["arch"])])
    if inputs.get("platform"):
        a.extend(["--platform", str(inputs["platform"])])
    if inputs.get("encoder"):
        a.extend(["-e", str(inputs["encoder"])])
        notes.append("Encoders (-e) are NOT reliable AV evasion anymore — don't rely on them.")
    if inputs.get("iterations"):
        a.extend(["-i", str(int(inputs["iterations"]))])
    if inputs.get("badchars"):
        a.extend(["-b", str(inputs["badchars"])])
    if inputs.get("encrypt"):
        a.extend(["--encrypt", str(inputs["encrypt"])])

    # Template injection: wrap the payload inside an existing executable so it
    # keeps looking (and, with -k, working) like the original program. This is
    # literal trojan-creation technique — authorized lab/engagement files only.
    template = inputs.get("template")
    keep = _truthy(inputs.get("keep"))
    if template:
        a.extend(["-x", str(template)])
        if keep:
            a.append("-k")
        notes.append(
            "-x/--template injects the payload into an existing executable — the file you "
            "produce will look (and, with -k, still work) like a real program. Only use this "
            "on files you own, in an authorized lab/engagement — never against real "
            "third-party software."
        )
    elif keep:
        notes.append("-k (--keep) only has an effect together with a Template (-x) file — ignored without one.")

    # OUTPUT format + file
    if inputs.get("format"):
        o.extend(["-f", str(inputs["format"])])
    if inputs.get("outfile"):
        o.extend(["-o", str(inputs["outfile"])])

    return assemble("msfvenom", {Slot.ACTION_OPTIONS: a, Slot.OUTPUT_OPTIONS: o}, notes=notes)


@register_builder("msfconsole")
def build_msfconsole(inputs: Mapping[str, object]) -> CommandPlan:
    """Render console grammar into `msfconsole -q -x "use …; set …; run"`."""
    notes: list[str] = []
    commands: list[str] = []

    explicit = inputs.get("commands")
    if isinstance(explicit, (list, tuple)) and explicit:
        commands = [str(c) for c in explicit]
    else:
        if inputs.get("module"):
            commands.append(f"use {inputs['module']}")
        sets = inputs.get("sets")
        if isinstance(sets, Mapping):
            for k, v in sets.items():
                commands.append(f"set {k} {v}")
        action = inputs.get("action")
        if action:
            commands.append(str(action))

    if not commands:
        notes.append("No console steps — pick a module and the values to set (use/set/run).")
        return assemble("msfconsole", {Slot.GLOBAL_OPTIONS: ["-q"]}, notes=notes)

    script = "; ".join(commands)
    # -q quiet banner (GLOBAL); -x runs the script then drops into the console (ACTION).
    return assemble("msfconsole", {
        Slot.GLOBAL_OPTIONS: ["-q"],
        Slot.ACTION_OPTIONS: ["-x", script],
    }, notes=notes)
