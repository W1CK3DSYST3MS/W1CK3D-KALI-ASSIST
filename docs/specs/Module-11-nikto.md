# Module 11 — nikto (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, nmap template, Modules 02 & 10
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #10 (final)**

> Complete module for **nikto** — a web-server vulnerability scanner that checks for known
> dangerous files, outdated software, and misconfigurations. Built to the project template.
> **Generate-only.** nikto is **noisy by design** (it makes no attempt at stealth), so it
> carries an authorization gate and pacing/evasion guidance. Authorized targets / labs only.

---

## 1. Manifest

```yaml
module_id: tool.nikto
name: "nikto — Web Server Vulnerability Scanner"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [tool.nmap, tool.gobuster] }
provides:
  tool: nikto
  flows: [first_scan, port_ssl, tuning, output, auth_proxy_vhost, evasion_pace, update, integration]
  glossary_terms: [web_vuln_scan, tuning, ssl, evasion, plugin, false_positive, vhost, cgidirs]
content:
  tool: registry/tools/nikto.yaml
  flows: registry/flows/nikto_*.yaml
  builder: command_builders/nikto_builder.py
  glossary: explain/glossary/nikto.yaml
theme: theme.w1ck3d_systems        # category = Web App / Detect
source: "authored; verified against nikto -Help / cirt.net docs"
license: "project-proprietary lesson text; nikto is GPL (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: nikto
display_name: "nikto"
binary_candidates: [nikto]
install_check: "shutil.which('nikto'); optional: nikto -Version"
categories: [web_app, detect]
one_liner: "Scans a web server for known bad files, outdated software, and misconfigurations."
authorization_gate: true            # noisy web scanner — authorized targets only
flows: [first_scan, port_ssl, tuning, output, auth_proxy_vhost, evasion_pace, update, integration]
```

> **Where it fits:** nmap finds the web port (Module 02) → gobuster finds hidden content
> (Module 10) → **nikto flags server-level vulns/misconfigs**. Complementary, not duplicate.

---

## 3. nikto mapped to the 8 slots

Overall shape: `nikto -h <host> [-p <port>] [-ssl] [tuning/options] [-o file -Format …]`

| Slot | nikto content | Examples |
|------|---------------|----------|
| 1 PROGRAM | `nikto` | `nikto` |
| 2 GLOBAL_OPTIONS | run-wide | `-Display V` (verbose), `-timeout 10`, `-Pause 1`, `-maxtime 5m`, `-nointeractive` |
| 3 TARGET_PIVOT | the host | `-h https://10.0.0.20` (or `-h hosts.txt`) |
| 4 ACTION_OPTIONS | what to test | `-p <port>`, `-ssl`, `-Tuning <x>`, `-vhost <name>`, `-evasion <n>`, `-Plugins <list>` |
| 5 OUTPUT_OPTIONS | where results go | `-o report.html -Format htm` (also `csv`,`xml`,`json`,`txt`) |
| 6 POSITIONAL_ARGS | (none — all flags) | — |
| 7 ENV/PROXY | routing/auth | `-useproxy http://127.0.0.1:8080`, `-id user:pass` |
| 8 EXTRA_FILES | host/output files | `-h hosts.txt`, `-o report.html` |

> **Builder note:** target is always `-h` (never a bare argument); the builder pairs `-ssl`/
> `-p` with it for HTTPS/custom ports.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | Fills | Behavior | Note shown |
|---------|-------|----------|------------|
| **Quick scan** | `-h <host>` | default full check | "One command to baseline a server." |
| **HTTPS** | `-h <host> -ssl -p 443` | force TLS scan | "For sites that only speak HTTPS." |
| **Tuned** | `-Tuning <cats>` | run only chosen test categories | "Focus the scan, cut noise/time." |
| **Reported** | `-o report.html -Format htm` | save a shareable report | "For write-ups / handoff." |

All generate/reference only; every flag explained inline.

---

## 5. Flows (beginner → advanced)

Pattern per step: `concept` · `flag_detail` · `slot_mapping` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — First scan
- **Key flags:** `-h <host>` (URL or host). nikto auto-detects http/https and common ports.
- **show:** `nikto -h http://10.0.0.20`
- **success:** findings stream (server banner, headers, interesting files, OSVDB/CVE refs).
- **branches (No):**
  - *"No web server found / connection refused"* → confirm a web service first (nmap,
    Module 02); set the right `-p`/`-ssl`.
  - *hangs* → add `-timeout` / `-maxtime`.
- **glossary:** web_vuln_scan.

### Flow B — Port & SSL targeting
- **Complete layer:** `-p 8080` (non-standard port; comma-list for several), `-ssl` force
  TLS, `-nossl` force plain. Scan several hosts with `-h hosts.txt`.
