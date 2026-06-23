# Packaging — W1CK3D'S KALI ASSIST

Builds a **single, offline, generate-only** executable with PyInstaller. The build
bundles `modules/` (runtime content) + `assets/` (fonts + logo) into the binary, so
it runs with no internet and nothing else installed.

> **Distribution rule:** only the built binary is released — as a GitHub Release asset
> on a separate public repo. This source repo (and `docs/specs/`) stays private.
> PyInstaller is **not** a cross-compiler: build the Kali binary **on Kali/Linux**.

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
- **Kali / Ubuntu desktop (primary target):** run the same `pyinstaller` command **on
  Kali**. For a portable Linux artifact, wrap the one-dir output as an **AppImage**
  (e.g. with `appimagetool`) — recommended for distribution.

## Acceptance (per BUILD-BRIEF, Milestone 1)
On a clean Kali VM: launch the built binary, pass the login + disclaimer gate, build
the nmap command (authorization gate first), run the shell-grammar lesson, and walk the
networking troubleshooter to an Issue Log — all with **no internet**.

## Notes
- `dist/` and `build/` are git-ignored — the binary is never committed; it ships via Releases.
- Icon: PyInstaller auto-converts `assets/W1CK3D-SYSTEMS-logo.png` to `.ico` via Pillow.
- Fonts (OFL) are in `assets/fonts/` with `OFL.txt` + `ATTRIBUTION.md`.
