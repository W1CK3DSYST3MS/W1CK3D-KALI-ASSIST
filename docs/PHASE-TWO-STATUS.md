# Phase Two — Build Status

> Pick-up notes for the build. Read `CLAUDE.md` + `BUILD-BRIEF.md` first.

## Milestone 1a — Engine + vertical slice (COMPLETE, no GUI yet)

The UI-agnostic engine (`wizard_core`, **zero Qt imports**) is built, tested, and
proven end-to-end via a headless harness. **Nothing is ever executed.**

### What exists
- `wizard_core/slots.py` — the 8-slot model + fixed assembly order.
- `wizard_core/models.py` — all Pydantic v2 specs (Tool/Flow/Step/Lesson/
  Troubleshooter/ModuleManifest/CommandPlan), `extra="forbid"` so bad YAML fails loudly.
- `wizard_core/builders/` — shell-escaping assembler + builder registry + `nmap` builder.
- `wizard_core/stepper.py` — the adaptive "did it work? Yes/No" stepper + Unresolved Issue Log.
- `wizard_core/loader.py` — module loader (manifest validation, base_api check, glossary
  merge) + the T00 troubleshooter router (deterministic symptom search).
- `wizard_core/audit/` — JSONL audit log with secret redaction (never logs passwords).
- `wizard_core/auth/` — local login + disclaimer policy (PBKDF2 hashing, no plaintext).
- `wizard_core/glossary.py` — first-use glossary surfacing.

### Runtime modules (data converted from the specs)
- `modules/fundamentals.shell_grammar/` — lesson (7 steps) + glossary.
- `modules/tool.nmap/` — ToolSpec with all 9 flows + authorization gate + glossary;
  builder is the in-core registered `nmap` builder.
- `modules/troubleshoot.networking/` — 6 symptoms, tiered fixes, diagnostics, links + glossary.
- `modules/troubleshoot.index/` — T00 router manifest (aggregates the above).

### Proof
- `tests/` — 28 unit tests (slots, nmap builder, stepper, loader, audit). All pass.
- `tools/cli_harness.py` — runs the whole loop: login gate → load → nmap build (auth gate)
  → lesson stepper → troubleshooter → Issue Log → audit written.
  Run: `python -m tools.cli_harness`.

### How to run
```
python -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m tools.cli_harness
```

## Architecture decision logged
- **Command builders live in-core** (`wizard_core/builders/`) and self-register by id; flows
  reference them via `command_builder_id`. This avoids importing Python from data files
  (safer for a closed build) while keeping content additive. Revisit if third-party tool
  modules ever need to ship their own builders.

## Next — Milestone 1b (GUI), pending review
- PySide6 app: login + disclaimer screen → themed main window → category tabs → stepper
  view → command-preview pane. Apply `Design-System-Tokens.md` as QSS.
- Then Milestone 1c: one PyInstaller build that runs offline on Kali.

## Distribution guard (do not forget)
This repo is **PRIVATE / closed source** — source + `docs/specs` blueprints never ship.
Only the compiled binary is released (GitHub Release asset on a separate public repo),
preserving the future Enterprise edition. No git remote is configured; keep it that way
unless the remote is private.
