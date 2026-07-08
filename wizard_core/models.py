"""Pydantic v2 data models — the runtime contract for all spec/manifest content.

These mirror the data model in CLAUDE.md / Blueprint §6.2. The YAML files under
``modules/`` are validated against these on load; bad content fails loudly.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .slots import Slot

# --------------------------------------------------------------------------- #
#  Shared building blocks
# --------------------------------------------------------------------------- #


class _Strict(BaseModel):
    """Base: forbid unknown keys so typos in authored YAML fail loudly."""

    model_config = ConfigDict(extra="forbid", frozen=False)


class Explanation(_Strict):
    """The consistent what / why / where teaching triple shown on every step."""

    what: str = Field(..., description="What this piece is.")
    why: str = Field(..., description="Why it exists / why it's here.")
    where: str = Field("", description="Where it goes (which slot / position).")


class FieldSchema(_Strict):
    """One user input on a step; maps to exactly one slot via the builder."""

    field_id: str
    label: str
    type: Literal["string", "int", "bool", "choice", "path", "list", "range"] = "string"
    required: bool = False
    default: Any | None = None
    choices: list[str] = Field(default_factory=list)
    placeholder: str = ""
    constraint_regex: str | None = None
    help: str = ""


class QuickBuild(_Strict):
    """A tool's one-screen quick-BUILD form (Tools tab).

    ``builder`` is the registered builder id the collected inputs are fed to;
    ``fields`` are rendered top-to-bottom, and each field's ``field_id`` must
    match the input key that builder reads. Purely for the fast on-ramp — the
    adaptive stepper remains the guided path.
    """

    builder: str
    title: str = "Quick build"
    fields: list[FieldSchema] = Field(default_factory=list)


class StepAlternative(_Strict):
    """A 'No' branch for a step: a likely cause + the fix to retry + what to check."""

    trigger: str = Field("", description="The symptom this alternative addresses.")
    cause: str = Field(..., description="Likely root cause.")
    fix: str = Field(..., description="What to change / the alternative to try.")
    check: str = Field("", description="Which log/output to inspect to confirm.")
    destructive: bool = False
    recovery: str = Field("", description="How to undo, if destructive.")


class StepSpec(_Strict):
    """One adaptive step (Blueprint §4.3). Used by lessons, flows and troubleshooters."""

    step_id: str
    title: str
    slot_target: Slot | None = None
    field_schema: list[FieldSchema] = Field(default_factory=list)
    explanation: Explanation
    required: bool = True
    try_this: str = Field("", description="Exact command the learner runs in their terminal.")
    success_criteria: str = Field("", description="What success looks like.")
    expected_output: str = Field(
        "", description="Reference: what a successful run looks like on screen "
        "(monospace sample output shown under the Did-it-work? gate)."
    )
    alternatives: list[StepAlternative] = Field(default_factory=list)
    glossary_refs: list[str] = Field(default_factory=list)
    destructive: bool = False
    recovery: str = ""

    @field_validator("slot_target", mode="before")
    @classmethod
    def _coerce_slot(cls, v: Any) -> Any:
        if v is None or isinstance(v, Slot):
            return v
        if isinstance(v, int):
            return Slot(v)
        return Slot.from_name(str(v))


# --------------------------------------------------------------------------- #
#  Lessons
# --------------------------------------------------------------------------- #


class LessonSpec(_Strict):
    lesson_id: str
    title: str
    topic_tags: list[str] = Field(default_factory=list)
    audience: str = "beginner"
    os_profile: Literal["kali", "parrot", "agnostic"] = "kali"
    intro: str = ""
    goal: str = ""
    steps: list[StepSpec]
    completion_criteria: str = ""
    next_suggestions: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
#  Tools + flows
# --------------------------------------------------------------------------- #


class OutputManifest(_Strict):
    """Planned (NOT written) artifact naming for a flow — display only."""

    base_dir: str = "./out"
    files: list[str] = Field(default_factory=list)
    note: str = ""


class FlowSpec(_Strict):
    flow_id: str
    title: str
    goal: str = ""
    slots: list[Slot] = Field(default_factory=list)
    steps: list[StepSpec] = Field(default_factory=list)
    command_builder_id: str
    profile: str | None = None
    output_manifest: OutputManifest | None = None

    @field_validator("slots", mode="before")
    @classmethod
    def _coerce_slots(cls, v: Any) -> Any:
        if not v:
            return []
        out = []
        for item in v:
            if isinstance(item, Slot):
                out.append(item)
            elif isinstance(item, int):
                out.append(Slot(item))
            else:
                out.append(Slot.from_name(str(item)))
        return out


class ToolSpec(_Strict):
    tool_id: str
    display_name: str
    binary_candidates: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    os_profile: Literal["kali", "parrot", "agnostic"] = "kali"
    one_liner: str = ""
    authorization_gate: bool = False
    authorization_text: str = ""
    flows: list[FlowSpec] = Field(default_factory=list)
    quick_build: QuickBuild | None = None


# --------------------------------------------------------------------------- #
#  Troubleshooter
# --------------------------------------------------------------------------- #

Tier = Literal["basic", "intermediate", "extensive"]


class TroubleshooterFix(_Strict):
    fix_id: str
    tier: Tier = "basic"
    title: str
    command: str = ""
    why: str = ""
    verify: str = ""
    destructive: bool = False
    recovery: str = ""


class TroubleshooterSymptom(_Strict):
    """A symptom-first flow: the user picks the symptom, gets a diagnostic ladder
    (adaptive steps) then tiered fixes; on exhaustion -> Issue Log + links."""

    symptom_id: str
    label: str = Field(..., description="Plain-language symptom as the user sees it.")
    aliases: list[str] = Field(default_factory=list, description="Keyword/error match terms.")
    triage: list[FieldSchema] = Field(default_factory=list)
    diagnosis: list[StepSpec] = Field(default_factory=list)
    fixes: list[TroubleshooterFix] = Field(default_factory=list)


class ExternalResource(_Strict):
    title: str
    url: str = ""
    note: str = ""


class TroubleshooterSpec(_Strict):
    troubleshooter_id: str
    title: str
    os_profile: Literal["kali", "parrot", "agnostic"] = "kali"
    category_color: str = "info"
    triage: list[FieldSchema] = Field(default_factory=list, description="Asked once, shared by all symptoms.")
    symptoms: list[TroubleshooterSymptom]
    external_resources: list[ExternalResource] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
#  Glossary
# --------------------------------------------------------------------------- #


class GlossaryTerm(_Strict):
    term: str
    definition: str


# --------------------------------------------------------------------------- #
#  Module manifest
# --------------------------------------------------------------------------- #

ModuleType = Literal[
    "lesson", "tool", "troubleshooter", "troubleshooter_router", "knowledge", "theme"
]


class ModuleRequires(_Strict):
    base_api: str = ">=1.0"
    modules: list[str] = Field(default_factory=list)


class ModuleManifest(_Strict):
    module_id: str
    name: str
    version: str
    type: ModuleType
    os_profile: Literal["kali", "parrot", "agnostic"] = "kali"
    requires: ModuleRequires = Field(default_factory=ModuleRequires)
    provides: dict[str, Any] = Field(default_factory=dict)
    content: dict[str, str] = Field(default_factory=dict)
    routes_to: list[str] = Field(default_factory=list)
    source: str = ""
    license: str = ""
    checksum: str = ""


# --------------------------------------------------------------------------- #
#  Command plan (builder output)
# --------------------------------------------------------------------------- #

SlotTokens = Annotated[dict[Slot, list[str]], "tokens grouped per slot"]


class CommandPlan(_Strict):
    """A built command, three synchronized views (Blueprint §3.3 / §6.3).

    Nothing here is ever executed — the array form is purely illustrative.
    """

    program: str
    slot_values: dict[Slot, list[str]]
    array_form: list[str]
    bash_preview_string: str
    skeleton: str = ""
    notes: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
