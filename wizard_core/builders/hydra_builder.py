"""hydra command builder (Module 04 spec).

Shape: hydra [options] -L users -P passwords <target> <service> [formstring].
target + service are POSITIONAL and go LAST, so credential flags live in
ACTION_OPTIONS (slot 4, before POSITIONAL slot 6) — never in EXTRA_FILES, which
would place them after the target. Also covers -x (password bruteforce
GENERATION — candidates built from a MIN:MAX:CHARSET spec instead of a
wordlist), -S (explicit SSL/TLS), and -m (module-specific option string).
Generate-only; online brute force is noisy.

Recognised keys (all optional except target+service): profile, resume, tasks,
port, ssl, verbose, stop_on_success, stop_global, wait, extra_tries, login,
login_list, combo, bruteforce, password, password_list, module_opts,
targets_file, output, output_format, target, service, http_form.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_PROFILES: dict[str, list[str]] = {
    "single": ["-t", "4", "-V", "-f"],
    "targeted": ["-t", "4", "-V", "-f"],
    "standard": ["-t", "4", "-V"],
    "careful": ["-t", "1", "-w", "30"],
}
_FORM_SERVICES = {"http-post-form", "http-get-form", "https-post-form", "https-get-form"}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("hydra")
def build_hydra(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []

    # Resume stands alone.
    if _truthy(inputs.get("resume")):
        return assemble("hydra", {Slot.GLOBAL_OPTIONS: ["-R"]},
                        notes=["Resumes the previously aborted hydra session."])

    g: list[str] = []   # GLOBAL_OPTIONS
    a: list[str] = []   # ACTION_OPTIONS (creds + service flags, before positionals)
    o: list[str] = []   # OUTPUT_OPTIONS
    pos: list[str] = []  # POSITIONAL_ARGS (target service [formstring])

    profile = inputs.get("profile")
    if profile:
        preset = _PROFILES.get(str(profile))
        if preset is None:
            raise ValueError(f"Unknown hydra profile {profile!r}. Valid: {', '.join(_PROFILES)}")
        g.extend(preset)
        notes.append(f"Profile '{profile}' pre-filled tuning options.")

    # GLOBAL tuning
    if inputs.get("tasks") not in (None, ""):
        g.extend(["-t", str(int(inputs["tasks"]))])
    if inputs.get("port"):
        g.extend(["-s", str(inputs["port"])])
    if _truthy(inputs.get("ssl")):
        g.append("-S")
        notes.append("-S forces an explicit SSL/TLS connect — use it when a plain service name "
                     "(e.g. telnet, ftp) is actually running over TLS on that port.")
    if _truthy(inputs.get("verbose")) and "-V" not in g:
        g.append("-V")
    if _truthy(inputs.get("stop_on_success")) and "-f" not in g:
        g.append("-f")
    if _truthy(inputs.get("stop_global")):
        g.append("-F")
    if inputs.get("wait") not in (None, ""):
        g.extend(["-w", str(inputs["wait"])])
    if inputs.get("extra_tries"):
        g.extend(["-e", str(inputs["extra_tries"])])

    # ACTION: credentials (single or list or combo) + multi-target file
    if inputs.get("login"):
        a.extend(["-l", str(inputs["login"])])
    elif inputs.get("login_list"):
        a.extend(["-L", str(inputs["login_list"])])

    # Passwords: -x (GENERATE candidates from a charset/length range) is a
    # different technique from -p/-P/-C (try candidates FROM a list/file) —
    # it wins if set, since hydra doesn't combine password sources.
    bruteforce = inputs.get("bruteforce")
    if bruteforce:
        a.extend(["-x", str(bruteforce)])
        if inputs.get("combo") or inputs.get("password") or inputs.get("password_list"):
            notes.append(
                "-x (bruteforce generation) replaces -p/-P/-C — those password inputs are "
                "ignored while a bruteforce spec is set."
            )
        notes.append("-x implies -u (loop usernames on the outside) automatically.")
    elif inputs.get("combo"):
        a.extend(["-C", str(inputs["combo"])])
    elif inputs.get("password"):
        a.extend(["-p", str(inputs["password"])])
    elif inputs.get("password_list"):
        a.extend(["-P", str(inputs["password_list"])])

    if inputs.get("module_opts"):
        a.extend(["-m", str(inputs["module_opts"])])

    targets_file = inputs.get("targets_file")
    if targets_file:
        a.extend(["-M", str(targets_file)])

    # OUTPUT
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])
    if inputs.get("output_format"):
        o.extend(["-b", str(inputs["output_format"])])

    # POSITIONAL: target (unless -M), service, optional form string
    if not targets_file:
        if inputs.get("target"):
            pos.append(str(inputs["target"]))
        else:
            notes.append("No target — supply a host (or a -M targets file).")
    service = inputs.get("service")
    if service:
        pos.append(str(service))
        if str(service) in _FORM_SERVICES:
            if inputs.get("http_form"):
                pos.append(str(inputs["http_form"]))
            else:
                notes.append(
                    "Form service needs a \"path:body(^USER^/^PASS^):F=failure\" string."
                )
    else:
        notes.append("No service module (e.g. ssh, ftp, http-post-form).")

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.POSITIONAL_ARGS: pos,
    }
    return assemble("hydra", slot_values, notes=notes)
