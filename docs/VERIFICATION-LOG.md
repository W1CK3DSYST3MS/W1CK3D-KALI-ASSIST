# Content Verification Log

Tracks the review/correction of every tool module's commands, flags, argument order
and `expected_output` against authoritative documentation.

## Method (source hierarchy, most authoritative first)
1. **The installed tool on Kali** — `man <tool>` and `<tool> --help` for the EXACT packaged
   version. Captured via `tools/verify_capture.sh` (run on Kali, output reconciled here).
   This is the only reliable source for byte-accurate `expected_output`.
2. **Official man pages / project docs** — manpages.debian.org (Debian/Kali packages),
   the project's own README/wiki, kali.org/tools/<tool>.
3. Cross-checked, never assumed.

## What "verified" covers
- **Flags & syntax** — every flag used exists and means what we say; argument ORDER is correct.
- **expected_output** — SHAPE verified against docs; byte-accuracy pending a real Kali run
  (marked `expected: shape-only` until reconciled with `verify_capture.sh` output).

## Status
Legend: ✅ verified · ✍️ corrected · ⏳ pending · 🔬 expected_output needs a real Kali run

| Tool | Flags/syntax | Source | Notes |
|------|--------------|--------|-------|
| dnsmap | ✅ | kali.org/tools/dnsmap | domain-first + -w/-r/-c/-d/-i all correct |
| gobuster | ✅ | github OJ/gobuster README | -u/-w/-x/-t/-k/-o/-a/-c/-H/-r/-s confirmed; -b blacklist; "can't set both -s and -b" + version-default note accurate |
| photon | ✅ | github s0md3v/Photon wiki (Usage) | -u/-l/-t/-d/-o/--wayback confirmed; output categories internal/external/robots/scripts/etc. match |
| btscanner | ✍️ | manpages.debian.org/btscanner | **CORRECTED**: removed invented `-o`; real options are only `--help`/`--cfg`/`--no-reset`; dumps go to config `device_path` |
| nmap | ⏳🔬 | | |
| sqlmap | ⏳🔬 | | |
| nikto | ⏳🔬 | | check `-Display V`, `-Tuning`, `-Format` |
| hydra | ⏳🔬 | | check http-post-form string; -L/-P/-C/-e/-M |
| john | ⏳🔬 | | check --single/--wordlist/--rules/--format/--show |
| hashcat | ⏳🔬 | | check -m/-a/-r/--show/--identify/-D |
| aircrack-ng suite | ⏳🔬 | | airmon-ng/airodump-ng/aireplay-ng/aircrack-ng flags |
| tshark | ⏳🔬 | | -i/-r/-Y/-f/-T fields/-e/-z |
| metasploit (msfvenom/msfconsole) | ⏳🔬 | | payload/LHOST/LPORT/-f/-o; vsftpd module path |
| sherlock | ⏳🔬 | | --site/--print-found/--output/--csv/--tor |
| bettercap | ⏳🔬 | | -iface/-eval/-caplet/-silent; module names |
| blueranger | ⏳🔬 | | `blueranger <hci#> <bdaddr>` |
| gqrx | ⏳🔬 | | -l/-d/-c/-e/-r |
| rfcat | ⏳🔬 | | -r research shell; d.* methods |
| gvm | ⏳🔬 | | gvm-start/check-setup/feed-update; UI port 9392 |
| heartleech | ⏳🔬 | | --scan/--dump/-p; hostname positional |
| dirb | ⏳🔬 | | `dirb <url> <wordlist>` order; -X/-o/-r/-a/-c |
| dirbuster | ⏳🔬 | | -H/-u/-l/-e/-r headless flags |
| burpsuite | ⏳🔬 | | --project-file=/--config-file=; proxy/CA workflow |
| kismet | ⏳🔬 | | -c source; web UI :2501 |

## Lessons (14) — pending a separate pass
Commands in the fundamentals lessons (shell/files/permissions/etc.) are standard coreutils
and were authored from stable behaviour, but will get the same doc pass + Kali-capture check.
