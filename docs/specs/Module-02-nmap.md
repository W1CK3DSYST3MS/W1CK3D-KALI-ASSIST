# Module 02 — nmap (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.6, Design Tokens, Module 01
**Last updated:** 2026-06-22

> The first **complete tool module** and the template for every tool after it. It proves
> the core principle — **simple to use, complete in depth**: a beginner picks a profile
> and answers two prompts; an advanced user sees every flag, scan type, and port state
> explained. Built on the slot model (Module 01) and the adaptive "did it work?" stepper.
>
> **Generate-only.** The app shows and explains the command; the learner runs it in their
> own terminal **against systems they are authorized to scan**, then reports the result.
> The stepper branches on the answer.

---

## 1. Manifest

```yaml
module_id: tool.nmap
name: "nmap — Network Mapper"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, fundamentals.setup_and_securing.kali] }
provides:
  tool: nmap
  flows: [discovery, portscan, service_version, os_detect, udp, nse, timing_stealth, output, full]
  glossary_terms: [host_discovery, port_state, syn_scan, connect_scan, udp_scan, service_detection, os_detection, nse, timing_template, privileged_scan]
content:
  tool: registry/tools/nmap.yaml
  flows: registry/flows/nmap_*.yaml
  builder: command_builders/nmap_builder.py
  glossary: explain/glossary/nmap.yaml
theme: theme.w1ck3d_systems        # category = Reconnaissance → --status-recon (purple)
source: "authored; verified against nmap man page + official docs (nmap.org)"
license: "project-proprietary lesson text; nmap is GPL (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: nmap
display_name: "nmap (Network Mapper)"
binary_candidates: [nmap]
install_check: "shutil.which('nmap'); optional: nmap --version"
categories: [reconnaissance]          # tab color: --status-recon (#561593 purple)
one_liner: "Discovers hosts and the services/ports they expose on a network."
authorization_gate: true              # must confirm authorized-target before showing built command
flows: [discovery, portscan, service_version, os_detect, udp, nse, timing_stealth, output, full]
```

---

## 3. nmap mapped to the 8 slots

This is the fixed assembly order the builder always uses, so the learner never reorders.

| Slot | nmap content | Examples |
|------|--------------|----------|
| 1 PROGRAM | `nmap` | `nmap` |
| 2 GLOBAL_OPTIONS | run-wide behavior | `-v` (verbose), `-n` (no DNS), `-Pn` (skip host discovery), `-T0..5` (timing), `--reason` |
| 3 TARGET_PIVOT | scope (positional) | `192.168.1.10`, `192.168.1.0/24`, `scanme.nmap.org` |
| 4 ACTION_OPTIONS | what to do | scan type `-sS/-sT/-sU/-sn`, ports `-p/-F/--top-ports`, `-sV`, `-O`, `-A`, `--script` |
| 5 OUTPUT_OPTIONS | where results go | `-oN file` `-oX file` `-oG file` `-oA base` |
| 6 POSITIONAL_ARGS | (targets occupy this — same as slot 3 for nmap) | — |
| 7 ENV/INTERFACE | interface/source | `-e <iface>`, `--source-port` |
| 8 EXTRA_FILES | input/aux files | `-iL targets.txt`, `--script-args`, NSE script files |

> **Builder note:** targets are *positional* in nmap. The builder places them as the
> TARGET_PIVOT and never lets scan/output flags drift into that position.

---

## 4. Profiles (the "simple" on-ramp)

Profiles pre-fill the hard slots (2 + 4) so a beginner only supplies **targets** (+ output).

| Profile | Fills | Resulting behavior | Teaching note shown |
|---------|-------|--------------------|---------------------|
| **Quick look** | `-T4 -F` | fast scan of top 100 ports | "Fast and light — a first glance." |
| **Standard** | `-sV -T4 --top-ports 1000` | top 1000 ports + service versions | "The everyday scan." |
| **Thorough** | `-sV -O -T4 -p-` | all 65535 ports, versions + OS guess | "Complete but slower/noisier." |
| **Quiet** | `-sS -T2 -Pn` | slower, stealthier SYN scan | "Lower-noise; needs privileges." |

Profiles are teaching scaffolds — still generate/reference only. Each flag they set is
fully explained inline (the "complete" layer) so the user learns what the profile did.

---

## 5. Flows (beginner → advanced)

Each flow is a guided walkthrough using the adaptive stepper. Common pattern per step:
`concept` (what/why, simple) · `flag_detail` (every flag explained, complete) ·
`slot_mapping` · `try_this` · `success_criteria` · `did_it_work` gate with `alternatives`
· `glossary_refs`.

