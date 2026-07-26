"""responder command builder — LLMNR/NBT-NS/mDNS poisoner + rogue auth servers.

Poisons name resolution for the WHOLE network segment it's run on, not a single
target — there is no target host, only an interface. Generate-only.
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
      dhcp, dhcp_dns, dhcpv6, external_ip, external_ip6.
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

    if _truthy(inputs.get("basic")):
        a.append("-b")
    if _truthy(inputs.get("verbose")):
        a.append("-v")

    return assemble(
        "responder",
        {
            Slot.ENV_INTERFACE: env,
            Slot.ACTION_OPTIONS: a,
        },
        notes=notes,
        elevation="sudo",
    )
