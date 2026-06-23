# W1CK3D'S KALI ASSIST — Pick-up Notes

**Project:** W1CK3D'S KALI ASSIST (a **W1CK3D SYSTEMS** project)
**What it is:** standalone, **Kali-only**, generate-only interactive learning/reference +
self-help troubleshooter for Linux + security CLI tools. Teaches via the **slot model** +
an **adaptive "did it work? Yes/No" stepper**. Modular (base + add-on modules). No command
execution. **Fully self-contained — no AI in the free build.**
**Last worked:** 2026-06-22

## Files (all in this folder)
- `Tool-Wizard-Blueprint.md` (v1.8) — master spec
- `Coverage-and-Data-Sources.md` — what to cover + where to source it
- `Design-System-Tokens.md` — W1CK3D SYSTEMS brand tokens (dark cyber/terminal)
- `Module-00-Setup-and-Securing.md` — router (Kali-only)
- `Module-00-Kali-Setup-and-Securing.md` — ACTIVE setup/securing lesson
- `Module-00-Parrot-Setup-and-Securing.md` — PARKED (field notes saved)
- `Module-01-Shell-Grammar.md` — ACTIVE first lesson (teaches the slots)
- `Module-02-nmap.md` — ACTIVE tool module (template for all tools)
- `Module-03-sqlmap.md` — ACTIVE tool module
- `Module-04-hydra.md` — ACTIVE tool module
- `Module-05-john.md` — ACTIVE tool module
- `Module-06-hashcat.md` — ACTIVE tool module
- `Module-07-aircrack-ng.md` — ACTIVE tool module (suite)
- `Module-08-metasploit.md` — ACTIVE tool module (framework; most complete)
- `Module-09-wireshark-tshark.md` — ACTIVE tool module
- `Module-10-gobuster.md` — ACTIVE tool module
- `assets/W1CK3D-SYSTEMS-logo.png` — logo asset (PNG 1254×1254; not true SVG)
- `Troubleshooter-Subsystem.md` — the assisted symptom-first troubleshooter (biggest part)
- `Module-T01-Networking-Troubleshooter.md` — ACTIVE first full troubleshooter (template)
- `Module-T02-Packages-Keys-Certs-Troubleshooter.md` — ACTIVE (apt/keys/certs/git installs)
- `Module-T03-Services-Systemd-Troubleshooter.md` — ACTIVE (systemctl/journalctl/GVM/SSH)
- `Module-T04-Permissions-Filesystem-Troubleshooter.md` — ACTIVE (perms/sudo/mount/find)
- `Module-T05-Rare-Hard-Cases-Troubleshooter.md` — ACTIVE (boot/GRUB/GPU/disk/persistence/clock/PATH)
- `Module-T00-Troubleshooter-Index.md` — ACTIVE entry/router (symptom + paste-error → T01–T05)

## Decisions locked
- Kali only; Parrot parked (sandbox/MAC complexity) but re-addable via OS-profile model.
- Generate-only; login + on-device audit log for accountability.
- Module/theme system so it ships small and grows by add-ons.
- Design = W1CK3D SYSTEMS brand (group, not project); tokens captured; status colors double
  as category + stepper states.
- **Free build = fully self-contained, NO AI.** Help = authored flows + glossary + the
  Unresolved Issue Log + curated trusted external links. No live assistant/service/teacher.
- **AI (local LLM / paid portal) deferred to a future Enterprise/retail edition.**
- **Distribution = GitHub, BUILT TOOL FILE ONLY.** Source code + these blueprints stay
  private/closed (preserves the paid Enterprise option). Blueprints are internal assets.

## Next session — start here
1. Pick the **next complete tool module** (authored to the nmap template in
   `Module-02-nmap.md`) — e.g. gobuster, sqlmap, hydra, or gvm.
2. **Troubleshooter** COMPLETE: T00 router + T01–T05.
3. **CLI Top 10 tool modules** (one at a time, nmap template):
   DONE: nmap (M02), sqlmap (M03), hydra (M04), john (M05), hashcat (M06), aircrack-ng (M07),
   metasploit (M08), wireshark/tshark (M09), gobuster (M10), nikto (M11).
   ✅ CLI Top 10 COMPLETE. ✅ PHASE ONE COMPLETE — see `Phase-One-Summary.md`.

## Phase Two (next)
   1. Build/packaging handoff to developer (PySide6 + PyInstaller).
   2. Content ingestion pipeline (curated KB).
   3. More tools (ffuf/wpscan/netexec/gvm…), more lessons, more troubleshooters.
   4. Termux edition; logo→SVG; (later) Enterprise AI edition.
3. Optionally: vectorize the logo to true SVG for crisp scaling.

## Core principle (locked)
**Simple to use, complete in depth** — easy on-ramp (profiles + a couple prompts) AND
complete coverage (every flag/option explained). Every module is held to both.

## Outstanding (bring when convenient — not blocking)
- **True SVG logo** — current asset is a high-res PNG (works fine; SVG only needed for
  razor-crisp scaling/print).
- Confirm fonts (Google Fonts substitutes ok to bundle?).
- Optional: layout mockups/screens so component placement matches the design.
