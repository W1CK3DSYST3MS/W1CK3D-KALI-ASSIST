# Module 00 (Kali edition) — First Setup & Securing

**Type:** Lesson module · **os_profile: kali** · **Status:** spec v1
**Companion to:** Blueprint v1.2 (§15) · routed by Module 00 parent
**Last updated:** 2026-06-21

> The "day one" guide **for Kali Linux only**. Distro-correct setup and securing flow.
> Generate-only: the app shows/explains each command; the learner runs it in their own
> terminal and reports "did it work?" The adaptive stepper branches on the answer.

---

## 1. Manifest

```yaml
module_id: fundamentals.setup_and_securing.kali
name: "First Setup & Securing — Kali"
version: 1.0.0
type: lesson
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar] }
provides: { lessons: [lesson.setup_and_securing.kali] }
source: "authored; verifiable against man pages + kali.org/docs"
license: "project-proprietary"
```

## 2. LessonSpec

```yaml
lesson_id: lesson.setup_and_securing.kali
title: "First Setup & Securing (Kali)"
os_profile: kali
audience: beginner
goal: "Take a fresh Kali system from default to set-up-and-secured."
steps: [s1, s2, s3, s4, s5, s6, s7, s8, s9]
safety_note: "Apply only to systems you own or are authorized to administer."
```

## 3. Steps (Kali-correct)

### s1 — Confirm you're on Kali
- **try_this:** `cat /etc/os-release`
- **expected:** output names **Kali GNU/Linux** (rolling).
- **success:** "Kali" appears. **No →** if it says Parrot/other, **stop — use that
  distro's edition.** (The router should have handled this.)

### s2 — Update (Kali rolling)
- **concept:** "Kali is a rolling release on Debian *testing* — update often. The
  correct sequence is refresh-then-upgrade with `full-upgrade` (handles dependency
  changes that plain `upgrade` won't)."
- **try_this:** `sudo apt update` then `sudo apt full-upgrade`
- **expected:** lists refresh, then packages upgrade (confirm `y`).
- **success:** completes, returns to prompt; reboot if a kernel updated.
- **No → alternatives:**
  - *`NO_PUBKEY` / signature error* → "Refresh Kali's signing keys:
    `sudo apt install kali-archive-keyring`, then retry. (This is the canonical Kali
    fix and will become its own helpdesk flow.)"
  - *`Could not get lock`* → "Another apt process is running; wait/close it, retry."
  - *network/DNS* → "Confirm connectivity, then retry (networking module covers this)."

### s3 — Set a strong password
- **concept:** "Kali's default `kali`/`kali` credentials are public — change yours now."
- **try_this:** `passwd`
- **expected:** prompts old then new (twice); no echo is normal.
- **success:** `password updated successfully`.

### s4 — Use `sudo`, don't live as root
- **concept:** "Kali's default `kali` user is **non-root** and already in the `sudo`
  group. Work as that user; escalate with `sudo` only when a task needs it."
- **try_this:** `id` then `sudo whoami`
- **expected:** `id` shows your user/groups (incl. `sudo`); `sudo whoami` → `root`.
- **success:** `sudo whoami` returns `root`.
- **No →** *`not in the sudoers file`* → "Rare on Kali defaults; needs adding the user
  to `sudo` as root — flag for a dedicated flow."

### s5 — Turn on the firewall
- **concept:** "`ufw` = beginner-friendly firewall. Default deny incoming."
- **try_this:** `sudo apt install ufw` → `sudo ufw default deny incoming` →
  `sudo ufw default allow outgoing` → `sudo ufw enable` → `sudo ufw status verbose`
- **success:** `Status: active`.
- **No →** *on a remote SSH session* → "Allow SSH first: `sudo ufw allow 22/tcp`, then
  enable, or you'll lock yourself out."

### s6 — See & reduce attack surface
- **try_this:** `ss -tulpn` then `systemctl list-units --type=service --state=running`
- **success:** lists print (empty 'listening' is good).
- **note:** "Unused SSH? `sudo systemctl disable --now ssh` (disable so it stays off
  after reboot)."
- **No →** *unsure what to disable* → "Leave unknowns; ask the Helpdesk Assistant."

### s7 — Privacy basics (Kali: add-ons)
- **concept:** "On Kali these aren't preinstalled — add them if you want them."
- **try_this:** `sudo apt install macchanger` then `macchanger --help` (reversible; for
  authorized testing). Tor can be added via `sudo apt install tor`.
- **success:** the tool's help prints.
- **No →** skip; optional, revisit in a privacy module.

### s8 — Backups / persistence
- **try_this:** `df -h` then `ls -la ~`
- **note:** "Running Kali from a **live USB**? Changes vanish on reboot unless you set up
  **persistence** (its own guided flow). Installed to disk? Back up `~` and `/etc`."

### s9 — Verify
- **try_this:** `sudo ufw status` · `sudo apt update` · `ss -tulpn`
- **success:** firewall active; lists current; only intended ports listening.

## 4. Next
Module 01 (Shell Grammar) · Helpdesk "apt keyring errors" · Networking module ·
First tool module (nmap basic).

*End of Kali edition v1.*
