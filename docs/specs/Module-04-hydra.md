# Module 04 — hydra (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, Module 02 (nmap) template
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #3**

> Complete tool module for **hydra** — a fast, parallel **online** login brute-forcer for
> many protocols (SSH, FTP, HTTP forms, SMB, RDP, databases…). Built to the nmap template.
> **Generate-only.** hydra is offensive *and noisy* (it makes real login attempts), so this
> module carries a **strong authorization gate** plus explicit **account-lockout / detection
> warnings**, and points to legal practice targets.

---

## 1. Manifest

```yaml
module_id: tool.hydra
name: "hydra — Online Login Brute-Forcer"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, tool.nmap] }
provides:
  tool: hydra
  flows: [single_test, lists, wordlists_tune, http_form, extras, output_resume, multi_target]
  glossary_terms: [online_vs_offline, service_module, login, password_list, combo_list, tasks, lockout, rockyou, http_post_form, null_login]
content:
  tool: registry/tools/hydra.yaml
  flows: registry/flows/hydra_*.yaml
  builder: command_builders/hydra_builder.py
  glossary: explain/glossary/hydra.yaml
theme: theme.w1ck3d_systems        # offensive → red authorization + lockout callouts
source: "authored; verified against hydra -h / official docs (THC-Hydra)"
license: "project-proprietary lesson text; hydra is AGPL/GPL (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: hydra
display_name: "hydra (THC-Hydra)"
binary_candidates: [hydra]
install_check: "shutil.which('hydra'); optional: hydra -h"
categories: [password, exploitation]
one_liner: "Tries many username/password combos against a live login service."
authorization_gate: true            # OFFENSIVE + NOISY — mandatory consent + lockout warning
flows: [single_test, lists, wordlists_tune, http_form, extras, output_resume, multi_target]
```

> **Online vs offline (taught up front):** hydra attacks a **live service** over the network
> (every guess is a real login attempt — slow, noisy, can lock accounts). Cracking captured
> **hashes offline** is a different job → that's **john** (Module 05) / **hashcat** (06).

---

## 3. hydra mapped to the 8 slots

hydra's overall shape: `hydra [options] -L users -P passwords <target> <service>`

| Slot | hydra content | Examples |
|------|---------------|----------|
| 1 PROGRAM | `hydra` | `hydra` |
| 2 GLOBAL_OPTIONS | run-wide behavior | `-t 4` (parallel tasks), `-V`/`-vV` (verbose), `-f` (stop on first hit), `-w 30` (wait), `-e nsr` (extra tries) |
| 3 TARGET_PIVOT | the host | `192.168.1.10` (or `-M hosts.txt` for many) |
| 4 ACTION_OPTIONS | creds + service | `-l user`/`-L users.txt`, `-p pass`/`-P pass.txt`/`-C combos.txt`, `-s <port>`, **the service module** (`ssh`, `ftp`, `http-post-form`, …) |
| 5 OUTPUT_OPTIONS | where results go | `-o found.txt` (`-b json` format) |
| 6 POSITIONAL_ARGS | target + service (end of line) | `192.168.1.10 ssh` |
| 7 ENV/PROXY | routing/port | `-s 2222`, `HYDRA_PROXY` env |
| 8 EXTRA_FILES | wordlists/combos | `-L users.txt`, `-P rockyou.txt`, `-C user:pass.txt` |

> **Builder note:** `<target> <service>` are **positional and go last**. The builder always
> assembles options first, then target, then service module + its args — so ordering is never
> the user's problem.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | Fills | Behavior | Note shown |
|---------|-------|----------|------------|
| **Single check** | `-t 4 -V -f` | one user, one/few passwords; stop on hit | "Verify access works before any list." |
| **Targeted list** | `-t 4 -V -f` | known user + a small password list | "Low-and-slow; least likely to lock out." |
| **Standard wordlist** | `-t 4 -V` | user list + rockyou-style list | "The everyday attempt — still authorized only." |
| **Careful (lockout-aware)** | `-t 1 -w 30` | one task, long wait | "When lockout/detection is a concern." |

All generate/reference only; every flag is explained inline.

---

## 5. Flows (beginner → advanced)

Pattern per step: `concept` · `flag_detail` · `slot_mapping` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — Target + service + a single credential test
- **Key flags:** `-l <user>` (single login), `-p <pass>` (single password), then
  `<target> <service>`. Add `-V` to see each attempt, `-f` to stop on success.
- **show:** `hydra -l admin -p admin123 -V -f 192.168.1.10 ssh`
- **success:** hydra prints `[ssh] host: … login: admin password: admin123` on a hit.
- **branches (No):**
  - *connection refused / wrong port* → confirm the service is up (nmap, Module 02) and set
    `-s <port>` if non-standard.
  - *no valid pair* → move to lists (Flow B).
- **glossary:** service_module, login.

### Flow B — Username list × password list
- **Key flags:** `-L users.txt` (login list), `-P passwords.txt` (password list).
- **show:** `hydra -L users.txt -P passwords.txt -V -f 192.168.1.10 ssh`
- **success:** any valid pair(s) reported.
- **branches:** *very slow / many users* → lower `-t`, keep lists small first; consider `-u`
  (loop users outer) for lockout-sensitive targets.
