# Module T01 — Networking, DNS & Wi-Fi Troubleshooter

**Project:** W1CK3D'S KALI ASSIST · **Type:** Troubleshooter module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** `Troubleshooter-Subsystem.md`, Blueprint v1.8
**Last updated:** 2026-06-22

> The first complete troubleshooter module — the highest-frequency problem area. Built to
> the subsystem template: **symptom-first** entry → triage → guided diagnosis (one command
> at a time, user reports what they saw) → verified fix → if exhausted, **Unresolved Issue
> Log** + curated trusted links. **Generate-only, self-contained, no AI.** Authored at three
> tiers (Basic → Intermediate → Extensive) so it's simple to start and complete to finish.

---

## 1. Manifest

```yaml
module_id: troubleshoot.networking
name: "Networking, DNS & Wi-Fi Troubleshooter"
version: 1.0.0
type: troubleshooter
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar] }
provides:
  symptoms: [no_internet, dns_fail, wifi_connect, adapter_missing, monitor_mode, slow_intermittent]
  glossary_terms: [interface, ip_address, gateway, dns, dhcp, nameserver, rfkill, driver, firmware, monitor_mode, regulatory_domain]
content:
  flows: registry/troubleshoot/networking_*.yaml
  resources: registry/resources/networking_links.yaml
  glossary: explain/glossary/networking.yaml
theme: theme.w1ck3d_systems     # category color: --status-info (blue) for diagnostics
source: "authored; verified against ip/iw/nmcli/rfkill man pages + Kali docs"
license: "project-proprietary"
```

---

## 2. Symptom router (entry)

User picks the symptom that best matches (plain language, no jargon needed):

| # | Symptom (as the user sees it) | Routes to |
|---|-------------------------------|-----------|
| S1 | "I have no internet at all" | §4 |
| S2 | "Some things work but websites won't load by name" | §5 (DNS) |
| S3 | "My Wi-Fi won't connect / I see no networks" | §6 |
| S4 | "My Wi-Fi/network adapter isn't showing up at all" | §7 (drivers/firmware) |
| S5 | "I can't get monitor mode working" (security tooling) | §8 |
| S6 | "It connects but is slow or keeps dropping" | §9 |

**Triage (asked once, used by all):**
- Wired (Ethernet) or Wi-Fi?
- Did it work before today — what changed (update, reboot, new location)?
- Is this a built-in adapter or a USB one?

---

## 3. The universal first-line ladder (shared by S1/S2)

Run one at a time; report what you see. Each answer narrows the cause.

1. **Do you have an IP address?** → `ip a`
   *Look for:* an `inet 192.168.x.x` (or similar) line under your interface (not just
   `127.0.0.1`). · *No IP →* §4 Basic (link/DHCP). · *Has IP →* step 2.
2. **Is there a default route?** → `ip route`
   *Look for:* a line starting `default via …`. · *Missing →* §4 (gateway/route). · *Present →* step 3.
3. **Can you reach the internet by number?** → `ping -c3 1.1.1.1`
   *Replies →* networking works; it's almost certainly **DNS** → §5. · *No replies →* §4.
4. **Can you reach it by name?** → `ping -c3 example.com`
   *Fails but step 3 worked →* **DNS** → §5.

---

## 4. S1 — No internet at all

### Basic
- **Fix 1 — restart the network stack:** `sudo systemctl restart NetworkManager`
  *Verify:* re-run `ip a` → expect an IP within ~10s. *Why:* clears a stuck manager/DHCP.
- **Fix 2 — bring the interface up:** `sudo ip link set <iface> up` (use the name from
  `ip a`, e.g. `eth0`, `wlan0`). *Verify:* `ip a` shows `state UP`.
- **Fix 3 — Wi-Fi soft-blocked?** `rfkill list` → if "Soft blocked: yes",
  `sudo rfkill unblock wifi`. *Verify:* `rfkill list` shows "no".

### Intermediate
- **Check NetworkManager is running:** `systemctl status NetworkManager`
  (*not* running → `sudo systemctl enable --now NetworkManager`).
- **List/inspect connections:** `nmcli device status` and `nmcli connection show`.
- **Renew addressing:** `sudo nmcli device reapply <iface>` or reconnect
  `nmcli device connect <iface>`.
- **No gateway?** confirm `ip route` has a `default via`; if absent, the DHCP server isn't
  providing one — reconnect, or (lab only) add a static route.

### Extensive
- Static IP config via `nmcli` when DHCP is unavailable.
- `dmesg | grep -i eth` / `-i wlan` for link/driver errors.
- VPN/proxy left half-configured (check `nmcli connection show --active`, env `http_proxy`).
- Conflicting manager (e.g., `systemd-networkd` vs NetworkManager) both enabled.
- `journalctl -u NetworkManager -e` — read the actual failure.

