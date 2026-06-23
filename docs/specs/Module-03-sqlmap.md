# Module 03 — sqlmap (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, Module 02 (nmap) template, Design Tokens
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #2**

> Complete tool module for **sqlmap** — automated SQL-injection detection and exploitation —
> built to the nmap template. **Simple to use, complete in depth:** profiles give a safe
> on-ramp; underneath, every flag, technique, and `--level/--risk` is explained.
> **Generate-only** (shows/explains commands; never runs them). sqlmap is a powerful
> offensive tool, so it carries a **strong authorization gate** and points to legal
> practice labs.

---

## 1. Manifest

```yaml
module_id: tool.sqlmap
name: "sqlmap — Automated SQL Injection"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, tool.nmap] }
provides:
  tool: sqlmap
  flows: [detect, enum_dbs, enum_tables, dump, tune, auth_post, proxy_tor, advanced_shell]
  glossary_terms: [sql_injection, injection_point, dbms, parameter, level, risk, technique, batch, request_file, tamper]
content:
  tool: registry/tools/sqlmap.yaml
  flows: registry/flows/sqlmap_*.yaml
  builder: command_builders/sqlmap_builder.py
  glossary: explain/glossary/sqlmap.yaml
theme: theme.w1ck3d_systems        # category = Web App → tinted; offensive → red authz gate
source: "authored; verified against sqlmap --help / official wiki (sqlmap.org)"
license: "project-proprietary lesson text; sqlmap is GPL (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: sqlmap
display_name: "sqlmap"
binary_candidates: [sqlmap]
install_check: "shutil.which('sqlmap'); optional: sqlmap --version"
categories: [web_app, exploitation]
one_liner: "Detects and exploits SQL-injection flaws in a web app's parameters."
authorization_gate: true            # OFFENSIVE — mandatory consent + legal-practice pointer
flows: [detect, enum_dbs, enum_tables, dump, tune, auth_post, proxy_tor, advanced_shell]
```

---

## 3. sqlmap mapped to the 8 slots

| Slot | sqlmap content | Examples |
|------|----------------|----------|
| 1 PROGRAM | `sqlmap` | `sqlmap` |
| 2 GLOBAL_OPTIONS | run-wide behavior | `--batch` (no prompts), `-v 3` (verbosity), `--random-agent`, `--threads 4` |
| 3 TARGET_PIVOT | what to test | `-u "http://site/p.php?id=1"`, `-r request.txt` (saved HTTP request), `-m urls.txt` |
| 4 ACTION_OPTIONS | what to do | enumerate (`--dbs`,`--tables`,`--columns`,`--dump`), scope (`-D`,`-T`,`-C`), depth (`--level`,`--risk`,`--technique`) |
| 5 OUTPUT_OPTIONS | where results go | `--output-dir <dir>` (results auto-saved per target) |
| 6 POSITIONAL_ARGS | (none — sqlmap is all flags) | — |
| 7 ENV/PROXY | routing/identity | `--proxy http://127.0.0.1:8080`, `--tor --check-tor` |
| 8 EXTRA_FILES | request/data inputs | `-r request.txt`, `--data "id=1"` (POST), `--cookie "…"`, `--tamper <script>` |

> **Builder note:** sqlmap takes no positional args — the *target* lives in `-u`/`-r`, not a
> bare argument. The builder always emits the target flag in slot 3.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | Fills | Behavior | Note shown |
|---------|-------|----------|------------|
| **Detect only** | `--batch --level 1 --risk 1` | just find if a param is injectable | "Lowest-impact; start here." |
| **Map the database** | `--batch --dbs` (then guided `-D … --tables/--columns`) | enumerate structure, no data dump | "See what's there before pulling data." |
| **Targeted dump** | `--batch -D <db> -T <tbl> -C <cols> --dump` | pull specific columns only | "Take the minimum you need." |
| **Thorough (loud)** | `--batch --level 5 --risk 3` | test everything (cookies/headers, heavy payloads) | "Slow + noisy + higher impact — authorized only." |

Profiles are teaching scaffolds; still generate/reference only. Each flag they set is fully
explained inline (the "complete" layer).

---

## 5. Flows (beginner → advanced)

Pattern per step: `concept` (what/why, simple) · `flag_detail` (every flag) · `slot_mapping`
· `show_command` · `success_criteria` · `did_it_work` gate + `alternatives` · `glossary_refs`.

### Flow A — Detect an injection point
- **Slots:** PROGRAM + TARGET(`-u`) + GLOBAL(`--batch`).
- **Key flags:** `-u "URL?param=value"` (the parameter under test), `--batch` (use defaults,
  no prompts). Optionally `-p <param>` to target one parameter.
- **show:** `sqlmap -u "http://TARGET/page.php?id=1" --batch`
- **success:** sqlmap reports a parameter is injectable and identifies the **DBMS**.
- **branches (No):**
  - *"all tested parameters do not appear to be injectable"* → raise depth: `--level 3`
    (tests more places) and/or `--risk 2`; confirm the right parameter (`-p`).
  - *needs POST/cookie/login* → Flow F (auth).
- **glossary:** sql_injection, injection_point, dbms, parameter, batch.

### Flow B — Enumerate databases
- **Key flags:** `--dbs` (list databases), `--current-db`, `--current-user`, `--is-dba`,
  `--banner`.
- **show:** `sqlmap -u "…?id=1" --batch --dbs`
- **success:** a list of database names prints.
- **branches:** *not a DBA / limited* → note privilege limits; continue with what's readable.
- **glossary:** dbms.

### Flow C — Enumerate tables & columns
- **Key flags:** `-D <db> --tables`, then `-D <db> -T <table> --columns`.
- **show:** `sqlmap -u "…?id=1" --batch -D shop --tables` →
  `sqlmap -u "…?id=1" --batch -D shop -T users --columns`
