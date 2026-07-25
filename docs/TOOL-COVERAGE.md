# Kali Tool Coverage Tracker

Auto-generated 2026-07-25 from Kali's own `kali-tools-*` metapackage dependency lists (`apt-cache depends kali-tools-*`) on this machine (Kali 2026.3) — the authoritative catalog of what Kali ships, not a hand-typed guess.

**34 / 407 done.** Goal: a guided walkthrough + quick-build form for every tool in Kali's catalog, same depth as the 34 already done (see `docs/VERIFICATION-LOG.md` for the doc-verification standard each one is held to). **`kali-tools-top10` is fully closed out.** `database` is at 7/10 — the only 3 remaining (`jsql-injection`/`sqldict`/`sqlitebrowser`) are GUI-only or a broken legacy-Wine tool, deliberately skipped as not a fit for this app's format.

**Read before treating this as a literal to-do list:** this is the raw `apt-cache depends` output per category, which includes some incidental dependencies pulled in alongside real tools (utility packages, libraries, a few GUI-only apps that don't fit this app's command-builder/guided-walkthrough format). Each category needs a quick human skim to strip those before treating its list as committed scope — don't assume every row here becomes a module.

## Status by category

| Category | Done | Total |
|---|---|---|
| top10 | 10 | 10 |
| information-gathering | 5 | 51 |
| vulnerability | 3 | 37 |
| web | 15 | 79 |
| database | 7 | 10 |
| passwords | 3 | 48 |
| wireless | 2 | 4 |
| 802-11 | 3 | 19 |
| bluetooth | 2 | 11 |
| rfid | 0 | 3 |
| sdr | 1 | 12 |
| voip | 2 | 18 |
| exploitation | 2 | 9 |
| sniffing-spoofing | 3 | 24 |
| post-exploitation | 0 | 22 |
| reverse-engineering | 1 | 14 |
| forensics | 3 | 100 |
| crypto-stego | 0 | 6 |
| fuzzing | 0 | 4 |
| social-engineering | 0 | 5 |
| hardware | 0 | 11 |
| gpu | 0 | 2 |
| identify | 0 | 16 |
| detect | 0 | 2 |
| protect | 0 | 5 |
| recover | 0 | 8 |
| respond | 0 | 6 |
| reporting | 0 | 8 |
| windows-resources | 1 | 16 |

## top10  (10/10 done)

- [x] aircrack-ng
- [x] burpsuite
- [x] hydra
- [x] john
- [x] metasploit-framework — implemented as metasploit
- [x] netexec
- [x] nmap
- [x] responder
- [x] sqlmap
- [x] wireshark — implemented as tshark (CLI)

## information-gathering  (5/51 done)

- [ ] 0trace
- [ ] braa
- [ ] dmitry
- [ ] dnsenum
- [x] dnsmap
- [ ] dnsrecon
- [ ] dnstracer
- [ ] dnswalk
- [ ] enum4linux
- [ ] fierce
- [ ] firewalk
- [ ] fping
- [ ] fragrouter
- [ ] ftester
- [ ] hping3
- [ ] ike-scan
- [ ] intrace
- [ ] iputils-arping
- [ ] irpas
- [ ] lbd
- [ ] legion
- [ ] maltego
- [ ] masscan
- [ ] metagoofil
- [ ] nbtscan
- [ ] ncat
- [ ] netdiscover
- [ ] netmask
- [x] nmap
- [ ] onesixtyone
- [ ] p0f
- [x] photon
- [ ] qsslcaudit
- [ ] recon-ng
- [x] sherlock
- [ ] smbmap
- [ ] smtp-user-enum
- [ ] snmpcheck
- [ ] ssldump
- [ ] sslh
- [ ] sslscan
- [ ] sslyze
- [ ] swaks
- [ ] thc-ipv6
- [x] theharvester
- [ ] tlssled
- [ ] twofi
- [ ] unicornscan
- [ ] urlcrazy
- [ ] wafw00f
- [ ] zenmap

## vulnerability  (3/37 done)

- [ ] afl++
- [ ] bed
- [ ] cisco-auditing-tool
- [ ] cisco-global-exploiter
- [ ] cisco-ocs
- [ ] cisco-torch
- [ ] copy-router-config
- [ ] dhcpig
- [ ] enumiax
- [x] gvm
- [ ] iaxflood
- [ ] inviteflood
- [ ] legion
- [ ] lynis
- [x] nikto
- [x] nmap
- [ ] ohrwurm
- [ ] peass
- [ ] protos-sip
- [ ] rtpbreak
- [ ] rtpflood
- [ ] rtpinsertsound
- [ ] rtpmixsound
- [ ] sctpscan
- [ ] sfuzz
- [ ] siege
- [ ] siparmyknife
- [ ] sipp
- [ ] sipsak
- [ ] sipvicious
- [ ] slowhttptest
- [ ] spike
- [ ] t50
- [ ] thc-ssl-dos
- [ ] unix-privesc-check
- [ ] voiphopper
- [ ] yersinia

