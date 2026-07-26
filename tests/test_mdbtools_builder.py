"""mdbtools builder: per-action binary dispatch, including mdb-sql."""

from wizard_core.builders import get_builder
from wizard_core.slots import Slot

build = get_builder("mdbtools")


def test_sql_action_picks_mdb_sql_binary():
    plan = build({"action": "sql", "file": "database.mdb", "sql_file": "query.sql"})
    assert plan.program == "mdb-sql"
    assert plan.slot_values[Slot.ACTION_OPTIONS] == ["-i", "query.sql"]
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["database.mdb"]


def test_sql_without_sql_file_notes_interactive_limitation():
    plan = build({"action": "sql", "file": "database.mdb"})
    assert any("interactive prompt" in n for n in plan.notes)


def test_sql_output_and_no_header():
    plan = build({
        "action": "sql", "file": "database.mdb", "sql_file": "q.sql",
        "sql_output": "out.csv", "no_header": True,
    })
    assert "-o" in plan.array_form and "out.csv" in plan.array_form
    assert "-H" in plan.array_form


def test_export_action_unaffected():
    plan = build({"action": "export", "file": "database.mdb", "table": "Employees"})
    assert plan.program == "mdb-export"
    assert plan.slot_values[Slot.POSITIONAL_ARGS] == ["database.mdb", "Employees"]
