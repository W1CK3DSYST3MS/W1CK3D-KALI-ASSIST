# Coverage Map & Data-Sourcing Plan

**Companion to:** Tool Wizard & Linux Learning Companion — Project Blueprint v1.0
**Purpose:** Define *what the learning tool must cover* to be effective, and *where the
reference content comes from* (existing maintained libraries to download and catalog,
vs. what we must author ourselves).
**Last updated:** 2026-06-21

---

## 0. Key finding from research

Most of what this tool needs to teach is **already maintained, structured, openly
licensed, and downloadable.** The job is mainly to **ingest, normalize, and re-present**
it through the slot model and adaptive stepper — not to write thousands of command
references by hand. That dramatically lowers the build effort.

> **Backend decision (updated):** the **Free Standalone edition is curated-only — NO AI/model
> layer** (runs for everyone, offline, no hardware/subscription barrier). The data is still
> designed so a model layer *could* be added, but that is **reserved for the future
> Enterprise edition**, not the free build. See Blueprint §1 (Editions) and §7.

See §3 for the source catalog. See §4 for the ingest pipeline.

---

## 1. Two coverage domains

To be effective, the tool must cover two distinct but linked domains:

- **Domain A — The security/pentest tooling** ("how to use the tools available to
  these OSes"). The named programs: `nmap`, `gvm-start`, `amass`, `sqlmap`, etc.
- **Domain B — The operating system itself and its functions** ("the system and its
  function"). The Linux fundamentals + the Kali/Parrot-specific quirks that make these
  distros behave differently from generic Linux.

Both are taught with the **same slot model and the same adaptive verify-and-branch
stepper**. A "lesson" on the filesystem and a "flow" on nmap share the same engine.

---

## 2. The coverage taxonomy

### 2.A — Operating-system & shell fundamentals (Domain B)

This is the foundation. Without it, tool commands are memorized blindly. Suggested
top-level lesson categories (each becomes a `LessonSpec` group):

1. **Terminal & shell grammar** — what a shell is; bash command structure (this is
   where the slot model is *introduced*); arguments vs flags vs options; quoting &
   escaping; globbing/wildcards; variables & `$PATH`; command substitution; pipes `|`
   and redirection `>` `>>` `<` `2>`; chaining `&&` `||` `;`; job control & `&`;
   history & shortcuts; aliases; `man` / `--help` / `tldr` themselves.
   *(Kali defaults to **zsh**, not bash — call this out explicitly.)*
2. **Filesystem & files** — Filesystem Hierarchy Standard (what `/etc`, `/var`, `/opt`,
   `/proc` are for); navigation (`cd`, `ls`, `pwd`); file ops (`cp`, `mv`, `rm`,
   `mkdir`, `touch`); viewing (`cat`, `less`, `head`, `tail`); searching (`find`,
   `locate`, `grep`); links (`ln`); archives & compression (`tar`, `gzip`, `zip`).
3. **Permissions & ownership** — the `rwx` model; `chmod` (symbolic + octal); `chown`,
   `chgrp`; `umask`; SUID/SGID/sticky bits; why "permission denied" happens.
4. **Users, groups & privilege** — `sudo` vs `su` vs root; `useradd`/`usermod`/
   `passwd`; `/etc/passwd` & `/etc/shadow`; groups; *(Kali's non-root default user
   model since 2020 — a common source of confusion).*
5. **Package management** — `apt` / `apt-get` / `dpkg`; repositories & `sources.list`;
   signing keys/keyrings; `pip`/`pipx`, `gem`, `go install`; building from source
   (`./configure && make && make install`); **Kali metapackages** (`kali-linux-default`,
   `-headless`, `-large`) and **`kali-tweaks`**; Parrot package specifics.
6. **Processes & services** — `ps`, `top`/`htop`, signals & `kill`; **systemd**
   (`systemctl` start/stop/enable/status), `journalctl`; scheduling (`cron`, `at`,
   systemd timers). *(Directly relevant to `gvm-start`, which manages services.)*
7. **Networking** — interfaces with `ip` (and legacy `ifconfig`); NetworkManager;
   DNS & `/etc/resolv.conf`; routing; `ss`/`netstat`; firewalls (`iptables`,
   `nftables`, `ufw`); **wireless** (`iw`, `iwconfig`, monitor mode, `rfkill`,
   `airmon-ng`); DHCP; proxies/VPN/Tor; `macchanger`.
8. **Storage & devices** — `lsblk`, `fdisk`/`parted`, `mount`/`umount`, `/etc/fstab`;
   USB; loop devices; LUKS encryption; **Kali live-USB persistence**.
9. **Hardware, drivers & kernel modules** — `lspci`/`lsusb`; `lsmod`/`modprobe`;
   wireless drivers & firmware; GPU drivers (needed for `hashcat`); `dmesg`;
   `/proc` & `/sys`.
10. **Boot & kernel** — GRUB basics; kernel parameters; recovery.
11. **Environment & productivity** — env vars; dotfiles; **tmux/screen**; shell
    customization.
12. **Logging & troubleshooting** — where logs live (`/var/log`, journald); how to
    read them; the general "what failed and why" loop (feeds the adaptive stepper's
    branch hints).

### 2.B — Kali & Parrot specific quirks (Domain B, high value)

The differences that "separate them from other Linux environments" — call each out as a
dedicated lesson:

- **Kali:** zsh default shell; non-root default user; `kali-tweaks`; **undercover mode**;
  metapackages; rolling release on Debian *testing*; NetHunter (mobile); persistence;
  default tool layout under the menu.
- **Parrot:** **AnonSurf** (Tor-forcing anonymity, GUI+CLI, iptables-based);
  **firejail** sandboxing by default; editions (Security / Home / HTB); Debian *stable*
  base; built-in privacy posture; MATE/KDE defaults.
- **Shared:** rolling vs stable trade-offs; why a tool present on one may differ on the
  other; menu → CLI mapping (the GUI menu entries are wrappers around CLI commands).

### 2.C — Security tooling (Domain A)

Organize tools by **methodology phase** (matches the user's existing tab headers and
maps cleanly to recognized kill-chain stages). Each tool gets one or more **flows**:

| Phase / category | Representative tools | Example flows |
|------------------|----------------------|---------------|
| Reconnaissance | nmap, masscan, theHarvester, dnsrecon, fierce | host discovery, port/service scan, DNS enum |
| Resource development / OSINT | amass, recon-ng, maltego, spiderfoot | subdomain enum, asset mapping |
| Vulnerability scanning | **GVM/OpenVAS (`gvm-start`)**, nikto, wpscan | start/verify services, web scan |
| Wireless | aircrack-ng suite, kismet, wifite, reaver | monitor mode, capture, handshake |
| Web app | burpsuite, sqlmap, ffuf, gobuster, dirb | dir brute, injection test, fuzzing |
| Exploitation | metasploit, searchsploit, hydra, netexec | search exploit, service login test |
| Password / cred | hashcat, john, hydra | hash ID, wordlist attack (reference) |
| Post-exploitation | netexec, mimikatz (concept), linpeas | enumeration (learning) |
| Forensics | autopsy, volatility, foremost, binwalk, exiftool | image triage, carving, metadata |
| Detect / monitor | suricata, zeek, wireshark, tcpdump | capture, filter, read pcap |
| Protect / harden | ufw/nftables, fail2ban, lynis, anonsurf | rule structure, audit |
| Respond / recover | chntpw, testdisk, photorec, ddrescue | recovery flow structure |
| Reporting | (templates) | organizing output artifacts |

> Coverage goal is eventually "all tools," but each tool enters via the same recipe:
> ToolSpec → FlowSpec(s) → builder → explanations → success criteria + alternatives.

### 2.D — Common helpdesk tasks (the everyday "how do I…")

The frequent, practical requests a helpdesk would field — these should be first-class
guided flows because they're what people actually get stuck on:

- "My wireless adapter won't go into monitor mode."
- "`apt` won't update / GPG key / repository errors."
- "Permission denied — how do I fix it safely?"
- "A service won't start (e.g., GVM/PostgreSQL) — how do I diagnose it?"
- "How do I mount/access another drive or USB?"
- "How do I set up persistence / output directories?"
- "How do I check what's listening on a port?"
- "How do I connect to / troubleshoot the network or DNS?"
- "How do I install a tool that isn't in the default metapackage?"

These map naturally onto the adaptive stepper (try → did it work? → branch).

---

## 3. Source catalog — what to download and catalog

Ranked by usefulness. **License matters**: prefer CC0/CC-BY/MIT for bundling; treat
GPL/AGPL content carefully (link or isolate rather than derive into a closed product).

| Source | Covers | Format | License | Ingest value |
|--------|--------|--------|---------|--------------|
| **tldr-pages** (`github.com/tldr-pages/tldr`) | Practical examples for ~thousands of commands & tools, platform-tagged | Markdown, very regular | **CC-BY 4.0** (pages) | ⭐ High — clean, parseable example lines; great seed for "filled" command views. Attribution required. |
| **cheat/cheatsheets** (`github.com/cheat/cheatsheets`) | Community command cheatsheets | Plain text | **CC0 1.0** (public domain) | ⭐ High — most permissive; safe to bundle/derive freely. |
| **explainshell DB** (`github.com/idank/explainshell`) | Per-flag/option meaning parsed from man pages | SQLite (~70MB dump: `manpages`, `parsed_manpages` with options as JSON) | Verify (code AGPL-class — check before bundling) | ⭐ High for the **slot/flag extraction** — exactly the "what does this flag do + where" data. |
| **Kali tools docs** (`gitlab.com/kalilinux/documentation/kali-tools`) | Per-tool metadata, descriptions, usage examples for Kali's catalog | Structured repo (Markdown/metadata) | Check Kali terms | ⭐ High for Domain A breadth + category tagging; authoritative for Kali. |
| **Linux Command Library** (`github.com/SimonSchubert/LinuxCommandLibrary`) | 5,500+ man pages + ~22 categories + tips, offline-first | App data / structured | Open source (verify) | ⭐ High for **Domain B taxonomy** + offline model; good structural reference. |
| **man pages** (on-device: `man`, `--help`) | Authoritative, version-correct flags for installed tools | roff / text | Per-tool (mixed) | ⭐ Ground truth for accuracy; can be read live on the user's box. |
| **GTFOBins** (`github.com/GTFOBins/GTFOBins.github.io`) | Unix binaries usable for privesc/bypass (technique data) | YAML (`_gtfobins/`) | **GPL-3.0** | Medium — great technique reference; GPL = keep isolated / attribute, don't fold into closed code. |
| **Parrot docs** (`parrotsec.org/docs`) | AnonSurf, firejail, Parrot features/quirks | Web/Markdown | Check terms | ⭐ Authoritative for Parrot-specific lessons. |
| **Kali docs** (`kali.org/docs`) | Metapackages, kali-tweaks, persistence, undercover | Web/Markdown | Check terms | ⭐ Authoritative for Kali-specific lessons. |
| **GNU coreutils / util-linux / Debian docs** | Core OS commands authoritative reference | Texinfo/man | GFDL/GPL (verify) | Medium — ground truth for fundamentals. |

**Licensing rule of thumb for the build:** bundle CC0/CC-BY/MIT freely (with attribution
where required); for GPL/AGPL/GFDL sources, prefer **referencing or fetching at runtime**,
or keep them in an isolated data module, rather than deriving them into the proprietary
core. Confirm each source's exact terms before shipping (tracked in §13 of the blueprint).

---

## 4. Ingest & cataloging pipeline

A repeatable pipeline turns external sources into the internal schema from the blueprint
(`ToolSpec` / `FlowSpec` / `StepSpec` / `LessonSpec`):

```
   [ external source ]
          │  fetch (git clone / DB dump / docs)
          ▼
   [ raw store ]  (versioned, untouched copies — provenance preserved)
          │  parse  (md/yaml/sqlite → normalized records)
          ▼
   [ normalized records ]  (command, flags, examples, descriptions)
          │  map     (assign each flag/value to a SLOT; write what/why/where)
          ▼
   [ slot-structured entries ]
          │  enrich  (success_criteria + alternatives for the stepper)
          ▼
   [ accuracy review gate ]  ← verify against man page / authoritative source
          │  approve (+ record source + license per entry)
          ▼
   [ curated knowledge base ]  → consumed by wizard-core (both editions)
```

**Every catalog entry carries provenance + license fields** (`source`, `source_url`,
`license`, `verified_by`, `verified_date`) so the tool stays auditable and license-safe —
this is also what lets the optional RAG/model layer cite ground truth instead of
inventing flags.

---

## 5. What we must author ourselves (not downloadable)

The downloadable sources give commands, flags, and examples. They do **not** give:

1. **Slot mappings** — assigning each flag/value to one of the 8 slots. (Semi-automatable
   from explainshell's option data, but needs review.)
2. **The what/why/where micro-explanations** in your consistent teaching voice.
3. **`success_criteria`** — "what success looks like" for each step.
4. **`alternatives[]`** — the branch content for the "did it work? No" path. This is the
   genuinely original, high-value IP of the product and the hardest to source.
5. **Kali/Parrot quirk lessons** stitched into coherent guided walkthroughs.

This is where the optional small model helps most: drafting explanations and alternative
steps **from** the curated facts — always reviewed, never authoritative on exact syntax.

---

## 6. Recommended v1 scope (prove the whole loop on a thin slice)

Rather than boil the ocean, validate the full pipeline + engine on a vertical slice:

- **Fundamentals lessons:** shell grammar (introduces slots), permissions, package mgmt,
  services/systemd.
- **Helpdesk flows:** "apt update errors," "service won't start," "permission denied,"
  "monitor mode."
- **Tool flows:** `nmap` basic scan (clean proof of the slot model) + `gvm-start`
  service start/verify (proves the harder, service-oriented case the user wants).
- **One source ingested end-to-end:** tldr-pages (CC-BY, easiest) → through the full
  pipeline → into curated KB → rendered in both editions.

Succeeding here proves the engine, the ingest pipeline, the slot model, the adaptive
stepper, and the licensing workflow all work together — then scaling is repetition.

---

## 7. Open items feeding back into the blueprint

- Confirm exact license terms per source before bundling (esp. explainshell, Kali/Parrot
  docs, Linux Command Library).
- Decide: bundle a snapshot of sources (offline) vs. fetch/update on demand (esp. Termux
  size constraints).
- Decide automation level for slot-mapping (manual vs. explainshell-assisted).
- Define the accuracy-review gate owner/process (who signs off an entry as correct).

*End of Coverage Map & Data-Sourcing Plan v1.0.*
