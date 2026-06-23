# Kali Troubleshooter — Subsystem Design & Coverage Map

**Project:** W1CK3D'S KALI ASSIST · **Type:** Subsystem spec (the largest part)
**Companion to:** Blueprint v1.6 (§4 stepper, §7 helpdesk), Coverage Map, Design Tokens
**Last updated:** 2026-06-22

> The interactive, **symptom-first** assisted troubleshooter — a **fully self-contained,
> self-paced self-help tool**. All help comes from its own authored flows: there is **no
> live assistant, no behind-the-scenes service, and no teacher.** It reuses the adaptive
> verify-and-branch stepper as its diagnostic engine and is authored at three depths
> (**Basic → Intermediate → Extensive**) so it's simple to start and complete to finish.
> **Generate-only:** it never runs anything — it shows diagnostic/fix commands, the user
> runs them in their own terminal and reports what they saw, and the wizard branches on
> that. The internal flows should resolve the **majority** of issues; when a genuinely
> novel problem exhausts the known steps, the tool produces an **Unresolved Issue Log**
> (§6B) so the user can search effectively themselves. Every problem area below becomes
> one or more modules over time.

---

## 1. The assisted template (how every troubleshooter flow works)

```
 ENTRY (symptom-first)
   "Pick or describe what's wrong"  → e.g. "No internet"
        │
        ▼
 TRIAGE  (1–3 quick questions to localize)
   "Wired or Wi-Fi?"  "All sites or one?"  "What changed recently?"
        │
        ▼
 GUIDED DIAGNOSIS  (the adaptive stepper)
   Step: run ONE diagnostic command in your terminal
   "Run this →  ip a"      [show + explain what to look for]
   "What did you see?"  → branch on the answer
        │  (each answer narrows the cause)
        ▼
 VERIFIED FIX
   "Here's the fix →  sudo systemctl restart NetworkManager"
   "Did it work?  [Yes] / [No]"
        │Yes → resolved (+ offer the matching lesson to learn why)
        │No  → next candidate fix, or ↓
        ▼
 EXHAUSTED ALL KNOWN STEPS?  (§6B — no live assistance)
   generate an Unresolved Issue Log (steps tried + actual error output) to copy,
   + point to trustworthy external places to keep searching themselves
```

Principles carried in: **symptom-first** (no jargon required to start), **one step at a
time** (so an error is caught where it happens), **explain every command** (self-help,
learn-as-you-go), **always verify** before moving on, and **self-contained** (the tool's
own flows do the work — no external service or assistant).

---

## 2. Depth tiers (basic → extensive)

Every problem area is authored at three tiers; the user can stop as soon as it's solved.

| Tier | What it covers | Example (networking) |
|------|----------------|----------------------|
| **Basic** | the common quick fixes most issues need | restart NetworkManager; `rfkill unblock wifi` |
| **Intermediate** | multi-step diagnosis isolating the real cause | DNS-vs-routing isolation; edit resolv.conf; static IP |
| **Extensive** | deep decision trees, logs, edge cases, rare faults | Wi-Fi chipset driver/firmware, regulatory domain, captive portals, VPN/monitor-mode conflicts |

The wizard starts at Basic and offers "still not fixed? go deeper →" to climb tiers.

---

## 3. Data model (extends the existing stepper)

```yaml
TroubleshooterFlowSpec:
  flow_id, title
  symptom: { label, aliases[], category }        # for symptom-first matching / search
  os_profile: kali
  triage[]:                                       # quick localizing questions
    - { question, options[], routes_to }
  diagnosis[]:                                     # StepSpec items (the stepper)
    - step_id
      instruction                                 # the diagnostic command to RUN
      explain { what, why, what_to_look_for }
      observe: [ choices the user reports ]        # e.g. "got an IP" / "no IP"
      branch: { <observation>: <next step_id | fix_id> }
  fixes[]:
    - fix_id
      command(s)                                  # the fix to show (never executed)
      explain { what, why }
      verify: success_criteria                    # "did it work?" check
      on_fail: <next fix_id | escalate>
  tier: basic | intermediate | extensive
  on_exhausted:                                   # NO live assistant — self-directed
    generate_issue_log: true                      # steps tried + error output (see §6B)
    external_resources: [ curated trustworthy links ]
    related_reference: <module_id>                # self-paced in-app guide, not a "lesson/teacher"
  audit: log [symptom, tier reached, fix applied?, resolved?]   # no secrets
```

