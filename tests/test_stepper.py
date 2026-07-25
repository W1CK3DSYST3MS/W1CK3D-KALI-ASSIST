"""Adaptive stepper: Yes advances, No branches through alternatives, exhaustion -> Issue Log."""

import pytest

from wizard_core.models import Explanation, StepAlternative, StepSpec
from wizard_core.stepper import StepperSession, StepperState


def _step(step_id, alts=()):
    return StepSpec(
        step_id=step_id,
        title=f"Step {step_id}",
        explanation=Explanation(what="w", why="y", where="z"),
        try_this=f"do {step_id}",
        success_criteria="it worked",
        alternatives=list(alts),
    )


def test_all_yes_completes():
    s = StepperSession([_step("a"), _step("b")], flow_title="t")
    assert s.current().step_id == "a"
    assert s.answer_yes() is StepperState.IN_PROGRESS
    assert s.current().step_id == "b"
    assert s.answer_yes() is StepperState.COMPLETE
    assert s.is_done()


def test_no_walks_alternatives_then_yes_recovers():
    alts = [StepAlternative(cause="c1", fix="f1"), StepAlternative(cause="c2", fix="f2")]
    s = StepperSession([_step("a", alts), _step("b")], flow_title="t")
    assert s.answer_no() is StepperState.IN_PROGRESS
    v = s.current()
    assert v.on_alternative and v.alternative_index == 0 and v.fix == "f1"
    # second No -> next alternative
    s.answer_no()
    assert s.current().alternative_index == 1
    # now it works -> advance to b
    assert s.answer_yes() is StepperState.IN_PROGRESS
    assert s.current().step_id == "b"


def test_exhaustion_produces_issue_log():
    alts = [StepAlternative(cause="c1", fix="f1")]
    s = StepperSession([_step("a", alts)], flow_title="Networking",
                       context={"link_type": "wifi"})
    s.record_output("error: no carrier")
    s.answer_no()              # show alternative 0
    state = s.answer_no()      # no alternatives left -> exhausted
    assert state is StepperState.EXHAUSTED
    log = s.issue_log()
    assert log.flow_title == "Networking"
    assert log.context["link_type"] == "wifi"
    text = log.to_text()
    assert "Unresolved Issue Log" in text
    assert "Step a" in text


def test_cannot_answer_after_done():
    s = StepperSession([_step("a")])
    s.answer_yes()
    with pytest.raises(RuntimeError):
        s.answer_yes()


def test_review_completed_step_after_advancing():
    s = StepperSession([_step("a"), _step("b"), _step("c")], flow_title="t")
    s.answer_yes()  # passes a
    s.answer_yes()  # passes b, now on c
    assert s.completed_positions() == [0, 1]
    v = s.review_view(0)
    assert v.step_id == "a" and not v.on_alternative
    v = s.review_view(1)
    assert v.step_id == "b" and not v.on_alternative
    # review doesn't disturb the live session
    assert s.current().step_id == "c"


def test_review_reflects_alternative_shown_at_yes():
    alts = [StepAlternative(cause="c1", fix="f1"), StepAlternative(cause="c2", fix="f2")]
    s = StepperSession([_step("a", alts), _step("b")], flow_title="t")
    s.answer_no()   # alternative 0 shown
    s.answer_yes()  # passed while alternative 0 was on screen
    v = s.review_view(0)
    assert v.on_alternative and v.alternative_index == 0 and v.fix == "f1"


def test_review_view_rejects_uncompleted_position():
    s = StepperSession([_step("a"), _step("b")], flow_title="t")
    with pytest.raises(ValueError):
        s.review_view(1)  # not reached yet
    with pytest.raises(ValueError):
        s.review_view(0)  # reached but not yet answered


def test_flow_goal_survives_to_completion():
    # Regression: the completion screen used to show only a hardcoded generic
    # message with no way to point at a related flow (e.g. sherlock's
    # next_steps) -- flow_goal must still be readable once the session is
    # actually COMPLETE, not just while a step is still in progress.
    s = StepperSession([_step("a"), _step("b")], flow_title="t",
                        flow_goal="see the next_steps flow for what's next")
    s.answer_yes()
    s.answer_yes()
    assert s.is_done() and s.state is StepperState.COMPLETE
    assert s.flow_goal == "see the next_steps flow for what's next"
