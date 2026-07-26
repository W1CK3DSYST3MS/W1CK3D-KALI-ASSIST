# Depth Audit — is each tool *fully* taught and *fully* buildable?

`docs/TOOL-COVERAGE.md` tracks breadth (which of Kali's ~406 tools have a module
at all). This file tracks **depth**: for the tools that DO have a module, does
it actually cover everything a real user would reasonably want from that tool?

Generated 2026-07-25 after a user field-test found nmap's guide was "ok, but a
huge part of its function [was] missing." A full audit of all 34 existing tool
modules followed, comparing each tool's real `--help`/`man` output against (a)
what its `wizard_core/builders/<id>_builder.py` can actually emit, and (b) what
its `quick_build:` GUI form exposes, and (c) what its flows/steps teach.

Two distinct failure modes:

- **Form gap** — the builder already supports an input in code, but the
  `quick_build` GUI form has no field for it, so a user can never reach it
  without hand-editing. Mechanical to fix: add the missing field(s).
- **Content gap** — a real, significant capability of the tool is absent from
  BOTH the builder AND every flow/step. Nothing teaches it, nothing can build
  it. Requires real authoring: builder logic + new step(s)/flow with
  plain-English explanation, `try_this`, `expected_output`, `alternatives`.

## Verdicts (34/34 audited)

