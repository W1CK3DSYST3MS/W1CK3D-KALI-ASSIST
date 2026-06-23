# Module T03 — Services & systemd Troubleshooter

**Project:** W1CK3D'S KALI ASSIST · **Type:** Troubleshooter module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** `Troubleshooter-Subsystem.md`, T01, T02, Blueprint v1.8
**Last updated:** 2026-06-22

> Third complete troubleshooter: getting services to start, stay up, and be readable when
> they fail — the systemd skills every Kali user needs (and the home of the GVM/PostgreSQL
> cases from the early brainstorming). Built to the template: **symptom-first** → triage →
> one-command-at-a-time diagnosis → verified fix → if exhausted, **Unresolved Issue Log** +
> curated trusted links. **Generate-only, self-contained, no AI.** Three tiers.

---

## 1. Manifest

```yaml
module_id: troubleshoot.services
name: "Services & systemd Troubleshooter"
version: 1.0.0
type: troubleshooter
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, troubleshoot.networking] }
provides:
  symptoms: [wont_start, not_enabled, read_logs, port_conflict, masked_dep, unit_changed, service_specific]
  glossary_terms: [service, daemon, unit, systemd, enable_vs_start, journal, masked_unit, target, daemon_reload]
content:
  flows: registry/troubleshoot/services_*.yaml
  resources: registry/resources/services_links.yaml
  glossary: explain/glossary/services.yaml
theme: theme.w1ck3d_systems
source: "authored; verified against systemctl/journalctl man pages + Kali/Debian docs"
license: "project-proprietary"
```

---

## 2. Symptom router (entry)

| # | Symptom (plain language) | Routes to |
|---|--------------------------|-----------|
| S1 | "A service won't start / says failed" | §4 |
| S2 | "It works now but not after reboot" (not enabled) | §5 |
| S3 | "How do I see *why* it failed?" (logs) | §3 (shared) |
| S4 | "Port already in use / address in use" | §6 |
| S5 | "It's masked / a dependency failed" | §7 |
| S6 | "I edited a unit and nothing changed" | §8 |
| S7 | "PostgreSQL / GVM / SSH specifically" | §9 |

**Triage (asked once):**
- What's the **exact service name**? (e.g. `ssh`, `postgresql`, `gvmd`)
- "Won't start at all," "starts then dies," or "not running after reboot"?
- Did it work before — what changed (update, config edit, new install)?

---

## 3. The universal first look (shared by all)

Always start here; report what you see.
1. **State + recent logs in one view:** `systemctl status <svc>`
   *Look for:* `Active:` line (`failed`/`inactive`/`active`), and the last few log lines —
   they usually name the cause. Also note `Loaded:` (could say `masked`).
2. **Full recent logs for that unit:** `journalctl -u <svc> -e` (end of log) or
   `journalctl -u <svc> -b` (this boot). *Look for:* the first ERROR/`Failed`/`fatal`.
3. **Is it enabled / active?** `systemctl is-enabled <svc>` and `systemctl is-active <svc>`.

> Reading `status` + `journalctl` is *the* core skill — almost every fix below starts from
> the exact error those reveal.

---

## 4. S1 — Service won't start / shows "failed"

### Basic
- **Read the cause** (from §3 `status`/`journalctl`), then **try a clean start:**
  `sudo systemctl restart <svc>` and re-check `systemctl status <svc>`.
- **Common: a config error** — the log names a file + line; fix it, then
  `sudo systemctl restart <svc>`. *Verify:* `Active: active (running)`.

### Intermediate
- **Starts then dies (`activating`→`failed`):** read `journalctl -u <svc> -e` for the exit
  reason; check `systemctl show <svc> -p ExecStart` to see exactly what it runs.
- **Missing dependency/file/permission** named in the log → fix the named item, restart.
- **Reset a flapping unit's failure count:** `sudo systemctl reset-failed <svc>` then start.

### Extensive
- Exit-code mapping (`status=…`), `Result=` lines; core dumps via `coredumpctl`.
- Unit ordering/race (`After=`/`Requires=`) → `systemctl list-dependencies <svc>`.
- Resource limits (memory/ulimit) in the unit; environment files not loaded.

---

## 5. S2 — Works now, but not after reboot (enable vs start)

### Basic
- **Key concept:** `start` runs it **now**; `enable` makes it run **at boot**. You usually
  want both: `sudo systemctl enable --now <svc>`.
  *Verify:* `systemctl is-enabled <svc>` → `enabled`, `is-active` → `active`.

### Intermediate
- **Enabled but still not up after boot** → check it didn't fail at boot:
  `journalctl -u <svc> -b`; check its target/`WantedBy`.
- **Should NOT auto-start** (e.g., ssh you only use sometimes) →
  `sudo systemctl disable --now <svc>` (and start manually when needed).
  **⚠ note:** disabling a service others rely on (e.g., remote ssh) can lock you out —
  warned first.

### Extensive
- Unit enabled in the wrong target; `systemctl get-default`; `multi-user` vs `graphical`.
- Conditional units (`ConditionPathExists=` etc.) silently skipping at boot.

---

## 6. S4 — Port already in use / "address already in use"

### Basic
- **Find what's holding the port:** `sudo ss -tulpn | grep :<port>` → it shows the PID and
  program. *Then decide:* is the holder a duplicate of this service, or a different program?

### Intermediate
- **Duplicate instance:** stop the stray one (`sudo systemctl stop <svc>` or stop the PID's
  owning service), then start the intended one.
- **Different program owns the port:** change one side's port (in the service's config),
  `daemon-reload` if you edited the unit, restart.

