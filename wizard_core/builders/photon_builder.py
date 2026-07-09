"""photon command builder — fast web crawler for OSINT.

Crawls a site collecting URLs, emails, keys, and files. Generate-only.
URL via -u; depth -l, threads -t, output dir -o, --wayback for archived URLs.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("photon")
def build_photon(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    env: list[str] = []    # ENV_INTERFACE (-u url)
    a: list[str] = []      # ACTION_OPTIONS (depth/threads/delay/wayback)
    o: list[str] = []      # OUTPUT_OPTIONS (-o)

    url = inputs.get("url")
    if url:
        env.extend(["-u", str(url)])
    else:
        notes.append("No URL — supply the site to crawl with -u (e.g. https://example.com).")
    if inputs.get("depth") not in (None, ""):
        a.extend(["-l", str(int(inputs["depth"]))])
    if inputs.get("threads") not in (None, ""):
        a.extend(["-t", str(int(inputs["threads"]))])
    if inputs.get("delay") not in (None, ""):
        a.extend(["-d", str(inputs["delay"])])
    if _truthy(inputs.get("wayback")):
        a.append("--wayback")
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])

    return assemble("photon", {
        Slot.ENV_INTERFACE: env,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes)