### Flow A — Host discovery ("who is alive?")
- **Goal:** find live hosts without port scanning. **Slots:** PROGRAM + ACTION(`-sn`) + TARGET.
- **Key flags:** `-sn` (ping/host-discovery only, no port scan), `-n` (skip DNS for speed),
  `--reason` (why a host is considered up).
- **try_this:** `nmap -sn 192.168.1.0/24`
- **success:** a list of hosts reported "up."
- **branches (No):**
  - *no hosts found* → "The network may block ping. Try adding `-Pn` to assume hosts are
    up, or confirm you're on the right subnet (`ip a`)."
  - *very slow* → "Add `-n` to skip DNS, and/or `-T4` to speed timing."
- **glossary:** host_discovery.

### Flow B — Port scan ("what is open?")
- **Goal:** find open ports. **Slots:** + ACTION(scan type + `-p`).
- **Key flags & choices (complete layer):**
  - `-sS` **SYN scan** (default when privileged; fast, half-open) **vs** `-sT` **connect
    scan** (no root needed; completes the TCP handshake, noisier).
  - Port selection: `-p 22,80,443` (list), `-p 1-1000` (range), `-p-` (all 65535),
    `-F` (fast, top 100), `--top-ports N`.
- **try_this (privileged):** `nmap -sS -p 22,80,443 192.168.1.10`
  **(unprivileged):** `nmap -sT -p 22,80,443 192.168.1.10`
- **success:** a port table with states (open/closed/filtered).
- **branches (No):**
  - *"requires root privileges" / `-sS` fails* → "SYN scan needs privileges; use `sudo`,
    or switch to `-sT` (connect scan) which doesn't."
  - *all ports `filtered`* → "A firewall is likely dropping probes. Try `-Pn`, fewer
    ports, or slower timing `-T2`."
  - *host seems down* → "Add `-Pn` to skip host discovery and scan anyway."
- **glossary:** port_state, syn_scan, connect_scan, privileged_scan.

### Flow C — Service & version detection ("what is running?")
- **Goal:** identify the service + version on open ports. **Slots:** + ACTION(`-sV`).
- **Key flags:** `-sV` (probe versions), `--version-intensity 0-9` (depth/noise trade-off),
  `--version-all` (max).
- **try_this:** `nmap -sV -p 22,80,443 192.168.1.10`
- **success:** the port table now shows SERVICE + VERSION columns.
- **branches (No):**
  - *version shows "tcpwrapped"/unknown* → "The service hid its banner; try
    `--version-all` or an NSE script (Flow F)."
- **glossary:** service_detection.

### Flow D — OS detection ("what system is it?")
- **Goal:** fingerprint the OS. **Slots:** + ACTION(`-O`).
- **Key flags:** `-O` (OS detection, needs privileges), `--osscan-guess` (aggressive guess).
- **try_this:** `sudo nmap -O 192.168.1.10`
- **success:** an OS guess with accuracy %.
- **branches (No):**
  - *"requires privileges"* → "Run with `sudo`."
  - *"too many fingerprints / no exact match"* → "Add `--osscan-guess`; accuracy depends on
    open+closed ports being found."
- **glossary:** os_detection.

### Flow E — UDP scan ("the other half of the network")
- **Goal:** find open UDP services (DNS, SNMP, DHCP). **Slots:** + ACTION(`-sU`).
- **Key flags:** `-sU` (UDP scan — slow by nature), often `--top-ports` to keep it sane.
- **try_this:** `sudo nmap -sU --top-ports 20 192.168.1.10`
- **success:** UDP port table (note many show `open|filtered` — explained).
- **branches (No):**
  - *extremely slow* → "UDP is slow by design; limit with `--top-ports`, raise timing, be
    patient. This is normal, not a failure."
- **glossary:** udp_scan, port_state.

### Flow F — NSE scripting ("go deeper")
- **Goal:** run Nmap Scripting Engine checks. **Slots:** + ACTION(`--script`) + EXTRA(`--script-args`).
- **Key flags (complete layer):** `-sC` (default safe scripts), `--script <name|category>`
  (e.g., `default`, `safe`, `vuln`, `http-title`), `--script-args k=v`.
- **try_this:** `nmap -sV --script=default -p 80,443 192.168.1.10`
- **success:** extra script output appears under the relevant ports.
- **branches (No):**
  - *script not found* → "List/locate scripts; check the name/category spelling."
  - *vuln category seems intrusive* → "Prefer `safe`/`default` for learning; some
    categories are noisy or intrusive — only on authorized targets."
