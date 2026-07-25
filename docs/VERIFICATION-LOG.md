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
| nmap | ✅ | installed `--help`/man, Nmap 7.99 (Kali 2026.3) | all flags (`-sn/-Pn/-n/-T0-5/-sV/--version-all/-sS/-sT/-sU/-p/--top-ports/-p-/-O/-A/--script/-oN/-oX/-oG/-oA/--reason/-F/-iL/-e`) confirmed |
| sqlmap | ✅ | installed `--help`/`-hh`/man, sqlmap 1.10.6#stable | `-u/-g/--data/--cookie/--random-agent/--proxy/--tor/--check-tor/-p/--dbms/--level/--risk/--technique/-a/-b/--dump[-all]/-D/-T/-C/--os-shell/--os-pwn/--batch/--flush-session/--wizard` confirmed via `-hh` advanced help |
| nikto | ✍️ | installed nikto (no `--version`; single-dash parser) + `/var/lib/nikto/nikto.pl`/`nikto_core.plugin` source | **CORRECTED**: removed invented `-update` flag — real nikto has none; it only silently checks CIRT.net for a newer *nikto* version at startup (`-nocheck`/`-ask`), never fetches signatures. DB/plugins ship in the Kali package, so "update" now means `sudo apt update && sudo apt install --only-upgrade nikto`. `-Tuning/-Format/-ssl/-nossl/-vhost/-evasion/-Plugins/-id/-useproxy/-Pause/-maxtime/-timeout/-Display V/-list-plugins` all confirmed correct. Builder + test updated (`test_nikto_update_has_no_such_flag`) |
| hydra | ✅ | installed `--version`/help/man + `-U http-post-form`, Hydra v9.7 | `-l/-L/-p/-P/-C/-M/-o/-b/-f/-F/-t/-w/-e/-V/-R/-s` + http-post-form string format all confirmed |
| john | ✅ | installed `--help` (John 1.9.0-jumbo-1) — man page is stale non-jumbo, help used as authoritative per source hierarchy | `--format=/--wordlist=/--rules[=]/--single/--incremental[=]/--show/--session=/--restore[=]/--fork=/--pot=/--list=` confirmed; hash file positional per real usage line |
| hashcat | ✅ | installed `--help`/man, hashcat v7.1.2 | `-m/-a (0/1/3/6/7)/-r/--show/--identify/-D/-I/-d/-w/-O/--session/--force/-o/--username/--potfile-disable/-1/-b` confirmed |
| aircrack-ng suite | ✅ | installed `--help`/man for all 4 binaries | `aircrack-ng -w/-b`, `airmon-ng <start\|stop> <iface> [chan]` / `check [kill]`, `airodump-ng -c/-w/--bssid` (module correctly avoids `-b`, which means `--band` here, not BSSID), `aireplay-ng --deauth/-a/-c` all confirmed |
| tshark | ✅ | installed `tshark`/`dumpcap`/`capinfos`/`editcap`/`mergecap` --help/man, tshark 4.6.6 | `-D/-i/-r` (mutually exclusive, enforced in builder)/-f (BPF) vs -Y (display filter)/-T fields+-e/-E/-z io,phs\|conv,type\|endpoints,type\|follow,... /-s/-p/-o tls.keylog_file: all confirmed |
| metasploit (msfvenom/msfconsole) | ✅ | installed `--help`, Framework 6.4.145-dev | msfvenom `-l/-p/-f/-e/-a/--platform/-o/-b/-i` + `LHOST=/LPORT=` shape matches tool's own usage example verbatim; msfconsole `-q/-x "cmd; cmd"` confirmed. Interactive console grammar (search/use/set/exploit -j/sessions -i) not re-verified via `--help` (didn't launch the framework) but is long-stable documented syntax |
| sherlock | ✅ | installed `--help`/man, Sherlock v0.16.0 | `--timeout/--site/--print-found/--nsfw/--csv/--output(-o)/--folderoutput(-fo)/--tor(-t)/--proxy(-p)` confirmed; USERNAMES positional-last still parses correctly with `--tor`/`--proxy` under argparse regardless of the app's fixed slot order |
| bettercap | ✅ | installed `--help` | `-iface/-eval/-caplet/-silent/-no-colors` all real top-level flags; `-eval` module names (net.probe/net.recon/arp.spoof/net.sniff) match standard bettercap docs |
| blueranger | ✅ | installed `--help`/man | SYNOPSIS `blueranger <hciX> <bdaddr>` matches builder's positional order exactly |
| gqrx | ✍️ | installed `--help`/man | **CORRECTED**: removed invented `-d` device-select flag — real gqrx only has `-h/--help-all/-s/-l/-c/-e/-r`; device selection is GUI-only (Configure I/O Devices dialog). Dropped the `device` quick_build field and `ENV_INTERFACE` slot usage from tool.yaml + builder |
| rfcat | ✅ | installed `--help`/man | `-r` (research shell)/`-i INDEX` confirmed; `d.*` rflib API calls happen inside the interactive shell, not CLI flags |
| gvm | ✍️ | installed `gvm-start`/`gvm-check-setup`/`greenbone-feed-sync --help` + `apt list --installed` | **CORRECTED**: `gvm-feed-update` is not installed on current Kali (GVM 25.04 packaging) — replaced with `greenbone-feed-sync` (confirmed installed, drop-in role, defaults `--type all`, drops root to `_gvm`) in tool.yaml, manifest.yaml, and builder's `_ACTIONS` map. `gvm-start`/`gvm-check-setup` confirmed correct as-is |
| heartleech | ✍️ | installed `man heartleech` (full OPTIONS list) | **CORRECTED**: removed invented short flags `-p`/`-a` — real heartleech only has long-form `--port <port>` and `--autopwn` (only genuine short flag in the tool is `-d` for debug, unused here). Fixed builder + every tool.yaml mention across guided flow g1-g3 and reference flow hl1 |
| dirb | ✅ | installed `man dirb`, DIRB v2.22 | `-X/-c/-a/-r/-S/-o` + positional `<url> [<wordlist>]` order confirmed |
| dirbuster | ✅ | installed `-h` fallback (real DirBuster 1.0-RC1 usage text; `--version` only printed a GUI startup banner) | `-H/-u/-l/-e/-r` confirmed verbatim |
| burpsuite | ✅ | installed `--help`, Burp Suite Community 2026.3.2 | `--project-file=`/`--config-file=` confirmed verbatim |
| kismet | ✅ | installed `--help`/man, Kismet 2025.09.0 | `-c` (capture source)/`--no-ncurses`/`--log-prefix` confirmed in both help and man |
| responder | ✅ | installed `--help` (no man page), Responder v3.2.2.0, + `/usr/share/doc/responder/README.md` | `-I/-A/-v/-b/-w` + all other flags confirmed against real help text; log path confirmed as `/usr/share/responder/logs/` (packaged wrapper `cd`s into `/usr/share/responder/` before exec); hashcat `-m 5600` for NetNTLMv2 is well-established public knowledge, not independently re-verified against hashcat's own help in this pass |
| netexec | ✅ | installed `--help` + `netexec smb --help` (no man page), NetExec v1.5.1 "Yippie-Ki-Yay" | `smb` subcommand + `-u/-p/-H/-d/--local-auth/--shares/--sam/-x` all confirmed against real help text; target is positional (TARGET_PIVOT), protocol is a subcommand. `[+]`/`(Pwn3d!)` output markers and `--sam`/`--ntds` semantics are well-established public knowledge (netexec.wiki, widely documented), not independently re-verified against a live authenticated target in this pass — byte-accuracy of expected_output remains the same deferred item as every other tool |

### Verification pass 2 (2026-07-24)
Ran `tools/verify_capture.sh` on this Kali 2026.3 box (read-only `--help`/`--version`/`man`
capture for every referenced tool + helper — nothing executed against a target) and
cross-checked all 20 previously-pending tools against it, with direct read-only
`--help`/`man`/source-grep follow-ups where a capture was truncated or a tool's basic help
hid advanced flags. **4 corrections found**: nikto (invented `-update` flag — real nikto has
none), gqrx (invented `-d` device flag — device select is GUI-only), gvm (`gvm-feed-update`
renamed to `greenbone-feed-sync` in current Kali packaging), heartleech (invented `-p`/`-a`
short flags — real tool only has `--port`/`--autopwn`). The other 16 verified clean, no
changes. Full test suite: 104 passed. `expected_output` byte-accuracy (as opposed to
flags/syntax) remains unreconciled for all rows above the original 4 and is still deferred to
an actual run against a live target/lab — out of scope for this pass, same as noted below.

## Lessons (14) — pending a separate pass
Commands in the fundamentals lessons (shell/files/permissions/etc.) are standard coreutils
and were authored from stable behaviour, but will get the same doc pass + Kali-capture check.