**⚠ destructive note:** stopping NetworkManager (e.g., for manual config) drops all
managed connections. Warned before shown.

---

## 5. S2 — DNS failures (IP works, names don't)

### Basic
- **Confirm the symptom:** `ping -c3 1.1.1.1` works **and** `ping -c3 example.com` fails →
  it's DNS.
- **Check resolvers:** `cat /etc/resolv.conf` → is there a `nameserver` line?
- **Fix — set a working resolver via NetworkManager** (don't hand-edit resolv.conf if NM
  manages it): `nmcli connection modify <name> ipv4.dns "1.1.1.1 9.9.9.9"` then
  `nmcli connection up <name>`. *Verify:* `ping example.com` resolves.

### Intermediate
- **Is systemd-resolved in play?** `resolvectl status` (if `resolv.conf` points to
  `127.0.0.53`, resolved is the stub). Check `systemctl status systemd-resolved`.
- **Test a specific resolver directly:** `nslookup example.com 1.1.1.1` or
  `dig @1.1.1.1 example.com` → isolates "DNS server down" vs "local config wrong".

### Extensive
- resolv.conf being overwritten (who owns it: NM vs resolved vs manual) — pick one source
  of truth.
- Split-DNS / VPN pushing bad resolvers.
- `/etc/nsswitch.conf` `hosts:` ordering; stale `/etc/hosts` entries.
- Captive portal intercepting DNS (see S3 extensive).

---

## 6. S3 — Wi-Fi won't connect / no networks shown

### Basic
- **Unblock radios:** `rfkill list` → `sudo rfkill unblock all`.
- **See networks:** `nmcli device wifi list` (rescan: `nmcli device wifi rescan`).
- **Connect:** `nmcli device wifi connect "<SSID>" password "<password>"`.
  *Verify:* `nmcli device status` shows the Wi-Fi device `connected`.

### Intermediate
- **Wrong password / auth loop:** delete the saved profile and re-add:
  `nmcli connection delete "<SSID>"` then reconnect.
- **Radio present but no scan results:** confirm the interface exists (`iw dev`); check
  `nmcli radio wifi` is `enabled` (`nmcli radio wifi on`).
- **Hidden SSID:** `nmcli device wifi connect "<SSID>" password "<pw>" hidden yes`.

### Extensive
- **Captive portal:** connects but no internet until you log in — open a browser to any
  http site; check `nmcli` reports "portal".
- **MAC randomization** breaking allow-lists: set
  `nmcli connection modify "<SSID>" wifi.cloned-mac-address permanent`.
- **Regulatory domain** hiding channels: `iw reg get` → `sudo iw reg set <CC>`.
- **5GHz/6GHz channels** unsupported by driver — confirm band support.
- Driver/firmware faults → go to S4.

---

## 7. S4 — Adapter not recognized / interface missing (drivers & firmware)

### Basic
- **Is the device seen by the system at all?**
  built-in/PCIe → `lspci -nnk | grep -iA3 net`; USB → `lsusb`.
  *Look for:* your adapter listed, and a `Kernel driver in use:` line (PCIe).
- **No driver bound / firmware errors?** `sudo dmesg | grep -iE 'firmware|wlan|driver'`
  *Look for:* "failed to load firmware" / "direct firmware load failed".

### Intermediate
- **Install missing firmware** (common on fresh Kali): e.g.
  `sudo apt update && sudo apt install firmware-iwlwifi` (Intel),
  `firmware-realtek` (Realtek), `firmware-atheros`, then reload the module or reboot.
  *Verify:* `ip a` / `iw dev` now lists the interface.
- **Module loaded?** `lsmod | grep <driver>`; load with `sudo modprobe <driver>`.

### Extensive
- USB adapter needing an out-of-tree driver (e.g., certain Realtek chipsets) — identify the
  chipset from `lsusb`, then the matching DKMS driver package; note kernel-header
  requirements (`linux-headers-$(uname -r)`).
- Adapter works on another kernel but not the current rolling kernel (regression) — check
  `dmesg`, consider a known-good kernel.
- Power/USB issues (powered hub) for high-draw adapters.

**Authorization/authenticity note:** only install drivers/firmware from Kali/Debian repos
or the chipset vendor; third-party driver blobs are a supply-chain risk.

---

## 8. S5 — Monitor mode won't work (security tooling)

> **Authorization:** monitor mode / packet capture is for networks you own or are
> explicitly authorized to test. The module states this before showing commands.

### Basic
- **Does the adapter support monitor mode?** `iw list | grep -A10 "Supported interface
  modes"` → look for `* monitor`. *Not listed →* this chipset can't do it (hardware limit);
  see S4 for a compatible adapter.