## web  (15/79 done)

- [ ] apache-users
- [ ] apache2
- [ ] beef-xss
- [x] burpsuite
- [ ] cadaver
- [ ] commix
- [ ] cutycapt
- [ ] davtest
- [ ] default-mysql-server
- [x] dirb
- [x] dirbuster
- [ ] dotdotpwn
- [ ] eyewitness
- [ ] ferret-sidejack
- [ ] ftester
- [x] gobuster
- [ ] hakrawler
- [ ] hamster-sidejack
- [x] heartleech
- [ ] httprint
- [ ] httrack
- [x] hydra
- [ ] hydra-gtk
- [ ] jboss-autopwn
- [ ] joomscan
- [ ] jsql-injection
- [ ] laudanum
- [ ] lbd
- [ ] maltego
- [ ] medusa
- [ ] mitmproxy
- [ ] ncrack
- [x] nikto
- [ ] nishang
- [x] nmap
- [x] oscanner
- [ ] owasp-mantra-ff
- [ ] padbuster
- [ ] paros
- [ ] patator
- [ ] php
- [ ] php-mysql
- [ ] proxychains4
- [ ] proxytunnel
- [ ] qsslcaudit
- [ ] redsocks
- [x] sidguesser
- [ ] siege
- [ ] skipfish
- [ ] slowhttptest
- [ ] sqldict
- [ ] sqlitebrowser
- [x] sqlmap
- [x] sqlninja
- [x] sqlsus
- [ ] ssldump
- [ ] sslh
- [ ] sslscan
- [ ] sslsniff
- [ ] sslsplit
- [ ] sslyze
- [ ] stunnel4
- [ ] thc-ssl-dos
- [ ] tlssled
- [x] tnscmd10g
- [ ] uniscan
- [ ] wafw00f
- [ ] wapiti
- [ ] watobo
- [ ] webacoo
- [ ] webscarab
- [ ] webshells
- [ ] weevely
- [ ] wfuzz
- [ ] whatweb
- [x] wireshark — implemented as tshark (CLI)
- [ ] wpscan
- [ ] xsser
- [ ] zaproxy

## database  (7/10 done)

- [ ] jsql-injection
- [x] mdbtools
- [x] oscanner
- [x] sidguesser
- [ ] sqldict
- [ ] sqlitebrowser
- [x] sqlmap
- [x] sqlninja
- [x] sqlsus
- [x] tnscmd10g

## passwords  (3/48 done)

- [ ] cewl
- [ ] chntpw
- [ ] cisco-auditing-tool
- [ ] cmospwd
- [ ] crackle
- [ ] creddump7
- [ ] crunch
- [ ] fcrackzip
- [ ] freerdp3-x11
- [ ] gpp-decrypt
- [ ] hash-identifier
- [x] hashcat
- [ ] hashcat-utils
- [ ] hashid
- [x] hydra
- [ ] hydra-gtk
- [x] john
- [ ] johnny
- [ ] maskprocessor
- [ ] medusa
- [ ] mimikatz
- [ ] ncrack
- [ ] onesixtyone
- [ ] ophcrack
- [ ] ophcrack-cli
- [ ] pack
- [ ] pack2
- [ ] passing-the-hash
- [ ] patator
- [ ] pdfcrack
- [ ] pipal
- [ ] polenum
- [ ] rainbowcrack
- [ ] rarcrack
- [ ] rcracki-mt
- [ ] rsmangler
- [ ] samdump2
- [ ] seclists
- [ ] sipcrack
- [ ] sipvicious
- [ ] smbmap
- [ ] sqldict
- [ ] statsprocessor
- [ ] sucrack
- [ ] thc-pptp-bruter
- [ ] truecrack
- [ ] twofi
- [ ] wordlists

## wireless  (2/4 done)

- [x] rfcat
- [ ] rfkill
- [ ] sakis3g
- [x] wireshark — implemented as tshark (CLI)

## 802-11  (3/19 done)

- [x] aircrack-ng
- [ ] airgeddon
- [ ] asleap
- [ ] bully
- [ ] cowpatty
- [ ] eapmd5pass
- [ ] fern-wifi-cracker
- [ ] freeradius-wpe
- [x] hashcat
- [ ] hostapd-wpe
- [ ] iw
- [x] kismet
- [ ] macchanger
- [ ] mdk3
- [ ] mdk4
- [ ] pixiewps
- [ ] reaver
- [ ] wifi-honey
- [ ] wifite

