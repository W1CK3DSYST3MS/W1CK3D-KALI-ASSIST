"""Command builders.

A builder turns validated user inputs into a :class:`CommandPlan` by placing
tokens into the 8 slots; the common assembler then renders the fixed-order
bash preview + array form. Builders live in-core (this is a closed build that
ships its own builders) and self-register by id via :func:`register_builder`,
so a flow references one by ``command_builder_id`` — no code is loaded from data.
"""

from .common import (
    CommandBuilder,
    assemble,
    get_builder,
    register_builder,
    shell_escape,
)

# Import builder modules for their registration side effects.
from . import nmap_builder  # noqa: F401  (registers "nmap")

__all__ = [
    "CommandBuilder",
    "assemble",
    "get_builder",
    "register_builder",
    "shell_escape",
]
