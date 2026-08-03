"""gobuster command builder (Module 10 spec).

gobuster's first argument is a MODE (dir/dns/vhost/fuzz/tftp/s3/gcs) — a subcommand
that must come right after the program. The mode decides the target flag: -u for
dir/vhost/fuzz, --domain for dns, -s for tftp, none for s3/gcs. Generate-only.

2026-07-26: extended to cover gobuster's FULL `--help` surface for every mode
(previous pass only covered the "major gaps" a first audit flagged — see
docs/DEPTH-AUDIT.md). Verified against the installed `gobuster --help` /
`gobuster <mode> --help` (v3.8.2), which also surfaced two real bugs in the
prior version of this builder, both fixed here:
  - dns mode's target flag is `--domain` (there is no `-d` alias — `-d` is
    `--delay` in this gobuster version). Previously this builder emitted
    `-d <domain>`, which does NOT set the target domain on current gobuster.
  - dns mode's `--resolver` flag has no short form; previously this builder
    emitted `-r <resolver>` which isn't a valid dns-mode flag at all (in
    dir/vhost/fuzz mode `-r` means `--follow-redirect`).
`-i`/`--show-ips` (dns mode) has been removed entirely — it no longer exists
in gobuster 3.8.2's dns mode --help output, so it's dropped rather than kept
as a dead flag.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_MODES = {"dir", "dns", "vhost", "fuzz", "tftp", "s3", "gcs"}
# Modes that support HTTP Basic Auth (-U/-P) — bucket/tftp modes don't speak HTTP auth.
_BASIC_AUTH_MODES = {"dir", "vhost", "fuzz"}
# Modes with no target flag at all — bucket names come purely from the wordlist.
_NO_TARGET_MODES = {"s3", "gcs"}
# Modes that make real HTTP(S) requests — these share the client/TLS/proxy flag set.
_HTTP_MODES = {"dir", "vhost", "fuzz", "s3", "gcs"}
# Modes that are full HTTP-verb-aware request modes (method, headers, cookies, auth).
_HTTP_REQUEST_MODES = {"dir", "vhost", "fuzz"}
# Profiles map to (mode, global tokens, action tokens).
_PROFILES: dict[str, dict[str, object]] = {
    "quick_dir": {"mode": "dir", "global": ["-t", "40"], "action": []},
    "dir_files": {"mode": "dir", "global": ["-t", "40"], "action": ["-x", "php,html,txt,bak"]},
    "subdomains": {"mode": "dns", "global": ["-t", "40"], "action": []},
    "vhosts": {"mode": "vhost", "global": [], "action": ["--append-domain"]},
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("gobuster")
def build_gobuster(inputs: Mapping[str, object]) -> CommandPlan:
    g: list[str] = []
    a: list[str] = []
    o: list[str] = []
    env: list[str] = []
    extra: list[str] = []
    notes: list[str] = []

    mode = inputs.get("mode")
    profile = inputs.get("profile")
    if profile:
        preset = _PROFILES.get(str(profile))
        if preset is None:
            raise ValueError(f"Unknown gobuster profile {profile!r}. Valid: {', '.join(_PROFILES)}")
        mode = mode or preset["mode"]
        g.extend(list(preset["global"]))
        a.extend(list(preset["action"]))
        notes.append(f"Profile '{profile}' set mode '{mode}' and pre-filled options.")
    mode = str(mode or "dir")
    if mode not in _MODES:
        raise ValueError(f"Unknown gobuster mode {mode!r}. Valid: {', '.join(sorted(_MODES))}")

    # GLOBAL — flags shared by every mode's own --help listing.
    if inputs.get("threads"):
        g.extend(["-t", str(int(inputs["threads"]))])
    if _truthy(inputs.get("skip_tls")):
        g.append("-k")
    if _truthy(inputs.get("quiet")):
        g.append("-q")
    if inputs.get("delay"):
        g.extend(["-d", str(inputs["delay"])])
    if inputs.get("wordlist_offset") not in (None, ""):
        g.extend(["--wordlist-offset", str(int(inputs["wordlist_offset"]))])
    if inputs.get("timeout"):
        g.extend(["--timeout", str(inputs["timeout"])])
    if _truthy(inputs.get("retry")):
        g.append("--retry")
    if inputs.get("retry_attempts") not in (None, ""):
        g.extend(["--retry-attempts", str(int(inputs["retry_attempts"]))])
    if _truthy(inputs.get("no_progress")):
        g.append("--no-progress")
    if _truthy(inputs.get("no_error")):
        g.append("--no-error")
    if _truthy(inputs.get("no_color")):
        g.append("--no-color")
    if _truthy(inputs.get("debug")):
        g.append("--debug")
    if _truthy(inputs.get("random_agent")):
        g.append("--random-agent")

    # TARGET — correct flag per mode. s3/gcs have none at all (bucket names come
    # purely from the wordlist); tftp uses -s (server), dns uses --domain,
    # everything else (dir/vhost/fuzz) uses -u.
    target: list[str] = []
    tgt = inputs.get("target")
    if mode in _NO_TARGET_MODES:
        if tgt:
            notes.append(f"'{mode}' mode has no target flag — bucket names come from the "
                         "wordlist alone. The Target field is ignored for this mode.")
    elif tgt:
        flag = {"dns": "--domain", "tftp": "-s"}.get(mode, "-u")
        target = [flag, str(tgt)]
    else:
        notes.append("No target — supply a URL (dir/vhost/fuzz), domain (dns), or TFTP server (tftp).")

    # ACTION
    if inputs.get("wordlist"):
        extra.extend(["-w", str(inputs["wordlist"])])
    else:
        notes.append("No wordlist (-w) — gobuster needs one to run.")
    if mode == "dir" and inputs.get("extensions"):
        a.extend(["-x", str(inputs["extensions"])])
    if mode == "dir" and inputs.get("extensions_file"):
        a.extend(["-X", str(inputs["extensions_file"])])
    # status filters: blacklist (-b) OR whitelist (-s), never both. In fuzz mode
    # -b is spelled --exclude-statuscodes and there is no whitelist counterpart.
    if inputs.get("status_blacklist") and inputs.get("status_whitelist"):
        raise ValueError("Set EITHER status_blacklist (-b) OR status_whitelist (-s), not both.")
    if inputs.get("status_blacklist"):
        a.extend(["-b", str(inputs["status_blacklist"])])
    if mode != "fuzz" and inputs.get("status_whitelist"):
        a.extend(["-s", str(inputs["status_whitelist"])])
    elif mode == "fuzz" and inputs.get("status_whitelist"):
        notes.append("fuzz mode has no status whitelist (-s) — only --exclude-statuscodes (-b). "
                      "The status_whitelist value was ignored.")
    if inputs.get("exclude_length"):
        a.extend(["--exclude-length", str(inputs["exclude_length"])])
    if mode != "dns" and _truthy(inputs.get("follow_redirects")):
        a.append("-r")  # in dns mode there is no -r at all (see dns_check_cname/-c below)
    if mode == "vhost" and _truthy(inputs.get("append_domain")) and "--append-domain" not in a:
        a.append("--append-domain")
    if mode in _HTTP_REQUEST_MODES and inputs.get("cookie"):
        a.extend(["-c", str(inputs["cookie"])])
    if mode in _HTTP_MODES and inputs.get("header"):
        a.extend(["-H", str(inputs["header"])])
    if mode in _HTTP_MODES and inputs.get("user_agent"):
        a.extend(["-a", str(inputs["user_agent"])])
    if mode in _HTTP_REQUEST_MODES and inputs.get("method"):
        a.extend(["-m", str(inputs["method"])])
    if mode in _HTTP_REQUEST_MODES and _truthy(inputs.get("no_canonicalize_headers")):
        a.append("--no-canonicalize-headers")
    if mode == "fuzz" and inputs.get("fuzz_body"):
        a.extend(["-B", str(inputs["fuzz_body"])])

    # TLS client certificates + renegotiation (dir/vhost/fuzz/s3/gcs — every
    # mode that makes real HTTP(S) requests).
    if mode in _HTTP_MODES and inputs.get("client_cert_pem"):
        a.extend(["--client-cert-pem", str(inputs["client_cert_pem"])])
    if mode in _HTTP_MODES and inputs.get("client_cert_pem_key"):
        a.extend(["--client-cert-pem-key", str(inputs["client_cert_pem_key"])])
    if mode in _HTTP_MODES and inputs.get("client_cert_p12"):
        a.extend(["--client-cert-p12", str(inputs["client_cert_p12"])])
    if mode in _HTTP_MODES and inputs.get("client_cert_p12_password"):
        a.extend(["--client-cert-p12-password", str(inputs["client_cert_p12_password"])])
    if mode in _HTTP_MODES and _truthy(inputs.get("tls_renegotiation")):
        a.append("--tls-renegotiation")

    # Replacement-pattern files (shared by every mode).
    if inputs.get("pattern"):
        extra.extend(["-p", str(inputs["pattern"])])
    if inputs.get("discover_pattern"):
        extra.extend(["--discover-pattern", str(inputs["discover_pattern"])])

    # dir-mode-only output shaping.
    if mode == "dir" and _truthy(inputs.get("expanded")):
        a.append("-e")
    if mode == "dir" and _truthy(inputs.get("no_status")):
        a.append("-n")
    if mode == "dir" and _truthy(inputs.get("hide_length")):
        a.append("--hide-length")
    if mode == "dir" and _truthy(inputs.get("add_slash")):
        a.append("-f")
    if mode == "dir" and _truthy(inputs.get("discover_backup")):
        a.append("--discover-backup")
    if mode in {"dir", "vhost"} and _truthy(inputs.get("force")):
        a.append("--force")

    # dns-mode-only flags.
    if mode == "dns" and _truthy(inputs.get("check_cname")):
        a.append("-c")
    if mode == "dns" and _truthy(inputs.get("dns_wildcard")):
        a.append("--wildcard")
    if mode == "dns" and _truthy(inputs.get("dns_no_fqdn")):
        a.append("--no-fqdn")
    if mode == "dns" and inputs.get("dns_protocol"):
        a.extend(["--protocol", str(inputs["dns_protocol"])])
    if mode == "dns" and inputs.get("resolver"):
        a.extend(["--resolver", str(inputs["resolver"])])

    # vhost-mode-only flags.
    if mode == "vhost" and inputs.get("vhost_domain"):
        a.extend(["--domain", str(inputs["vhost_domain"])])
    if mode == "vhost" and inputs.get("vhost_exclude_status"):
        a.extend(["--exclude-status", str(inputs["vhost_exclude_status"])])
    if mode == "vhost" and _truthy(inputs.get("vhost_exclude_hostname_length")):
        a.append("--exclude-hostname-length")

    # s3/gcs-mode-only flags.
    if mode in {"s3", "gcs"} and inputs.get("s3_max_files") not in (None, ""):
        a.extend(["-m", str(int(inputs["s3_max_files"]))])

    if mode in _BASIC_AUTH_MODES and inputs.get("username"):
        a.extend(["-U", str(inputs["username"])])
    if mode in _BASIC_AUTH_MODES and inputs.get("password"):
        a.extend(["-P", str(inputs["password"])])
    if mode not in _BASIC_AUTH_MODES and (inputs.get("username") or inputs.get("password")):
        notes.append(f"Basic Auth (-U/-P) isn't available in '{mode}' mode — only dir/vhost/fuzz support it.")

    # OUTPUT
    if inputs.get("output"):
        o.extend(["-o", str(inputs["output"])])

    # ENV / proxy / network presentation.
    if inputs.get("proxy"):
        env.extend(["--proxy", str(inputs["proxy"])])
    if mode in _HTTP_MODES and inputs.get("interface"):
        env.extend(["--interface", str(inputs["interface"])])
    if mode in _HTTP_MODES and inputs.get("local_ip"):
        if inputs.get("interface"):
            notes.append("--interface and --local-ip can't be used together — only --interface was applied.")
        else:
            env.extend(["--local-ip", str(inputs["local_ip"])])

    slot_values = {
        Slot.GLOBAL_OPTIONS: g,
        Slot.TARGET_PIVOT: target,
        Slot.ACTION_OPTIONS: a,
        Slot.OUTPUT_OPTIONS: o,
        Slot.ENV_INTERFACE: env,
        Slot.EXTRA_FILES: extra,
    }
    return assemble("gobuster", slot_values, notes=notes, subcommand=[mode])
