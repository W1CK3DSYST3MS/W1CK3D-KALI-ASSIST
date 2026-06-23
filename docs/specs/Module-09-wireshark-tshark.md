# Module 09 — Wireshark / tshark (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, nmap template, T01, Module 07
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #8**

> Complete module for **Wireshark** and its CLI engine **tshark** — packet capture and
> analysis (mostly **defensive / blue-team**). CLI-first per this tool's model: the focus is
> **tshark** and the suite (`dumpcap`, `capinfos`, `editcap`, `mergecap`), with a note on the
> Wireshark GUI for visual work. Built to the project template. **Generate-only.**
>
> ⚠ Capturing traffic is **privacy-sensitive** — only on networks/traffic you own or are
> authorized to monitor.

---

## 1. Manifest

```yaml
module_id: tool.wireshark
name: "Wireshark / tshark — Traffic Analysis"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [troubleshoot.networking, tool.nmap] }
provides:
  tool: tshark
  binaries: [tshark, dumpcap, capinfos, editcap, mergecap, wireshark]
  flows: [setup_caps, live_capture, filters, read_pcap, fields_csv, stats, follow_stream, file_utils, gui, tls]
  glossary_terms: [packet, pcap, interface, capture_filter, display_filter, bpf, promiscuous, stream, snaplen, protocol_hierarchy]
content:
  tool: registry/tools/tshark.yaml
  flows: registry/flows/tshark_*.yaml
  builder: command_builders/tshark_builder.py
  glossary: explain/glossary/tshark.yaml
theme: theme.w1ck3d_systems        # category = Detect/Forensics (blue) tint
source: "authored; verified against tshark/wireshark-filter man pages + wireshark.org docs"
license: "project-proprietary lesson text; Wireshark is GPL (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: tshark
display_name: "tshark (Wireshark CLI)"
binary_candidates: [tshark, wireshark, dumpcap]
install_check: "shutil.which('tshark')"
categories: [detect, forensics, network]
one_liner: "Captures and dissects network packets; filter, extract, and summarize traffic."
authorization_gate: true            # PRIVACY — capture only your own/authorized traffic
flows: [setup_caps, live_capture, filters, read_pcap, fields_csv, stats, follow_stream, file_utils, gui, tls]
```

---

## 3. tshark mapped to the 8 slots

Overall shape: `tshark [global] -i <iface>|-r <file> [filters] [output]`

| Slot | tshark content | Examples |
|------|----------------|----------|
| 1 PROGRAM | `tshark` | `tshark` |
| 2 GLOBAL_OPTIONS | run-wide | `-n` (no name resolution), `-q` (quiet, for stats), `-c <n>` (packet count), `-a duration:<s>` (autostop) |
| 3 TARGET_PIVOT | the **source** | `-i <iface>` (live) **or** `-r <file.pcap>` (read) |
| 4 ACTION_OPTIONS | what to keep/show | **capture** filter `-f "BPF"`, **display** filter `-Y "wireshark"`, fields `-T fields -e …`, stats `-z …`, `-d` decode-as |
| 5 OUTPUT_OPTIONS | where results go | `-w out.pcap` (save packets), `-T fields -E header=y -E separator=,` (CSV-ish) |
| 6 POSITIONAL_ARGS | (none — all flags) | — |
| 7 ENV/INTERFACE | capture setup | `-D` (list interfaces), `-s <snaplen>`, `-p` (no promiscuous) |
| 8 EXTRA_FILES | inputs/keys | `-r input.pcap`, TLS key log for decryption |

> **Builder note:** the **source is either `-i` (live) or `-r` (file)** — exactly one fills
> slot 3. The builder won't let you set both.

---

## 4. The one concept to nail: capture vs display filters

The single biggest tshark/Wireshark confusion — **two different filter languages:**

