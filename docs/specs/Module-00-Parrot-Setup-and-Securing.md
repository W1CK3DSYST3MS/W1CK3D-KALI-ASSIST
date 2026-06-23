# Module 00 (Parrot edition) — First Setup & Securing  ⛔ PARKED

**Type:** Lesson module · **os_profile: parrot** · **Status:** PARKED / DEFERRED
**Companion to:** Blueprint v1.3 (§15) · routed by Module 00 parent
**Last updated:** 2026-06-21

> ⛔ **PARKED — not part of the current Kali-only build.** The product now targets Kali
> Linux as a standalone tool. Parrot is deferred because its security model needs
> dedicated testing to teach safely. This file is kept as a **head start** for whoever
> revives Parrot later. Do not ship as-is.

---

## 0. Field notes (why Parrot is hard — from real usage, to verify later)

Observations to investigate before building the Parrot edition for real:

- **Paths locked even to root.** Some filesystem locations are inaccessible *even as the
  root user* because they're governed by Parrot's security/opsec layer (firejail
  sandboxing + AppArmor mandatory access control) — not ordinary Unix permissions. Normal
  "become root and you can do anything" assumptions do **not** hold.
- **Elevated-write vs. user-read mismatch.** Because the terminal/tool may run at an
  elevated/sandboxed context, a tool can **write its report into a path that is then
  access-denied to the normal user** — the file gets created where the user can't read
  it. This breaks tool output/report flows and is confusing to diagnose.
- **Assumed-privileged but password-gated.** The user is treated as a privileged
  operator, yet **basic CLI system functions and tools still prompt for a password** to
  run. The privilege/elevation UX differs meaningfully from Kali.

