"""The universal CLI slot model (Blueprint §3).

Every command this app teaches is built from the same eight ordered *slots*.
The builder always assembles them in this fixed order, so the learner never has
to reorder anything. Not every flow uses every slot.
"""

from __future__ import annotations

from enum import IntEnum


class Slot(IntEnum):
    """The 8 ordered command slots. The integer value IS the assembly order."""

    PROGRAM = 1          # the executable name, e.g. ``nmap``
    GLOBAL_OPTIONS = 2   # run-wide behaviour: timing, DNS, verbosity (-n -Pn -T4)
    TARGET_PIVOT = 3     # the scope: hosts / CIDR / domains / URLs / files
    ACTION_OPTIONS = 4   # what the tool does to the targets (-sV -p 22,80)
    OUTPUT_OPTIONS = 5   # output formats + destinations (-oX ./out/scan.xml)
    POSITIONAL_ARGS = 6  # required positional values (tool-defined, if any)
    ENV_INTERFACE = 7    # interface / capture / proxy / host-binding (-e wlan0)
    EXTRA_FILES = 8      # wordlists, certs, script files (-iL targets.txt)

    @property
    def label(self) -> str:
        """Human-facing slot name used in the skeleton/why views."""
        return _SLOT_LABELS[self]

    @property
    def plain_why(self) -> str:
        """One short, true sentence: why a value goes in this slot."""
        return _SLOT_WHY[self]

    @classmethod
    def from_name(cls, name: str) -> "Slot":
        """Parse a slot from its enum name (case-insensitive). Fails loudly."""
        try:
            return cls[name.strip().upper()]
        except KeyError as exc:  # pragma: no cover - defensive
            valid = ", ".join(s.name for s in cls)
            raise ValueError(f"Unknown slot {name!r}. Valid slots: {valid}") from exc


# Ordered tuple, handy for iteration in assembly + UI rendering.
SLOT_ORDER: tuple[Slot, ...] = tuple(sorted(Slot, key=int))

_SLOT_LABELS: dict[Slot, str] = {
    Slot.PROGRAM: "Program",
    Slot.GLOBAL_OPTIONS: "Global options",
    Slot.TARGET_PIVOT: "Target / pivot",
    Slot.ACTION_OPTIONS: "Action options",
    Slot.OUTPUT_OPTIONS: "Output options",
    Slot.POSITIONAL_ARGS: "Positional args",
    Slot.ENV_INTERFACE: "Env / interface",
    Slot.EXTRA_FILES: "Extra files",
}

_SLOT_WHY: dict[Slot, str] = {
    Slot.PROGRAM: "the executable you run; it decides how the rest of the line is read.",
    Slot.GLOBAL_OPTIONS: "behaviour for the whole run (timing, DNS, verbosity).",
    Slot.TARGET_PIVOT: "the scope the tool operates on.",
    Slot.ACTION_OPTIONS: "what the tool does to the targets.",
    Slot.OUTPUT_OPTIONS: "where and how results are written.",
    Slot.POSITIONAL_ARGS: "required positional values the tool defines.",
    Slot.ENV_INTERFACE: "interface / capture / proxy / host-binding for the run.",
    Slot.EXTRA_FILES: "auxiliary input files (wordlists, certs, scripts).",
}