| | Capture filter (`-f`) | Display filter (`-Y`) |
|--|----------------------|----------------------|
| Syntax | **BPF / libpcap** | **Wireshark** |
| When | at capture time (drops packets before saving) | after capture (hides, keeps file intact) |
| Example | `-f "tcp port 80"` | `-Y "http"` |
| More | `host 10.0.0.5`, `port 53`, `not arp` | `ip.addr==10.0.0.5 && tcp.port==443`, `http.request` |

Teach this once, prominently — most "why isn't my filter working?" issues are using the
wrong language in the wrong place.

---

## 5. Profiles (the "simple" on-ramp)

| Profile | Fills | Behavior | Note shown |
|---------|-------|----------|------------|
| **Quick capture** | `-i <iface> -c 100` | grab 100 packets to screen | "A fast look at live traffic." |
| **Capture to file** | `-i <iface> -a duration:60 -w cap.pcap` | record 60s to a file | "Save for offline analysis." |
| **Read & filter** | `-r cap.pcap -Y "<filter>"` | analyze a saved file | "No capture rights needed." |
| **Overview stats** | `-r cap.pcap -q -z io,phs` | protocol breakdown | "What's in this capture?" |

---

## 6. Flows (beginner → advanced)

Pattern per step: `concept` · `flag_detail` · `slot_mapping` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — Capture privileges & list interfaces
- **Concept:** capturing needs privilege. On Kali, allow non-root capture by adding yourself
  to the `wireshark` group (one-time): `sudo dpkg-reconfigure wireshark-common` (choose "Yes")
  → `sudo usermod -aG wireshark $USER` → **log out/in**. Otherwise run with `sudo`.
- **List interfaces:** `tshark -D` (numbers + names).
- **show:** `tshark -D`
- **success:** your interfaces list (e.g., `1. eth0`, `2. wlan0`).
- **branches:** *"you don't have permission to capture"* → group step above, or `sudo`.
- **glossary:** interface, promiscuous.

### Flow B — Live capture basics
- **Key flags:** `-i <iface>`; limit with `-c <count>` and/or `-a duration:<s>`; save with
  `-w <file>`; `-n` skips slow DNS lookups.
- **show:** `tshark -i eth0 -c 50 -n` · save: `tshark -i eth0 -a duration:60 -w cap.pcap`
- **success:** packets scroll (or a file is written).
- **branches:** *nothing shown* → wrong interface (`-D`), or no traffic on it; generate some.
- **glossary:** packet, pcap, snaplen.

### Flow C — Capture vs display filters (apply §4)
- **show (capture/BPF):** `tshark -i eth0 -f "tcp port 80"`
- **show (display/Wireshark):** `tshark -r cap.pcap -Y "http.request"`
- **branches (No):**
  - *filter rejected at capture* → you used Wireshark syntax with `-f`; switch to BPF (or use
    `-Y` after reading).
  - *`-Y` finds nothing* → check field names (`ip.addr` not `ip`); confirm the traffic exists.
- **glossary:** capture_filter, display_filter, bpf.

### Flow D — Read & filter a saved pcap
- **Key flags:** `-r <file>` + `-Y "<display filter>"`. No capture rights needed — great for
  analyzing captures from elsewhere (e.g., an aircrack-ng capture, Module 07).
- **show:** `tshark -r cap.pcap -Y "dns" -n`
- **success:** only matching packets print.

### Flow E — Extract specific fields (CSV-style)
- **Complete layer:** `-T fields -e <field> -e <field> …` with `-E header=y -E separator=,`
  produces tabular output you can pipe to a file or analysis tool.
- **show:** `tshark -r cap.pcap -Y "http.request" -T fields -e ip.src -e http.host -e http.request.uri -E header=y -E separator=,`
- **branches:** *empty columns* → field name typo or those fields aren't in matched packets.

### Flow F — Statistics (what's in this traffic?)
- **Complete layer (use `-q -z …`):**
  - `-z io,phs` protocol hierarchy (what protocols, how much)
  - `-z conv,tcp` TCP conversations; `-z endpoints,ip` talkers
  - `-z http,tree` HTTP stats; `-z dns,tree`
