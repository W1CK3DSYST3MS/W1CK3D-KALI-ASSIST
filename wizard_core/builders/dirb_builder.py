"""dirb command builder — web content scanner (dictionary brute-force of paths).

Shape: dirb <url> [<wordlist>] [options] — url and wordlist must come first, so
both go in TARGET_PIVOT (which sorts before the option slots). Generate-only.

2026-07-26: extended past the usage banner to dirb's FULL `man dirb` option
list (previous pass only covered the "major gaps" a first, shallower audit
flagged — see the nmap builder for the same corrective pattern). Recognised
keys (all optional except ``url``):
  url, wordlist, extensions(-X), extensions_file(-x), cookie(-c), agent(-a),
  http_auth(-u), header(-H), client_cert(-E), proxy(-p), proxy_auth(-P),
  delay_ms(-z), no_recursion(-r), interactive_recursion(-R), silent(-S),
  case_insensitive(-i), show_location(-l), ignore_code(-N), tune_404(-f),
  show_not_found(-v), ignore_warnings(-w), raw_path(-b),
  no_trailing_slash(-t), output(-o). Verified against `man dirb` for the
  installed dirb v2.22 (its bare usage banner is missing several of these).
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
    if inputs.get("extensions_file"):
        a.extend(["-x", str(inputs["extensions_file"])])
    if inputs.get("cookie"):
        a.extend(["-c", str(inputs["cookie"])])
    if inputs.get("agent"):
        a.extend(["-a", str(inputs["agent"])])
    if inputs.get("http_auth"):
        a.extend(["-u", str(inputs["http_auth"])])
    if inputs.get("header"):
        a.extend(["-H", str(inputs["header"])])
    if inputs.get("client_cert"):
        a.extend(["-E", str(inputs["client_cert"])])
    if inputs.get("proxy"):
        a.extend(["-p", str(inputs["proxy"])])
    if inputs.get("proxy_auth"):
        if not inputs.get("proxy"):
            notes.append("-P (proxy auth) only takes effect together with -p (Proxy) — set the Proxy field too.")
        a.extend(["-P", str(inputs["proxy_auth"])])
    delay_ms = inputs.get("delay_ms")
    if delay_ms not in (None, ""):
        a.extend(["-z", str(int(delay_ms))])
    no_recursion = _truthy(inputs.get("no_recursion"))
    interactive_recursion = _truthy(inputs.get("interactive_recursion"))
    if no_recursion and interactive_recursion:
        notes.append("-r (don't recurse) and -R (interactive recursion) are alternate recursion "
                     "modes — using both together is unusual, pick one.")
    if no_recursion:
        a.append("-r")
    if interactive_recursion:
        a.append("-R")
    if _truthy(inputs.get("silent")):
        a.append("-S")
    if _truthy(inputs.get("case_insensitive")):
        a.append("-i")
    if _truthy(inputs.get("show_location")):
        a.append("-l")
    ignore_code = inputs.get("ignore_code")
    if ignore_code not in (None, ""):
        a.extend(["-N", str(ignore_code)])
    if _truthy(inputs.get("tune_404")):
        a.append("-f")
    if _truthy(inputs.get("show_not_found")):
        a.append("-v")
    if _truthy(inputs.get("ignore_warnings")):
        a.append("-w")
    if _truthy(inputs.get("raw_path")):
        a.append("-b")
    if _truthy(inputs.get("no_trailing_slash")):
        a.append("-t")
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])

    return assemble("dirb", {
        Slot.TARGET_PIVOT: target,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes)
