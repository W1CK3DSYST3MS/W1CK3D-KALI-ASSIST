# W1CK3D'S KALI ASSIST

A standalone, **offline**, **generate-only** desktop app that teaches the correct use of
Kali Linux tools and the OS itself. It's a reference, a guided learning tool, and a self-help
troubleshooter, all in one — a **W1CK3D SYST3MS** project.

It never runs security tools for you. It builds and explains the exact command you'd type
(using a consistent **slot model**, so every tool's command is assembled the same predictable
way) and walks you through tasks and fixes with an adaptive **"did it work? Yes/No"** stepper.
When a step fails, it offers alternatives; if nothing resolves it, it generates an **Unresolved
Issue Log** plus curated trusted links — no live help, no AI, nothing phoned home.

## What's inside

- **34 tool modules** — nmap, sqlmap, gobuster, nikto, hydra, john, hashcat, the aircrack-ng
  suite, tshark/wireshark, metasploit, sherlock, dnsmap, bettercap, blueranger, btscanner,
  gqrx, rfcat, gvm, heartleech, dirb, dirbuster, burpsuite, kismet, photon, responder, netexec,
  oscanner, sidguesser, tnscmd10g, sqlninja, mdbtools, sqlsus, theHarvester, exiftool — each as
  a guided walkthrough plus a quick-build form, with an authorization gate before anything
  offensive is shown. Recon/OSINT tools don't just stop at "here's your scan output" either —
  sherlock's guide, for example, walks into archiving evidence and pivoting into photon/
  exiftool/theHarvester once you've found something.
- **14 fundamentals lessons** (shell grammar, permissions, networking, packages, users/groups,
  and more) and a **full symptom-first troubleshooter** (networking, packages/keys/certs,
  services/systemd, permissions/filesystem, and rare/hard cases).
- Every tool's flags/syntax have been cross-checked against the real installed tool's
  `--help`/`man` output on Kali — see `docs/VERIFICATION-LOG.md` for the source and status of
  each one.
- Working toward guides for every tool in Kali's official catalog — see
  `docs/TOOL-COVERAGE.md` for the tracked checklist (407 tools across 29 categories).

## Status

Fully built and passing: 127 automated tests, the CLI harness, the GUI smoke test, and a
native Kali/Linux binary build (`--self-test` reports `tools=34 lessons=14 troubleshooters=5`).
Released at [github.com/W1CK3DSYST3MS/W1CK3D-KALI-ASSIST/releases](https://github.com/W1CK3DSYST3MS/W1CK3D-KALI-ASSIST/releases)
— see `docs/PHASE-TWO-STATUS.md` for the detailed build log and what's still outstanding
(per-tool GUI form polish, more tool coverage).

## Staying updated

The app itself never phones home or checks for updates — that's by design (see Principles
below). To get notified when a new version ships, use GitHub's own notifications instead of
relying on the app: on this repo, click **Watch → Custom → Releases only** (top of the GitHub
page). You'll get a notification/email for each new release, with nothing running on your
machine in the meantime.

## Prerequisites

- **Kali Linux** (primary target; also runs on Ubuntu desktop) — the app is Linux-only for now.
- **Python 3.11+**
- On a minimal Kali install, the Qt GUI may need `libxcb-cursor0`:
  `sudo apt install libxcb-cursor0`

## Install & run (from source)

```bash
git clone https://github.com/W1CK3DSYST3MS/W1CK3D-KALI-ASSIST.git
cd W1CK3D-KALI-ASSIST

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[desktop,dev]"

# optional but recommended: confirm everything works before running
.venv/bin/python -m pytest -q

# launch the app
.venv/bin/python -m wizard_desktop.app
```

On first run you'll pass a login + disclaimer gate, then land on three tabs: **Lessons**,
**Tools**, and **Troubleshooter**.

## Building a standalone binary

A single-file offline executable can be built with PyInstaller (see `packaging/README.md`
for full detail):

```bash
.venv/bin/python -m pip install pyinstaller pillow
pyinstaller packaging/w1ck3d-kali-assist.spec --noconfirm

./dist/w1ck3d-kali-assist --self-test   # verify the bundle finds everything
./dist/w1ck3d-kali-assist               # run it
```

PyInstaller can't cross-compile — build the Linux binary on Kali/Linux itself.

## Principles

Generate-only · offline · no AI/telemetry · Kali-only (extensible via an `os_profile` field) ·
modular (adding a tool/lesson means adding a data module, not editing UI code) · local login +
on-device audit log (never logs secrets) · W1CK3D SYST3MS design system throughout.

## Legal / ethics

For use on systems you own or are explicitly authorized to test. Offensive tool modules are
gated behind an authorization confirmation before any command is shown. The app is educational
and does not execute attacks — it only ever displays and explains commands you choose to run
yourself.

## License

**MIT** — see `LICENSE`. This is the free, open-source edition. A paid **Enterprise** edition
(adds local-LLM / AI assistance) is planned as a separate future offering and is not part of
this repo.

## Development

Working on the app itself? Read `CLAUDE.md` first (project rules + architecture), then
`BUILD-BRIEF.md` (milestone plan) and `docs/specs/Phase-One-Summary.md` (the design spec
index).
