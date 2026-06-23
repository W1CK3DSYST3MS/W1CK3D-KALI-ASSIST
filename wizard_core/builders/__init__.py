"""Command builders.

A builder turns validated user inputs into a :class:`CommandPlan` by placing
tokens into the 8 slots; the common assembler then renders the fixed-order
bash preview + array form. Builders live in-core (this is a closed build that
ships its own builders) and self-register by id via :func:`register_builder`,
so a flow references one by ``command_builder_id`` — no code is loaded from data.
"""

import importlib
import pkgutil

from .common import (
    CommandBuilder,
    assemble,
    get_builder,
    register_builder,
    registered_builders,
    shell_escape,
)

# Auto-import every *_builder.py module for its registration side effects, so a
# new tool builder is picked up just by adding the file (no edit here needed).
for _mod in pkgutil.iter_modules(__path__):
    if _mod.name.endswith("_builder"):
        importlib.import_module(f"{__name__}.{_mod.name}")

__all__ = [
    "CommandBuilder",
    "assemble",
    "get_builder",
    "register_builder",
    "registered_builders",
    "shell_escape",
]
