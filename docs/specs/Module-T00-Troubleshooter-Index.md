# Module T00 — Troubleshooter Index / Router

**Project:** W1CK3D'S KALI ASSIST · **Type:** Troubleshooter router (entry point)
**Status:** spec v1 · **Companion to:** `Troubleshooter-Subsystem.md`, T01–T05, Blueprint v1.8
**Last updated:** 2026-06-22

> The **single front door** to the whole troubleshooter. The user arrives here, describes
> or picks what's wrong, and T00 routes them to the exact module + flow (T01–T05) — no AI,
> just deterministic matching against a curated symptom/error index. It also owns the
> **session-wide Issue Log** so a problem that crosses modules produces one clean record.
> **Generate-only, self-contained.**

---

## 1. Manifest

```yaml
module_id: troubleshoot.index
name: "Troubleshooter — Start Here"
version: 1.0.0
type: troubleshooter_router
os_profile: kali
requires: { base_api: ">=1.0" }
routes_to: [troubleshoot.networking, troubleshoot.packages, troubleshoot.services,
            troubleshoot.permissions, troubleshoot.rare_hard]
provides:
  entry: troubleshoot.start
  index: registry/troubleshoot/index.yaml          # auto-aggregated symptom catalog
content:
  index: registry/troubleshoot/index.yaml
  error_map: registry/troubleshoot/error_signatures.yaml
  resources: registry/resources/global_links.yaml
theme: theme.w1ck3d_systems
source: "authored; index auto-built from each module's declared symptoms + aliases"
license: "project-proprietary"
```

---

## 2. How it works

```
   START HERE
      │  three ways in (pick whichever suits the user)
      ├── A) Browse by symptom      → curated plain-language list
      ├── B) Search / paste error   → keyword + error-signature match (no AI)
      └── C) Browse by category     → Networking / Packages / Services / Permissions / Hard
      ▼
   MATCH → resolves to a module + flow (e.g. troubleshoot.packages §4 "NO_PUBKEY")
      ▼
   (hand off to that flow's triage → diagnosis → fix, per T01–T05)
      ▼
   if exhausted anywhere → session-wide Unresolved Issue Log + global links (§7/§8)
```

No model is required: entry B works by matching the user's words / pasted error text against
a **curated keyword + error-signature index** (deterministic, offline).

---

## 3. Universal triage (asked once, shared by all modules)

Captured here so the user answers once even if routed across modules:
- What were you trying to do, and what's the **exact error** (paste it if you have it)?
- Installed-to-disk or **live USB**?
- Did it start after an **update**, a **config/driver change**, a **reboot**, or **power loss**?
- Can you reach a normal desktop/terminal, only a text console (TTY), or nothing?

These answers pre-seed whichever flow you land in (and the Issue Log).

---

## 4. Master symptom index (browse — entry A)

Plain-language symptom → module → section. (This table is the human-readable view of the
auto-aggregated `index.yaml`.)

| If the user says… | Route to | Flow |
|-------------------|----------|------|
| "No internet at all" | T01 Networking | S1 |
| "Sites won't load by name / DNS" | T01 | S2 |
| "Wi-Fi won't connect / no networks" | T01 | S3 |
| "Adapter/interface not showing up" | T01 | S4 |
| "Monitor mode won't work" | T01 | S5 |
| "Connection slow / keeps dropping" | T01 | S6 |
| "apt update/upgrade errors" | T02 Packages | S1 |
| "NO_PUBKEY / signature / not signed" | T02 | S2 |
| "Broken / held dependencies" | T02 | S3 |
| "Could not get lock / dpkg interrupted" | T02 | S4 |
| "Install a tool / add a repo safely" | T02 | S5 |
| "Certificate / TLS verify failed" | T02 | S6 |
| "Install from a git repo" | T02 | S7 |
| "A service won't start / failed" | T03 Services | S1 |
| "Not running after reboot" | T03 | S2 |
| "How do I see why it failed (logs)" | T03 | S3 |
| "Port already in use" | T03 | S4 |
| "Masked / dependency failed" | T03 | S5 |
| "Edited a unit, nothing changed" | T03 | S6 |
| "PostgreSQL / GVM / SSH specifically" | T03 | S7 |
| "Permission denied" | T04 Permissions | S1 |
| "sudo / not in sudoers" | T04 | S2 |
| "Can't edit a file that's mine (ownership)" | T04 | S3 |
| "USB/drive won't mount" | T04 | S4 |
| "Where did my file go / find it" | T04 | S5 |
| "Script/binary won't run" | T04 | S6 |
| "Weird permission bits / can't change a file" | T04 | S7 |
| "Read-only filesystem" | T04 | S8 |
| "Won't boot / GRUB / hangs at boot" | T05 Hard | S1 |
| "No desktop / login loop / black screen" | T05 | S2 |
| "Display/GPU/resolution/NVIDIA" | T05 | S3 |
| "Disk full / no space" | T05 | S4 |
| "Live-USB persistence not saving" | T05 | S5 |
| "Errors after a time/date change" | T05 | S6 |
| "Locale/keyboard wrong / installed tool not found" | T05 | S7 |

---

## 5. Paste-the-error quick match (entry B)

Deterministic routing from common **error-string fragments** (the user pastes their error;
the index matches a fragment). Stored in `error_signatures.yaml`.

