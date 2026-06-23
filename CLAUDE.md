# CLAUDE.md — W1CK3D'S KALI ASSIST

> Project memory for Claude Code. Read this first, then `BUILD-BRIEF.md`, then the specs in
> `docs/specs/` (start with `Phase-One-Summary.md` for the index).

## What this project is
**W1CK3D'S KALI ASSIST** — a standalone **desktop application** that teaches the correct use
of Kali Linux tools and the OS itself. It is a **reference + learning + self-help
troubleshooting** tool. A **W1CK3D SYSTEMS** project.

## HARD RULES (do not violate)
1. **Generate-only. The app NEVER executes target commands.** It displays and explains
   commands; the user runs them in their own terminal. No `subprocess` running of tool
   commands, no auto-exec. (The app may read local system state for *its own* UI, e.g.
   detecting installed tools via `shutil.which`, but never runs the security tools.)
2. **No AI / no network service in the free build.** All content is pre-authored and shipped
   locally. No LLM calls, no telemetry, no "phone home". (AI is a future Enterprise edition,
   out of scope here.)
3. **Kali only** for now. Architecture keeps an `os_profile` field so other distros can be
   added later, but build for Kali.
4. **Offline-first.** Must run with no internet. Bundle all content/assets.
5. **Accountability:** first-run **login + disclaimer gate**, and an **on-device audit log**
   (JSON Lines). Never log secrets (passwords, tokens, keys, sensitive paths).

## Tech stack (locked)
- **Language:** Python 3.11+
- **GUI:** **PySide6** (desktop). Package to a single executable with **PyInstaller**
  (AppImage acceptable for portable Linux).
- **Schema/validation:** **Pydantic v2**.
- **Content format:** **YAML** registries + Python command builders (see data model below).
- **Target OS:** Kali Linux desktop (Debian-based); also runnable on Ubuntu desktop.
- A future **Termux TUI** edition reuses the same core — keep `wizard_core` UI-agnostic.

## Architecture (from the blueprint)
- `wizard_core/` — UI-agnostic engine: the **slot model**, the **adaptive stepper**,
  schema/validation, module loader, glossary, audit logger, login policy. **No UI imports.**
- `wizard_desktop/` — PySide6 app: login screen, category tabs, stepper pages, command-
  preview pane. Imports `wizard_core` only.
- **Module system:** the base ships small; tools/lessons/troubleshooters/themes load as
  **versioned modules** (manifests) at runtime. Adding content = adding data, not editing UI.

### Core concepts to implement
- **Slot model:** every command is built from ordered slots (PROGRAM, GLOBAL_OPTIONS,
  TARGET_PIVOT, ACTION_OPTIONS, OUTPUT_OPTIONS, POSITIONAL_ARGS, ENV/INTERFACE, EXTRA_FILES).
  The builder assembles in this fixed order; the UI never asks the user to reorder.
- **Adaptive stepper:** each step shows instruction + explanation, then a "Did it work?
  Yes/No" gate. Yes → next; No → show alternatives (cause + fix). Exhausted → generate an
  **Unresolved Issue Log** + show curated trusted links. (No live help.)
- **Slot/lesson/tool/troubleshooter specs** live in `docs/specs/` as Markdown design specs;
  convert them into runtime YAML + builders (see BUILD-BRIEF).

## Data model (implement as Pydantic models)
- `ToolSpec` (tool_id, display_name, binary_candidates, categories, flows[], authorization_gate)
- `FlowSpec` (flow_id, title, slots[], steps[], command_builder_id, output_manifest)
- `StepSpec` (step_id, title, slot_target, field_schema[], explanation{what,why,where},
  requiredness, success_criteria, alternatives[])
- `LessonSpec` / `TroubleshooterFlowSpec` (symptom, triage[], diagnosis[], fixes[], tier,
  on_exhausted{generate_issue_log, external_resources, related_reference})
- `ModuleManifest` (module_id, name, version, type, requires, provides, content, os_profile,
  source, license, checksum)
- `CommandPlan` (program, slot_values, bash_preview_string, array_form)

## Design system (W1CK3D SYSTEMS)
- Tokens are the **source of truth** in `docs/specs/Design-System-Tokens.md` (the `:root` CSS
  variable block). Implement as a QSS/theme file from those exact values. Dark cyber/terminal
  aesthetic; **monospace fonts for all command/slot views**; status colors double as category
  tints AND stepper states (green=Yes/success, red/orange=No/alternative).
- Logo: `assets/W1CK3D-SYSTEMS-logo.png` (true SVG TBD — PNG is fine for now).
- Fonts are Google Fonts (Black Ops One, Orbitron, Chakra Petch, JetBrains Mono, Share Tech
  Mono) — bundle them.

## Conventions
- Keep `wizard_core` free of any PySide6/Qt imports (testable, reusable for Termux).
- Every offensive tool module has an `authorization_gate`; render it as a blocking red dialog
  before showing any built command. Destructive steps render red warnings with recovery notes.
- Type-hint everything; validate all spec/manifest loading with Pydantic; fail loudly on bad
  manifests.
- Write unit tests for the slot builders (assemble correct order/escaping) and the module
  loader.

## Where to start
See `BUILD-BRIEF.md` for the MVP vertical slice and milestone order. Don't build all modules
at once — build the engine + one of each module type first, prove it, then scale.
