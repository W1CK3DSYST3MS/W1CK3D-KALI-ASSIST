"""photon command builder — fast web crawler for OSINT.

Crawls a site collecting URLs, emails, keys, and files. Generate-only.
URL via -u; depth -l, threads -t, delay -d, output dir -o, --wayback for
archived URLs, --keys for secret/API-key detection, --dns for subdomain
enumeration during the crawl, --clone to mirror the site locally, and
-e/--export to also write a csv/json summary.

2026-07-26: extended to cover photon's FULL `--help` surface (previous pass
only covered the "major gaps" a first audit flagged, which itself wasn't
exhaustive). Adds: -c/--cookie, -r/--regex, -v/--verbose, -s/--seeds,
--user-agent, --exclude, --timeout, --headers, --only-urls, --stdout.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_EXPORT_FORMATS = {"csv", "json"}

# Valid dataset names for --stdout, taken directly from photon's own `datasets`
# dict (photon.py) — 'subdomains' only exists in that dict when --dns is set.
_STDOUT_DATASETS = {
    "files", "intel", "robots", "custom", "failed", "internal", "scripts",
    "external", "fuzzable", "endpoints", "keys", "subdomains",
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("photon")
def build_photon(inputs: Mapping[str, object]) -> CommandPlan:
    """Build a photon CommandPlan from validated inputs.

    Recognised keys (all optional except ``url``):
      url, depth, threads, delay, wayback, keys, dns, clone, export, output,
      cookie, regex, verbose, seeds, user_agent, exclude, timeout, headers,
      only_urls, stdout.
    """
    notes: list[str] = []
    env: list[str] = []    # ENV_INTERFACE (-u url)
    a: list[str] = []      # ACTION_OPTIONS (depth/threads/delay/wayback/keys/dns/clone/...)
    o: list[str] = []      # OUTPUT_OPTIONS (-o, -e, --stdout)

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

    # Request customization — cookie/headers/user-agent/timeout/verbose.
    cookie = inputs.get("cookie")
    if cookie:
        a.extend(["-c", str(cookie)])
    user_agent = inputs.get("user_agent")
    if user_agent:
        a.extend(["--user-agent", str(user_agent)])
    if _truthy(inputs.get("headers")):
        a.append("--headers")
        notes.append(
            "--headers opens an interactive editor (nano) when you actually RUN this command, "
            "to type custom 'Header: value' lines before the crawl starts — there's nothing to "
            "fill in here, since this app only builds and displays the command."
        )
    timeout = inputs.get("timeout")
    if timeout not in (None, ""):
        a.extend(["--timeout", str(timeout)])
    if _truthy(inputs.get("verbose")):
        a.append("-v")

    # Precision crawling & piping — custom regex, seeds, exclude, only-urls.
    regex = inputs.get("regex")
    if regex:
        a.extend(["-r", str(regex)])
    seeds = inputs.get("seeds")
    if seeds:
        # photon's -s/--seeds takes multiple URLs (nargs="+"); accept a
        # space-separated string from the quick_build field.
        a.append("-s")
        a.extend(str(seeds).split())
    exclude = inputs.get("exclude")
    if exclude:
        a.extend(["--exclude", str(exclude)])
    if _truthy(inputs.get("only_urls")):
        a.append("--only-urls")
        notes.append(
            "--only-urls skips key/email/file/DNS analysis and just extracts URLs — pair it "
            "with --stdout to pipe results straight into another tool."
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
    stdout = inputs.get("stdout")
    if stdout:
        if str(stdout) not in _STDOUT_DATASETS:
            raise ValueError(
                f"Unknown --stdout dataset {stdout!r}. Valid: {', '.join(sorted(_STDOUT_DATASETS))}"
            )
        o.extend(["--stdout", str(stdout)])
        notes.append(
            "--stdout prints ONLY that dataset, one item per line, to standard output — ideal "
            "for piping into another tool (e.g. `| sort -u` or `| httpx`)."
        )
        if str(stdout) == "subdomains" and not _truthy(inputs.get("dns")):
            notes.append(
                "--stdout subdomains needs --dns (Enumerate subdomains) also enabled — "
                "otherwise that dataset doesn't exist and photon will error."
            )

    return assemble("photon", {
        Slot.ENV_INTERFACE: env,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
    }, notes=notes)