### MAJOR GAPS (14)
| tool | form gap | content gap |
|---|---|---|
| nmap | 11+ of ~20 builder inputs hidden from quick_build | evasion/firewall-bypass entirely absent (decoys -D, fragmentation -f, spoofing) |
| gobuster | 13 of ~20 hidden | tftp/s3/gcs modes + Basic Auth absent |
| sqlmap | 22 of 28 hidden | can't actually extract data: --banner/--current-user/--passwords/--dump/-a/--os-pwn absent |
| wireshark (tshark) | 10 of 15 hidden, incl. `-w` save-to-file (guided flow tells you to save, form can't) | ring-buffer/file-rotation, autostop beyond count, Decode-As |
| hydra | 14 of 20 hidden | `-x` bruteforce-generation mode (MIN:MAX:CHARSET) absent |
| hashcat | 15 of 21 hidden | combinator attack (-a 1), custom charsets 2-8, -j/-k rule-left/right absent |
| john | 8 of 11 hidden | `--mask` attack mode absent |
| nikto | 13 of 18 hidden | `-mutate` deeper enumeration absent |
| netexec | none | `-M` module system (mimikatz/lsassy/nanodump — headline feature) absent; --lsa/--ntds taught in prose but not buildable |
| photon | 1 field (delay) | `--keys` secret/API-key detection + `--dns` subdomain enum absent (arguably Photon's main selling points) |
| responder | none | DHCP/DHCPv6 poisoning, rogue proxy NTLM/Basic auth capture, IP/IPv6 spoofing, forced WPAD absent |
| metasploit (msfvenom) | 7 of 11 hidden | template-injection payload delivery (-x/-k), --encrypt absent |
| dirb | cookie/agent/silent hidden (flow text tells you to add -a, form can't) | proxy, HTTP basic auth, custom headers, request throttle absent |
| aircrack_ng | write_prefix/action/client/deauth_count hidden | other aireplay attack modes (fakeauth/arpreplay/fragment/chopchop/caffe-latte) absent, only --deauth buildable |

### PARTIAL (13)
| tool | gap |
|---|---|
| bettercap | dns.spoof, https-proxy/injection, wifi/ble modules untaught (reachable only via free-text -eval escape hatch) |
| burpsuite | --use-defaults/--disable-extensions/--collaborator-server/--data-dir not exposed (GUI-only tool, core workflow well taught) |
| dirbuster | threads/start-point/GET-only/non-recursive/verbose not built or taught (legacy, GUI-primary tool) |
| exiftool | metadata removal/scrubbing (-all=) absent — deliberate read-only scope decision, but a common real use case (strip GPS before sharing) is never even mentioned |
| heartleech | --autopwn hidden from form |
| kismet | --log-types/--config-file/--daemonize untaught (CLI deliberately thin by design) |
| mdbtools | mdb-sql (raw SQL against the DB) never wired in at all; mdb-json export absent |
| oscanner | host_file (-f) hidden from form despite being taught in a flow |
| rfcat | standalone spectrum-analyzer mode (-s/-f/-c/-n) absent |
| sherlock | folder_output/nsfw/proxy hidden from form |
| sqlninja | 7 of 13 modes selectable in the GUI dropdown with zero flow ever explaining what they do |
| theharvester | --screenshot, -s/--shodan, -a/--api-scan absent (Shodan only mentioned in passing) |
| tnscmd10g | rawcmd hidden from form despite a flow step demonstrating it |

### COMPREHENSIVE (7)
blueranger, btscanner, dnsmap, gqrx, gvm, sidguesser, sqlsus — verified against
real `--help`/usage output, builder + form + flows already match reality.

## Fix order — COMPLETE (2026-07-26)

All 14 MAJOR GAPS + all 13 PARTIAL tools fixed. Each tool: re-verified real
flag/behavior against the installed binary on this Kali box, extended builder
code, added missing quick_build fields, added/extended flow steps for content
gaps (plain-English explanation + try_this + expected_output + alternatives,
house style), added/extended a dedicated `tests/test_<id>_builder.py`. Done
partly by hand (nmap/gobuster/sqlmap, as the pattern-setting examples) and
partly via parallel background agents given the same instructions + audit
findings; a few tools (kismet, mdbtools) were finished by hand after two
agents hit the account's monthly spend limit mid-run.

- [x] nmap — quick_build 5→27 fields; evasion flow (-f/-D/-g/--spoof-mac/-S) + 4 glossary terms
- [x] gobuster — quick_build 5→21 fields; tftp/s3/gcs modes + Basic Auth (-U/-P)
- [x] sqlmap — quick_build 6→44 fields; --current-user/--current-db/--hostname/--is-dba/--users/--passwords/--privileges/--roles/--schema/--count/--search/--exclude-sysdbs (new quick_recon flow)
- [x] wireshark — quick_build 5→20 fields; ring-buffer rotation (-b), autostop beyond count (-a), Decode-As (-d)
- [x] hydra — quick_build 6→23 fields; `-x` bruteforce-generation mode, `-S` explicit SSL, `-m` module options
- [x] hashcat — quick_build 5→24 fields; combinator attack (-a 1, two wordlists) + -j/-k rule-left/right
- [x] john — quick_build →17 fields, `mask` flow added; `--mask` attack mode
- [x] nikto — quick_build →23 fields, `mutate` flow added; `-mutate` deeper enumeration
- [x] netexec — `modules` flow added; `-M` module system (mimikatz/lsassy/etc.), --lsa/--ntds now actually buildable
- [x] photon — quick_build 5→10 fields; `--keys` secret detection, `--dns` subdomain enum, `--clone`, `-e`/`--export`
- [x] responder — quick_build 5→12 fields; DHCP/DHCPv6 poisoning, rogue proxy auth (-P), forced WPAD (-F), IP/IPv6 spoofing — all `destructive: true` with strong warnings
- [x] metasploit (msfvenom) — quick_build 5→15 fields; template injection (-x/-k), --encrypt
- [x] dirb — quick_build 5→13 fields; proxy routing, proxy auth, HTTP basic auth, custom headers, throttle (-z)
- [x] aircrack_ng — quick_build 7→16 fields; fake-auth + ARP-replay attack modes added to the aireplay dispatcher
- [x] bettercap — new step teaching `dns.spoof` via -eval, with a destructive/authorization warning
- [x] burpsuite — --use-defaults/--disable-extensions exposed
- [x] dirbuster — headless-CLI flow added (threads/start-point/GET-only/non-recursive/verbose), framed as legacy vs. gobuster/dirb
- [x] exiftool — metadata-removal (-all=/-gps:all=) now taught and buildable (privacy use case)
- [x] heartleech — --autopwn exposed in quick_build
- [x] kismet — quick_build 3→7 fields (log_types/config_file/daemonize/no_sudo added)
- [x] mdbtools — `sql` action wired in (mdb-sql via -i/-o/-H), new glossary.yaml + guided step
- [x] oscanner — host_file (-f) exposed in quick_build
- [x] rfcat — standalone spectrum-analyzer mode (-s/-f/-c/-n) added as a new reference flow
- [x] sherlock — folder_output/nsfw/proxy exposed in quick_build
- [x] sqlninja — new flow explaining all 7 previously-unexplained modes (dirshell/revshell/dnstunnel/icmpshell/sqlcmd/backscan/metasploit/upload)
- [x] theharvester — -s/--shodan, --screenshot, -a/--api-scan added
- [x] tnscmd10g — rawcmd exposed in quick_build

## Fundamentals lessons + troubleshooters (2026-07-26)

Same user complaint ("acronyms unexplained," "walkthroughs only cover total
success, not partial/varied output") applies beyond tool guides — extended
the audit to all 14 `modules/fundamentals.*` lessons and all 5
`modules/troubleshoot.*` flows. Per-file: added missing `glossary_refs` +
glossary terms for unexplained jargon (grep-checked against the whole merged
glossary first to avoid collisions), added realistic partial/varied-output
`alternatives` where a step only handled clean pass/fail, and checked each
lesson's step sequence actually delivers on its stated `goal`.

- [x] All 14 fundamentals lessons — archives_transfer needed the most partial-output
      work (tar/unzip/scp/rsync interrupted-transfer cases); wordlists needed the most
      jargon work (symlink/gzip unreferenced); pipes_redirection and shell_grammar were
      already solid, no changes needed.
- [x] All 5 troubleshooters (networking/packages/permissions/rare_hard/services) — added
      partial-state diagnosis alternatives (e.g. "some but not all packages update," "service
      running but not listening on the expected port") and new fix tiers/symptoms where a
      real common gap existed (e.g. rare_hard gained a `/boot`-specifically-full case and an
      LVM root-volume-growth fix).

## Verification

Full test suite: **302 passed, 0 failures** (`.venv/bin/python -m pytest -q`),
up from 128 before this depth-audit initiative started. See
`docs/VERIFICATION-LOG.md` for the per-tool flag-verification trail.
