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

    2026-07-26: extended to cover msfvenom's FULL `-h` surface (previous pass
    only covered the "major gaps" a first audit flagged — see the nmap builder
    for the same corrective pattern). Recognised keys (all optional except
    ``payload``):
      payload, lhost, lport, options(dict or "KEY=VAL,KEY2=VAL2" string),
      list_options, arch, platform, encoder, iterations, badchars, encrypt,
      encrypt_key, encrypt_iv, smallest, space, encoder_space, nopsled,
      pad_nops, add_code, service_name, sec_name, var_name, timeout,
      template, keep, format, outfile, list (shortcut: overrides everything
      else).
    """
    notes: list[str] = []

    if inputs.get("list"):
        return assemble("msfvenom", {Slot.ACTION_OPTIONS: ["--list", str(inputs["list"])]},
                        notes=["Lists payloads/formats/encoders."])

    if inputs.get("list_options"):
        payload = inputs.get("payload")
        if not payload:
            notes.append("--list-options needs a Payload selected first — pick one, then "
                         "check this box to see exactly what it needs (LHOST, LPORT, etc.).")
            return assemble("msfvenom", {}, notes=notes)
        return assemble("msfvenom", {Slot.ACTION_OPTIONS: ["-p", str(payload), "--list-options"]},
                        notes=["Shows this payload's standard/advanced/evasion options — this is "
                               "how you discover what to fill in BEFORE building. Generates nothing."])

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
    encrypt_key = inputs.get("encrypt_key")
    if encrypt_key:
        if not inputs.get("encrypt"):
            notes.append("--encrypt-key only applies together with Encrypt (--encrypt) — set that field too.")
        a.extend(["--encrypt-key", str(encrypt_key)])
    encrypt_iv = inputs.get("encrypt_iv")
    if encrypt_iv:
        if not inputs.get("encrypt"):
            notes.append("--encrypt-iv only applies together with Encrypt (--encrypt) — set that field too.")
        a.extend(["--encrypt-iv", str(encrypt_iv)])

    # Size / NOP-sled shaping — distinct from encoding: these control the
    # RAW BYTE SIZE of the result, not how it's obfuscated.
    if _truthy(inputs.get("smallest")):
        a.append("--smallest")
        notes.append("--smallest already tries every available encoder to find the smallest "
                     "result — an explicit Encoder above is usually redundant alongside it.")
    space = inputs.get("space")
    if space not in (None, ""):
        a.extend(["-s", str(int(space))])
    encoder_space = inputs.get("encoder_space")
    if encoder_space not in (None, ""):
        a.extend(["--encoder-space", str(int(encoder_space))])
    nopsled = inputs.get("nopsled")
    has_nopsled = nopsled not in (None, "")
    if has_nopsled:
        a.extend(["-n", str(int(nopsled))])
    if _truthy(inputs.get("pad_nops")):
        if not has_nopsled:
            notes.append("--pad-nops only has an effect together with -n/NOP sled length — set that field too.")
        a.append("--pad-nops")
    add_code = inputs.get("add_code")
    if add_code:
        a.extend(["-c", str(add_code)])

    # Output-artifact branding — helps a generated binary blend in.
    service_name = inputs.get("service_name")
    if service_name:
        a.extend(["--service-name", str(service_name)])
    sec_name = inputs.get("sec_name")
    if sec_name:
        a.extend(["--sec-name", str(sec_name)])
    var_name = inputs.get("var_name")
    if var_name:
        a.extend(["-v", str(var_name)])
    timeout = inputs.get("timeout")
    if timeout not in (None, ""):
        a.extend(["-t", str(int(timeout))])
        notes.append("-t/--timeout only matters when Payload is '-' or STDIN (reading custom "
                     "shellcode from standard input) — ignored for a normal named payload.")

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
    """Render console grammar into `msfconsole -q -x "use …; set …; run"`.

    2026-07-26: also covers msfconsole's own launch-time CLI flags, which
    previously had ZERO representation anywhere outside the console-grammar
    steps (see docs/DEPTH-AUDIT.md pattern) — -r/--resource (run a saved
    resource script on startup), -o/--output (log console output to a file),
    and -n/--no-database (skip the PostgreSQL connection entirely). Recognised
    keys: commands, module, sets, action, resource_file, output_file,
    no_database.
    """
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

    g: list[str] = ["-q"]  # quiet banner (GLOBAL) — always on, matches prior behaviour.
    a: list[str] = []
    o: list[str] = []

    if _truthy(inputs.get("no_database")):
        g.append("-n")

    resource_file = inputs.get("resource_file")
    if resource_file:
        a.extend(["-r", str(resource_file)])

    if commands:
        # -x runs the script then drops into the console (ACTION).
        a.extend(["-x", "; ".join(commands)])

    output_file = inputs.get("output_file")
    if output_file:
        o.extend(["-o", str(output_file)])

    if not commands and not resource_file:
        notes.append("No console steps — pick a module and the values to set (use/set/run), "
                     "or point Resource script at a saved .rc file to run instead.")
        return assemble("msfconsole", {Slot.GLOBAL_OPTIONS: g, Slot.OUTPUT_OPTIONS: o}, notes=notes)

    return assemble("msfconsole", {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes)
