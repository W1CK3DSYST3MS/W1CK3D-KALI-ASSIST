"""Every tool leads with a beginner walk-through: a 'guided' flow whose steps
teach inputs (find_it) and syntax (command_anatomy) with an expected sample."""

from pathlib import Path

import pytest

from wizard_core.loader import load_modules

MODULES = Path(__file__).resolve().parents[1] / "modules"


def _tools():
    return load_modules(MODULES).tools


def test_every_tool_has_a_guided_flow():
    for tid, tool in _tools().items():
        ids = [f.flow_id for f in tool.flows]
        assert "guided" in ids, f"{tid} has no 'guided' walk-through flow ({ids})"


@pytest.mark.parametrize("tid", sorted(_tools()))
def test_guided_steps_teach_inputs_and_syntax(tid):
    tool = _tools()[tid]
    guided = next(f for f in tool.flows if f.flow_id == "guided")
    assert len(guided.steps) >= 4, f"{tid} guided flow is too short"
    for step in guided.steps:
        assert step.try_this.strip(), f"{tid}:{step.step_id} missing try_this"
        assert step.expected_output.strip(), f"{tid}:{step.step_id} missing expected_output"
        assert step.command_anatomy, f"{tid}:{step.step_id} missing command_anatomy"
        assert step.alternatives, f"{tid}:{step.step_id} missing alternatives"