## bluetooth  (2/11 done)

- [ ] blue-hydra
- [ ] bluelog
- [x] blueranger
- [ ] bluesnarfer
- [ ] bluez
- [ ] bluez-hcidump
- [x] btscanner
- [ ] crackle
- [ ] redfang
- [ ] spooftooph
- [ ] ubertooth

## rfid  (0/3 done)

- [ ] gnuradio
- [ ] proxmark3
- [ ] rfdump

## sdr  (1/12 done)

- [ ] chirp
- [ ] gnuradio
- [x] gqrx-sdr — implemented as gqrx
- [ ] gr-air-modes
- [ ] gr-iqbal
- [ ] gr-osmosdr
- [ ] hackrf
- [ ] inspectrum
- [ ] kalibrate-rtl
- [ ] multimon-ng
- [ ] uhd-host
- [ ] uhd-images

## voip  (2/18 done)

- [ ] enumiax
- [ ] iaxflood
- [ ] inviteflood
- [ ] libfindrtp
- [x] nmap
- [ ] ohrwurm
- [ ] protos-sip
- [ ] rtpbreak
- [ ] rtpflood
- [ ] rtpinsertsound
- [ ] rtpmixsound
- [ ] sctpscan
- [ ] siparmyknife
- [ ] sipcrack
- [ ] sipp
- [ ] sipvicious
- [ ] voiphopper
- [x] wireshark — implemented as tshark (CLI)

## exploitation  (2/9 done)

- [ ] armitage
- [ ] beef-xss
- [ ] exploitdb
- [x] metasploit-framework — implemented as metasploit
- [ ] msfpc
- [ ] set
- [ ] shellnoob
- [x] sqlmap
- [ ] termineter

## sniffing-spoofing  (3/24 done)

- [ ] above
- [x] bettercap
- [ ] darkstat
- [ ] dnschef
- [ ] driftnet
- [ ] dsniff
- [ ] ettercap-text-only
- [ ] ferret-sidejack
- [ ] fiked
- [ ] hamster-sidejack
- [ ] hexinject
- [ ] isr-evilgrade
- [ ] macchanger
- [ ] mitmproxy
- [ ] netsniff-ng
- [ ] rebind
- [x] responder
- [ ] sniffjoke
- [ ] sslsniff
- [ ] sslsplit
- [ ] tcpflow
- [ ] tcpreplay
- [ ] wifi-honey
- [x] wireshark — implemented as tshark (CLI)

## post-exploitation  (0/22 done)

- [ ] cymothoa
- [ ] dbd
- [ ] dns2tcp
- [ ] exe2hexbat
- [ ] iodine
- [ ] laudanum
- [ ] mimikatz
- [ ] miredo
- [ ] nishang
- [ ] powersploit
- [ ] proxychains4
- [ ] proxytunnel
- [ ] ptunnel
- [ ] pwnat
- [ ] sbd
- [ ] shellter
- [ ] sslh
- [ ] stunnel4
- [ ] udptunnel
- [ ] veil
- [ ] webacoo
- [ ] weevely

## reverse-engineering  (1/14 done)

- [ ] apktool
- [ ] bytecode-viewer
- [ ] clang
- [ ] dex2jar
- [ ] edb-debugger
- [ ] jadx
- [ ] javasnoop
- [ ] jd-gui
- [x] metasploit-framework — implemented as metasploit
- [ ] ollydbg
- [ ] radare2
- [ ] rizin
- [ ] rizin-cutter
- [ ] rz-ghidra

## forensics  (3/100 done)

