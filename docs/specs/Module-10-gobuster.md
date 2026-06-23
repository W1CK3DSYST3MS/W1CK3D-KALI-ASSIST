# Module 10 — gobuster (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, nmap template, Module 02
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #9**

> Complete module for **gobuster** — fast brute-force discovery of hidden web content,
> subdomains, and virtual hosts. Built to the project template. **Generate-only.** It's a
> web-recon tool that makes many requests (noisy), so it carries an authorization gate and
> pacing guidance. Targets you own / are authorized to test only.

---

## 1. Manifest

```yaml
module_id: tool.gobuster
name: "gobuster — Content / DNS / VHost Brute-Forcer"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [tool.nmap, fundamentals.shell_grammar] }
provides:
  tool: gobuster
  modes: [dir, dns, vhost, fuzz]
  flows: [first_dir, wordlists_ext, status_filter, perf_tls, auth_headers, dns_mode, vhost_mode, output]
  glossary_terms: [mode, wordlist, extension, status_code, threads, vhost, subdomain, redirect, seclists]
content:
  tool: registry/tools/gobuster.yaml
  flows: registry/flows/gobuster_*.yaml
  builder: command_builders/gobuster_builder.py
  glossary: explain/glossary/gobuster.yaml
theme: theme.w1ck3d_systems        # category = Web App / Recon
source: "authored; verified against gobuster help (v3) / OJ gobuster docs"
license: "project-proprietary lesson text; gobuster is Apache-2.0 (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: gobuster
display_name: "gobuster"
binary_candidates: [gobuster]
install_check: "shutil.which('gobuster'); optional: gobuster version"
categories: [web_app, reconnaissance]
one_liner: "Brute-forces hidden web paths/files, subdomains, or virtual hosts from a wordlist."
authorization_gate: true            # web recon, noisy — authorized targets only
flows: [first_dir, wordlists_ext, status_filter, perf_tls, auth_headers, dns_mode, vhost_mode, output]
```

> **Modes are the pivot:** gobuster's first argument is a **mode** — `dir` (paths/files),
> `dns` (subdomains), `vhost` (virtual hosts), `fuzz` (custom). The mode decides which target
> flag and options apply.

---

## 3. gobuster mapped to the 8 slots

Overall shape: `gobuster <mode> -u|-d <target> -w <wordlist> [options]`

| Slot | gobuster content | Examples |
|------|------------------|----------|
| 1 PROGRAM | `gobuster` | `gobuster` |
| 2 GLOBAL_OPTIONS | run-wide | `-t 50` (threads), `-q` (quiet), `-z` (no progress), `-k` (skip TLS verify), `--no-error` |
| 3 TARGET_PIVOT | mode + target | `dir -u https://site` · `dns -d example.com` · `vhost -u https://site` |
| 4 ACTION_OPTIONS | what to try / keep | `-w <wordlist>`, `-x php,html,txt` (extensions), status filters (`-b`/`-s`), `--exclude-length`, `-r` (follow redirects) |
| 5 OUTPUT_OPTIONS | where results go | `-o results.txt`, `-q` |
| 6 POSITIONAL_ARGS | the mode (first) | `dir` / `dns` / `vhost` |
| 7 ENV/PROXY | routing/TLS | `--proxy http://127.0.0.1:8080`, `-k` |
| 8 EXTRA_FILES | wordlist | `-w /usr/share/seclists/Discovery/Web-Content/common.txt` |

> **Builder note:** the **mode is the positional subcommand** and comes first; the right
> target flag (`-u` for dir/vhost, `-d` for dns) follows. The builder picks the correct
> target flag for the chosen mode.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | Fills | Behavior | Note shown |
|---------|-------|----------|------------|
| **Quick dir** | `dir -t 40` + common.txt | find hidden paths fast | "Start here on a web target." |
| **Dir + files** | adds `-x php,html,txt,bak` | also find files by extension | "Catches pages, not just folders." |
| **Subdomains** | `dns -t 40` + a DNS list | enumerate subdomains | "Map the attack surface." |
| **VHosts** | `vhost --append-domain` | find virtual hosts on one IP | "Sites hiding behind the same server." |

All generate/reference only; every flag explained inline.

---

## 5. Flows (beginner → advanced)

Pattern per step: `concept` · `flag_detail` · `slot_mapping` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — First directory scan (`dir`)
- **Key flags:** `dir -u <url> -w <wordlist>`. Add `-k` for self-signed HTTPS.
- **show:** `gobuster dir -u https://10.0.0.20 -w /usr/share/wordlists/dirb/common.txt -k`
- **success:** found paths print with status codes (e.g., `/admin (Status: 301)`).
- **branches (No):**
  - *connection refused / no web server* → confirm the port is a web service first (nmap,
    Module 02); set the right scheme/port (`-u https://host:8443`).
  - *everything 403/Forbidden* → server may block the scanner UA → set `-a <user-agent>`.
- **glossary:** mode, wordlist, status_code.

### Flow B — Wordlists + extensions
- **Complete layer:** good lists ship with Kali — **dirb** (`/usr/share/wordlists/dirb/
  common.txt`) and **SecLists** (`/usr/share/seclists/Discovery/Web-Content/…` e.g.
  `directory-list-2.3-medium.txt`, `raft-*`). Find files (not just dirs) with
  `-x php,html,txt,bak,zip`.