| Error fragment (contains…) | Route |
|----------------------------|-------|
| `NO_PUBKEY` · `not signed` · `signature ... invalid` | T02 §2 (keys) — also check clock T05 §6 |
| `Could not get lock` · `dpkg was interrupted` | T02 §4 |
| `Unable to locate package` | T02 §5 |
| `Could not resolve` · `Temporary failure in name resolution` | T01 §2 (DNS) |
| `Failed to fetch` · `Connection timed out` | T01 §1 then T02 §1 |
| `certificate verify failed` · `server certificate verification` | T02 §6 → if odd date, T05 §6 |
| `externally-managed-environment` | T02 §7 (pip/pipx) |
| `Permission denied` | T04 §1 |
| `is not in the sudoers file` | T04 §2 |
| `Operation not permitted` (changing a file as root) | T04 §7 (immutable) |
| `Read-only file system` | T04 §8 → T05 §1 if at boot |
| `command not found` (for an installed tool) | T05 §7 (PATH) / T04 §6 |
| `No space left on device` | T05 §4 |
| `Job for X.service failed` · `Failed to start` | T03 §1 |
| `Unit X is masked` | T03 §5 |
| `Address already in use` | T03 §4 |
| `Dependency failed for` | T03 §5 |
| `failed to load firmware` · `direct firmware load failed` | T01 §4 (→ T05 if at boot) |
| `bad interpreter` | T04 §6 (often CRLF) |
| `emergency mode` · `grub rescue` | T05 §1 |

> Matching is substring/keyword based and case-insensitive — fully offline, no AI. Multiple
> matches show the most likely first with the alternates listed.

---

## 6. Cross-module chains (the router knows these)

Some problems span modules; T00 sequences them so the user isn't bounced around:
- **Clock skew → apt/cert:** fix time (T05 §6) **then** retry apt/cert (T02 §1/§6).
- **Bad fstab → boot:** an fstab edit (T04 §7) can cause emergency mode (T05 §1).
- **Port in use ↔ firewall:** service port (T03 §4) relates to firewall rules (T01 / Module 00).
- **Network down → apt fetch fails:** "Failed to fetch" is usually T01, not T02.
- **Disk full → no GUI:** login loop (T05 §2) is often disk full (T05 §4).

---

## 7. "Not sure where to start" fallback

If the user can't categorize it, T00 offers the **broad category browse** (entry C) and a
2-question narrowing: *what were you doing* + *what changed* → suggests the 1–2 most likely
modules. Worst case it starts the universal first-look (`ip a` / `systemctl status` /
`df -h` / `ls -l` depending on the rough area) and routes on the result.

---

## 8. Session-wide Unresolved Issue Log (owned here)

Because a session can cross modules, T00 owns the **aggregated Issue Log**:
- the universal triage answers (collected once);
- every module/flow visited, with the commands shown and the user's reported outputs/errors;
- environment snapshot (Kali version, kernel, install vs live);
- timestamps; **no secrets** (passwords, tokens, keys, sensitive paths excluded/redacted).

One copyable record for the whole problem, ready to paste into a search or forum post.

**Global curated links** (shown with the log; user searches themselves):
- Kali docs (kali.org/docs) · forums (forums.kali.org) · bug tracker (bugs.kali.org)
- Debian wiki (wiki.debian.org) · Arch Wiki (wiki.archlinux.org)
- Unix & Linux Stack Exchange (unix.stackexchange.com)
- The specific tool's official docs / GitHub issues
- On-system: `man <command>` and `<command> --help`

---

## 9. Auto-registration (how the index stays complete)

The index is **data, not hardcoded**: each troubleshooter module declares its `symptoms`
(label + aliases + error fragments) in its manifest. A build step aggregates those into
`index.yaml` + `error_signatures.yaml`. **Adding a new troubleshooter module automatically
adds its symptoms to T00** — no edits to the router. (Same growth model as the rest of the
system, Blueprint §11.4.)

```yaml
# each module contributes entries like:
- symptom_id: pubkey_signature
  module: troubleshoot.packages
  flow: S2
  label: "NO_PUBKEY / signature / not signed"
  aliases: ["public key", "not signed", "GPG error", "keyring"]
  error_fragments: ["NO_PUBKEY", "not signed", "is not signed"]
```

---

## 10. Design, generate-only, audit

- **Tokens:** the Start-Here screen uses the brand neutral surfaces; category chips tinted by
  `--status-*`; search box prominent; matched results in cards with the routing reason.
- **Generate-only:** T00 only routes and assembles the Issue Log — it runs nothing.
- **Audit (no secrets):** entry mode used, symptom matched, module(s) visited, resolved?
- **Consistency:** every destination flow keeps its own guardrails (T01–T05); T00 adds none
  of its own risk.

---

## 11. Why this is the capstone

T00 turns five strong-but-separate modules into one coherent experience: the user just says
what's wrong (or pastes the error) and lands in the right place, with one Issue Log across
the whole journey. It's deterministic and offline (fits the no-AI free build), and it
auto-grows as new troubleshooter modules are added — so the troubleshooter can expand
toward "extensive" without ever reworking the front door.

*End of Module T00 (Troubleshooter Index/Router) spec v1.*
