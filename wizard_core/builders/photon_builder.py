"""photon command builder — fast web crawler for OSINT.

Crawls a site collecting URLs, emails, keys, and files. Generate-only.
URL via -u; depth -l, threads -t, delay -d, output dir -o, --wayback for
archived URLs, --keys for secret/API-key detection, --dns for subdomain
enumeration during the crawl, --clone to mirror the site locally, and
-e/--export to also write a csv/json summary.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_EXPORT_FORMATS = {"csv", "json"}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("photon")
def build_photon(inputs: Mapping[str, object]) -> CommandPlan:
    """Build a photon CommandPlan from validated inputs.

    Recognised keys (all optional except ``url``):
      url, depth, threads, delay, wayback, keys, dns, clone, export, output.
    """
    notes: list[str] = []
    env: list[str] = []    # ENV_INTERFACE (-u url)
    a: list[str] = []      # ACTION_OPTIONS (depth/threads/delay/wayback/keys/dns/clone)
    o: list[str] = []      # OUTPUT_OPTIONS (-o, -e)

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
    if _truthy(inputs.get("keys")):
        a.append("--keys")
        notes.append(
            "--keys flags anything that LOOKS like an API key/secret in crawled pages/JS — "
            "always verify a hit manually before treating it as a real finding."
        )
    if _truthy(inputs.get("dns")):
        a.append("--dns")
    if _truthy(inputs.get("clone")):
        a.append("--clone")
        notes.append(
            "--clone downloads a local copy of every crawled page's content, not just its URL — "
            "can use real disk space on a large site or deep crawl."
        )
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])
    export = inputs.get("export")
    if export:
        if str(export) not in _EXPORT_FORMATS:
            raise ValueError(
                f"Unknown export format {export!r}. Valid: {', '.join(sorted(_EXPORT_FORMATS))}"
            )
        o.extend(["-e", str(export)])

    return assemble("photon", {
        Slot.ENV_INTERFACE: env,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes)
