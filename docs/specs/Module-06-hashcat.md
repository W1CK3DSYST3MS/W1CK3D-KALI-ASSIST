# Module 06 — hashcat (Complete Tool Module)

**Project:** W1CK3D'S KALI ASSIST · **Type:** Tool module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** Blueprint v1.8, nmap template, Module 05 (john)
**Last updated:** 2026-06-22 · **CLI-focused Top 10: #5**

> Complete tool module for **hashcat** — GPU-accelerated **offline** hash cracking. Same goal
> as john (Module 05), different engine: hashcat is built for **speed on a GPU** and is the
> right tool for slow hashes (bcrypt) and big keyspaces (WPA, NTLM). Built to the nmap
> template. **Generate-only.** Authorized data only.

---

## 1. Manifest

```yaml
module_id: tool.hashcat
name: "hashcat — GPU Hash Cracking"
version: 1.0.0
type: tool
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, tool.john] }
provides:
  tool: hashcat
  flows: [identify_mode, wordlist, rules, mask, hybrid, show_output, performance, wpa]
  glossary_terms: [hash_mode, attack_mode, mask, charset, rule, potfile, workload, optimized_kernel, increment, gpu_opencl]
content:
  tool: registry/tools/hashcat.yaml
  flows: registry/flows/hashcat_*.yaml
  builder: command_builders/hashcat_builder.py
  glossary: explain/glossary/hashcat.yaml
theme: theme.w1ck3d_systems        # category = Password
source: "authored; verified against hashcat --help / hashcat.net wiki"
license: "project-proprietary lesson text; hashcat is MIT (referenced, not bundled)"
```

---

## 2. ToolSpec

```yaml
tool_id: hashcat
display_name: "hashcat"
binary_candidates: [hashcat]
install_check: "shutil.which('hashcat'); optional: hashcat -I  # device info"
categories: [password]
one_liner: "Cracks password hashes very fast using your GPU, by wordlist or mask."
authorization_gate: true            # crack only hashes you're authorized to (own/lab/CTF)
flows: [identify_mode, wordlist, rules, mask, hybrid, show_output, performance, wpa]
hardware_note: "Best with a supported GPU + OpenCL drivers; CPU-only works but is slow."
```

> **john vs hashcat (taught up front):** both crack offline. **john** is CPU-friendly and
> great for mixed/unknown hashes and quick wins; **hashcat** is GPU-fast and wins on slow
> hashes and huge keyspaces. Same hashes, pick the engine that fits.

---

## 3. hashcat mapped to the 8 slots

Overall shape: `hashcat -m <type> -a <attack> [options] <hashfile> <wordlist|mask>`

| Slot | hashcat content | Examples |
|------|-----------------|----------|
| 1 PROGRAM | `hashcat` | `hashcat` |
| 2 GLOBAL_OPTIONS | run-wide | `-w 3` (workload), `-O` (optimized kernels), `-D 1,2` (device types), `--session=<n>`, `--status` |
| 3 TARGET_PIVOT | the hashes | `hashes.txt` (positional) |
| 4 ACTION_OPTIONS | **what + how** | `-m <hash-type>` (**critical**), `-a <attack-mode>`, `-r <rules>`, `--increment`, `--username`, `--show` |
| 5 OUTPUT_OPTIONS | results | `-o cracked.txt`; potfile `~/.hashcat/hashcat.potfile` |
| 6 POSITIONAL_ARGS | hashfile then wordlist/mask | `hashes.txt rockyou.txt` · `hashes.txt ?u?l?l?l?d?d?d?d` |
| 7 ENV/DEVICE | GPU/CPU selection | `-d 1` (device id), `-I` (list devices) |
| 8 EXTRA_FILES | wordlists / rules / masks | `rockyou.txt`, `rules/best64.rule`, mask files |

> **Builder note:** order is `-m … -a … <options> <hashfile> <wordlist-or-mask>`. The hash
> file and the wordlist/mask are **positional and come last, in that order** — the builder
> enforces it so it's never the user's job.

