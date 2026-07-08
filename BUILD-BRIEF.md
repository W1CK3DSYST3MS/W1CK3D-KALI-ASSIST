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

### Building the Kali/Linux binary — one clean pass
PyInstaller **cannot cross-compile**: build the Linux binary ON Kali (bare metal, VM, or
win-kex/WSL2). The spec bundles `modules/` + `assets/` and slims the Qt payload, so the one
file contains all 9 lessons, 10 tools and 5 troubleshooters and runs fully offline.

```bash
# 0. Get the source onto Kali (the "send me" folder). Then, from the repo root:
cd w1ck3d-kali-assist

# 1. Isolated environment + deps (do NOT `pip install -e .` — just the runtime deps).
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pydantic PyYAML PySide6 pyinstaller pillow

# 2. Prove the engine before packaging.
python -m pytest -q                     # expect: all pass
python tools/gui_smoke.py               # offscreen; expect: GUI SMOKE PASSED

# 3. Build the one-file binary.
pyinstaller packaging/w1ck3d-kali-assist.spec --noconfirm

# 4. Verify the FROZEN binary finds everything (no GUI needed).
./dist/w1ck3d-kali-assist              # launches the app, OR:
./dist/w1ck3d-kali-assist --self-test  # expect: SELF-TEST OK ... lessons=9 tools=10 builders=11
```

**Expected size:** ~70–90 MB (the spec drops WebEngine/Quick/Multimedia etc., which cut a
raw ~250 MB build down by ~3×). The `[slim] Qt filter removed N entries` line prints during
the build.

**Harmless warnings you can ignore:** `ignoring icon` / PNG-not-.ico (Linux ELFs carry no
embedded icon); `hidden import "pycparser.lextab" not found`; `library ole32 ... not found`
(a Windows-only lib, irrelevant on Linux). None affect the build.

**If the binary fails to start on Kali** with a Qt *"could not load the xcb platform plugin"*
(or similar platform-plugin) error, the Qt slim filter removed one lib too many. Escape
hatch: open `packaging/w1ck3d-kali-assist.spec`, comment out the whole
`# --- Slim the Qt payload ---` block (the `a.binaries = [...]` / `a.datas = [...]` lines),
and rebuild — you get a larger but guaranteed-complete binary. Then report which lib was
missing so the droplist can be corrected. On Kali the xcb plugin also needs the system
package `libxcb-cursor0` (`sudo apt install libxcb-cursor0`) — install it if Qt complains.

**AppImage (optional, portable across distros):** wrap `dist/w1ck3d-kali-assist` with
`appimagetool` (an AppDir with the binary + a `.desktop` + the logo). The PyInstaller one-file
already runs on Kali/Ubuntu directly, so AppImage is only for wider portability.

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
