"""dirb command builder — web content scanner (dictionary brute-force of paths).

Shape: dirb <url> [<wordlist>] [options] — url and wordlist must come first, so
both go in TARGET_PIVOT (which sorts before the option slots). Generate-only.

Recognised keys (all optional except ``url``):
  url, wordlist, extensions(-X), cookie(-c), agent(-a), http_auth(-u),
  header(-H), proxy(-p), proxy_auth(-P), delay_ms(-z), no_recursion(-r),
  silent(-S), output(-o). Verified against the installed dirb v2.22 usage
  banner (`dirb` with no args).
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("dirb")
def build_dirb(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    target: list[str] = []  # TARGET_PIVOT (url then wordlist, in that order)
    a: list[str] = []       # ACTION_OPTIONS
    o: list[str] = []       # OUTPUT_OPTIONS (-o)

    url = inputs.get("url")
    if url:
        target.append(str(url))
    else:
        notes.append("No URL — supply the base URL (e.g. http://host/).")
    if inputs.get("wordlist"):
        target.append(str(inputs["wordlist"]))

    if inputs.get("extensions"):
        a.extend(["-X", str(inputs["extensions"])])
    if inputs.get("cookie"):
        a.extend(["-c", str(inputs["cookie"])])
    if inputs.get("agent"):
        a.extend(["-a", str(inputs["agent"])])
    if inputs.get("http_auth"):
        a.extend(["-u", str(inputs["http_auth"])])
    if inputs.get("header"):
        a.extend(["-H", str(inputs["header"])])
    if inputs.get("proxy"):
        a.extend(["-p", str(inputs["proxy"])])
    if inputs.get("proxy_auth"):
        if not inputs.get("proxy"):
            notes.append("-P (proxy auth) only takes effect together with -p (Proxy) — set the Proxy field too.")
        a.extend(["-P", str(inputs["proxy_auth"])])
    delay_ms = inputs.get("delay_ms")
    if delay_ms not in (None, ""):
        a.extend(["-z", str(int(delay_ms))])
    if _truthy(inputs.get("no_recursion")):
        a.append("-r")
    if _truthy(inputs.get("silent")):
        a.append("-S")
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])

    return assemble("dirb", {
        Slot.TARGET_PIVOT: target,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes)