This is the same `StepSpec`/adaptive engine from the blueprint — a troubleshooter flow is
just a stepper with a symptom + triage front-end, a fixes list, and a self-directed
exhaustion handoff (no external service).

---

## 4. Coverage map (what to build, basic → extensive)

### 4.1 Core problem areas (all four prioritized)

**A. Networking, DNS & Wi-Fi**
- Symptoms: no internet; DNS fails; interface down; Wi-Fi won't connect; slow.
- Diagnostic ladder: `ip a` (IP?) → `ping 1.1.1.1` (routing/link?) → `ping google.com`
  (DNS?) → `nmcli device status` / `systemctl status NetworkManager` → `rfkill list`.
- Extensive: chipset driver/firmware, `iw reg`, MAC randomization, captive portals,
  VPN/monitor-mode conflicts, systemd-resolved vs `/etc/resolv.conf`.

**B. Packages & apt**
- Symptoms: `apt update`/`full-upgrade` errors; `NO_PUBKEY`; broken/held dependencies;
  "could not get lock"; tool not in default metapackage.
- Ladder: read the exact error → keyring (`kali-archive-keyring`) → locks
  (`/var/lib/dpkg/lock`) → `apt --fix-broken install` → `dpkg --configure -a`.
- Extensive: partial-upgrade breakage on rolling, pinning, third-party repo conflicts
  (ties to 4.2).

**C. Services & systemd**
- Symptoms: a service won't start / shows `failed`; needed service not enabled
  (PostgreSQL for Metasploit/GVM, ssh).
- Ladder: `systemctl status <svc>` → `journalctl -u <svc> -e` (read the error) →
  `systemctl enable --now <svc>` → check port/conflict (`ss -tulpn`).
- Extensive: dependency ordering, failed unit masking, socket activation, log forensics.

**D. Permissions, sudo & filesystem**
- Symptoms: permission denied; "not in sudoers"; can't write/mount; "where did my file
  go?"; SUID confusion.
- Ladder: `ls -l` (who owns it?) → `id` (am I in the group?) → `chmod`/`chown` (correct
  fix) → mounting (`lsblk`, `mount`, `/etc/fstab`).
- Extensive: ACLs, immutable bits (`chattr`), bind mounts, ownership across USB/NTFS.

### 4.2 Integral Kali functions (requested — keys, certs, authority, installs)

**E. Installing tools from a git repo (clone + build)**
- Flow: `git clone <url>` → read its README → install dependencies → build/run
  (`make`, `pip install .` / `pipx install`, `go build`) → where the binary lands / PATH.
- Branches: missing deps; Python "externally-managed-environment" (use `pipx`/venv);
  build errors; permission/location of the resulting binary.

**F. Repository trust — GPG keys & signed sources (modern apt model)**
- Concept: apt **requires signed repos**; `apt-key` is **deprecated**. Keys go in
  `/etc/apt/keyrings/`, referenced per-source with `signed-by=`.
