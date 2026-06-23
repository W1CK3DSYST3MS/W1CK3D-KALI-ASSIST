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

## Milestone 1b — PySide6 GUI (COMPLETE, pending review)

`wizard_desktop/` (imports `wizard_core` only):
- `theme.py` — QSS generated from the exact `Design-System-Tokens.md` hexes.
- `ui/login_window.py` — login + disclaimer gate (wired to `LoginPolicy`).
- `ui/main_window.py` — header + LESSONS / TOOLS / TROUBLESHOOTER tabs (list→detail).
- `ui/stepper_view.py` — the shared adaptive Yes/No stepper widget (alternatives,
  destructive warnings, glossary first-use, Issue Log + links on exhaustion).
- `ui/command_preview.py` — skeleton / filled / slot-breakdown views (mono).
- `ui/tool_page.py` — profile+inputs → built command; honors the authorization gate.
- `ui/auth_gate.py` — blocking red authorization dialog.
- `app.py` — entrypoint: theme → login → load modules → main window; audit to
  `~/.w1ck3d-kali-assist/activity.audit.jsonl`.

Proof: `tools/gui_smoke.py` (offscreen) builds every screen + drives each section.
Run the real app: `.venv/Scripts/python -m wizard_desktop.app`.

KNOWN: fonts (Black Ops One/Orbitron/JetBrains Mono…) are not bundled yet, so on a
box with none installed glyphs fall back to boxes. Bundling the Google Fonts is the
remaining theme task (Milestone 4 / outstanding items).

## Milestone 1c — Packaging (COMPLETE on Windows; Kali build pending on Linux)

- `wizard_desktop/fonts.py` — loads the 5 bundled brand fonts (OFL) via QFontDatabase;
  glyphs now render (stencil wordmark, Orbitron, JetBrains Mono). Fonts + `OFL.txt` +
  `ATTRIBUTION.md` live in `assets/fonts/`.
- `wizard_desktop/resources.py` — resolves `assets/` + `modules/` in both source and
  PyInstaller (`sys._MEIPASS`) layouts.
- `packaging/w1ck3d-kali-assist.spec` — one-file build, bundles fonts/logo/modules.
- `packaging/README.md` — build + verify + Kali/AppImage instructions.
- `app.py --self-test` — headless check that the bundle finds its packaged resources.

Proof: built `dist/w1ck3d-kali-assist.exe` (~54 MB, one file); `--self-test` reports
`fonts=5 tools=1 lessons=1 troubleshooters=1` and builds a command — fully offline.

TODO to finish Milestone 1: produce the **Kali/Linux** binary by running the same
`pyinstaller` command on Kali (PyInstaller can't cross-compile), then run the BUILD-BRIEF
acceptance pass on a clean Kali VM. Optionally wrap as an AppImage for distribution.

## Phase Two — remaining (Milestones 2–4)
- M2: convert the rest of the CLI Top 10 (sqlmap…nikto) to runtime tool modules.
- M3: convert troubleshooters T02–T05 + Module-00 setup/securing lesson.
- M4: theme polish, onboarding checklist, settings (output base dir); finalize AppImage.

## Distribution guard (do not forget)
This repo is **PRIVATE / closed source** — source + `docs/specs` blueprints never ship.
Only the compiled binary is released (GitHub Release asset on a separate public repo),
preserving the future Enterprise edition. No git remote is configured; keep it that way
unless the remote is private.
