"""netexec command builder — network execution / AD testing swiss-army knife.

netexec <protocol> <target> [options]. The protocol is a subcommand, the
target(s) are positional (TARGET_PIVOT), everything else — credentials,
enumeration flags, execution — is ACTION_OPTIONS. Generate-only.

Recognised keys (all optional except ``target``): protocol, target, username,
password, hash, domain, local_auth, shares, sam, lsa, ntds, module,
module_options, exec_command, ps_command, list_modules, spider, spider_content.
Verified against the installed build (``netexec smb --help`` / ``-L``, nxc 1.5.1).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("netexec")
def build_netexec(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    t: list[str] = []      # TARGET_PIVOT
    a: list[str] = []      # ACTION_OPTIONS

    protocol = str(inputs.get("protocol") or "smb")

    # -L (list modules for this protocol) is standalone — no credentials needed.
    if _truthy(inputs.get("list_modules")):
        target = inputs.get("target")
        if target:
            t.append(str(target))
        return assemble(
            "netexec", {Slot.TARGET_PIVOT: t, Slot.ACTION_OPTIONS: ["-L"]},
            notes=["Lists every module available for this protocol — no credentials needed."],
            subcommand=[protocol],
        )

    target = inputs.get("target")
    if target:
        t.append(str(target))
    else:
        notes.append("No target — netexec needs an IP/CIDR/hostname/file of targets.")

    if inputs.get("username"):
        a.extend(["-u", str(inputs["username"])])
    if inputs.get("password"):
        a.extend(["-p", str(inputs["password"])])
    if inputs.get("hash"):
        a.extend(["-H", str(inputs["hash"])])
    if inputs.get("domain"):
        a.extend(["-d", str(inputs["domain"])])
    if _truthy(inputs.get("local_auth")):
        a.append("--local-auth")
    if _truthy(inputs.get("shares")):
        a.append("--shares")

    # Credential-material dumping: --sam / --lsa / --ntds (spec gap fix — the
    # builder used to only ever emit --sam even though the guided flow's prose
    # already talked about all three).
    if _truthy(inputs.get("sam")):
        a.append("--sam")
    if _truthy(inputs.get("lsa")):
        a.append("--lsa")
    if _truthy(inputs.get("ntds")):
        a.append("--ntds")
        notes.append("--ntds only works against a Domain Controller — it dumps the WHOLE domain's password database.")

    # The -M module system (spec gap fix — netexec's headline feature was entirely
    # absent). -o takes one or more KEY=VALUE module options after -M <name>.
    if inputs.get("module"):
        a.extend(["-M", str(inputs["module"])])
        mod_opts = inputs.get("module_options")
        if mod_opts:
            a.extend(["-o", *str(mod_opts).split()])
        notes.append(
            "Check a module's own options first with: netexec "
            + protocol + " -M " + str(inputs["module"]) + " --options"
        )

    # -x (CMD) vs -X (PowerShell) are mutually exclusive on the real CLI.
    if inputs.get("exec_command") and inputs.get("ps_command"):
        raise ValueError("Use either exec_command (-x, CMD) or ps_command (-X, PowerShell), not both.")
    if inputs.get("exec_command"):
        a.extend(["-x", str(inputs["exec_command"])])
    elif inputs.get("ps_command"):
        a.extend(["-X", str(inputs["ps_command"])])

    # Share spidering.
    if inputs.get("spider"):
        a.extend(["--spider", str(inputs["spider"])])
        if _truthy(inputs.get("spider_content")):
            a.append("--content")

    return assemble(
        "netexec",
        {
            Slot.TARGET_PIVOT: t,
            Slot.ACTION_OPTIONS: a,
        },
        notes=notes,
        subcommand=[protocol],
    )