### Extensive
- Lingering socket in `TIME_WAIT`; socket-activated units (`<svc>.socket`) holding the port
  — manage the `.socket`, not just the `.service`.
- IPv4 vs IPv6 bind conflicts; bind address `0.0.0.0` vs specific IP.

---

## 7. S5 — Masked unit / dependency failed

### Basic
- **`status` says `masked`** → the unit is hard-disabled (symlinked to /dev/null).
  Re-enable: `sudo systemctl unmask <svc>` then `sudo systemctl enable --now <svc>`.

### Intermediate
- **A required dependency failed** (log shows `Dependency failed for …`) → find the failing
  upstream unit (`systemctl --failed`), fix *that* one first (back to §3/§4), then start
  the dependent service.

### Extensive
- Whole `.target` failing; ordering cycles (systemd will log "breaking ordering cycle").
- `systemctl list-dependencies --all <svc>` to trace the tree.

---

## 8. S6 — Edited a unit and nothing changed (daemon-reload)

### Basic
- **systemd caches unit files.** After editing a `.service`, reload then restart:
  `sudo systemctl daemon-reload` → `sudo systemctl restart <svc>`.
  *Verify:* `systemctl cat <svc>` shows your edited content; `status` reflects it.

### Intermediate
- **Don't edit vendor units in place** — use a drop-in: `sudo systemctl edit <svc>` (creates
  `…/override.conf`), then `daemon-reload` + restart. Survives package updates.
- Confirm which file is active with `systemctl cat <svc>` (shows path + drop-ins).

### Extensive
- Multiple unit files shadowing each other (`/etc/systemd` overrides `/lib/systemd`);
  `systemd-analyze verify <unit>` to catch syntax errors.

---

## 9. S7 — Service-specific flows (the common Kali ones)

### PostgreSQL (needed by Metasploit, and by GVM)
- Start/enable: `sudo systemctl enable --now postgresql`; verify `systemctl status
  postgresql` and `ss -tulpn | grep 5432`.
- Metasploit DB not connecting → `sudo msfdb init` (sets up the DB), then in `msfconsole`
  check `db_status`.

### GVM / OpenVAS (Greenbone)
- This is a **service stack**, not one service: `gvmd`, `ospd-openvas`, `gsad`.
- First-time/after-issues: `sudo gvm-check-setup` (it diagnoses what's wrong and suggests
  the next command), `sudo gvm-setup` (initial setup + feed sync — slow), then
  `sudo gvm-start`.
- Verify each: `systemctl status gvmd ospd-openvas gsad`; web UI on its local port (check
  with `ss -tulpn`).
- Common causes: PostgreSQL not running (fix above); feeds still syncing; redis/ospd socket
  not up. Read each unit's `journalctl -u <unit> -e`.

### SSH
- Enable/start: `sudo systemctl enable --now ssh`.
- "won't start on a fresh install" → host keys missing: `sudo ssh-keygen -A` (or
  `sudo dpkg-reconfigure openssh-server`), then restart.
- Remember the firewall (T01/Module 00): allow the port if you need remote access
  (`sudo ufw allow 22/tcp`). **⚠** opening SSH widens attack surface — warned.

---

## 10. When known steps are exhausted (§6B applied)

**Unresolved Issue Log — services fields:**
- symptom + triage (service name, won't-start vs dies vs not-after-reboot, what changed);
- outputs run: `systemctl status <svc>`, the key `journalctl -u <svc> -e` error lines,
  `systemctl is-enabled/is-active`, `ss -tulpn` for port cases, `systemctl --failed`;
- environment: Kali version, the unit file path (`systemctl cat <svc>`), package version.
- *(No secrets — redact any credentials shown in configs/logs.)*

**Curated trusted links:**
- Kali docs / forums / bug tracker; Greenbone docs for GVM specifically
- Debian wiki — systemd pages; Arch Wiki — systemd (excellent reference)
- freedesktop.org systemd man pages; Unix & Linux Stack Exchange
- On-system: `man systemctl`, `man journalctl`, `man systemd.unit`, `man systemd.service`

---

## 11. Glossary (shipped with this module)

- **service / daemon** — a background program; managed as a systemd **unit**.
- **unit** — systemd's managed object (`.service`, `.socket`, `.target`, `.timer`).
- **systemd** — the init/service manager that starts and supervises everything.
- **enable vs start** — `start` = run now; `enable` = run at boot (use `enable --now` for both).
- **journal** — systemd's log store, read with `journalctl`.
- **masked_unit** — a unit hard-disabled so it can't start until `unmask`ed.
- **target** — a group of units representing a system state (like a runlevel).
- **daemon_reload** — re-reads unit files after you edit them.

---

## 12. Design, safety, audit

- **Tokens:** commands in `--font-mono`; "did it work?" gate green/red; **destructive**
  steps (disabling/masking services, opening SSH, killing a port owner) as
  `--status-critical` callouts with "what this does / risk / how to undo" first.
- **Generate-only:** all commands shown for the user to run; nothing executed.
- **Audit (no secrets):** symptom, service, tier reached, fix applied?, resolved?
- **Cross-links:** port/firewall → T01 + Module 00; PostgreSQL/feeds → here; `man`/glossary
  inline; exhaustion → §10.

---

## 13. Why this matters in the project

systemd is where a huge share of "it just won't work" lives, and reading
`status`/`journalctl` is the single most transferable troubleshooting skill — so this
module teaches the *method* (read the log → fix the named cause → verify), not just fixes.
It also finally grounds the original `gvm-start` thread in a real, correct service flow.

*End of Module T03 (Services & systemd) spec v1.*
