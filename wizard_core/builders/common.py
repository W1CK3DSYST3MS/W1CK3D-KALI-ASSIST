"""Shared builder machinery: shell escaping, fixed-order slot assembly, registry.

Structured assembly (not string concatenation) guarantees correct slot order and
safe quoting. Since nothing is ever executed, the array form is illustrative —
but we still quote correctly so the copyable bash preview is always valid.
"""

from __future__ import annotations

import shlex
from typing import Callable, Mapping, Protocol

from ..models import CommandPlan
from ..slots import SLOT_ORDER, Slot


def shell_escape(token: str) -> str:
    """POSIX-safe quoting for the copyable bash preview string.

    ``shlex.quote`` leaves already-safe tokens untouched and single-quotes the
    rest, which is exactly what we want for a human-readable, copy-paste preview.
    """
    return shlex.quote(token)


def assemble(program: str, slot_values: Mapping[Slot, list[str]],
             notes: list[str] | None = None,
             elevation: str | None = None,
             subcommand: list[str] | None = None) -> CommandPlan:
    """Assemble slot tokens into a :class:`CommandPlan` in the fixed slot order.

    ``program`` is forced into the PROGRAM slot. ``elevation`` (e.g. ``"sudo"``)
    is rendered ahead of the program when a flow needs privileges. ``subcommand``
    (e.g. gobuster's ``dir`` mode) is rendered immediately after the program and
    before any flags — both kept separate from the slots so PROGRAM stays the
    tool name. Empty slots are skipped. The same ordering drives both the array
    form and the bash preview string.
    """
    values: dict[Slot, list[str]] = {}
    # PROGRAM is always slot 1 and always the program name (+ optional subcommand).
    values[Slot.PROGRAM] = [program] + list(subcommand or [])
    for slot in SLOT_ORDER:
        if slot is Slot.PROGRAM:
            continue
        tokens = [t for t in slot_values.get(slot, []) if t != "" and t is not None]
        if tokens:
            values[slot] = tokens

    array_form: list[str] = []
    skeleton_parts: list[str] = []
    if elevation:
        array_form.append(elevation)
        skeleton_parts.append(elevation)
    for slot in SLOT_ORDER:
        if slot not in values:
            continue
        array_form.extend(values[slot])
        if slot is Slot.PROGRAM:
            skeleton_parts.append(" ".join(values[slot]))
        else:
            skeleton_parts.append("{%s}" % slot.label.lower().replace(" / ", "/").replace(" ", "_"))

    bash_preview = " ".join(shell_escape(t) for t in array_form)

    return CommandPlan(
        program=program,
        slot_values=values,
        array_form=array_form,
        bash_preview_string=bash_preview,
        skeleton=" ".join(skeleton_parts),
        notes=notes or [],
    )


class CommandBuilder(Protocol):
    """A builder: ``build(validated_inputs) -> CommandPlan``."""

    def __call__(self, inputs: Mapping[str, object]) -> CommandPlan: ...


_REGISTRY: dict[str, CommandBuilder] = {}


def register_builder(builder_id: str) -> Callable[[CommandBuilder], CommandBuilder]:
    """Decorator: register a builder under ``builder_id``."""

    def _wrap(fn: CommandBuilder) -> CommandBuilder:
        if builder_id in _REGISTRY:
            raise ValueError(f"Builder id already registered: {builder_id!r}")
        _REGISTRY[builder_id] = fn
        return fn

    return _wrap


def get_builder(builder_id: str) -> CommandBuilder:
    """Look up a registered builder. Fails loudly if a flow references an unknown id."""
    try:
        return _REGISTRY[builder_id]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise KeyError(
            f"No command builder registered for {builder_id!r}. Known: {known}"
        ) from exc


def registered_builders() -> list[str]:
    return sorted(_REGISTRY)
