"""mdbtools command builder — reads Microsoft Access (.mdb/.accdb) files.

mdbtools is a SUITE of small binaries (mdb-ver, mdb-tables, mdb-schema,
mdb-export, mdb-sql), not one program — the chosen ``action`` picks which
binary becomes PROGRAM. Positional shape differs per action: mdb-schema takes
the table as a -T flag, while mdb-export takes it as a second positional.
Generate-only.
"""

from __future__ import annotations

from typing import Mapping

from ..models import CommandPlan
from ..slots import Slot
from .common import assemble, register_builder

_BINARIES = {
    "ver": "mdb-ver",
    "tables": "mdb-tables",
    "schema": "mdb-schema",
    "export": "mdb-export",
    "sql": "mdb-sql",
}


def _truthy(v: object) -> bool:
    return bool(v) and str(v).lower() not in {"false", "0", "no", ""}


@register_builder("mdbtools")
def build_mdbtools(inputs: Mapping[str, object]) -> CommandPlan:
    notes: list[str] = []
    a: list[str] = []      # ACTION_OPTIONS (-S/-1/-T)
    pos: list[str] = []    # POSITIONAL_ARGS (file [table])

    action = str(inputs.get("action") or "tables")
    program = _BINARIES.get(action, "mdb-tables")

    file_ = inputs.get("file")
    if not file_:
        notes.append(f"No database file — {program} needs one.")

    table = inputs.get("table")

    if action == "tables":
        if _truthy(inputs.get("include_system")):
            a.append("-S")
        if _truthy(inputs.get("single_column")):
            a.append("-1")
        if file_:
            pos.append(str(file_))
    elif action == "schema":
        if table:
            a.extend(["-T", str(table)])
        if file_:
            pos.append(str(file_))
    elif action == "export":
        if file_:
            pos.append(str(file_))
        if table:
            pos.append(str(table))
        else:
            notes.append("No table name — mdb-export needs <file> <table>.")
    elif action == "sql":
        if inputs.get("sql_file"):
            a.extend(["-i", str(inputs["sql_file"])])
        else:
            notes.append(
                "No SQL file (-i) — without one, mdb-sql opens an interactive prompt "
                "(not usable from this generate-only app). Save your query to a .sql file first."
            )
        if inputs.get("sql_output"):
            a.extend(["-o", str(inputs["sql_output"])])
        if _truthy(inputs.get("no_header")):
            a.append("-H")
        if file_:
            pos.append(str(file_))
    else:  # ver
        if file_:
            pos.append(str(file_))

    return assemble(
        program,
        {
            Slot.ACTION_OPTIONS: a,
            Slot.POSITIONAL_ARGS: pos,
        },
        notes=notes,
    )
