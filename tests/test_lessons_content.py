"""Content integrity: every lesson loads and meets the richer-template bar."""

from pathlib import Path

from wizard_core.loader import load_modules

MODULES = Path(__file__).resolve().parents[1] / "modules"


def test_all_lessons_load_and_have_expected_output():
    reg = load_modules(MODULES)
    assert len(reg.lessons) >= 8, f"expected the fundamentals set, got {sorted(reg.lessons)}"
    for lid, lesson in reg.lessons.items():
        assert lesson.steps, f"{lid} has no steps"
        for step in lesson.steps:
            # Every step must carry a reference block and a try-this command.
            assert step.expected_output.strip(), f"{lid}:{step.step_id} missing expected_output"
            assert step.try_this.strip(), f"{lid}:{step.step_id} missing try_this"
            # Each step must offer at least one alternative (the deeper-branch bar).
            assert step.alternatives, f"{lid}:{step.step_id} has no alternatives"


def test_fundamentals_curriculum_present():
    reg = load_modules(MODULES)
    expected = {
        "lesson.shell_grammar", "lesson.files_navigation", "lesson.permissions",
        "lesson.viewing_editing", "lesson.pipes_redirection", "lesson.processes",
        "lesson.packages", "lesson.networking",
    }
    assert expected <= set(reg.lessons)


def test_glossary_terms_are_rich():
    reg = load_modules(MODULES)
    assert len(reg.glossary) >= 150
