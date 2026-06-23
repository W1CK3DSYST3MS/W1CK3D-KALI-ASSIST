"""Headless proof-of-loop for Milestone 1 (no GUI).

Exercises the whole vertical slice through wizard_core only:
  login + disclaimer gate -> module load -> nmap command build (with auth gate)
  -> shell-grammar lesson stepper -> networking troubleshooter to an Issue Log
  -> audit log written (no secrets).

Run:  python -m tools.cli_harness
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Allow running from a source checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wizard_core.audit import AuditLogger
from wizard_core.auth import LoginPolicy
from wizard_core.builders import get_builder
from wizard_core.loader import load_modules
from wizard_core.stepper import StepperSession

MODULES = Path(__file__).resolve().parents[1] / "modules"

RULE = "─" * 70


def banner(title: str) -> None:
    print(f"\n{RULE}\n  {title}\n{RULE}")


def main() -> int:
    audit_path = Path(tempfile.gettempdir()) / "w1ck3d_harness.audit.jsonl"
    audit = AuditLogger(audit_path, user="hunter")

    # 1. Login + disclaimer gate ------------------------------------------ #
    banner("1. LOGIN + DISCLAIMER GATE")
    policy = LoginPolicy()
    bad = policy.validate("hi", "short", False)
    print(f"  reject weak input: ok={bad.ok}  errors={len(bad.errors)}")
    good = policy.validate("hunter", "correcthorse", True)
    print(f"  accept valid input: ok={good.ok}")
    audit.login("hunter")
    assert good.ok and not bad.ok

    # 2. Module loader ----------------------------------------------------- #
    banner("2. MODULE LOADER")
    reg = load_modules(MODULES)
    print(f"  modules loaded : {', '.join(sorted(reg.modules))}")
    print(f"  tools          : {', '.join(sorted(reg.tools))}")
    print(f"  lessons        : {', '.join(sorted(reg.lessons))}")
    print(f"  troubleshooters: {', '.join(sorted(reg.troubleshooters))}")
    print(f"  glossary terms : {len(reg.glossary)}")

    # 3. nmap command build (authorization gate first) -------------------- #
    banner("3. TOOL: nmap — authorization gate + slot build")
    tool = reg.tools["nmap"]
    if tool.authorization_gate:
        print("  [AUTHORIZATION REQUIRED]")
        print("   " + tool.authorization_text.strip())
        audit.authorization_ack("nmap")
        print("  -> acknowledged (logged)")
    plan = get_builder("nmap")({
        "profile": "standard", "targets": "scanme.nmap.org",
        "output_format": "all", "output_path": "./out/scan",
    })
    print(f"\n  Skeleton : {plan.skeleton}")
    print(f"  Filled   : {plan.bash_preview_string}")
    print("  Slots:")
    for slot, toks in plan.slot_values.items():
        print(f"    {slot.value} {slot.label:<16} {' '.join(toks)}")
    for n in plan.notes:
        print(f"  note: {n}")
    audit.command_preview(tool="nmap", flow="standard")

    # 4. Lesson stepper (all-yes path) ------------------------------------ #
    banner("4. LESSON: shell_grammar — adaptive stepper (Yes path)")
    lesson = reg.lessons["lesson.shell_grammar"]
    s = StepperSession(lesson.steps, flow_title=lesson.title)
    while not s.is_done():
        v = s.current()
        print(f"  step {v.index + 1}/{v.total}  {v.title}")
        print(f"      try: {v.try_this}")
        for term in v.glossary_refs:
            d = reg.glossary.first_use(term)
            if d:
                print(f"      glossary[{term}]: {d}")
        audit.step_milestone(lesson.lesson_id, v.step_id, "yes")
        s.answer_yes()
    print(f"  -> lesson state: {s.state.value}")

    # 5. Troubleshooter -> exhaustion -> Issue Log ------------------------ #
    banner("5. TROUBLESHOOTER: networking — diagnose to Unresolved Issue Log")
    matches = reg.search_symptoms("no internet at all")
    top = matches[0]
    print(f"  router matched symptom: {top.label}  ({top.troubleshooter_id})")
    ts = reg.troubleshooters[top.troubleshooter_id]
    symptom = next(s for s in ts.symptoms if s.symptom_id == top.symptom_id)
    sess = StepperSession(symptom.diagnosis, flow_title=ts.title,
                          context={"link_type": "wifi", "changed": "after reboot"})
    # Walk every diagnostic answering "No" through all alternatives -> exhaust.
    sess.record_output("only 127.0.0.1 present")
    while not sess.is_done():
        v = sess.current()
        tag = f" [alt {v.alternative_index}]" if v.on_alternative else ""
        print(f"  diag: {v.title}{tag}  (try: {v.try_this})")
        sess.answer_no()
    print(f"  -> state: {sess.state.value}")
    print("\n  Tiered fixes available for this symptom:")
    for fx in symptom.fixes:
        warn = "  ⚠ destructive" if fx.destructive else ""
        print(f"    [{fx.tier}] {fx.title}: {fx.command}{warn}")
    print("\n" + sess.issue_log().to_text())
    print("\n  Curated trusted links (search yourself — no live help):")
    for r in ts.external_resources:
        print(f"    - {r.title} {r.url}{(' — ' + r.note) if r.note else ''}")

    banner("DONE — full Milestone-1 loop proven, no command executed")
    print(f"  audit log written: {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
