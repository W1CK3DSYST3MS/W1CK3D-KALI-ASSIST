# W1CK3D'S KALI ASSIST — Phase One Summary & Master Index

**Project:** W1CK3D'S KALI ASSIST — a **W1CK3D SYSTEMS** project
**What it is:** a standalone, **Kali-only**, **generate-only** interactive learning,
reference, and self-help troubleshooting tool for Linux + security CLI tools.
**Phase One status: COMPLETE (design/spec).** **Date:** 2026-06-22

> Phase One delivered the full design foundation and the spec content for a releasable v1:
> the architecture, the brand design system, the onboarding/lessons, the complete
> self-help troubleshooter subsystem, and the CLI-focused Top 10 tool modules. Everything
> here is **internal design/spec** — per the distribution decision, only the *built tool
> file* ships (via GitHub); source + these specs stay private.

---

## 1. The product in one paragraph

A desktop (and later Termux) app that teaches the correct use of Kali tools and the OS
itself using a consistent **slot model** (every command taught as ordered slots) and an
**adaptive "did it work? Yes/No" stepper**. It never executes anything — it shows and
explains commands the user runs in their own terminal. It's **simple to use, complete in
depth** (profiles for beginners; every flag explained underneath), **modular** (ships small,
grows via add-on modules), **self-contained** (no AI/service in the free build), and gated by
a **login + on-device audit log** for accountability.

---

## 2. Master index of Phase One deliverables (all in this folder)

### Foundation / design
- `Tool-Wizard-Blueprint.md` (v1.8) — master architecture & decisions
- `Coverage-and-Data-Sources.md` — what to cover + where to source content
- `Design-System-Tokens.md` — W1CK3D SYSTEMS brand tokens (dark cyber/terminal)
- `assets/W1CK3D-SYSTEMS-logo.png` — logo asset (PNG 1254×1254; SVG TODO)

### Lessons (fundamentals & onboarding)
- `Module-00-Setup-and-Securing.md` — router (Kali-only)
- `Module-00-Kali-Setup-and-Securing.md` — ACTIVE first-run setup & securing
- `Module-00-Parrot-Setup-and-Securing.md` — PARKED (field notes for future Parrot)
- `Module-01-Shell-Grammar.md` — teaches the slot model + core glossary

### Troubleshooter subsystem (the "biggest part")
- `Troubleshooter-Subsystem.md` — architecture, tiers, Issue-Log model
- `Module-T00-Troubleshooter-Index.md` — symptom/error router (entry point)
- `Module-T01-Networking-Troubleshooter.md` — networking / DNS / Wi-Fi
- `Module-T02-Packages-Keys-Certs-Troubleshooter.md` — apt / keys / certs / git installs
- `Module-T03-Services-Systemd-Troubleshooter.md` — systemctl / journalctl / GVM / SSH
- `Module-T04-Permissions-Filesystem-Troubleshooter.md` — perms / sudo / mount / find
- `Module-T05-Rare-Hard-Cases-Troubleshooter.md` — boot / GPU / disk / persistence / clock

### Tool modules — CLI-focused Top 10 (all to the nmap template)
- `Module-02-nmap.md` — network scanning (template-defining)
- `Module-03-sqlmap.md` — SQL injection
- `Module-04-hydra.md` — online login brute-force
- `Module-05-john.md` — offline hash cracking (CPU)
- `Module-06-hashcat.md` — offline hash cracking (GPU)
- `Module-07-aircrack-ng.md` — Wi-Fi suite (workflow)
- `Module-08-metasploit.md` — exploitation framework (most complete)
- `Module-09-wireshark-tshark.md` — traffic capture/analysis
- `Module-10-gobuster.md` — content/DNS/vhost brute-force
- `Module-11-nikto.md` — web server vuln scanner

### Working notes
- `_START-HERE-next-session.md` — quick pick-up notes

---

## 3. Locked decisions (the spine of the project)

- **Kali only.** Parrot parked (sandbox/MAC complexity); re-addable via the OS-profile model.
- **Generate-only.** Never executes; teaches commands to run in the user's own terminal.
- **Slot model + adaptive stepper.** One grammar everywhere; verify-and-branch interaction.
- **Simple to use, complete in depth.** Profiles + a couple prompts on top; every flag below.
- **Modular.** Base ships small; tools/lessons/troubleshooters/themes are add-on modules
  (auto-registering, e.g., the troubleshooter index).
- **Self-contained free build — NO AI.** Help = authored flows + glossary + the Unresolved
  Issue Log + curated trusted links. No live assistant/service/teacher.
- **Editions:** Free Standalone (no AI) now; **Enterprise/retail** (local-LLM / paid AI)
  later.
- **Distribution:** GitHub, **built tool file only**; source + blueprints private/closed.
- **Accountability:** login + disclaimer + on-device audit log (no secrets logged).
- **Brand:** W1CK3D SYSTEMS (the group/org) design system applied to the project.

---

## 4. Recurring quality patterns (held across all modules)

- **Authorization gates** on offensive tools (sqlmap/hydra/metasploit/aircrack), **double-
  gated** for the most dangerous (Wi-Fi deauth).
- **Destructive-action guardrails** (red callouts + safe alternative + how-to-recover) on
  risky steps (chmod 777, fstab, GRUB/chroot, removing apt locks, airmon check-kill).
- **Honest caveats** instead of hype (encoders aren't AV evasion; nikto is noisy & signature-
  based; gobuster's version-specific status-code behavior; PMKID/handshake realities).
- **Cross-links** so the toolkit is one system (nmap→gobuster→nikto; hydra↔john↔hashcat;
  aircrack→hashcat; metasploit↔nmap/postgres/john; troubleshooter chains).

---

## 5. Phase Two roadmap (proposed)

1. **Build/packaging handoff** — hand the specs + design tokens + logo to the developer
   (Claude Code or other) to build the desktop executable (PySide6 + PyInstaller).
2. **Content ingestion pipeline** — implement the curated KB ingest (tldr/SecLists/man/Kali
   docs) per the Coverage doc, with provenance + license fields.
3. **More tool modules** — beyond the Top 10 (e.g., ffuf, wpscan, netexec, enum4linux,
   responder, gvm) to the same template.
4. **More lessons** — the remaining OS fundamentals (files/permissions, pipes/redirection,
   networking, services) and Kali-quirk lessons.
5. **More troubleshooter modules** — extend the index as new symptom areas are added.
6. **Termux edition** — same core, TUI front-end, curated-only.
7. **Logo → true SVG**, font licensing confirmation, and layout mockups → finalize the theme.
8. **(Later) Enterprise edition** — AI layer grounded in the curated KB.

---

## 6. Outstanding items (carried from Phase One)

- True **SVG logo** (current asset is high-res PNG — fine, SVG only for crisp scaling/print).
- Confirm **font licensing/bundling** (Google Fonts substitutes).
- **Layout mockups/screens** so component placement matches the W1CK3D design.
- Periodic **accuracy re-verification** of fast-moving specifics (apt keyring/`signed-by`,
  PEP 668, gobuster status-code defaults, GVM setup).

---

*Phase One complete. This index is the entry point to the W1CK3D'S KALI ASSIST design set.*
