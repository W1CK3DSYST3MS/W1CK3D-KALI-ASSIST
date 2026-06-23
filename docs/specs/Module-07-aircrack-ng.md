# Module 07 — aircrack-ng suite (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module (suite/workflow) · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, nmap template, T01 (monitor mode), Module 06 (hashcat)
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #6**

> Complete module for the **aircrack-ng suite** — Wi-Fi security testing: enable monitor
> mode, discover networks, capture a WPA handshake (or PMKID), and crack it. It's a
> **workflow across several binaries** (`airmon-ng`, `airodump-ng`, `aireplay-ng`,
> `aircrack-ng`). Built to the nmap template. **Generate-only.**
>
> ⚠ **Most legally sensitive module so far.** Wi-Fi attacks on networks you don't own are
> illegal in most jurisdictions, and deauthentication actively disrupts real users. This
> module **double-gates** the active steps and assumes your own AP / lab only.

---

## 1. Manifest

```yaml
module_id: tool.aircrack_ng
name: "aircrack-ng — Wi-Fi Security Suite"
version: 1.0.0
type: tool_suite
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [troubleshoot.networking, tool.hashcat] }
provides:
  tool: aircrack-ng
  binaries: [airmon-ng, airodump-ng, aireplay-ng, aircrack-ng]
  flows: [monitor, discover, capture, deauth, crack, pmkid, cleanup, wep_note]
  glossary_terms: [monitor_mode, bssid, essid, channel, handshake, pmkid, deauth, injection, eapol, hc22000]
content:
  tool: registry/tools/aircrack_ng.yaml
  flows: registry/flows/aircrack_*.yaml
  builder: command_builders/aircrack_builder.py
  glossary: explain/glossary/aircrack.yaml
theme: theme.w1ck3d_systems        # category = Wireless; active steps → red double-gate
source: "authored; verified against aircrack-ng suite man pages / aircrack-ng.org docs"
license: "project-proprietary lesson text; aircrack-ng is GPL (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: aircrack-ng
display_name: "aircrack-ng suite"
binary_candidates: [aircrack-ng, airmon-ng, airodump-ng, aireplay-ng]
install_check: "shutil.which('aircrack-ng')"
categories: [wireless]
one_liner: "Capture and crack Wi-Fi (WPA/WPA2) authentication on networks you own/are authorized to test."
authorization_gate: true            # WIRELESS — strong; active steps require a SECOND gate
hardware_note: "Needs a Wi-Fi adapter that supports monitor mode (and injection for deauth). See T01 §5."
flows: [monitor, discover, capture, deauth, crack, pmkid, cleanup, wep_note]
```

> **The whole workflow at a glance:** monitor mode → find the target AP → capture the
> 4-way **handshake** (passively, or by nudging a client off with a deauth) → crack the
> handshake against a wordlist (here, or faster in **hashcat** mode 22000).

---

## 3. Suite mapped to the 8 slots (per binary)

Each binary still follows the slot model; the suite chains them.

| Binary | PROGRAM | GLOBAL/ACTION | TARGET | OUTPUT |
|--------|---------|---------------|--------|--------|
| `airmon-ng` | `airmon-ng` | `start`/`stop`/`check kill` | `<iface>` | (creates `<iface>mon`) |
| `airodump-ng` | `airodump-ng` | `-c <ch>` `--bssid <AP>` | `<ifacemon>` | `-w <prefix>` (→ `.cap`) |
| `aireplay-ng` | `aireplay-ng` | `--deauth <n>` `-a <AP>` `-c <client>` | `<ifacemon>` | (on-air) |
| `aircrack-ng` | `aircrack-ng` | `-w <wordlist>` `-b <BSSID>` | `<capture.cap>` | cracked key to stdout |

> **Builder note:** interface/`<ifacemon>` and the capture file are the pivots; the builder
> always places mode flags first, then the interface or capture file.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | What it does | Note shown |
|---------|--------------|------------|
| **Passive capture** | monitor → discover → capture handshake by waiting | "Least intrusive; just listen." |
| **Active capture** | adds a targeted deauth to speed handshake | "⚠ Disrupts a client — authorized only (2nd gate)." |
| **PMKID (clientless)** | grab PMKID without any client, convert → hashcat | "No deauth needed; needs a supporting AP." |
| **Crack** | run a captured `.cap` against a wordlist | "Offline; or use hashcat 22000 for GPU speed." |

---

## 5. Flows (the workflow, beginner → advanced)

Pattern per step: `concept` · `flag_detail` · `slot_mapping` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — Enable monitor mode (`airmon-ng`)
- **Concept:** capturing Wi-Fi frames needs the adapter in **monitor mode**.
- **Key flags:** `sudo airmon-ng start <iface>` → creates `<iface>mon`. Interfering
  processes (NetworkManager/wpa_supplicant) grab the adapter: `sudo airmon-ng check kill`.
- **show:** `sudo airmon-ng check kill` → `sudo airmon-ng start wlan0`
- **success:** `iw dev` shows a `type monitor` interface (e.g. `wlan0mon`).
- **⚠** `check kill` **stops NetworkManager → you lose normal Wi-Fi/internet** until you
  restart it (Flow G). Adapter must support monitor mode (T01 §5). Shown before the command.
- **glossary:** monitor_mode, injection.

### Flow B — Discover networks (`airodump-ng`)
- **Key flags:** `sudo airodump-ng <ifacemon>` scans all channels; note the target's
  **BSSID** (AP MAC), **channel**, and **ESSID** (name).
- **show:** `sudo airodump-ng wlan0mon`
- **success:** a live list of APs + connected clients.
- **branches:** *target not appearing* → it may be on 5 GHz (adapter/band support), or
  hidden; let it cycle channels.
