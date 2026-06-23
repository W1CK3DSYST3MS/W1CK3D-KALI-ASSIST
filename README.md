# W1CK3D'S KALI ASSIST

A standalone, **offline**, **generate-only** desktop app that teaches the correct use of
Kali Linux tools and the OS itself — reference, guided learning, and a self-help
troubleshooter. A **W1CK3D SYST3MS** project.

It never runs security tools for you; it shows and explains the commands (using a consistent
**slot model**) and walks you through tasks and fixes with an adaptive **"did it work?"**
stepper. Simple to use, complete in depth.

## Status
**Phase One (design) complete.** Phase Two = build (this repo). See `BUILD-BRIEF.md`.

## For developers / Claude Code
1. Read `CLAUDE.md` (project rules + architecture).
2. Read `BUILD-BRIEF.md` (build plan + MVP).
3. Browse `docs/specs/` — start with `Phase-One-Summary.md` (index of all specs).

## Tech
Python 3.11+ · PySide6 · Pydantic v2 · YAML content modules · packaged with PyInstaller.

## Principles
Generate-only · offline · no AI/telemetry in the free build · Kali-only (extensible) ·
modular (content = data) · login + on-device audit log · W1CK3D SYST3MS design system.

## Editions
- **Free Standalone** (this build): no AI, ships as a built tool file via GitHub (source
  private).
- **Enterprise / retail** (future): adds local-LLM / paid AI assistance.

## Legal / ethics
For use on systems you own or are explicitly authorized to test. Offensive tool modules are
gated behind an authorization confirmation. The app is educational and does not execute
attacks.
