# Module T05 — Rare & Hard Cases Troubleshooter

**Project:** W1CK3D'S KALI ASSIST · **Type:** Troubleshooter module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** `Troubleshooter-Subsystem.md`, T01–T04, Blueprint v1.8
**Last updated:** 2026-06-22

> The "extensive tail" — the gnarly, lower-frequency, higher-stakes problems: the machine
> won't boot, no GUI, GPU/display, disk full, live-USB persistence, clock-skew cascades,
> and locale/PATH gremlins. These often need **recovery mode or live media**, and several
> steps can make a system unbootable if done wrong — so this module is **heavy on safety
> rails, disk-identity checks, and "back up first."** Built to the template: symptom-first
> → guided diagnosis → verified fix → if exhausted, **Unresolved Issue Log** + curated
> links. **Generate-only, self-contained, no AI.**
>
> ⚠ **Whole-module caution:** boot/GRUB/partition steps assume the user is recovering *their
> own* machine and has backups of anything important. Every destructive step shows what it
> does, how to confirm the right disk, and how to recover.

---

## 1. Manifest

```yaml
module_id: troubleshoot.rare_hard
name: "Rare & Hard Cases Troubleshooter"
version: 1.0.0
type: troubleshooter
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [troubleshoot.networking, troubleshoot.packages, troubleshoot.permissions] }
provides:
  symptoms: [wont_boot, no_gui, gpu_display, disk_full, persistence, clock_skew, locale_path]
  glossary_terms: [grub, recovery_mode, chroot, display_manager, tty, nomodeset, xrandr, journald_vacuum, inode, persistence, rtc_utc, locale, path]
content:
  flows: registry/troubleshoot/rare_*.yaml
  resources: registry/resources/rare_links.yaml
  glossary: explain/glossary/rare.yaml
theme: theme.w1ck3d_systems     # high-danger steps use --status-critical (red)
source: "authored; verified against grub/systemd/xrandr/timedatectl docs + Kali/Arch wikis"
license: "project-proprietary"
```

---

## 2. Symptom router (entry)

| # | Symptom (plain language) | Routes to |
|---|--------------------------|-----------|
| S1 | "It won't boot / I get a GRUB prompt / it hangs at boot" | §3 |
| S2 | "It boots but there's no desktop / login keeps looping / black screen" | §4 |
| S3 | "Display/GPU: wrong resolution, external monitor, NVIDIA" | §5 |
| S4 | "Disk full / no space left on device" | §6 |
| S5 | "Live-USB persistence isn't saving my changes" | §7 |
| S6 | "Weird errors after a date/time change (apt/cert/sudo)" | §8 (clock) |
| S7 | "Locale/keyboard wrong, or a tool 'not found' that I installed" | §9 |

**Triage (asked once):**
- Can you reach **any** screen — a GRUB menu, a text login (TTY), or nothing at all?
- Installed-to-disk or running from a **live USB**?
- Did this start after an **update**, a **config/driver change**, or a **power loss**?

---

## 3. S1 — Won't boot / GRUB prompt / boot hangs

> ⚠ Highest-stakes area. Prefer non-destructive recovery first; treat GRUB reinstall as a
> last resort done with the **correct disk** identified.

### Tier 1 — get *a* working boot
- **Show the GRUB menu:** hold **Shift** (BIOS) or tap **Esc** (UEFI) at power-on →
  **Advanced options** → boot an **older kernel** (a bad kernel update is a common cause).
- **Recovery mode:** Advanced options → "recovery" → drops to a root maintenance shell.
- **GPU black-screen at boot:** at the GRUB menu press **`e`**, find the line starting
  `linux …`, add `nomodeset` at the end, **Ctrl+X** to boot once (then see §5 to fix
  properly).

### Tier 2 — "emergency mode" / fstab
- A boot that drops to **emergency mode** is very often a bad `/etc/fstab` entry
  (cross-ref T04 §7): read what failed (`journalctl -xb`), fix/comment the offending line,
  `sudo mount -a` to test, reboot.

### Tier 3 — repair GRUB from live media (last resort)
- Boot the **Kali live USB** → "Live" → open a terminal.
- Identify the **root partition**: `lsblk -f` (find your install, e.g. `/dev/sda2`).
  **⚠ confirm the right device — picking the wrong disk can wipe a bootloader you need.**
- Mount + chroot, then reinstall GRUB:
  ```
  sudo mount /dev/sdXN /mnt
  sudo mount --bind /dev  /mnt/dev
  sudo mount --bind /proc /mnt/proc
  sudo mount --bind /sys  /mnt/sys
  # UEFI: also  sudo mount /dev/sdXP /mnt/boot/efi
  sudo chroot /mnt
  grub-install /dev/sdX      # the DISK, not the partition (e.g. /dev/sda)
  update-grub
  exit
  ```
  **⚠** `grub-install` writes the bootloader — the target must be the correct **disk**.
  Shown with each placeholder explained and a "confirm with `lsblk` first" gate.

---