- **glossary:** bssid, essid, channel.

### Flow C — Capture the handshake (`airodump-ng`, locked)
- **Key flags:** lock to the target and write a capture:
  `-c <channel> --bssid <AP> -w <prefix> <ifacemon>`.
- **show:** `sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon`
- **success:** when a client (re)connects, the top line shows **"WPA handshake: <BSSID>"**;
  files `capture-01.cap` etc. are written.
- **branches (No):**
  - *no handshake appearing* → wait for a client to connect, or use a deauth (Flow D), or
    try PMKID (Flow F).
- **glossary:** handshake, eapol.

### Flow D — Force a handshake with a deauth (`aireplay-ng`) — ⚠ ACTIVE
- **⚠⚠ SECOND authorization gate.** A deauth **kicks a real device off the network** to make
  it reconnect (revealing the handshake). This is **active interference** — only ever on your
  own network / authorized lab.
- **Key flags:** `--deauth <count>` (0 = continuous), `-a <AP BSSID>`, `-c <client MAC>`
  (target one client — gentler than broadcast).
- **show:** `sudo aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 wlan0mon`
- **success:** back in the airodump window, the handshake is captured.
- **branches:** *no injection* → adapter/driver may not support injection
  (`sudo aireplay-ng --test wlan0mon`); see T01 §5 for a compatible adapter.
- **glossary:** deauth, injection.

### Flow E — Crack the handshake (`aircrack-ng`)
- **Key flags:** `-w <wordlist>` `-b <BSSID>` `<capture.cap>`. rockyou is gzipped on Kali
  (gunzip once).
- **show:** `aircrack-ng -w /usr/share/wordlists/rockyou.txt -b AA:BB:CC:DD:EE:FF capture-01.cap`
- **success:** "KEY FOUND! [ password ]" if the passphrase is in the wordlist.
- **branches (No):**
  - *"no valid handshake" / "got 0 handshakes"* → the capture didn't contain a complete
    handshake → back to Flow C/D.
  - *not in wordlist* → bigger/targeted list, or convert to **hashcat 22000** for GPU speed +
    rules/masks (Module 06).
- **glossary:** handshake.

### Flow F — PMKID / clientless capture → hashcat
- **Concept:** many APs leak a **PMKID** that lets you skip waiting for a client/deauth.
- **Flow:** capture with `hcxdumptool` → convert with `hcxpcapngtool` to a `.hc22000` →
  crack in **hashcat -m 22000** (Module 06).
- **show:** `hcxpcapngtool -o hash.hc22000 capture.pcapng` →
  `hashcat -m 22000 -a 0 hash.hc22000 /usr/share/wordlists/rockyou.txt`
- **branches:** *no PMKID* → not all APs are vulnerable; fall back to handshake capture.
- **glossary:** pmkid, hc22000.

### Flow G — Clean up / restore normal Wi-Fi
- **Key flags:** `sudo airmon-ng stop wlan0mon` then `sudo systemctl start NetworkManager`
  (reverses the `check kill` from Flow A).
- **show:** `sudo airmon-ng stop wlan0mon` → `sudo systemctl start NetworkManager`
- **success:** normal Wi-Fi/internet returns (`nmcli device status`).

### Flow H — WEP note (legacy)
- **Concept:** old WEP networks crack differently/easily (IV collection + `aircrack-ng`),
  but WEP is essentially extinct. Mentioned for completeness; modern targets are WPA/WPA2/3.

---

## 6. Authorization & ethics (mandatory; active steps double-gated)

> "Testing Wi-Fi networks you do not own or lack **explicit written permission** to test is
> illegal almost everywhere. Deauthentication disrupts real users' connectivity. Continue
> only for your own network or an authorized lab." — logged to the audit log.

- **Flow D (deauth) and Flow F active capture require a SECOND explicit confirmation.**
- **Practice legally:** your own router, a dedicated test AP, or a wireless lab you control.

---

## 7. Glossary additions

- **monitor_mode** — adapter mode that captures all nearby Wi-Fi frames (T01 §5).
- **injection** — sending crafted frames (needed for deauth); not all adapters support it.
- **bssid / essid / channel** — the AP's MAC / its network name / its radio channel.
- **handshake** — the WPA 4-way auth exchange; capturing it lets you test the passphrase offline.
- **eapol** — the protocol frames that make up the handshake.
- **deauth** — a frame that forces a client to disconnect (active, disruptive).
- **pmkid** — an AP-side value that can enable clientless cracking on some APs.
- **hc22000** — the hashcat mode-22000 format for WPA (via `hcxpcapngtool`).

---

## 8. Design / token mapping

- Category **Wireless** → tinted tab. This module has a **two-tier red gate**: the standard
  authorization callout, plus a **second `--status-critical` confirmation on the active
  deauth/capture steps.** Connectivity-loss (`check kill`) and adapter-support notes as
  `--status-warning`.
- Commands in `--font-mono`; "did it work?" gate green/red.

---

## 9. Why this fits the template

It proves the template handles a **multi-binary workflow**, not just one command: each step
maps to slots, profiles offer passive vs active vs PMKID on-ramps, and branches cover the
real snags (no handshake → deauth/PMKID, no injection → adapter issue, not in wordlist →
hashcat). It chains cleanly into **hashcat (Module 06)** for GPU cracking and leans on
**T01 §5** for the monitor-mode hardware reality — and it carries the strongest ethics
gating in the set, fitting its legal sensitivity.

*End of Module 07 (aircrack-ng) spec v1. Next in CLI Top 10: metasploit.*
