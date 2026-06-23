"""sqlmap command builder (Module 03 spec).

sqlmap takes NO positional args — the target lives in -u/-r/-m, always emitted in
the TARGET_PIVOT slot. Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_PROFILES: dict[str, dict[str, list[str]]] = {
    "detect": {"global": ["--batch"], "action": ["--level", "1", "--risk", "1"]},
    "map": {"global": ["--batch"], "action": ["--dbs"]},
    "dump": {"global": ["--batch"], "action": ["--dump"]},
    "thorough": {"global": ["--batch"], "action": ["--level", "5", "--risk", "3"]},
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("sqlmap")
def build_sqlmap(inputs: Mapping[str, object]) -> CommandPlan:
    g: list[str] = []
    a: list[str] = []
    o: list[str] = []
    env: list[str] = []
    extra: list[str] = []
    notes: list[str] = []

    profile = inputs.get("profile")
    if profile:
        preset = _PROFILES.get(str(profile))
        if preset is None:
            raise ValueError(f"Unknown sqlmap profile {profile!r}. Valid: {', '.join(_PROFILES)}")
        g.extend(preset["global"])
        a.extend(preset["action"])
        notes.append(f"Profile '{profile}' pre-filled global + action slots.")

    # GLOBAL
    if _truthy(inputs.get("batch")) and "--batch" not in g:
        g.append("--batch")
    if inputs.get("verbosity") not in (None, ""):
        g.extend(["-v", str(int(inputs["verbosity"]))])
    if _truthy(inputs.get("random_agent")):
        g.append("--random-agent")
    if inputs.get("threads"):
        g.extend(["--threads", str(int(inputs["threads"]))])

    # TARGET (request file wins over URL).
    target: list[str] = []
    if inputs.get("request_file"):
        target = ["-r", str(inputs["request_file"])]
    elif inputs.get("url"):
        target = ["-u", str(inputs["url"])]
    elif inputs.get("urls_file"):
        target = ["-m", str(inputs["urls_file"])]
    else:
        notes.append("No target — supply a URL (-u), request file (-r) or list (-m).")

    # ACTION
    if inputs.get("param"):
        a.extend(["-p", str(inputs["param"])])
    if inputs.get("level") not in (None, ""):
        a.extend(["--level", str(int(inputs["level"]))])
    if inputs.get("risk") not in (None, ""):
        a.extend(["--risk", str(int(inputs["risk"]))])
    if inputs.get("technique"):
        a.append(f"--technique={inputs['technique']}")
    if inputs.get("dbms"):
        a.extend(["--dbms", str(inputs["dbms"])])
    if _truthy(inputs.get("dbs")):
        a.append("--dbs")
    if inputs.get("db"):
        a.extend(["-D", str(inputs["db"])])
    if _truthy(inputs.get("tables")):
        a.append("--tables")
    if inputs.get("table"):
        a.extend(["-T", str(inputs["table"])])
    if _truthy(inputs.get("columns")):
        a.append("--columns")
    if inputs.get("cols"):
        a.extend(["-C", str(inputs["cols"])])
    if _truthy(inputs.get("dump")) and "--dump" not in a:
        a.append("--dump")
    if _truthy(inputs.get("sql_shell")):
        a.append("--sql-shell")
    if _truthy(inputs.get("os_shell")):
        a.append("--os-shell")
        notes.append("High-impact: --os-shell executes commands on the target. Authorized engagements only.")

    # OUTPUT
    if inputs.get("output_dir"):
        o.extend(["--output-dir", str(inputs["output_dir"])])

    # ENV / proxy
    if inputs.get("proxy"):
        env.extend(["--proxy", str(inputs["proxy"])])
    if _truthy(inputs.get("tor")):
        env.extend(["--tor", "--check-tor"])

    # EXTRA inputs
    if inputs.get("data"):
        extra.extend(["--data", str(inputs["data"])])
    if inputs.get("cookie"):
        extra.extend(["--cookie", str(inputs["cookie"])])
    if inputs.get("tamper"):
        extra.append(f"--tamper={inputs['tamper']}")

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: target,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.EXTRA_FILES: extra,
    }
    return assemble("sqlmap", slot_values, notes=notes)
