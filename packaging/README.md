# Packaging — W1CK3D'S KALI ASSIST

Builds a **single, offline, generate-only** executable with PyInstaller. The build
bundles `modules/` (runtime content) + `assets/` (fonts + logo) into the binary, so
it runs with no internet and nothing else installed.

> **Note:** PyInstaller is **not** a cross-compiler: build the Kali binary **on Kali/Linux**.

## Prerequisites
```
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[desktop,dev]" pyinstaller pillow   # Windows
# Linux:  .venv/bin/python -m pip install -e ".[desktop,dev]" pyinstaller pillow
```

## Build (from the repo root)
```
pyinstaller packaging/w1ck3d-kali-assist.spec --noconfirm
```
Output: `dist/w1ck3d-kali-assist` (`.exe` on Windows). The same spec works on Linux
and produces a native ELF binary.

## Verify the build (no GUI needed)
```
dist/w1ck3d-kali-assist --self-test
# -> SELF-TEST OK: fonts=5 tools=N lessons=N troubleshooters=N
```
This confirms the bundled fonts + modules resolve from inside the binary.

## Target builds
- **Windows desktop:** the `.exe` produced here (dev/proof; also usable on Windows).
- **Kali / Ubuntu desktop (primary target):** run the same `pyinstaller` command **on Kali**.
- **AppImage (portable Linux artifact, proven working 2026-07-25):**
  ```bash
  # one-time: get appimagetool (official, from the AppImage project)
  curl -L -o ~/.local/bin/appimagetool \
    "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
  chmod +x ~/.local/bin/appimagetool

  # build the AppDir
  APPDIR=/tmp/W1CK3D-KALI-ASSIST.AppDir
  rm -rf "$APPDIR" && mkdir -p "$APPDIR"
  cp dist/w1ck3d-kali-assist "$APPDIR/AppRun" && chmod +x "$APPDIR/AppRun"
  cp packaging/w1ck3d-kali-assist.desktop "$APPDIR/w1ck3d-kali-assist.desktop"
  cp assets/W1CK3D-KALI-ASSIST-logo.png "$APPDIR/w1ck3d-kali-assist.png"

  # package it
  ARCH=x86_64 ~/.local/bin/appimagetool "$APPDIR" dist/W1CK3D-KALI-ASSIST-x86_64.AppImage

  # verify (works with or without FUSE)
  dist/W1CK3D-KALI-ASSIST-x86_64.AppImage --self-test
  ```
  Since the PyInstaller build is already a self-contained one-file binary, the AppDir only
  needs those three files — no `usr/` tree required. If `appimagetool` warns about missing
  AppStream metadata, that's expected and harmless (optional metadata, not required to run).
- **Installed on a regular Kali desktop (not packaged):** a ready-to-copy `.desktop` launcher
  is easiest done by hand — see `~/.local/share/applications/w1ck3d-kali-assist.desktop` for a
  working example. Point `Exec=` at a stable location (e.g. `~/.local/bin/w1ck3d-kali-assist`,
  not directly into a project checkout) so it survives the source folder moving.

## Acceptance (per BUILD-BRIEF, Milestone 1)
On a clean Kali VM: launch the built binary, pass the login + disclaimer gate, build
the nmap command (authorization gate first), run the shell-grammar lesson, and walk the
networking troubleshooter to an Issue Log — all with **no internet**.

## Notes
- `dist/` and `build/` are git-ignored — the binary is never committed; it ships via Releases.
- Icon: PyInstaller auto-converts `assets/W1CK3D-KALI-ASSIST-logo.png` (the tool-specific
  crest — raven perched on a book, matching the W1CK3D SYSTEMS brand style) to `.ico` via
  Pillow. The plain `W1CK3D-SYSTEMS-logo.png` is the org crest, still used on the in-app
  login screen.
- Fonts (OFL) are in `assets/fonts/` with `OFL.txt` + `ATTRIBUTION.md`.
