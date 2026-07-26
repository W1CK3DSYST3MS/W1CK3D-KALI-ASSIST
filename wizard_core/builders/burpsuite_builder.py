"""burpsuite command builder — web proxy / application testing platform (GUI).

Launches the Burp Suite GUI. Generate-only. Options preload a project/config file;
most work happens in the GUI + browser proxy, not on the command line. Startup flags
per `burpsuite --help` (Kali burpsuite wrapper).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("burpsuite")
def build_burpsuite(inputs: Mapping[str, object]) -> CommandPlan:
    g: list[str] = []
    if _truthy(inputs.get("use_defaults")):
        g.append("--use-defaults")
    if _truthy(inputs.get("disable_extensions")):
        g.append("--disable-extensions")
    if inputs.get("project_file"):
        g.append("--project-file=" + str(inputs["project_file"]))
    if inputs.get("config_file"):
        g.append("--config-file=" + str(inputs["config_file"]))
    if inputs.get("data_dir"):
        g.append("--data-dir=" + str(inputs["data_dir"]))
    if _truthy(inputs.get("auto_repair")):
        g.append("--auto-repair")
    return assemble("burpsuite", {Slot.GLOBAL_OPTIONS: g})
