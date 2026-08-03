"""responder command builder — LLMNR/NBT-NS/mDNS poisoner + rogue auth servers.

Poisons name resolution for the WHOLE network segment it's run on, not a single
target — there is no target host, only an interface. Generate-only.

2026-07-26: extended to cover Responder's FULL `-h` surface (previous pass
only covered the "major gaps" a first audit flagged, which itself wasn't
exhaustive). Adds the rest of the Poisoning Options group (--rdnss, --dnssl,
-t/--ttl, -N/--AnswerName), the rest of WPAD/Proxy Options (-u/--upstream-
proxy), the rest of Authentication Options (--lm, --disable-ess, -E), and the
rest of Output Options (-Q/--quiet). (-i/--ip under Platform Options is
explicitly documented as OSX-only and is skipped — this app targets Kali.)
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("responder")
def build_responder(inputs: Mapping[str, object]) -> CommandPlan:
    """Build a responder CommandPlan from validated inputs.

    Recognised keys (all optional except ``iface``):
      iface, analyze, verbose, basic, wpad, force_wpad_auth, proxy_auth,
      dhcp, dhcp_dns, dhcpv6, external_ip, external_ip6, rdnss, dnssl, ttl,
      answer_name, upstream_proxy, lm, disable_ess, error_code, quiet.
    """
    notes: list[str] = []
    env: list[str] = []    # ENV_INTERFACE (-I)
    a: list[str] = []      # ACTION_OPTIONS

    iface = inputs.get("iface")
    if iface:
        env.extend(["-I", str(iface)])
    else:
        notes.append("No -I — Responder requires an interface; pick one with `ip a`.")

    if _truthy(inputs.get("analyze")):
        a.append("-A")

    external_ip = inputs.get("external_ip")
    if external_ip:
        a.extend(["-e", str(external_ip)])
    external_ip6 = inputs.get("external_ip6")
    if external_ip6:
        a.extend(["-6", str(external_ip6)])

    # Rest of the "Poisoning Options" group (Responder -h): IPv6 Router
    # Advertisement poisoning, plus TTL/answer-name detail flags.
    rdnss = _truthy(inputs.get("rdnss"))
    if rdnss:
        a.append("--rdnss")
    dnssl = inputs.get("dnssl")
    if dnssl:
        a.extend(["--dnssl", str(dnssl)])
    if rdnss or dnssl:
        notes.append(
            "Router Advertisement poisoning (--rdnss/--dnssl) broadcasts on the WHOLE IPv6 "
            "segment, exactly like DHCPv6 poisoning — a client that accepts it can have its "
            "IPv6 DNS server or search suffix silently changed for every host listening, not "
            "just one target."
        )
    ttl = inputs.get("ttl")
    if ttl:
        a.extend(["-t", str(ttl)])
    answer_name = inputs.get("answer_name")
    if answer_name:
        a.extend(["-N", str(answer_name)])

    # DHCP/DHCPv6 poisoning — competes with the segment's REAL DHCP server for new
    # lease requests. Unlike LLMNR/NBT-NS (which only answers already-failed lookups),
    # a client that accepts a poisoned lease can lose real network/DNS connectivity
    # entirely, not just have credentials captured. Flag this every time it's used.
    dhcp = _truthy(inputs.get("dhcp"))
    dhcp_dns = _truthy(inputs.get("dhcp_dns"))
    dhcpv6 = _truthy(inputs.get("dhcpv6"))
    if dhcp:
        a.append("-d")
    if dhcp_dns:
        a.append("-D")
    if dhcpv6:
        a.append("--dhcpv6")
    if dhcp or dhcp_dns or dhcpv6:
        notes.append(
            "DHCP/DHCPv6 poisoning answers lease requests for the WHOLE segment, competing "
            "with the real DHCP server — a client that accepts the poisoned lease can lose "
            "normal network/DNS connectivity, not just have credentials captured. This is "
            "disruptive to shared infrastructure, not just eavesdropping — advanced/high-risk "
            "even by Responder's already-high bar."
        )

    wpad = _truthy(inputs.get("wpad"))
    if wpad:
        a.append("-w")
    if _truthy(inputs.get("force_wpad_auth")):
        a.append("-F")
    if _truthy(inputs.get("proxy_auth")):
        if wpad:
            raise ValueError(
                "-P (--ProxyAuth) can't be combined with -w (--wpad) — Responder's rogue WPAD "
                "proxy and its rogue proxy-auth capture are mutually exclusive. Turn off "
                "'Start rogue WPAD proxy' to use Proxy auth capture."
            )
        a.append("-P")
        notes.append(
            "-P (rogue proxy auth capture) is Responder's own highlighted standout feature — it "
            "forces NTLM/Basic proxy authentication from ANY client that tries to use a proxy on "
            "this segment, capturing credentials even from apps that never send an LLMNR/NBT-NS "
            "lookup at all."
        )

    # Rest of "WPAD / Proxy Options": relay the rogue proxy's traffic onward.
    upstream_proxy = inputs.get("upstream_proxy")
    if upstream_proxy:
        a.extend(["-u", str(upstream_proxy)])
        if not wpad:
            notes.append(
                "-u (upstream proxy) only has an effect when -w (Start rogue WPAD proxy) is "
                "also on — it forwards traffic THROUGH the rogue proxy, it does nothing alone."
            )

    if _truthy(inputs.get("basic")):
        a.append("-b")

    # Rest of "Authentication Options": force weaker/legacy credential formats.
    if _truthy(inputs.get("lm")):
        a.append("--lm")
        notes.append(
            "--lm forces a downgrade to the LM hash format — much weaker/faster to crack than "
            "NTLM, but only legacy Windows XP/2003-era clients still support it; modern Windows "
            "simply won't respond with an LM hash even if asked."
        )
    if _truthy(inputs.get("disable_ess")):
        a.append("--disable-ess")
        notes.append(
            "--disable-ess strips Extended Session Security, downgrading captures to the older, "
            "weaker NTLMv1 format (hashcat -m 5500, not NTLMv2's -m 5600) — much faster to crack "
            "than NTLMv2, but a detectable protocol downgrade."
        )
    if _truthy(inputs.get("error_code")):
        a.append("-E")
        notes.append(
            "-E returns STATUS_LOGON_FAILURE instead of silently accepting the authentication — "
            "this can prompt some clients (notably WebDAV/WebClient) to retry with credentials "
            "Responder wouldn't otherwise see, at the cost of telling every client its auth failed."
        )

    # Rest of "Output Options".
    quiet = _truthy(inputs.get("quiet"))
    if quiet:
        a.append("-Q")
    verbose = _truthy(inputs.get("verbose"))
    if verbose:
        a.append("-v")
    if quiet and verbose:
        notes.append(
            "-Q (quiet) and -v (verbose) pull in opposite directions — pick one; Responder will "
            "run with both present, but the output-detail intent is unclear."
        )

    return assemble(
        "responder",
        {
            Slot.ENV_INTERFACE: env,
            Slot.ACTION_OPTIONS: a,
        },
        notes=notes,
        elevation="sudo",
    )
