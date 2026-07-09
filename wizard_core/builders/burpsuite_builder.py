"""burpsuite command builder — web proxy / application testing platform (GUI).

Launches the Burp Suite GUI. Generate-only. Options preload a project/config file;
most work happens in the GUI + browser proxy, not on the command line.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


@register_builder("burpsuite")
def build_burpsuite(inputs: Mapping[str, object]) -> CommandPlan:
    g: list[str] = []
    if inputs.get("project_file"):
        g.append("--project-file=" + str(inputs["project_file"]))
    if inputs.get("config_file"):
        g.append("--config-file=" + str(inputs["config_file"]))
    return assemble("burpsuite", {Slot.GLOBAL_OPTIONS: g})