- **show:** `nikto -h 10.0.0.20 -p 8443 -ssl`
- **glossary:** ssl.

### Flow C — Tuning (pick what to test)
- **Complete layer:** `-Tuning` selects test categories (faster, less noise). Common values:
  `1` interesting files, `2` misconfig/default files, `3` info disclosure, `4` injection
  (XSS), `5` remote file retrieval, `6` DoS, `9` SQLi, `0` file upload, `x` **exclude** the
  listed ones. Combine digits, e.g. `-Tuning 123b`.
- **show:** `nikto -h http://site -Tuning 1234`
- **branches:** *too slow / too noisy* → tune to the categories you care about; skip `6` (DoS)
  on anything you can't afford to disrupt.
- **glossary:** tuning.

### Flow D — Output & reports
- **Complete layer:** `-o <file> -Format <htm|csv|xml|json|txt>`. HTML is great for write-ups;
  CSV/JSON for parsing.
- **show:** `nikto -h http://site -o report.html -Format htm`
- **branches:** *format error* → the file extension and `-Format` should agree.

### Flow E — Auth, proxy & virtual hosts
- **Complete layer:** `-id user:pass` (HTTP basic auth); `-useproxy http://127.0.0.1:8080`
  (route via Burp/ZAP to watch/log); `-vhost <name>` to scan a specific virtual host on a
  shared IP (pairs with gobuster vhost results, Module 10).
- **show:** `nikto -h http://10.0.0.20 -vhost admin.site.local -useproxy http://127.0.0.1:8080`
- **glossary:** vhost, cgidirs.

### Flow F — Evasion & pacing (the noisy-tool reality)
- **Concept:** nikto is **not stealthy** — it *will* show up in logs and may be blocked by a
  WAF/IPS. For learning about IDS behavior, `-evasion <1-8>` applies encoding/obfuscation tricks; to
  be gentler, `-Pause <sec>` between requests and `-maxtime <time>` to cap the run.
- **show:** `nikto -h http://site -Pause 2 -maxtime 10m`
- **branches:** *blocked / lots of 403s* → a WAF is filtering; pacing/evasion may help on
  authorized tests, but expect detection — that's inherent to nikto.
- **glossary:** evasion.

### Flow G — Update database & plugins
- **Complete layer:** `nikto -update` refreshes the vulnerability database/plugins;
  `nikto -list-plugins` shows what's available; `-Plugins <name>` runs specific ones.
- **show:** `nikto -update`
- **note:** on Kali you can also update via apt (Module T02).

### Flow H — Integration & reading results
- **Complete layer:** chain it — nmap (web port) → gobuster (paths/vhosts) → nikto (server
  vulns) → save a report (`-o`). **Expect false positives:** nikto is signature-based and
  flags *possible* issues; verify each finding manually before reporting.
- **glossary:** false_positive.

---

## 6. Authorization & ethics (before commands shown)

> "Scanning web servers you don't own or aren't authorized to test is illegal, and nikto is
> deliberately loud — it floods logs and trips defenses. Continue only for authorized
> targets." — logged to the audit log.

**Practice legally:** your own servers, DVWA / OWASP Juice Shop / Metasploitable, HTB/THM.

---

## 7. Glossary additions

- **web_vuln_scan** — automated checks for known web-server flaws/misconfigs.
- **tuning (`-Tuning`)** — choose which test categories to run (focus + speed).
- **ssl (`-ssl`)** — force a TLS/HTTPS scan.
- **evasion (`-evasion`)** — request-mangling to study/avoid IDS (nikto stays noisy regardless).
- **plugin** — a modular nikto test (`-list-plugins`, `-Plugins`).
- **false_positive** — a flagged issue that isn't real; verify before reporting.
- **vhost / cgidirs** — scan a named virtual host / where to look for CGI scripts.

---

## 8. Design / token mapping

- Category **Web App / Detect** → tinted tab; authorization + "noisy/will be logged" gate as
  `--status-critical` callout; the verify-false-positives reminder as `--status-warning`.
- Commands in `--font-mono`; "did it work?" gate green/red.

---

## 9. Why this completes the set

nikto rounds out the **web-recon chain** (nmap → gobuster → nikto) and reinforces two honest
themes: it's **noisy by design** (no pretending otherwise) and **signature-based** (verify
false positives). Same template shape — profiles, every flag explained, real branches (no web
server → nmap first, WAF blocks, format mismatch) — closing the CLI-focused Top 10.

*End of Module 11 (nikto) spec v1. — CLI-focused Top 10 COMPLETE.*
