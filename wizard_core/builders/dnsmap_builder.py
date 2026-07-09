"""dnsmap command builder — subdomain brute-forcer via DNS.

Enumerates subdomains of a domain from a built-in or supplied wordlist.
Generate-only. Domain is POSITIONAL; -w wordlist, -r/-c save results.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


@register_builder("dnsmap")
def build_dnsmap(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    # dnsmap requires the domain as the FIRST argument (argv[1]); TARGET_PIVOT
    # sorts before ACTION/OUTPUT/EXTRA, so the domain leads and options follow.
    target: list[str] = []  # TARGET_PIVOT (domain, must come first)
    a: list[str] = []       # ACTION_OPTIONS (delay / ignore-ips)
    o: list[str] = []       # OUTPUT_OPTIONS (-r / -c)
    extra: list[str] = []   # EXTRA_FILES (-w wordlist)

    domain = inputs.get("domain")
    if domain:
        target.append(str(domain))
    else:
        notes.append("No domain — supply the target domain (e.g. example.com) as the first argument.")

    if inputs.get("wordlist"):
        extra.extend(["-w", str(inputs["wordlist"])])
    if inputs.get("delay"):
        a.extend(["-d", str(int(inputs["delay"]))])
    if inputs.get("ignore_ips"):
        a.extend(["-i", str(inputs["ignore_ips"])])
    if inputs.get("results"):
        o.extend(["-r", str(inputs["results"])])
    if inputs.get("csv"):
        o.extend(["-c", str(inputs["csv"])])

    return assemble(
        "dnsmap",
        {
            Slot.TARGET_PIVOT: target,
            Slot.ACTION_OPTIONS: a,
            Slot.OUTPUT_OPTIONS: o,
            Slot.EXTRA_FILES: extra,
        },
        notes=notes,
    )
