"""Every tool exposes a quick_build form whose fields drive its registered builder."""

from pathlib import Path

import pytest

from wizard_core.builders import get_builder
from wizard_core.loader import load_modules

MODULES = Path(__file__).resolve().parents[1] / "modules"

_SAMPLE = {
    "string": "sample",
    "path": "sample.txt",
    "int": "1",
    "range": "1",
    "list": "a,b",
}


def _tools():
    return load_modules(MODULES).tools


def test_every_tool_has_a_quick_build():
    for tid, tool in _tools().items():
        assert tool.quick_build, f"{tid} is missing a quick_build form"
        assert tool.quick_build.fields, f"{tid} quick_build has no fields"


def test_quick_build_builders_are_registered():
    for tid, tool in _tools().items():
        # get_builder raises KeyError for an unknown id — that's the assertion.
        get_builder(tool.quick_build.builder)


def test_quick_build_field_ids_are_unique():
    for tid, tool in _tools().items():
        ids = [f.field_id for f in tool.quick_build.fields]
        assert len(ids) == len(set(ids)), f"{tid} has duplicate field ids: {ids}"


def _fill(field):
    """Mimic the ToolPage collector for a single field with a valid value."""
    if field.type == "bool":
        return True
    if field.type == "choice":
        return field.default if field.default is not None else field.choices[0]
    return field.default if field.default not in (None, "") else _SAMPLE[field.type]


@pytest.mark.parametrize("tid", sorted(_tools()))
def test_quick_build_produces_a_plan_when_required_fields_are_filled(tid):
    tool = _tools()[tid]
    build = get_builder(tool.quick_build.builder)
    inputs = {f.field_id: _fill(f) for f in tool.quick_build.fields if f.required}
    plan = build(inputs)  # must not raise with all required fields present
    assert plan.array_form, f"{tid} produced an empty command"
    assert plan.bash_preview_string.strip()