## 4. S2 — Boots but no desktop / login loop / black screen

### Tier 1 — get a usable shell
- **Switch to a text console:** **Ctrl+Alt+F2** (try F3/F4). Log in there — this proves the
  system is up and lets you fix the GUI from text.
- **Disk full breaks the GUI silently** → from the TTY run `df -h`; if `/` is 100%, go to §6
  first (this is a very common login-loop cause).

### Tier 2 — the classic login loop
- **`~/.Xauthority` owned by root** (from running a GUI app with `sudo`) loops you back to
  login. Fix from the TTY: `ls -l ~/.Xauthority` → if root-owned,
  `sudo chown $USER:$USER ~/.Xauthority` (or `rm ~/.Xauthority`), then log in.
- **Display manager state:** `systemctl status gdm3` (or `lightdm`);
  `sudo systemctl restart gdm3`. (cross-ref T03 for reading the unit.)

### Tier 3 — deeper
- Reconfigure the display manager: `sudo dpkg-reconfigure gdm3` (or `lightdm`).
- Broken `~/.xsession`/desktop config → move it aside and retry; check `~/.local/share/
  xorg/Xorg.*.log` / `journalctl -b` for the Xorg error.
- GPU driver is the cause → §5.

---

## 5. S3 — Display / GPU (resolution, external monitor, NVIDIA)

### Tier 1
- **Black screen / won't start X with a GPU** → boot once with `nomodeset` (§3 Tier 1),
  then fix the driver from a working session.
- **Wrong resolution / add external monitor:** `xrandr` lists outputs/modes;
  `xrandr --output <NAME> --auto` or `--mode 1920x1080`.

### Tier 2 — NVIDIA on Kali
- Detect/recommend: `nvidia-detect`. Install the packaged driver per Kali docs
  (`sudo apt install nvidia-driver` + the matching kernel headers), then reboot.
- **After a kernel update the GPU breaks** (module didn't rebuild) → ensure
  `linux-headers-$(uname -r)` is installed and reinstall/`dkms` the driver; reboot.

### Tier 3
- Hybrid graphics (Optimus) selection; `/etc/X11/xorg.conf` conflicts (often best removed
  to let auto-config work); Wayland vs X session choice at the login screen.

---

## 6. S4 — Disk full / "No space left on device"

### Tier 1 — find it
- **Which mount is full?** `df -h` (look for 100% — usually `/`).
- **Also check inodes** (can be full even with free space): `df -i`.
- **Biggest offenders:** `sudo du -xh / 2>/dev/null | sort -h | tail -20`
  (`-x` stays on one filesystem).

### Tier 2 — safe reclaim (most space, least risk)
- **APT cache:** `sudo apt clean`.
- **Old kernels/unused deps:** `sudo apt autoremove --purge`.
- **Journald logs:** `journalctl --disk-usage` then `sudo journalctl --vacuum-size=200M`
  (or `--vacuum-time=7d`).
- **Trash / big downloads** in your home; old files in `/var/log`. *Verify:* `df -h`.

### Tier 3
- Huge forgotten files: `find / -xdev -type f -size +500M 2>/dev/null`.
- Inode exhaustion from many tiny files (find the dir with the most entries).
- Leftover loop/mount images; Docker/VM images if installed.
- **⚠** never blindly delete from `/var`, `/usr`, `/etc` — delete caches/logs/your-own files,
  not system files. Warned with safe targets listed.

---

## 7. S5 — Live-USB persistence not saving

> Concept first: a Kali **live** session is normally amnesiac. Saving changes needs a
> **persistence** partition and you must pick the persistence entry at boot.

### Tier 1 — the usual misses
- **Did you boot the persistence entry?** At the Kali boot menu choose **"Live system
  (persistence)"** (or encrypted persistence) — not plain "Live".
- **Is there a persistence partition?** `lsblk -f` → a partition **labeled `persistence`**.

### Tier 2 — set it up / fix it
- The persistence partition needs a file `persistence.conf` containing exactly:
  `/ union`. If missing/empty, changes won't persist. (Follow the Kali persistence docs
  for creating the partition + conf — steps vary by USB layout.)
- Encrypted persistence: ensure you're unlocking it at boot.

### Tier 3
- Wrong filesystem/label; multiple USBs confusing the boot; size/space on the persistence
  partition (cross-ref §6). This area is fiddly — the Issue Log + Kali docs link are the
  honest fallback.

---

## 8. S6 — Clock / time skew cascades (apt, certs, sudo)

