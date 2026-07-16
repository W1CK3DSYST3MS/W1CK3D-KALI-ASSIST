#!/usr/bin/env bash
# W1CK3D'S KALI ASSIST — documentation capture for content verification.
#
# Run this ON KALI to dump the authoritative --help / --version / man page for
# every tool and helper the app references. Send the output file back so the
# guided-flow commands, flags, and expected_output can be reconciled against the
# EXACT versions you have installed.
#
#   bash tools/verify_capture.sh > verify_output.txt 2>&1
#   # then send verify_output.txt
#
# Nothing here scans or attacks anything — it only asks each tool for its help.

set +e
export MANWIDTH=100 PAGER=cat GIT_PAGER=cat

# Tool binaries + the helper commands used inside guided flows.
CMDS=(
  nmap sqlmap gobuster nikto hydra john hashcat
  aircrack-ng airmon-ng airodump-ng aireplay-ng
  tshark dumpcap capinfos msfvenom msfconsole
  sherlock dnsmap bettercap btscanner blueranger
  gqrx rfcat gvm-start gvm-check-setup gvm-feed-update
  heartleech dirb dirbuster burpsuite kismet photon
  # helpers referenced in guided/reference steps:
  curl ip iw hciconfig l2ping hcitool bluetoothctl rfkill
  rtl_test hashid hcxpcapngtool unshadow zip2john gunzip
  dig ping nmcli hcxdumptool
)

section() { printf '\n\n========== %s ==========\n' "$1"; }

for c in "${CMDS[@]}"; do
  section "$c"
  path="$(command -v "$c" 2>/dev/null)"
  if [ -z "$path" ]; then
    echo "[NOT INSTALLED] (apt-cache search / apt install may be needed)"
    continue
  fi
  echo "PATH: $path"
  echo "--- version ---"
  timeout 12 "$c" --version   2>&1 | head -n 4 \
    || timeout 12 "$c" -V     2>&1 | head -n 4 \
    || echo "(no --version)"
  echo "--- help (first 120 lines) ---"
  { timeout 15 "$c" --help 2>&1 || timeout 15 "$c" -h 2>&1 || timeout 15 "$c" help 2>&1; } | head -n 120
  echo "--- man synopsis/options (first 140 lines) ---"
  man "$c" 2>/dev/null | col -b | head -n 140 || echo "(no man page)"
done

section "DONE"
echo "Capture complete. Send this file back for reconciliation."
