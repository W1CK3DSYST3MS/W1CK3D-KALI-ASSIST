"""rfcat command builder — sub-GHz RF transceiver research tool (e.g. YARD Stick One).

Opens an interactive Python REPL to receive/transmit sub-GHz RF. Generate-only.
Transmitting is heavily regulated — the module carries an authorization gate.

-s/--specan is a second, distinct standalone CLI mode (unlike -r, it never drops
into a Python shell) that opens a graphical spectrum-analyzer window straight
from the command line — see rfcat's own argparse setup and rflib's
RfCat.specan()/​_doSpecAn(): -f is the CENTER frequency in Hz, -c is the
per-channel spacing in Hz, -n is how many channels to sweep either side of
that center. rfcat's own CLI checks -s before -r, so if both are given specan
wins and -r is silently ignored — we surface that as a note instead of hiding it.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("rfcat")
def build_rfcat(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []

    specan = _truthy(inputs.get("specan"))
    if specan:
        a.append("-s")
        if inputs.get("centfreq") not in (None, ""):
            a.extend(["-f", str(inputs["centfreq"])])
        if inputs.get("chan_spacing") not in (None, ""):
            a.extend(["-c", str(inputs["chan_spacing"])])
        if inputs.get("spec_channels") not in (None, ""):
            a.extend(["-n", str(int(inputs["spec_channels"]))])
        if _truthy(inputs.get("interactive")):
            notes.append(
                "Both -s (spectrum analyzer) and -r (research shell) were given — "
                "rfcat checks -s first, so it opens the spectrum analyzer and -r is ignored."
            )
        notes.append("-s opens a graphical window (needs a display/X session, not just a terminal).")
    # -r launches the interactive research shell (the usual entry point).
    elif inputs.get("interactive") is None or _truthy(inputs.get("interactive")):
        a.append("-r")

    if inputs.get("index") not in (None, ""):
        a.extend(["-i", str(int(inputs["index"]))])
    return assemble("rfcat", {Slot.ACTION_OPTIONS: a}, notes=notes)