---

## 4. Profiles (the "simple" on-ramp)

| Profile | Fills | Behavior | Note shown |
|---------|-------|----------|------------|
| **Wordlist** | `-a 0` + rockyou | dictionary attack | "Start here for human passwords." |
| **Wordlist + rules** | `-a 0 -r rules/best64.rule` | dictionary × mangling | "Big win for little cost." |
| **Mask (targeted)** | `-a 3` + a pattern | brute a known shape (e.g. 8 chars) | "When you know the format." |
| **Benchmark** | `-b` | measure your hardware speed | "See what your GPU can do." |

The user must still set `-m` (hash type) — that's the one thing profiles can't guess.

---

## 5. Flows (beginner → advanced)

Pattern per step: `concept` · `flag_detail` · `slot_mapping` · `show_command` ·
`success_criteria` · `did_it_work` + `alternatives` · `glossary_refs`.

### Flow A — Identify the hash type (`-m`) — do this first
- **Concept:** hashcat needs the **exact hash mode number** (`-m`). Wrong `-m` = it never
  cracks (or errors). This is the #1 mistake.
- **Find it:** `hashcat --identify hashes.txt` (newer builds), or match against
  `hashcat --example-hashes | less`, or reason from length/prefix (`$2b$`=bcrypt→3200,
  32-hex=MD5→0, NTLM→1000, `$6$`=sha512crypt→1800, WPA→22000).
- **show:** `hashcat --identify hashes.txt`
- **success:** you have the right `-m` number for the next flow.
- **branches:** *ambiguous* → try the most likely; a wrong `-m` fails fast, so test.
- **glossary:** hash_mode.

### Flow B — Wordlist (straight) attack — `-a 0`
- **Key flags:** `-a 0` (straight/dictionary), `-m <type>`, then `<hashfile> <wordlist>`.
- **show:** `hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt`
  (rockyou is gzipped on Kali → `sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz` once).
- **success:** cracked lines appear; check with `--show` (Flow F).
- **branches (No):**
  - *"No hashes loaded" / "Separator unmatched"* → wrong `-m`, or the file has `user:hash`
    (add `--username`), or stray blank lines.
  - *device/driver error* → see Flow G (workload/`--force`/CPU).
- **glossary:** attack_mode.

### Flow C — Add rules — `-r`
- **Complete layer:** `-r <rulefile>` mangles each word (case, digits, leet). Bundled rules
  live in `/usr/share/hashcat/rules/` (e.g. `best64.rule`, `rockyou-30000.rule`,
  `dive.rule`). Stack multiple `-r` for more transforms (more time).
- **show:** `hashcat -m 0 -a 0 hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule`
- **glossary:** rule.

### Flow D — Mask / brute force — `-a 3`
- **Complete layer:** `-a 3` builds candidates from a **mask** of charsets:
  `?l` lower, `?u` upper, `?d` digit, `?s` special, `?a` all, `?b` raw byte. Custom sets:
  `-1 ?l?d` then use `?1`. `--increment` tries growing lengths.
- **show:** `hashcat -m 0 -a 3 hashes.txt ?u?l?l?l?l?d?d?d`  (Ulll lll + 3 digits)
  · custom: `hashcat -m 0 -a 3 -1 ?l?d hashes.txt ?1?1?1?1?1?1`
- **branches:** *too slow / keyspace huge* → shorten the mask, use `--increment` ranges, or
  go back to wordlist+rules; `-O` speeds up but caps password length.
- **glossary:** mask, charset, increment.

### Flow E — Hybrid attacks — `-a 6` / `-a 7`
- **Complete layer:** combine a wordlist with a mask: `-a 6` = word + mask (e.g. `word2024`),
  `-a 7` = mask + word. Great for "dictionary word plus a few digits/symbols."
- **show:** `hashcat -m 0 -a 6 hashes.txt rockyou.txt ?d?d?d?d`