- **show:** `gobuster dir -u https://site -w /usr/share/seclists/Discovery/Web-Content/common.txt -x php,txt`
- **branches:** *SecLists missing* → `sudo apt install seclists`.
- **glossary:** extension, seclists.

### Flow C — Status-code filtering (version-aware gotcha)
- **Concept:** you want signal, not noise. Two approaches, and **gobuster's default changed
  between versions** — know which you have (`gobuster version`):
  - **blacklist** (modern default hides 404): broaden/narrow with
    `-b "404,403"` (`--status-codes-blacklist`).
  - **whitelist** (older style): `-s "200,204,301,302,307,401"`
    (`--status-codes`) — note you **can't set both** at once.
  - **`--exclude-length <n>`** hides responses of a given size (great for "soft 404" pages
    that return 200 with a fixed body).
- **show:** `gobuster dir -u https://site -w common.txt -b 404,403`
- **branches (No):**
  - *"status-codes and status-codes-blacklist are both set"* → clear one; pick whitelist OR
    blacklist.
  - *flood of false 200s* → use `--exclude-length` on the soft-404 size.
- **glossary:** status_code.

### Flow D — Threads, TLS & reliability
- **Complete layer:** `-t <n>` threads (speed vs load — default 10; raise on robust labs,
  lower if the server struggles or rate-limits); `-k` skip TLS verification (self-signed);
  `--timeout 10s`; `--retry`. Be a good neighbor — high threads hammer the target.
- **show:** `gobuster dir -u https://site -w common.txt -t 50 -k`
- **branches:** *errors/timeouts under load* → lower `-t`, raise `--timeout`.
- **glossary:** threads.

### Flow E — Auth, headers, cookies, redirects
- **Complete layer:** `-c "session=…"` cookies; `-H "Authorization: Bearer …"` (repeatable)
  custom headers; `-a "<user-agent>"`; `-r` follow redirects (otherwise a 301 is just
  reported, not followed); `-P`/`-U` for basic auth.
- **show:** `gobuster dir -u https://site -w common.txt -c "PHPSESSID=abc" -r`
- **glossary:** redirect.

### Flow F — DNS mode (subdomain enumeration)
- **Key flags:** `dns -d <domain> -w <subdomain-list>`; `-i` show resolved IPs; `-r <resolver>`
  use a specific DNS server; `-c` show CNAMEs.
- **show:** `gobuster dns -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -i`
- **success:** discovered subdomains (with IPs if `-i`).
- **branches:** *nothing found / rate-limited* → try a different resolver (`-r 1.1.1.1`), a
  bigger list, or note wildcard DNS (everything resolves → check for a wildcard).
- **glossary:** subdomain.

### Flow G — VHost mode (virtual hosts on one server)
- **Concept:** many sites share one IP, served by the `Host` header. vhost mode brute-forces
  hostnames to find hidden sites.
- **Key flags:** `vhost -u <url> -w <list> --append-domain` (modern gobuster requires
  `--append-domain` to add the base domain to each word).
- **show:** `gobuster vhost -u https://example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain`
- **branches:** *all show same length (false positives)* → filter with `--exclude-length`.
- **glossary:** vhost.

### Flow H — Output & integration
- **Complete layer:** `-o results.txt` saves findings; `-q` for clean output to pipe; feed
  discovered paths/subdomains into the next tool (e.g., nikto on found hosts, Module 11).
- **show:** `gobuster dir -u https://site -w common.txt -o dirs.txt`

---

## 6. Authorization & ethics (before commands shown)

> "Brute-forcing web content/subdomains on targets you don't own or aren't authorized to test
> is illegal and noisy (it floods logs and can stress the server). Continue only for
> authorized targets." — logged to the audit log.

**Practice legally:** your own apps, DVWA/Juice Shop, HTB/THM boxes. Pace with sensible `-t`.

---

## 7. Glossary additions

- **mode** — gobuster's first argument: `dir`, `dns`, `vhost`, `fuzz`.
- **wordlist** — the list of candidates tried (dirb/SecLists on Kali).
- **extension (`-x`)** — file types appended to each word (find files, not just dirs).
- **status_code** — the HTTP response code; filter with `-b` (blacklist) or `-s` (whitelist).
- **threads (`-t`)** — concurrent requests; higher = faster/louder.
- **subdomain / vhost** — DNS subdomains vs name-based virtual hosts on one IP.
- **redirect (`-r`)** — follow 3xx responses instead of just reporting them.
- **seclists** — the big wordlist collection (`sudo apt install seclists`).

---

## 8. Design / token mapping

- Category **Web App / Recon** → tinted tab; authorization + noise gate as `--status-critical`
  callout; thread/pacing tips as `--status-warning`.
- Commands in `--font-mono`; "did it work?" gate green/red; the **status-code whitelist-vs-
  blacklist** + version note highlighted (the main gotcha).

---

## 9. Why this fits the template

Same shape as the others: mode-as-pivot keeps ordering clear, profiles give the on-ramp, and
every flag is explained — with the genuinely common branches surfaced (no web server →
nmap first, soft-404 floods → `--exclude-length`, the whitelist/blacklist "both set" error,
the modern `vhost --append-domain` requirement, wildcard DNS). It chains from nmap (find web
ports) into nikto (Module 11) for vuln-flavored web checks.

*End of Module 10 (gobuster) spec v1. Next in CLI Top 10: nikto (final).*