- **show:** `tshark -r cap.pcap -q -z io,phs`
- **glossary:** protocol_hierarchy.

### Flow G — Follow / reassemble a stream
- **Complete layer:** `-z follow,tcp,ascii,<stream#>` reassembles one TCP conversation (e.g.,
  to read an HTTP exchange). Find stream numbers via `tcp.stream` field.
- **show:** `tshark -r cap.pcap -q -z follow,tcp,ascii,0`
- **glossary:** stream.

### Flow H — File utilities (the rest of the suite)
- **Complete layer:**
  - `capinfos cap.pcap` — summary (packet count, duration, size).
  - `editcap` — trim/split: `editcap -c 1000 big.pcap part.pcap` (split into 1000-pkt files);
    `editcap -A "<start>" -B "<end>"` time-slice.
  - `mergecap -w all.pcap a.pcap b.pcap` — combine captures.
  - `dumpcap` — the lightweight capture engine tshark uses under the hood (lower overhead for
    long captures): `dumpcap -i eth0 -w cap.pcap`.
- **show:** `capinfos cap.pcap`

### Flow I — Wireshark GUI (when visual is better)
- **Concept:** for deep manual analysis the **GUI** shines — same **display filter** syntax in
  the top bar, color rules, "Follow Stream" right-click, Statistics menus. Launch `wireshark`
  (or open a file: `wireshark cap.pcap`). tshark and Wireshark share the filter language, so
  skills transfer both ways.

### Flow J — TLS decryption (advanced, your own keys)
- **Concept:** HTTPS is encrypted; you can only decrypt traffic for which **you legitimately
  have the keys** — e.g., a browser `SSLKEYLOGFILE` you set on your own machine, or a server
  private key you own. Point tshark/Wireshark at the key log to decrypt. Authorized/own
  traffic only.
- **branches:** *still encrypted* → wrong/missing key material; modern PFS ciphers need the
  key log, not just a server key.

---

## 7. Authorization & privacy (before commands shown)

> "Capturing network traffic can expose other people's private data and may be illegal on
> networks you don't own or aren't authorized to monitor. Capture only your own traffic, your
> own lab, or with explicit permission." — logged to the audit log.

Defensive/learning use is great on **your own machine's traffic**, a lab, or captures you're
given for analysis.

---

## 8. Glossary additions

- **packet / pcap** — a unit of network data / the capture file format.
- **interface** — the NIC you capture on (`-D` lists them).
- **capture_filter (`-f`, BPF)** — drops packets *before* saving; libpcap syntax.
- **display_filter (`-Y`, Wireshark)** — hides packets *after* capture; Wireshark syntax.
- **bpf** — Berkeley Packet Filter, the capture-filter language.
- **promiscuous** — capturing all frames the NIC sees, not just yours (`-p` disables).
- **stream** — a reassembled conversation (e.g., one TCP session).
- **snaplen (`-s`)** — how many bytes of each packet to keep.
- **protocol_hierarchy (`-z io,phs`)** — a breakdown of protocols in a capture.

---

## 9. Design / token mapping

- Category **Detect / Forensics** → blue (`--status-info`) tint (defensive flavor). Privacy
  gate as a `--status-critical` callout (capturing others' data).
- Commands in `--font-mono`; "did it work?" gate green/red; the capture-vs-display filter box
  highlighted (most common confusion).

---

## 10. Why this fits the template

Same shape as the others, with one signature teaching beat: the **capture-filter vs
display-filter** distinction front-and-center, because it's the universal stumbling block.
Profiles cover capture vs read-only analysis; flows go from `-D` to field extraction, stats,
stream-follow, the file utilities, and the GUI — with the realistic branches (permission to
capture, wrong filter language, empty fields). It pairs with T01 (interfaces/monitor mode),
nmap (what's on the wire), and Module 07 (analyzing Wi-Fi captures).

*End of Module 09 (Wireshark/tshark) spec v1. Next in CLI Top 10: gobuster.*