### Flow F — Show results, output & user:hash files
- **Complete layer:** `--show hashes.txt` prints cracked from the **potfile**; `-o
  cracked.txt` writes results; `--username` if the file is `user:hash`;
  `--potfile-disable` to ignore the cache (re-crack).
- **show:** `hashcat -m 0 hashes.txt rockyou.txt --show`
- **branches:** *"already cracked" / nothing runs* → results are cached in the potfile;
  `--show` to see them, or `--potfile-disable` to force a re-run.
- **glossary:** potfile.

### Flow G — Performance, devices & sessions
- **Complete layer:** `-b` benchmark; `-I`/`-d <id>` list/select devices; `-w 1..4` workload
  (4=fastest, least responsive desktop); `-O` optimized kernels (faster, **limits max
  password length**); `--session=<name>` + `--restore` to pause/resume; `--status` for live
  stats.
- **GPU/driver reality:** hashcat wants a supported GPU + OpenCL/CUDA drivers. In a VM or
  without GPU drivers you may see "No devices found" → install drivers, or run CPU with
  `-D 1` (slow). `--force` bypasses warnings but is **not recommended** (can give wrong
  results) — flagged.
- **show:** `hashcat -b` · `hashcat -m 1800 -a 0 --session=crackA hashes.txt rockyou.txt`
  → resume `hashcat --restore --session=crackA`
- **glossary:** workload, optimized_kernel, gpu_opencl.

### Flow H — Cracking Wi-Fi captures (`-m 22000`)
- **Complete layer:** modern WPA cracking uses mode **22000**. You first convert a capture
  to the hashcat format (e.g. with `hcxpcapngtool` → `.hc22000`), then crack it like any
  hash. Capturing the handshake/PMKID is **aircrack-ng / hcxdumptool** territory → Module 07.
- **show:** `hashcat -m 22000 -a 0 capture.hc22000 /usr/share/wordlists/rockyou.txt`
- **branches:** *no handshake in file* → you need a valid capture first (Module 07,
  authorized networks only).
- **glossary:** (links to aircrack-ng).

---

## 6. Authorization & ethics (before commands shown)

> "Crack only hashes you own or are explicitly authorized to test (your systems, a lab, or a
> CTF). Cracking others' hashes — including Wi-Fi handshakes from networks you don't own — is
> illegal." — logged to the audit log.

Offline + heavy: the concern is **legal/ethical** and **hardware** (heat/power on long runs),
not network noise. Practice on CTFs, your own hashes, and your own Wi-Fi.

---

## 7. Glossary additions

- **hash_mode (`-m`)** — the numeric hash type; **must match** the hash or nothing cracks.
- **attack_mode (`-a`)** — 0 wordlist, 1 combinator, 3 mask/brute, 6/7 hybrid.
- **mask / charset** — a pattern of `?l ?u ?d ?s ?a` building brute-force candidates.
- **increment** — try growing password lengths within a mask.
- **rule (`-r`)** — transformations applied to wordlist words.
- **potfile** — `~/.hashcat/hashcat.potfile`; caches cracked hashes (`--show` reads it).
- **workload (`-w`)** — speed-vs-responsiveness profile (1–4).
- **optimized_kernel (`-O`)** — faster kernels that cap maximum password length.
- **gpu/opencl** — hashcat's accelerator; needs proper drivers (else "no devices").

---

## 8. Design / token mapping

- Category **Password** → tinted tab; authorization gate as `--status-critical` callout;
  `--force` and long-run heat notes as `--status-warning`.
- Commands in `--font-mono`; "did it work?" gate green/red.

---

## 9. Why this fits the template

Same shape as the others: profiles for the on-ramp, every `-m`/`-a`/mask/rule explained for
depth, and the genuinely common failure branches (wrong `-m` = "no hashes loaded", potfile
"already cracked", "no devices" driver issue, mask too slow → wordlist+rules). It closes the
cracking trilogy (hydra online → john CPU → hashcat GPU) and hands WPA capture off to
**aircrack-ng** (Module 07).

*End of Module 06 (hashcat) spec v1. Next in CLI Top 10: aircrack-ng.*