- **success:** table list, then the columns of the chosen table.
- **glossary:** (scope flags `-D/-T/-C`).

### Flow D — Dump data (targeted, minimal)
- **Key flags:** `-D <db> -T <table> -C <c1,c2> --dump`; `--dump` (whole table);
  `--dump-all` (everything — **⚠ heavy/over-collection**).
- **show:** `sqlmap -u "…?id=1" --batch -D shop -T users -C username,password --dump`
- **success:** the selected columns' rows are extracted (and auto-saved to the output dir).
- **branches:** *huge table* → add `--start/--stop` to limit rows; prefer specific `-C`.
- **note:** "Take the minimum needed; `--dump-all` is rarely appropriate." (red callout)

### Flow E — Tune level, risk & technique (the depth dial)
- **Complete layer:**
  - `--level 1..5` — how *many* places to test (5 also tests cookies, headers, etc.).
  - `--risk 1..3` — how *heavy* the payloads (3 includes potentially disruptive ones).
  - `--technique BEUSTQ` — restrict to specific injection types (Boolean, Error, Union,
    Stacked, Time, inline Query). e.g. `--technique=BEU`.
  - `--dbms mysql` — hint the backend to speed detection.
- **show:** `sqlmap -u "…?id=1" --batch --level 4 --risk 2 --technique=BEU`
- **branches:** *too slow* → narrow technique, lower level; *false negatives* → raise level.
- **glossary:** level, risk, technique.

### Flow F — Authenticated / POST / saved request
- **Complete layer:**
  - POST data: `--data "user=admin&id=1"`.
  - Session: `--cookie "PHPSESSID=…"`.
  - **Saved request (best for logged-in apps):** `-r request.txt` — paste a full HTTP
    request (e.g., exported from Burp/your browser); sqlmap reads target, headers, cookies,
    and body from it.
- **show:** `sqlmap -r request.txt --batch -p id`
- **success:** sqlmap tests within the authenticated context.
- **branches:** *session expired mid-run* → refresh the cookie/request file; consider
  `--csrf-token` options for CSRF-protected forms.
- **glossary:** request_file, parameter.

### Flow G — Through a proxy / Tor / blend in
- **Complete layer:** `--proxy http://127.0.0.1:8080` (route via Burp/ZAP to watch traffic);
  `--tor --check-tor` (anonymize — authorized testing only); `--random-agent` (vary UA);
  `--delay`/`--threads` (pace vs speed); `--tamper=<script>` (WAF evasion — advanced).
- **show:** `sqlmap -u "…?id=1" --batch --proxy http://127.0.0.1:8080 --random-agent`
- **branches:** *blocked by a WAF* → discuss `--tamper` scripts conceptually (authorized
  only); slow down with `--delay`.
- **glossary:** tamper.

### Flow H — Advanced: interactive shells (high impact)
- **⚠ High-impact, authorized engagements only.** `--sql-shell` (interactive SQL),
  `--os-shell` (OS command shell where the DB/permissions allow), `--os-pwn` (further).
- **show:** `sqlmap -u "…?id=1" --batch --os-shell`
- **concept:** "These move from *reading* data to *executing* commands on the target —
  serious impact and legal exposure. Only on systems you're explicitly authorized to test,
  ideally a lab. The module gates this behind an extra confirmation."
- **branches:** *not available* → depends on DBMS/privileges/stacked-query support.

---

## 6. Authorization gate (mandatory, before any command shown)

> "SQL injection testing against systems you do not own or lack **explicit written
> permission** to test is illegal in most jurisdictions. Continue only for authorized
> targets." — logged to the on-device audit log.

**Practice legally:** sqlmap ships test targets; learn on **DVWA**, **bWAPP**, **sqli-labs**,
**OWASP Juice Shop**, or your own lab VM — never on sites you don't control. Flow H requires
a **second** explicit confirmation.

---

## 7. Glossary additions

- **sql_injection** — tricking an app into running attacker-controlled SQL via its inputs.
- **injection_point / parameter** — the specific input (e.g., `?id=`) that's exploitable.
- **dbms** — the database engine (MySQL, PostgreSQL, MSSQL…); sqlmap fingerprints it.
- **level (1–5)** — how many input places sqlmap tests (higher = cookies/headers too).
- **risk (1–3)** — how aggressive the payloads (higher = potentially disruptive).
- **technique (BEUSTQ)** — which injection types to use (Boolean/Error/Union/Stacked/Time/Query).
- **batch** — `--batch` runs non-interactively using sensible defaults.
- **request_file** — a saved HTTP request (`-r`) carrying target+headers+cookies+body.
- **tamper** — scripts that mutate payloads to evade WAFs (advanced).

---

## 8. Design / token mapping (W1CK3D SYSTEMS)

- Category **Web App / Exploitation** → tinted tab; **offensive tool → the authorization
  gate is a `--status-critical` (red) callout**, and Flow H/`--dump-all` get red warnings.
- All command/skeleton/filled views → `--font-mono` / `--font-term`.
- "did it work?" gate → green (Yes) / red-orange (No → alternative).
- "minimal collection" reminders styled as `--status-warning`.

---

## 9. Why this fits the template

Same shape as nmap: profiles for the easy on-ramp, every flag/`--level`/`--risk`/technique
explained for depth, realistic adaptive branches (not injectable → raise level; behind login
→ use `-r`; WAF → tamper), an output plan, and (because it's offensive) a stronger,
double-gated authorization step. Confirms the template generalizes from a scanner to an
exploitation tool.

*End of Module 03 (sqlmap) spec v1. Next in CLI Top 10: hydra.*
