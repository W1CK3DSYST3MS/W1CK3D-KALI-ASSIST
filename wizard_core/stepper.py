"""The adaptive verify-and-branch stepper (Blueprint §4).

UI-agnostic state machine. Each step shows instruction + explanation + a command
to try, then a "Did it work? Yes/No" gate:

  * Yes -> advance to the next step.
  * No  -> offer the next authored alternative (cause + fix + what to check),
           the user retries and answers again.
  * No-with-no-alternatives-left -> the flow is EXHAUSTED: generate an
    Unresolved Issue Log + (caller shows) curated trusted links. No live help.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Sequence

from .models import StepAlternative, StepSpec


class StepperState(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    EXHAUSTED = "exhausted"


@dataclass(frozen=True)
class StepView:
    """Everything a front-end needs to render the current step (or its alternative)."""

    step_id: str
    title: str
    index: int
    total: int
    what: str
    why: str
    where: str
    try_this: str
    success_criteria: str
    expected_output: str
    slot_target: str | None
    glossary_refs: tuple[str, ...]
    destructive: bool
    recovery: str
    # Populated only while walking an alternative (the "No" branch):
    on_alternative: bool = False
    alternative_index: int = -1
    alternative_total: int = 0
    cause: str = ""
    fix: str = ""
    check: str = ""


@dataclass
class _Attempt:
    step_id: str
    title: str
    result: str                       # "yes" | "no" | "exhausted"
    alternative_used: int = -1        # -1 = main step, else alternative index
    observed_output: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class IssueLog:
    """The Unresolved Issue Log produced when authored alternatives are exhausted."""

    flow_title: str
    generated_at: str
    context: dict[str, str]
    attempts: list[dict[str, str]]
    last_step_id: str
    last_observed_output: str

    def to_text(self) -> str:
        lines = [
            "===== W1CK3D'S KALI ASSIST — Unresolved Issue Log =====",
            f"Flow: {self.flow_title}",
            f"Generated: {self.generated_at}",
            "",
            "Context:",
        ]
        for k, v in self.context.items():
            lines.append(f"  - {k}: {v}")
        lines.append("")
        lines.append("Steps attempted:")
        for i, a in enumerate(self.attempts, 1):
            alt = a.get("alternative_used", "-1")
            tag = "main step" if alt in ("-1", -1) else f"alternative #{alt}"
            lines.append(f"  {i}. [{a['result']}] {a['title']} ({tag})")
            if a.get("observed_output"):
                lines.append(f"        observed: {a['observed_output']}")
        lines.append("")
        lines.append("No authored fix resolved this. Use the curated links to search yourself.")
        return "\n".join(lines)


class StepperSession:
    """Drives one flow's steps. Front-end calls current()/answer_yes()/answer_no()."""

    def __init__(self, steps: Sequence[StepSpec], *, flow_title: str = "",
                 context: dict[str, str] | None = None, start_index: int = 0) -> None:
        if not steps:
            raise ValueError("StepperSession requires at least one step.")
        self._steps: list[StepSpec] = list(steps)
        self._flow_title = flow_title
        self._context = dict(context or {})
        # Resume support: clamp into range; len(steps) would mean already complete.
        self._i = max(0, min(start_index, len(self._steps) - 1))  # current step index
        self._alt = -1              # current alternative index (-1 = main step)
        self._state = StepperState.IN_PROGRESS
        self._attempts: list[_Attempt] = []
        self._last_output = ""

    # -- introspection ----------------------------------------------------- #
    @property
    def state(self) -> StepperState:
        return self._state

    @property
    def attempts(self) -> list[_Attempt]:
        return list(self._attempts)

    def is_done(self) -> bool:
        return self._state in (StepperState.COMPLETE, StepperState.EXHAUSTED)

    def current(self) -> StepView:
        if self.is_done():
            raise RuntimeError(f"Stepper is {self._state.value}; no current step.")
        step = self._steps[self._i]
        view = StepView(
            step_id=step.step_id,
            title=step.title,
            index=self._i,
            total=len(self._steps),
            what=step.explanation.what,
            why=step.explanation.why,
            where=step.explanation.where,
            try_this=step.try_this,
            success_criteria=step.success_criteria,
            expected_output=step.expected_output,
            slot_target=step.slot_target.name if step.slot_target else None,
            glossary_refs=tuple(step.glossary_refs),
            destructive=step.destructive,
            recovery=step.recovery,
        )
        if self._alt >= 0 and self._alt < len(step.alternatives):
            alt: StepAlternative = step.alternatives[self._alt]
            view = StepView(
                **{**view.__dict__,
                   "on_alternative": True,
                   "alternative_index": self._alt,
                   "alternative_total": len(step.alternatives),
                   "cause": alt.cause,
                   "fix": alt.fix,
                   "check": alt.check,
                   "destructive": alt.destructive or step.destructive,
                   "recovery": alt.recovery or step.recovery},
            )
        return view

    # -- the Yes/No gate --------------------------------------------------- #
    def record_output(self, text: str) -> None:
        """Optionally capture what the user saw (for the Issue Log). No secrets logged here."""
        self._last_output = text or ""

    def answer_yes(self) -> StepperState:
        if self.is_done():
            raise RuntimeError("Stepper already finished.")
        step = self._steps[self._i]
        self._attempts.append(_Attempt(step.step_id, step.title, "yes", self._alt, self._last_output))
        self._last_output = ""
        self._alt = -1
        self._i += 1
        if self._i >= len(self._steps):
            self._state = StepperState.COMPLETE
        return self._state

    def answer_no(self) -> StepperState:
        if self.is_done():
            raise RuntimeError("Stepper already finished.")
        step = self._steps[self._i]
        self._attempts.append(_Attempt(step.step_id, step.title, "no", self._alt, self._last_output))
        self._last_output = ""
        self._alt += 1
        if self._alt >= len(step.alternatives):
            # Authored alternatives exhausted for this step -> whole flow exhausted.
            self._attempts.append(_Attempt(step.step_id, step.title, "exhausted", self._alt))
            self._state = StepperState.EXHAUSTED
        return self._state

    # -- exhaustion output ------------------------------------------------- #
    def issue_log(self) -> IssueLog:
        return IssueLog(
            flow_title=self._flow_title,
            generated_at=datetime.now(timezone.utc).isoformat(),
            context=self._context,
            attempts=[
                {
                    "step_id": a.step_id,
                    "title": a.title,
                    "result": a.result,
                    "alternative_used": str(a.alternative_used),
                    "observed_output": a.observed_output,
                }
                for a in self._attempts
            ],
            last_step_id=self._steps[min(self._i, len(self._steps) - 1)].step_id,
            last_observed_output=self._last_output,
        )