- **Enable it:** `sudo airmon-ng start <iface>` → creates e.g. `wlan0mon`.
  *Verify:* `iw dev` shows the interface in `type monitor`.

### Intermediate
- **Interfering processes:** NetworkManager/wpa_supplicant grab the adapter.
  `sudo airmon-ng check` lists them; `sudo airmon-ng check kill` stops them.
  **⚠ destructive:** this stops NetworkManager → **you lose normal Wi-Fi/internet** until
  you restart it (`sudo systemctl start NetworkManager`). Warned before shown.
- **Manual method:** `sudo ip link set <iface> down` →
  `sudo iw dev <iface> set type monitor` → `sudo ip link set <iface> up`.

### Extensive
- Driver supports monitor but not injection — test with `sudo aireplay-ng --test <ifacemon>`.
- Channel setting: `sudo iw dev <ifacemon> set channel <n>`.
- Reverting cleanly: `sudo airmon-ng stop <ifacemon>` then restart NetworkManager.
- Regulatory domain limiting channels (see S3 extensive).

---

## 9. S6 — Connects but slow / keeps dropping

### Basic
- Signal/quality: `nmcli -f IN-USE,SSID,SIGNAL,CHAN device wifi` (low SIGNAL → distance/AP).
- Quick reset: `nmcli device disconnect <iface>` then `connect`.

### Intermediate
- Channel congestion (pick a clearer channel on the AP); 2.4 vs 5 GHz band.
- Power saving causing drops: check/disable adapter power management (`iw dev <iface> get
  power_save`; set off via NetworkManager `wifi.powersave`).
- Background updates/large transfers saturating the link.

### Extensive
- Driver-specific power-save bugs (`dmesg`, module parameters).
- MTU/MSS issues on some links; roaming between APs; intermittent DNS (cross-ref S2).
- Hardware: antenna/USB seating, interference sources.

---

## 10. When known steps are exhausted (§6B applied)

Generate the **Unresolved Issue Log** — networking fields:
- symptom + triage answers (wired/Wi-Fi, what changed, built-in/USB);
- outputs the user reported for each step run: `ip a`, `ip route`, `ping` results,
  `nmcli device status`, `rfkill list`, relevant `dmesg`/`journalctl` lines;
- environment: Kali version, kernel (`uname -r`), adapter chipset (`lspci`/`lsusb`).
- *(No secrets — Wi-Fi passwords never logged.)*

Then offer **curated trusted links** (user searches themselves):
- Kali docs (kali.org/docs) · Kali forums (forums.kali.org) · Kali bug tracker
- Debian wiki — WiFi/network pages (wiki.debian.org)
- Arch Wiki — Network configuration / Wireless (wiki.archlinux.org)
- Unix & Linux Stack Exchange (unix.stackexchange.com)
- Chipset/driver project pages (from `lspci`/`lsusb` identifiers)
- On-system: `man ip`, `man nmcli`, `man iw`, `iw --help`

---

## 11. Glossary (shipped with this module)

- **interface** — a network device (e.g., `eth0` wired, `wlan0` Wi-Fi).
- **ip_address** — the address your machine holds on a network (from `ip a`).
- **gateway** — the router your traffic exits through (the `default via` in `ip route`).
- **dns / nameserver** — translates names (example.com) to IPs; set in resolv.conf/NM.
- **dhcp** — auto-assigns IP/gateway/DNS from the network.
- **rfkill** — soft/hard radio block; can disable Wi-Fi entirely.
- **driver / firmware** — kernel module + chip code needed for an adapter to work.
- **monitor mode** — a Wi-Fi mode that captures all nearby traffic (for authorized testing).
- **regulatory_domain** — country setting that governs allowed channels/power.

---

## 12. Design, safety, audit

- **Tokens:** diagnostic steps in `--font-mono`; "did it work?" gate green/red; destructive
  steps (stopping NetworkManager, `airmon-ng check kill`) as `--status-critical` callouts
  with a "what this does / how to undo" note first.
- **Generate-only:** all commands shown for the user to run; nothing executed.
- **Audit (no secrets):** symptom, tier reached, fix applied?, resolved?
- **Cross-links:** `man`/glossary inline; on exhaustion → Issue Log + §10 links.

---

## 13. Why this is the troubleshooter template

Proves the full subsystem on the hardest-working area: symptom router, shared diagnostic
ladder, three tiers from one-line fixes to driver/firmware deep dives, realistic adaptive
branches, destructive-action guardrails, the Issue-Log exhaustion path, and the
security-tooling case (monitor mode). Every future troubleshooter module (apt/keys/certs,
services/systemd, permissions) is authored to this shape.

*End of Module T01 (Networking) spec v1.*