- [ ] 7zip
- [ ] afflib-tools
- [ ] apktool
- [ ] autopsy
- [ ] binwalk
- [ ] binwalk3
- [ ] bulk-extractor
- [ ] bytecode-viewer
- [ ] cabextract
- [ ] chkrootkit
- [ ] creddump7
- [ ] dc3dd
- [ ] dcfldd
- [ ] ddrescue
- [ ] dumpzilla
- [ ] edb-debugger
- [ ] ewf-tools
- [ ] exifprobe
- [x] exiftool
- [ ] exiv2
- [ ] ext3grep
- [ ] ext4magic
- [ ] extundelete
- [ ] fcrackzip
- [ ] firmware-mod-kit
- [ ] foremost
- [ ] forensic-artifacts
- [ ] forensics-colorize
- [ ] galleta
- [ ] gdb
- [ ] gpart
- [ ] gparted
- [ ] grokevt
- [ ] guymager
- [ ] hashdeep
- [ ] inetsim
- [ ] jadx
- [ ] javasnoop
- [ ] libhivex-bin
- [ ] libsmali-java
- [ ] lvm2
- [ ] lynis
- [ ] mac-robber
- [ ] magicrescue
- [x] mdbtools
- [ ] memdump
- [ ] metacam
- [ ] missidentify
- [ ] myrescue
- [ ] nasm
- [ ] nasty
- [ ] ollydbg
- [ ] parted
- [ ] pasco
- [ ] pdf-parser
- [ ] pdfid
- [ ] plaso
- [ ] polenum
- [ ] pst-utils
- [ ] python3-capstone
- [ ] python3-dfdatetime
- [ ] python3-dfvfs
- [ ] python3-dfwinreg
- [ ] python3-distorm3
- [ ] radare2
- [ ] readpe
- [ ] recoverdm
- [ ] recoverjpeg
- [ ] reglookup
- [ ] regripper
- [ ] rephrase
- [ ] rifiuti
- [ ] rifiuti2
- [ ] rizin-cutter
- [ ] rkhunter
- [ ] rsakeyfind
- [ ] rz-ghidra
- [ ] safecopy
- [ ] samdump2
- [ ] scalpel
- [ ] scrounge-ntfs
- [ ] sleuthkit
- [ ] sqlitebrowser
- [ ] ssdeep
- [ ] tcpdump
- [ ] tcpflow
- [ ] tcpick
- [ ] tcpreplay
- [ ] truecrack
- [ ] unar
- [ ] undbx
- [ ] unhide
- [ ] upx-ucl
- [ ] vinetto
- [ ] wce
- [ ] winregfs
- [x] wireshark — implemented as tshark (CLI)
- [ ] xmount
- [ ] xplico
- [ ] yara

## crypto-stego  (0/6 done)

- [ ] aesfix
- [ ] aeskeyfind
- [ ] ccrypt
- [ ] steghide
- [ ] stegosuite
- [ ] stegsnow

## fuzzing  (0/4 done)

- [ ] afl++
- [ ] sfuzz
- [ ] spike
- [ ] wfuzz

## social-engineering  (0/5 done)

- [ ] beef-xss
- [ ] maltego
- [ ] msfpc
- [ ] set
- [ ] veil

## hardware  (0/11 done)

- [ ] binwalk
- [ ] binwalk3
- [ ] cutecom
- [ ] flashrom
- [ ] minicom
- [ ] openocd
- [ ] qemu-system-x86
- [ ] qemu-user
- [ ] radare2
- [ ] rizin-cutter
- [ ] rz-ghidra

## gpu  (0/2 done)

- [ ] oclgausscrack
- [ ] truecrack

## identify  (0/16 done)

- [ ] amass
- [ ] assetfinder
- [ ] cisco-auditing-tool
- [ ] defectdojo
- [ ] exploitdb
- [ ] hb-honeypot
- [ ] kali-autopilot
- [ ] maltego
- [ ] maryam
- [ ] nipper-ng
- [ ] osrframework
- [ ] spiderfoot
- [ ] tiger
- [ ] wapiti
- [ ] witnessme
- [ ] zaproxy

## detect  (0/2 done)

- [ ] grokevt
- [ ] sentrypeer

## protect  (0/5 done)

- [ ] clamav
- [ ] cryptsetup
- [ ] cryptsetup-initramfs
- [ ] cryptsetup-nuke-password
- [ ] fwbuilder

## recover  (0/8 done)

- [ ] ddrescue
- [ ] ext3grep
- [ ] extundelete
- [ ] myrescue
- [ ] recoverdm
- [ ] recoverjpeg
- [ ] scrounge-ntfs
- [ ] undbx

## respond  (0/6 done)

- [ ] ewf-tools
- [ ] ghidra
- [ ] guymager
- [ ] hashrat
- [ ] impacket-scripts
- [ ] netsniff-ng

## reporting  (0/8 done)

- [ ] cutycapt
- [ ] dradis
- [ ] eyewitness
- [ ] faraday
- [ ] maltego
- [ ] metagoofil
- [ ] pipal
- [ ] recordmydesktop

## windows-resources  (1/16 done)

- [ ] dbd
- [ ] dnschef
- [x] heartleech
- [ ] hyperion
- [ ] mimikatz
- [ ] ncat-w32
- [ ] ollydbg
- [ ] powercat
- [ ] regripper
- [ ] sbd
- [ ] secure-socket-funneling-windows-binaries
- [ ] shellter
- [ ] tftpd32
- [ ] wce
- [ ] windows-binaries
- [ ] windows-privesc-check