- Flow (show, don't run): fetch key → `gpg --dearmor -o /etc/apt/keyrings/<name>.gpg` →
  add source `deb [signed-by=/etc/apt/keyrings/<name>.gpg] <url> <suite> <component>` →
  `apt update`.
- Branches: `NO_PUBKEY` (key missing/wrong path); "repository is not signed" (no
  `signed-by`); duplicate/conflicting source.
- **Authority note:** Kali warns against adding third-party repos to the base system
  (can break the rolling distro) — teach *how*, and *when not to*.

**G. Certificates & Certificate Authorities (TLS/license/trust)**
- Symptoms: HTTPS/`git`/`apt` "certificate verify failed"; needing to trust a custom CA.
- Flow: ensure `ca-certificates` installed → add a custom CA by placing `<ca>.crt` in
  `/usr/local/share/ca-certificates/` → `sudo update-ca-certificates` → verify.
- Branches: clock/time skew breaking certs (`timedatectl`); corporate/intercepting proxy
  CAs; per-app trust stores (browsers, Python `certifi`) differing from the system store.
- **Authority handling:** what a CA *is*, why trust is chain-based, risks of trusting an
  unknown CA — taught at the concept layer.

### 4.3 Rare / hard-to-solve cases (the "extensive" tail)
A dedicated tier for the gnarly ones, each as a deep decision tree:
- Boot/login failures: GRUB rescue, black screen, display-manager loop, fallback to TTY.
- Display/GPU & drivers: resolution stuck, external monitor, NVIDIA/driver mismatch.
- Wireless adapter not recognized / firmware missing / monitor-mode unsupported.
- Disk/space: full `/`, journald bloat, leftover loop/snap mounts.
- Persistence (live USB) not saving changes.
- Time/clock skew cascading into apt/cert failures.
- Locale/keyboard, zsh-vs-bash surprises, PATH gremlins (Kali quirks).

---

## 5. Worked flow #1 (template) — "No internet" (symptom-first, tiered)

**Symptom:** "I can't get online." · `os_profile: kali`

**Triage:** (1) Wired or Wi-Fi? (2) All sites or just one? (3) Worked before today?

**Diagnosis ladder (BASIC):**
1. **Have an IP?** Run `ip a`. *Look for:* an `inet` address on your interface.
   - *Has IP →* go to step 2.
   - *No IP →* fix B1 (bring interface up / restart NetworkManager).
2. **Reach the internet by number?** Run `ping -c3 1.1.1.1`.
   - *Replies →* it's almost certainly **DNS** → go to step 3.
   - *No replies →* routing/link → fix B2 (check `ip route`, restart NetworkManager).
3. **Reach it by name?** Run `ping -c3 google.com`.
   - *Fails (but step 2 worked) →* **DNS** → fix B3.

**Fixes:**
- **B1:** `sudo systemctl restart NetworkManager` (and `sudo ip link set <iface> up`).
  *Verify:* re-run `ip a`, expect an IP. *No →* climb to Intermediate.
- **B2:** `ip route` (is there a default gateway?); restart NetworkManager.
- **B3 (DNS):** check `/etc/resolv.conf` has a `nameserver`; set one via
  `nmcli`/NetworkManager. *Verify:* `ping google.com` works.

**INTERMEDIATE:** Wi-Fi soft-block (`rfkill list` → `rfkill unblock wifi`); reconnect with
`nmcli device wifi connect <ssid>`; set a static IP; distinguish systemd-resolved vs
resolv.conf.

**EXTENSIVE:** chipset driver/firmware install, `iw reg set`, MAC-randomization toggles,
captive-portal handling, VPN/monitor-mode interference, full `journalctl -u NetworkManager`
read.

**If still unresolved (§6B):** generate the Unresolved Issue Log (triage answers + each
command tried + its error output) for the user to copy and search with; offer the curated
networking resource links; point to the in-app **Networking** reference guide (self-paced).

---

## 6. Worked flow #2 (template) — "Add a third-party APT repo safely" (keys, certs, authority)

**Symptom/Goal:** "I need a tool from another repo" / fixing `NO_PUBKEY` or cert errors.
`os_profile: kali`

**Concept (shown first):** apt only trusts **signed** repositories; `apt-key` is
deprecated; keys live in `/etc/apt/keyrings/` and each source declares its key with
`signed-by=`. *Authority warning:* on Kali, adding third-party repos to the base system
can break the rolling distro — do this only when you trust the source and understand the
risk.

**Diagnosis/guided steps (show, never run):**
1. **Get + store the key:**
   `curl -fsSL <repo>/key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/<name>.gpg`
   *Explain:* `--dearmor` converts the key to the binary form apt expects.
2. **Add the source with `signed-by`:** create
   `/etc/apt/sources.list.d/<name>.list` containing
   `deb [signed-by=/etc/apt/keyrings/<name>.gpg] <url> <suite> <component>`.
3. **Refresh:** `sudo apt update`.

**Branches (did it work? No):**
- *`NO_PUBKEY`* → key missing or wrong path in `signed-by`; re-check step 1/2.
- *"repository is not signed"* → you omitted `signed-by=`; add it.
- *"certificate verify failed" (HTTPS repo)* → jump to **cert sub-flow:** ensure
  `ca-certificates` is installed → for a custom CA, put `<ca>.crt` in
  `/usr/local/share/ca-certificates/` and run `sudo update-ca-certificates`; also check
  the clock (`timedatectl`) since time skew breaks TLS.
- *duplicate/conflict* → remove the redundant source file.

**If still unresolved (§6B):** generate the Issue Log (steps + errors), offer curated
apt/repo/cert resource links, and point to the in-app **Packages & apt** and
**Certificates/Authority** reference guides (self-paced).

---

## 6B. When known steps are exhausted (self-directed handoff — no live help)

The tool is **fully self-contained.** There is no live assistant, no service call, and no
teacher. The authored flows are expected to resolve the **majority** of issues. But updates
sometimes break systems in genuinely new ways, so when a user has worked through every
known step for an issue, the tool does two honest things:

**1. Generate an "Unresolved Issue Log"** — saved on-device and copyable in one tap:
- the symptom + the triage answers given;
- **every step attempted**, each with the exact command shown and **the user's reported
  result / error output**;
- environment snapshot: Kali version (`/etc/os-release`), kernel, and any relevant package
  versions the user provided/observed;
- timestamps.
- *Excludes secrets* — passwords never logged; sensitive values can be redacted.

This gives the user a clean, complete record of "what I already tried and what it said," so
they can search efficiently and, if they post for help, give others the full picture
instead of starting from scratch.

**2. Offer a curated list of trustworthy places to look** (links only — the user goes there
themselves; the tool does not fetch or answer):
- **Kali official docs** — kali.org/docs
- **Kali forums** — forums.kali.org · **Kali bug tracker** — bugs.kali.org
- **Debian wiki** — wiki.debian.org (Kali is Debian-based)
- **Arch Wiki** — wiki.archlinux.org (excellent general Linux reference, even off-Arch)
- **Unix & Linux Stack Exchange** — unix.stackexchange.com
- **The specific tool's official docs / GitHub issues**
- On their own system: `man <command>` and `<command> --help`

Presented with a reminder to verify advice and only run commands they understand. Curate
for reliability — no random blogs. The list is itself maintained as data (a small module),
so trusted sources can be updated over time.

---

## 7. Cross-cutting

- **Generate-only + authorization:** diagnostic and fix commands are shown and explained;
  the user runs them. Anything destructive (e.g., disabling services, editing fstab) gets
  a `--status-critical` warning and a "are you sure / what this does" note first.
- **Audit log:** record symptom, tier reached, whether a fix was applied, resolved y/n —
  never passwords or full sensitive paths (blueprint §8.3).
- **Design tokens:** symptom/triage screens neutral; diagnostic steps in `--font-mono`;
  "did it work?" gate green/red; warnings `--status-warning`/`--status-critical`; resolved
  state `--status-secure`.
- **No live help / self-directed handoff:** there is no assistant or service. When flows
  are exhausted, the tool hands the user the **Unresolved Issue Log** + curated trusted
  links (§6B) so they can continue searching themselves.

---

## 8. Build order for the troubleshooter

1. **Engine reuse:** confirm the stepper supports symptom + triage front-end and a fixes
   list (data model §3) — small extension, no new UI.
2. **Networking module (Basic→Extensive)** — flow #1 above, highest-frequency area.
3. **apt/packages + repo-trust + certs** — flow #2 above (integral Kali functions).
4. **Services/systemd**, then **Permissions/sudo/filesystem**.
5. **Git-install** flow, then the **rare/hard-case** decision trees.
6. Wire the **Unresolved Issue Log** generator + curated trusted-resource list (§6B) and
   self-paced reference cross-links throughout.

Each ships as its own module (per the module system), so the troubleshooter grows from a
handful of common fixes to an extensive guided helpdesk over time.

*End of Troubleshooter subsystem spec v1.*