- **glossary:** nse.

### Flow G — Timing & stealth ("control noise & speed")
- **Goal:** understand how to go faster or quieter. **Slots:** GLOBAL_OPTIONS.
- **Key flags (complete layer):** `-T0..-T5` (paranoid→insane timing), `-Pn` (skip host
  discovery), `-n` (no DNS), `--max-rate`/`--min-rate`, fragmentation `-f` (concept only).
- **try_this:** `nmap -sS -T2 -Pn -n -p 1-1000 192.168.1.10`
- **success:** scan runs slower/quieter; same result table.
- **branches (No):**
  - *too slow to finish* → "`-T2` is deliberately slow; raise to `-T4` for labs."
  - *still blocked* → "Timing won't beat a strict firewall; this is expected — note it and
    move on."
- **glossary:** timing_template.

### Flow H — Output & reporting ("capture results")
- **Goal:** save results properly. **Slots:** OUTPUT_OPTIONS.
- **Key flags (complete layer):** `-oN file` (normal), `-oX file` (XML), `-oG file`
  (grepable), `-oA base` (all three at once). Directory plan from blueprint output strategy.
- **try_this:** `nmap -sV -p 22,80,443 -oA ./out/scan 192.168.1.10`
- **success:** `scan.nmap`, `scan.xml`, `scan.gnmap` created in `./out/`.
- **branches (No):**
  - *permission denied writing file* → "Pick a writable output dir (e.g., your home), or
    create it first: `mkdir -p ./out`."
- **glossary:** (output formats covered in concept).

### Flow I — Full / aggressive (combined, advanced)
- **Goal:** show how flags combine into one capable command. **Slots:** all.
- **Key flag:** `-A` = OS detection + version + default scripts + traceroute (one switch).
- **try_this:** `sudo nmap -A -T4 -p- -oA ./out/full 192.168.1.10`
- **concept:** "`-A` bundles several actions — convenient but loud. Now that you've learned
  each piece (Flows C/D/F), you can see exactly what `-A` is doing."
- **branches (No):** route the user to whichever sub-behavior failed (version/OS/NSE flows).

---

## 6. Authorization gate (before any built command is shown)

Because nmap scans live systems, the module shows a one-time confirm per session:

> "Only scan systems you own or have explicit written permission to test. Unauthorized
> scanning may be illegal. Continue?"  — logged to the on-device audit log (blueprint §8.3).

For practice, the module points learners to **`scanme.nmap.org`** (nmap's official,
permission-granted practice host) and their own lab/VMs.

---

## 7. Glossary additions

- **host_discovery** — finding which hosts are online before scanning ports.
- **port_state** — nmap's verdict per port: **open** (service listening), **closed**
  (reachable, nothing listening), **filtered** (a firewall blocked the probe),
  plus `open|filtered` (common in UDP — can't tell).
- **syn_scan (`-sS`)** — fast "half-open" TCP scan; needs privileges; default when root.
- **connect_scan (`-sT`)** — full TCP handshake; no privileges needed; noisier.
- **udp_scan (`-sU`)** — scans UDP services; slow by nature.
- **service_detection (`-sV`)** — probes open ports to name the service + version.
- **os_detection (`-O`)** — fingerprints the likely operating system.
- **nse** — Nmap Scripting Engine; bundled scripts for deeper checks (`--script`).
- **timing_template (`-T0..5`)** — preset speed/stealth trade-off (paranoid → insane).
- **privileged_scan** — scans (e.g., `-sS`, `-O`, `-sU`) that need root/sudo.

---

## 8. Design / token mapping (W1CK3D SYSTEMS)

- Category tab **Reconnaissance** → `--status-recon` (purple `#561593`).
- All command/skeleton/filled views → `--font-mono` / `--font-term`.
- "did it work?" gate → YES `--status-secure` (green), NO `--status-warning`/`--status-critical`.
- Port-state coloring in result explanations: open=green, closed=muted, filtered=orange.
- Authorization gate styled as a `--status-critical` (red) callout for emphasis.

---

## 9. Why this module is the template

- **Proves "simple but complete":** profiles + one-prompt on-ramp, with every flag, scan
  type, and port state explained underneath.
- **Exercises the full engine:** multi-flow tool, slot assembly, profiles, rich adaptive
  branches (privilege errors, filtered ports, slow UDP), authorization gate, output plan,
  and theme mapping — all on one tool.
- **Repeatable shape:** every future tool module (sqlmap, gobuster, hydra, gvm…) is
  authored to this exact structure.

*End of Module 02 (nmap) spec v1.*
