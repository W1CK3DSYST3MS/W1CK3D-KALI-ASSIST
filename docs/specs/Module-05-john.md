# Module 05 — John the Ripper (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, Module 02 (nmap) template, Module 04 (hydra)
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #4**

> Complete tool module for **John the Ripper** (`john`) — an **offline** password-hash
> cracker. Built to the nmap template. **Generate-only.** Where hydra guesses against a live
> service (Module 04), john works on **hashes you already have** — fast, no network, no
> lockouts. Authorized data only (your own systems, lab, CTF).

---

## 1. Manifest

```yaml
module_id: tool.john
name: "John the Ripper — Offline Hash Cracking"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, tool.hydra] }
provides:
  tool: john
  flows: [prepare, quickstart, wordlist_rules, single, incremental, formats, sessions]
  glossary_terms: [hash, offline_cracking, pot_file, unshadow, twojohn, wordlist_mode, single_mode, incremental_mode, rules, format]
content:
  tool: registry/tools/john.yaml
  flows: registry/flows/john_*.yaml
  builder: command_builders/john_builder.py
  glossary: explain/glossary/john.yaml
theme: theme.w1ck3d_systems        # category = Password
source: "authored; verified against john --help / Openwall docs (John the Ripper jumbo)"
license: "project-proprietary lesson text; john is GPL (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: john
display_name: "John the Ripper (jumbo)"
binary_candidates: [john]
install_check: "shutil.which('john'); optional: john --list=build-info"
categories: [password]
one_liner: "Cracks password hashes offline using wordlists, rules, and brute force."
authorization_gate: true            # crack only hashes you're authorized to (own/lab/CTF)
flows: [prepare, quickstart, wordlist_rules, single, incremental, formats, sessions]
```

> **Offline vs online (taught up front):** john needs the **hashes** (from a file, a captured
> dump, `/etc/shadow`, a protected archive…). No network, no account lockout — just CPU vs
> the hash. Live-service guessing is hydra (Module 04). GPU-accelerated cracking is **hashcat**
> (Module 06) — same goal, different engine.

---

## 3. john mapped to the 8 slots

Overall shape: `john [mode/options] [--format=…] <hashfile>`

| Slot | john content | Examples |
|------|--------------|----------|
| 1 PROGRAM | `john` | `john` |
| 2 GLOBAL_OPTIONS | run-wide | `--format=<name>`, `--session=<name>`, `--fork=<n>`, `--pot=<file>` |
| 3 TARGET_PIVOT | the hashes | `hashes.txt` (positional) |
| 4 ACTION_OPTIONS | the cracking mode | `--single`, `--wordlist=<f>`, `--rules`, `--incremental`, `--show` |
| 5 OUTPUT_OPTIONS | results store | the **pot file** (`~/.john/john.pot`); view with `--show` |
| 6 POSITIONAL_ARGS | the hash file (last) | `hashes.txt` |
| 7 ENV/INTERFACE | (n/a) | — |
| 8 EXTRA_FILES | wordlists + prep tools | `--wordlist=rockyou.txt`; prep via `unshadow`, `zip2john`, `ssh2john`, … |

> **Builder note:** the **hash file is positional and goes last**; mode/format flags precede
> it. Cracked results go to the pot file automatically — `--show` reads them back.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | Fills | Behavior | Note shown |
|---------|-------|----------|------------|
| **Auto** | (none) | john picks single → wordlist → incremental automatically | "Just point it at the file." |
| **Wordlist** | `--wordlist=rockyou.txt --rules` | dictionary + mangling rules | "Best bang-for-buck for human passwords." |
| **Targeted format** | `--format=<name> --wordlist=…` | when you know the hash type | "Faster + avoids mis-detection." |
| **Brute (last)** | `--incremental` | exhaustive char combos | "Slow; only for short/odd hashes." |

All generate/reference only; each flag explained inline.

---

## 5. Flows (beginner → advanced)

Pattern per step: `concept` · `flag_detail` · `slot_mapping` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — Prepare the hashes (you can't crack what you can't read)
- **Concept:** john needs hashes in a file, one per line (often `user:hash`). How you get
  them depends on the source:
  - **Linux accounts:** combine passwd+shadow → `sudo unshadow /etc/passwd /etc/shadow > hashes.txt`.
  - **Protected files** (great for CTF/learning): the `*2john` helpers extract a crackable
    hash — `zip2john secret.zip > zip.hash`, `ssh2john id_rsa > key.hash`,
    `rar2john`, `pdf2john`, `office2john`, etc. Then crack the produced `.hash`.
- **show:** `zip2john secret.zip > zip.hash`
- **success:** a hash line is written to the output file.
- **branches:** *which type is this hash?* → Flow F (formats) / identify before brute-forcing.
- **glossary:** hash, unshadow, twojohn.

### Flow B — Quick start (auto) + show results
- **Key flags:** just `john <hashfile>` (auto mode tries single → wordlist → incremental);
  then `john --show <hashfile>` to print cracked creds.
