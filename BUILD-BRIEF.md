# BUILD-BRIEF.md — W1CK3D'S KALI ASSIST (Phase Two: build)

> Developer build plan for Claude Code. Read `CLAUDE.md` first. The full design lives in
> `docs/specs/` — `Phase-One-Summary.md` is the index.

## Goal
Turn the Phase One design specs into a working, **offline, generate-only** Kali desktop app
(PySide6 → single executable). Build the **engine + a vertical slice first**, prove it end to
end, then scale content by adding modules.

## The specs are designs, not runtime files
`docs/specs/Module-*.md`, `Troubleshooter-*.md`, etc. are **human-readable specifications**.
Your job is to:
1. Implement the **engine** (`wizard_core`) and **UI** (`wizard_desktop`) per `CLAUDE.md`.
2. Convert each spec module into **runtime data**: a `ModuleManifest` + YAML flow/lesson/
   troubleshooter definitions + (for tools) a Python command builder.
3. Apply the **design tokens** from `Design-System-Tokens.md` as the theme.

## Proposed repo layout (create this)
```
w1ck3d-kali-assist/
  CLAUDE.md  README.md  BUILD-BRIEF.md
  pyproject.toml
  assets/            # logo, bundled fonts
  docs/specs/        # the Phase One design docs (provided)
  wizard_core/
    slots.py  stepper.py  models.py (pydantic)  loader.py
    builders/  explain/  audit/  auth/
  modules/           # runtime content (YAML + builders), one dir per module
    fundamentals.shell_grammar/
    tool.nmap/
    troubleshoot.networking/
    theme.w1ck3d_systems/
  wizard_desktop/
    app.py  ui/ (login, main_window, tabs, stepper_view, command_preview)
  tests/
```

## MVP — vertical slice (Milestone 1, build this first)
Prove the whole loop on the smallest real path:
- [ ] App boots → **login + disclaimer gate** → main window (W1CK3D theme applied).
- [ ] **Module loader** reads a manifest and registers content (no UI changes needed to add).
- [ ] **Slot engine + builder** assembles a command in fixed slot order with proper shell
      escaping; produces both a bash preview string and an array form (display only).
- [ ] **Adaptive stepper** renders steps + the Yes/No gate + alternatives; on exhaustion
      generates an **Issue Log** and shows curated links.
- [ ] Ship **one of each module type**, converted from the specs:
      - Lesson: `Module-01-Shell-Grammar.md`
      - Tool: `Module-02-nmap.md` (with its `authorization_gate`)
      - Troubleshooter: `Module-T01-Networking-Troubleshooter.md` (+ `T00` index entry)
- [ ] **Audit log** writes JSONL (no secrets).
- [ ] One **PyInstaller** build that runs offline on Kali.

**Acceptance:** on a clean Kali VM, launch the built binary, pass the login gate, complete
the nmap flow (command preview correct), run the shell-grammar lesson, and walk the
networking troubleshooter including an Issue Log — all with no internet.

## Milestone 2 — scale tools
Convert the rest of the CLI Top 10 (`Module-03`…`Module-11`) to runtime modules. Each is the
same shape; reuse the builder pattern. Keep authorization gates + destructive warnings.

## Milestone 3 — full troubleshooter + lessons
Convert `Module-T02..T05` + the `T00` router index (auto-register symptoms/error-signatures),
and `Module-00` setup/securing lesson (Kali edition + router).

## Milestone 4 — packaging & polish
Finalize PyInstaller/AppImage packaging, bundle fonts/logo, theme polish vs the tokens,
onboarding checklist, settings (output base dir).

## Milestone 5 (later) — Termux edition
Reuse `wizard_core`; add a TUI front-end. Curated-only, no GUI deps.

## Non-negotiables (from CLAUDE.md)
- Generate-only; no executing target commands; offline; no AI/telemetry in this build.
- `wizard_core` has **zero Qt imports** (so Termux can reuse it).
- Validate all manifests/specs with Pydantic; tests for builders + loader.
- Authorization gate blocks before any offensive command is shown; destructive steps warn +
  give recovery.

## First commands to run in Claude Code
1. "Read CLAUDE.md and BUILD-BRIEF.md and docs/specs/Phase-One-Summary.md, then propose the
   project scaffold and confirm the plan for Milestone 1."
2. Approve/adjust the plan.
3. "Implement Milestone 1 (engine + login + loader + one of each module type + PyInstaller),
   with tests."
Work milestone by milestone; review between.