- **glossary:** password_list.

### Flow C — Real wordlists + tuning tasks
- **Complete layer:** Kali ships **rockyou** gzipped — uncompress once:
  `sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz`. SecLists has more
  (`/usr/share/seclists/…` if installed).
- `-t <n>` = parallel tasks (default 16). **Lower it** for stability and to reduce
  lockouts/noise; raise only on robust lab targets.
- **show:** `hydra -L users.txt -P /usr/share/wordlists/rockyou.txt -t 4 -V 192.168.1.10 ssh`
- **branches:** *target rate-limits/blocks you* → drop to `-t 1 -w 30` (Careful profile).
- **glossary:** rockyou, tasks.

### Flow D — HTTP login form (`http-post-form`) — the tricky one
- **Complete layer:** form modules need three colon-separated parts:
  `"<path>:<body with ^USER^ and ^PASS^>:<failure marker>"`.
  - `^USER^`/`^PASS^` are where hydra injects each guess.
  - the **failure marker** is text that appears on a *failed* login (so hydra knows what
    "wrong" looks like); use `F=<text>` for failure or `S=<text>` for success.
- **show:**
  `hydra -L users.txt -P passwords.txt 192.168.1.10 http-post-form "/login.php:user=^USER^&pass=^PASS^:F=Invalid credentials"`
- **success:** valid pair reported.
- **branches (No):**
  - *every attempt shows as success/failure wrongly* → your failure/success marker is off;
    capture a real failed login (browser/Burp) and copy the exact message.
  - *CSRF token required* → forms with per-request tokens need extra handling (advanced;
    often easier via a tool that tracks tokens) — note and point to docs.
- **glossary:** http_post_form.

### Flow E — Extra tries & combo lists
- **Complete layer:** `-e nsr` adds **n**ull password, password = **s**ame as login,
  **r**eversed login; `-C user:pass.txt` uses a **combo** file (one `user:pass` per line)
  instead of `-L`+`-P`.
- **show:** `hydra -L users.txt -e nsr 192.168.1.10 ssh`
- **glossary:** null_login, combo_list.

### Flow F — Output, resume & stop-on-success
- **Complete layer:** `-o found.txt` (save hits), `-b json` (format); `-f` stop on first hit
  per host, `-F` stop globally; `-R` **resume** an aborted previous session.
- **show:** `hydra -L users.txt -P rockyou.txt -o hits.txt -f 192.168.1.10 ssh`
- **branches:** *interrupted* → `hydra -R` to continue.

### Flow G — Multiple targets
- **Complete layer:** `-M targets.txt` runs against many hosts; combine with `-o` for a
  consolidated result file. Pace carefully (`-t` low) to avoid hammering.
- **show:** `hydra -L users.txt -P passwords.txt -M targets.txt -o hits.txt ssh`

---

## 6. Authorization gate + operational warnings (before any command shown)

> "Brute-forcing logins on systems you do not own or lack **explicit written permission** to
> test is illegal. Continue only for authorized targets." — logged to the audit log.

**⚠ Operational reality (shown as a `--status-critical` callout):**
- hydra makes **real login attempts** — it can **lock out accounts**, flood logs, and trigger
  alerts/IPS. On engagements, confirm lockout policy first and pace with low `-t` + `-w`.
- **Practice legally:** your own lab VMs, **Metasploitable**, **DVWA**, or intentionally
  vulnerable targets — never real services you don't control.

---

## 7. Glossary additions

- **online vs offline** — hydra guesses against a *live service*; cracking captured *hashes*
  offline is john/hashcat (slower service = hydra; fast many-guesses = offline hashes).
- **service_module** — the protocol hydra speaks (`ssh`, `ftp`, `http-post-form`, `smb`…).
- **login / password_list / combo_list** — `-L` users, `-P` passwords, `-C` `user:pass` pairs.
- **tasks (`-t`)** — parallel attempts; lower = gentler/stealthier, higher = faster/noisier.
- **lockout** — accounts disabled after too many failures; brute force can trigger it.
- **rockyou** — the classic password wordlist (gzipped on Kali; gunzip first).
- **http_post_form** — module format `path:body(^USER^/^PASS^):failure-or-success marker`.
- **null_login (`-e n`)** — also try an empty password (and `s`=same, `r`=reversed).

---

## 8. Design / token mapping

- Category **Password / Exploitation** → tinted tab; **offensive + noisy → authorization
  gate and the lockout warning are `--status-critical` (red) callouts.**
- Commands in `--font-mono`; "did it work?" gate green/red; pacing/lockout tips as
  `--status-warning`.

---

## 9. Why this fits the template

Same shape as nmap/sqlmap: profiles for the on-ramp, every flag/service-module explained for
depth, and genuinely hard real-world branches — the `http-post-form` failure-marker gotcha,
rate-limiting → lower `-t`, resume with `-R`. It also teaches the **online-vs-offline**
distinction that sets up the next two modules (john, hashcat).

*End of Module 04 (hydra) spec v1. Next in CLI Top 10: john.*