> A wrong system clock breaks far more than the clock: package **signatures** ("not valid
> yet"), **TLS certificates** (git/apt/curl "verify failed"), even `sudo` timestamp warnings.

### Tier 1
- **Check it:** `timedatectl` (look at "Local time", "NTP service", "synchronized").
- **Fix via NTP:** `sudo timedatectl set-ntp true` → wait, re-check `timedatectl`.
  *Verify:* re-try the failing apt/cert/git action (cross-ref T02 §1/§6).

### Tier 2 — dual-boot / VM skew
- **Windows dual-boot makes the clock jump** (RTC-in-localtime vs UTC). Tell Linux the RTC
  is local time *or* set Windows to UTC — pick one. `timedatectl set-local-rtc 0` keeps RTC
  in UTC (recommended). 
- VM guest clock drift after suspend → enable guest time sync / re-sync NTP.

### Tier 3
- No network for NTP → set time manually `sudo timedatectl set-time "YYYY-MM-DD HH:MM:SS"`
  to get past cert/signature checks, then fix NTP once online.

---

## 9. S7 — Locale/keyboard wrong, or installed tool "not found" (PATH/shell)

### Tier 1 — locale & keyboard
- **`locale: Cannot set LC_*` warnings** → `sudo dpkg-reconfigure locales` (select/generate
  your locale), re-login.
- **Wrong keyboard layout** → `sudo dpkg-reconfigure keyboard-configuration` (console) /
  `setxkbmap <cc>` (X session).

### Tier 2 — "I installed it but command not found" (PATH)
- **Check PATH:** `echo $PATH`. Tools often install to `~/.local/bin` (pipx) or `~/go/bin`
  (Go) which may not be on PATH.
- **Add it (Kali default shell is zsh, not bash!):** append to **`~/.zshrc`** (not
  `~/.bashrc`): `export PATH="$HOME/.local/bin:$PATH"`, then `source ~/.zshrc`.
  pipx: `pipx ensurepath` does this for you.

### Tier 3 — shell surprises
- **Script works in bash but not your shell** → Kali defaults to **zsh**; run with `bash
  script.sh`, or fix the shebang. Switch default shell if preferred: `chsh -s /bin/bash`.
- `~/.zshrc` vs `~/.bashrc` confusion (which file your edits belong in); login vs
  non-login shells not sourcing what you expect.

---

## 10. When known steps are exhausted (§6B applied)

**Unresolved Issue Log — rare/hard fields:**
- symptom + triage (what screen you can reach, installed vs live, what changed);
- outputs run: `lsblk -f`, `df -h`/`df -i`, `journalctl -xb` key lines, `timedatectl`,
  `xrandr`, `nvidia-detect`, `echo $PATH` — whatever the flow used;
- environment: Kali version, kernel (`uname -r`), firmware/UEFI vs BIOS, GPU model.
- *(No secrets; redact disk identifiers if the user wishes.)*

**Curated trusted links (these areas especially benefit from the wikis):**
- Kali docs — persistence, NVIDIA, recovery (kali.org/docs); Kali forums / bug tracker
- Arch Wiki — GRUB, NVIDIA, Xorg, Persistent block device naming, System time (best-in-class)
- Debian wiki — GRUB / recovery / fstab
- Unix & Linux Stack Exchange
- On-system: `man grub-install`, `man timedatectl`, `man xrandr`, `man journalctl`

---

## 11. Glossary (shipped with this module)

- **grub** — the bootloader that loads the kernel; its menu lets you pick kernels/options.
- **recovery_mode** — a minimal boot to a root maintenance shell for repairs.
- **chroot** — run commands "inside" your installed system from live media (for repairs).
- **display_manager** — the graphical login (gdm3/lightdm) that starts your desktop.
- **tty** — a text console (Ctrl+Alt+F2…) usable when the GUI is broken.
- **nomodeset** — a boot option that skips early GPU mode-setting (fixes many black screens).
- **xrandr** — tool to query/set screen resolution and outputs.
- **journald vacuum** — trimming systemd logs to reclaim disk.
- **inode** — filesystem slots for files; can run out even with free space.
- **persistence** — the Kali live feature that saves changes across reboots.
- **RTC / UTC** — hardware clock; dual-boot localtime-vs-UTC mismatch causes skew.
- **PATH** — where the shell looks for commands; missing dirs cause "not found".

---

## 12. Design, safety, audit

- **Tokens:** commands in `--font-mono`; "did it work?" gate green/red. This module has the
  **most `--status-critical` (red) callouts** — every GRUB/chroot/`grub-install`, partition,
  and bulk-delete step shows: what it does, **how to confirm the right disk**, the risk, and
  how to recover. Safe alternatives are always presented first.
- **Generate-only:** all commands shown for the user to run; nothing executed.
- **Back-up reminder:** boot/partition flows lead with "back up anything important first."
- **Audit (no secrets):** symptom, tier reached, fix applied?, resolved?
- **Cross-links:** fstab → T04; apt/cert after clock fix → T02; display-manager unit → T03;
  exhaustion → §10.

---

## 13. Why this is the right "extensive tail"

These are exactly the cases where people panic, copy a dangerous command, and make it
worse. By gating the risky steps behind disk-identity confirmation, safe-first ordering,
and clear recovery paths — and by being honest (with the Issue Log + wikis) about the truly
novel ones — the module helps without pretending it can fix everything blind. It rounds out
the troubleshooter so the four core modules plus this tail cover the large majority of what
a Kali user actually hits.

*End of Module T05 (Rare & Hard Cases) spec v1.*