Implication: a safe Parrot edition must teach the sandbox/MAC model first (where files
*actually* go, why root isn't absolute, how to choose writable output paths) — otherwise
the standard setup/securing steps will mislead users. Verify all of the above against
current Parrot docs + hands-on testing before un-parking.

---

> The "day one" guide **for Parrot OS only**. Distro-correct setup and securing flow —
> note the update path and privilege/filesystem handling differ from Kali. Generate-only:
> the app shows/explains; the learner runs commands in their own terminal and reports
> "did it work?"; the adaptive stepper branches on the answer.
>
> ⚠ Two steps below carry **"confirm per install"** flags (privilege model, filesystem
> sandboxing) pending the open items in blueprint §16 — these are the areas where Parrot
> specifics must be verified before this edition is finalized.

---

## 1. Manifest

```yaml
module_id: fundamentals.setup_and_securing.parrot
name: "First Setup & Securing — Parrot"
version: 1.0.0
type: lesson
os_profile: parrot
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar] }
provides: { lessons: [lesson.setup_and_securing.parrot] }
source: "authored; verifiable against parrotsec.org/docs + man pages"
license: "project-proprietary"
```

## 2. LessonSpec

```yaml
lesson_id: lesson.setup_and_securing.parrot
title: "First Setup & Securing (Parrot)"
os_profile: parrot
audience: beginner
goal: "Take a fresh Parrot system from default to set-up-and-secured, the Parrot way."
steps: [s1, s2, s3, s4, s5, s6, s7, s8, s9]
safety_note: "Apply only to systems you own or are authorized to administer."
```

## 3. Steps (Parrot-correct)

### s1 — Confirm you're on Parrot
- **try_this:** `cat /etc/os-release`
- **expected:** output names **Parrot OS / Parrot Security**.
- **success:** "Parrot" appears. **No →** if it says Kali/other, **stop — use that
  distro's edition.**

### s2 — Update (the Parrot way: `parrot-upgrade`)
- **concept:** "**Do not** treat Parrot like generic Debian. Parrot's packages come from
  **its own curated mirrors**, configured in `/etc/apt/sources.list.d/parrot.list`. The
  **recommended** update path is the `parrot-upgrade` wrapper, which runs the correct
  apt steps with the right parameters so dependencies are handled properly."
- **try_this:** `sudo parrot-upgrade`
- **expected:** the wrapper refreshes and upgrades the system in the Parrot-approved
  sequence (confirm prompts as asked).
- **success:** completes, returns to prompt; reboot if a kernel updated.
- **important — do NOT:** add or modify repositories. "In Parrot it is neither necessary
  nor recommended to add new repos or edit `parrot.list` — doing so can break the
  curated upgrade path."
- **No → alternatives:**
  - *`parrot-upgrade: command not found`* → "On some installs the wrapper may be named
    differently or missing; the fallback is `sudo apt update && sudo apt full-upgrade`
    **without touching repos** — but prefer `parrot-upgrade` where present. (Confirm on
    your edition.)"
  - *signature/mirror error* → "A mirror/key issue — retry shortly; do **not** fix it by
    adding third-party repos. (Becomes a Parrot-specific helpdesk flow.)"
  - *`Could not get lock`* → "Another apt process is running; wait/close it, retry."

### s3 — Set a strong password
- **try_this:** `passwd`
- **expected:** prompts old then new (twice); no echo is normal.
- **success:** `password updated successfully`.

### s4 — Elevated commands on Parrot  ⚠ confirm per install
- **concept:** "Parrot uses a normal user with `sudo` for admin tasks, but Parrot's
  **elevated-command handling differs from Kali** and can vary by edition. Use `sudo`
  for admin actions; consult Parrot docs for your edition's specifics rather than
  assuming Kali's behavior."
- **try_this:** `id` then `sudo whoami`
- **expected:** `id` shows your user/groups; `sudo whoami` → `root`.
- **success:** `sudo whoami` returns `root`.
- **No →** *unexpected prompt/behavior* → "Parrot's privilege setup may differ on your
  install — check Parrot documentation; flagged in blueprint §16 to finalize."

### s5 — Turn on the firewall
- **concept:** "`ufw` provides a simple firewall front end on Parrot too. Default deny
  incoming."
- **try_this:** `sudo ufw default deny incoming` → `sudo ufw default allow outgoing` →
  `sudo ufw enable` → `sudo ufw status verbose`
  *(install first with `sudo apt install ufw` only if not already present)*
- **success:** `Status: active`.
- **No →** *on a remote SSH session* → "Allow SSH first (`sudo ufw allow 22/tcp`) before
  enabling, or you'll lock yourself out."

### s6 — See & reduce attack surface
- **try_this:** `ss -tulpn` then `systemctl list-units --type=service --state=running`
- **success:** lists print (empty 'listening' is good).
- **note:** "Unused SSH? `sudo systemctl disable --now ssh`."
- **No →** *unsure what to disable* → "Leave unknowns; ask the Helpdesk Assistant."

### s7 — Privacy basics (Parrot: built-in)  — a Parrot strength
- **concept:** "Parrot **ships AnonSurf and firejail by default** — a major difference
  from Kali. AnonSurf forces traffic through Tor; firejail sandboxes applications."
- **try_this:** `sudo anonsurf status`  *(start/stop: `sudo anonsurf start` /
  `sudo anonsurf stop`)*
- **expected:** AnonSurf reports its current status.
- **success:** status prints.
- **note:** "Use AnonSurf only on networks you're authorized to. firejail is already
  sandboxing many apps — relevant to the filesystem/root behavior in s8."
- **No →** *not present on your edition* → "Some editions vary; confirm via Parrot docs."

### s8 — Filesystem, sandboxing, backups  ⚠ confirm specifics
- **concept:** "Parrot applies **firejail sandboxing + AppArmor** by default, which
  changes how some processes access the filesystem and root areas compared to a plain
  Debian/Kali system. Know this before troubleshooting 'permission'/access oddities —
  the cause may be a sandbox profile, not a normal permission."
- **try_this:** `df -h` then `ls -la ~`
- **success:** both print.
- **note:** "Back up `~` and `/etc`. (Exact firejail/AppArmor effects on common tasks
  are flagged in blueprint §16 to verify and expand.)"

### s9 — Verify (Parrot)
- **try_this:** `sudo ufw status` · `sudo parrot-upgrade` (re-check) · `ss -tulpn`
- **success:** firewall active; system current via the Parrot path; only intended ports
  listening.

## 4. Next
Module 01 (Shell Grammar) · Helpdesk "Parrot mirror/upgrade issues" · Privacy module
(AnonSurf/firejail in depth) · First tool module (nmap basic).

*End of Parrot edition v1.*