- **show:** `john hashes.txt` → then `john --show hashes.txt`
- **success:** john reports cracked passwords; `--show` lists `user:password`.
- **branches (No):**
  - *"No password hashes loaded"* → wrong/garbled file or john can't detect the type → set
    `--format=` (Flow F).
  - *runs but cracks nothing* → go to a real wordlist + rules (Flow C).
- **glossary:** pot_file.

### Flow C — Wordlist mode + rules (the workhorse)
- **Complete layer:** `--wordlist=<file>` runs a dictionary; `--rules` applies mangling
  (capitalize, append digits, leetspeak…) to multiply each word. rockyou is gzipped on Kali:
  `sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz`.
- **show:** `john --wordlist=/usr/share/wordlists/rockyou.txt --rules hashes.txt`
- **success:** more hashes crack than plain wordlist.
- **branches:** *still nothing* → try a bigger list / different ruleset (`--rules=Jumbo`),
  or confirm the format (Flow F).
- **glossary:** wordlist_mode, rules.

### Flow D — Single crack mode (fast, context-aware)
- **Complete layer:** `--single` uses the **username/GECOS info** in the file to try
  related guesses (name-based passwords). Cheap and often a quick win — run it first.
- **show:** `john --single hashes.txt`
- **glossary:** single_mode.

### Flow E — Incremental / brute force (last resort)
- **Complete layer:** `--incremental` tries character combinations exhaustively (optionally
  a named set, e.g. `--incremental=Digits`). **Slow** — only sensible for short passwords or
  fast hashes; otherwise prefer wordlist+rules or GPU hashcat (Module 06).
- **show:** `john --incremental hashes.txt`
- **glossary:** incremental_mode.

### Flow F — Format selection (avoid mis-detection)
- **Complete layer:** john auto-detects, but on ambiguous hashes set `--format=` explicitly
  (e.g. `raw-md5`, `sha512crypt`, `bcrypt`, `NT`). List what's supported:
  `john --list=formats`. If unsure of the hash type, identify it first (length/prefix; a
  hash-identifier tool).
- **show:** `john --format=raw-md5 --wordlist=rockyou.txt hashes.txt`
- **branches:** *"No password hashes loaded (see FAQ)"* → almost always the wrong
  `--format` or a malformed file.
- **glossary:** format.

### Flow G — Sessions, status, and going faster
- **Complete layer:** `--session=<name>` names a run; `--restore[=name]` resumes an aborted
  one; press any key for live **status**; `--fork=<n>` splits across CPU cores.
- **show:** `john --session=crackA --wordlist=rockyou.txt --rules hashes.txt` →
  resume later: `john --restore=crackA`
- **branches:** *interrupted* → `--restore`; *too slow on slow hashes (bcrypt)* → this is
  where **hashcat + GPU** (Module 06) wins.

---

## 6. Authorization & ethics (before commands shown)

> "Crack only hashes you own or are explicitly authorized to test (your systems, a lab, or a
> CTF). Cracking others' password hashes is illegal." — logged to the audit log.

Cracking is computationally heavy, not noisy — the risk here is **legal/ethical**, not
detection. Great legal practice: CTFs (HackTheBox/TryHackMe), your own `/etc/shadow`, or
files you created.

---

## 7. Glossary additions

- **hash** — a one-way fingerprint of a password; cracking = finding an input that matches.
- **offline_cracking** — working on captured hashes, no live service (vs hydra).
- **pot_file** — `~/.john/john.pot`; where cracked results are stored (so `--show` works).
- **unshadow** — merges `/etc/passwd` + `/etc/shadow` into a crackable file.
- **\*2john** — helpers (`zip2john`, `ssh2john`, `rar2john`, `pdf2john`…) that extract a
  crackable hash from a file/key.
- **wordlist_mode / single_mode / incremental_mode** — dictionary / username-based /
  brute-force strategies.
- **rules** — transformations that mangle wordlist entries to catch variations.
- **format** — the hash type (`--format=`); listed via `john --list=formats`.

---

## 8. Design / token mapping

- Category **Password** → tinted tab. Risk here is legal, so the authorization gate is a
  `--status-critical` callout (no "noisy/lockout" warning needed — it's offline).
- Commands in `--font-mono`; "did it work?" gate green/red; "wrong format" hint as
  `--status-warning`.

---

## 9. Why this fits the template

Same shape as the others: profiles for the on-ramp; every mode/`--rules`/`--format`
explained for depth; real branches (the "No password hashes loaded" = wrong format trap,
nothing cracking → wordlist+rules, slow bcrypt → hashcat). It cements the **offline-vs-online**
pairing (hydra ↔ john) and hands off naturally to **hashcat** (Module 06) for GPU speed on
the same hashes.

*End of Module 05 (John the Ripper) spec v1. Next in CLI Top 10: hashcat.*
