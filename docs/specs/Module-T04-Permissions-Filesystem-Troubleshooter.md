# Module T04 — Permissions, sudo & Filesystem Troubleshooter

**Project:** W1CK3D'S KALI ASSIST · **Type:** Troubleshooter module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** `Troubleshooter-Subsystem.md`, T01–T03, Blueprint v1.8
**Last updated:** 2026-06-22

> Fourth complete troubleshooter: the "permission denied / can't write / where's my
> drive?" family — the everyday filesystem and privilege frictions, taught the right way
> (read who owns it → fix the *specific* thing, never sledgehammer it). Built to the
> template: **symptom-first** → triage → one-command-at-a-time diagnosis → verified fix →
> if exhausted, **Unresolved Issue Log** + curated trusted links. **Generate-only,
> self-contained, no AI.** Three tiers.

---

## 1. Manifest

```yaml
module_id: troubleshoot.permissions
name: "Permissions, sudo & Filesystem Troubleshooter"
version: 1.0.0
type: troubleshooter
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, fundamentals.setup_and_securing.kali] }
provides:
  symptoms: [permission_denied, sudo_issue, ownership, mount_drive, find_file, wont_execute, special_bits, readonly_fs]
  glossary_terms: [permissions_rwx, owner_group, chmod, chown, umask, sudo, group_membership, mount, fstab, suid_sgid_sticky, immutable, acl]
content:
  flows: registry/troubleshoot/permissions_*.yaml
  resources: registry/resources/permissions_links.yaml
  glossary: explain/glossary/permissions.yaml
theme: theme.w1ck3d_systems
source: "authored; verified against ls/chmod/chown/mount/find man pages + Debian/Arch docs"
license: "project-proprietary"
```

---

## 2. Symptom router (entry)

| # | Symptom (plain language) | Routes to |
|---|--------------------------|-----------|
| S1 | "Permission denied" reading/writing something | §4 |
| S2 | "sudo won't work / not in the sudoers file" | §5 |
| S3 | "I can't edit/write a file I think is mine" | §6 (ownership) |
| S4 | "My USB/drive won't mount or I can't access it" | §7 |
| S5 | "Where did my file go / how do I find it?" | §8 |
| S6 | "My script/binary won't run" | §9 |
| S7 | "Weird permission bits (SUID/sticky) / can't change a file" | §10 |
| S8 | "Read-only filesystem" errors | §11 |

**Triage (asked once):**
- What's the **exact path** and the **exact error**?
- Is it on your system disk or an external/USB drive?
- Is the file yours, system-owned, or on a Windows-formatted disk?

> **Guiding rule (stated up front):** fix the *specific* owner/permission that's wrong.
> **Never** reach for `chmod -R 777` or `chown -R` on system paths — those "fixes" create
> security holes and can break the system. The module enforces this with warnings.

---

## 3. The universal first look (shared)

1. **Who owns it and what are its permissions?** `ls -l <path>` (dir: `ls -ld <path>`)
   *Read:* `-rwxr-xr--  user group` → owner perms / group perms / others perms, then the
   owner and group names.
2. **Who am I and what groups am I in?** `id`
   *Compare:* are you the **owner**? in the **group**? If neither, you only get "others"
   permissions — which is often the whole problem.

---

## 4. S1 — "Permission denied"

### Basic
- Run §3 (`ls -l` + `id`). Three outcomes:
  - **You own it but lack a bit** (e.g., no write) → add just that bit for you:
    `chmod u+w <path>` (or `u+rwx`). *Verify:* the action works.
  - **It's group-owned and you're in the group but group lacks the bit** →
    `chmod g+rw <path>` (if it's appropriate that the group can).
  - **You're none of those / it's system-owned** → it likely *needs* root: prepend `sudo`
    to the command (if it's a legitimate admin action).

### Intermediate
- **A whole directory path is blocking you** → to enter a dir you need **execute (`x`)** on
  it: `ls -ld <each parent>`; the missing `x` on a parent denies access to everything below.
- **New files have wrong perms by default** → your `umask` (see glossary); check with
  `umask`.

### Extensive
- **ACLs overriding classic perms** → `getfacl <path>`; adjust with `setfacl` (an ACL can
  deny even when `ls -l` looks fine).
- SELinux/AppArmor contexts (rare on stock Kali) denying despite correct perms.

**⚠ Never "fix" with `chmod -R 777`** — it makes files world-writable (a security hole) and
won't even fix ownership problems. Warned with the correct narrow fix shown instead.

---

## 5. S2 — sudo won't work / "not in the sudoers file"

### Basic
- **Kali default** user `kali` is already in the `sudo` group; if `sudo` suddenly fails,
  confirm you're that user (`whoami`) and check membership: `id` (look for `sudo`).
- **"<user> is not in the sudoers file"** → that user lacks sudo rights. The fix must be
  done **by root**: `su -` (or a root shell), then `usermod -aG sudo <user>`; the user then
  **logs out and back in** for the group to take effect. *Verify:* `sudo whoami` → `root`.

### Intermediate
- **No root password / can't `su`** → you'd need another admin account or recovery mode to
  grant sudo (cross-ref the rare/hard-case boot module).
- **sudo works but asks every time / timeout** → expected; configurable via `visudo` only.

### Extensive
- **Editing sudo config safely:** *only* with `sudo visudo` (it syntax-checks before
  saving). **⚠ A broken `/etc/sudoers` can lock out all admin access** — never edit it with
  a plain editor; warned, with `visudo` mandated.
- Per-command sudo rules / `sudoers.d` drop-ins.

---

## 6. S3 — Can't edit/write a file I think is mine (ownership)

### Basic
- `ls -l <path>` → is the **owner** actually you? Files created via `sudo` are owned by
  **root**, which is the usual surprise.
- **Fix ownership** (for files that *should* be yours): `sudo chown <you>:<you> <path>`
  (add `-R` only for a directory you fully own and intend to reassign). *Verify:* `ls -l`
  shows your name; editing works.

### Intermediate
- Group collaboration: set group + group-write + setgid on a shared dir so new files
  inherit the group (`chmod g+s <dir>`).

### Extensive
- **⚠ `sudo chown -R` on the wrong path (e.g., `/`, `/usr`, your whole home as root) can
  break logins and the system.** Always target the precise directory; warned with the exact
  scope shown before running.

---

## 7. S4 — USB/drive won't mount or can't access it

### Basic
- **Is the drive seen?** `lsblk -f` (lists disks/partitions + filesystem + mountpoint).
  *No device →* check `dmesg | tail` after plugging in; try another port/cable.
- **Mount it:** `sudo mkdir -p /mnt/usb` then `sudo mount /dev/sdX1 /mnt/usb` (use the real
  name from `lsblk`). *Verify:* `ls /mnt/usb` shows files.

### Intermediate
- **Windows-formatted (NTFS/exFAT):** install drivers if needed
  (`sudo apt install ntfs-3g exfat-fuse`), then mount.
- **Mounted but "can't write / permission denied"** on FAT/NTFS (no Unix perms) → mount with
  your IDs: `sudo mount -o uid=$(id -u),gid=$(id -g) /dev/sdX1 /mnt/usb`.
- **"already mounted / busy" on unmount** → `sudo umount /mnt/usb`; if busy, find who's using
  it: `sudo lsof /mnt/usb`.

### Extensive
- **Auto-mount via `/etc/fstab`** for permanent drives — use `UUID=` (from `lsblk -f` or
  `blkid`), then test with `sudo mount -a` **before rebooting.**
  **⚠ A bad `/etc/fstab` line can stop the system from booting** — always `mount -a` test
  first; warned, with how to recover (edit from recovery/TTY) noted.
- Dirty NTFS (Windows fast-startup) refusing to mount → fix from Windows or `ntfsfix`
  (caution); filesystem errors → §11.

---

## 8. S5 — "Where did my file go / how do I find it?"

### Basic
- **By name:** `find / -iname "part-of-name*" 2>/dev/null` (the `2>/dev/null` hides the
  permission-denied noise). Narrow the start path (`find ~ …`) for speed.
- **Hidden files** (names starting `.`) → `ls -la`.

### Intermediate
- **Fast index search:** `locate <name>` (run `sudo updatedb` first if it's stale/missing).
- **Where is a command?** `which <cmd>` / `type <cmd>` / `command -v <cmd>`.
- **By recency/size:** `find ~ -mtime -1` (last day), `find ~ -size +100M`.

### Extensive
- A tool "downloaded" to the current working directory you've since left (`pwd` awareness);
  output written by a `sudo` run into a root-owned path (cross-ref T-tools output paths).
- `find` with `-exec`/`-type`/`-perm` for advanced queries.

---

## 9. S6 — Script/binary won't run

### Basic
- **"Permission denied" running a script** → it's not executable: `chmod +x <file>` then
  `./<file>`. *Verify:* it runs.
- **"command not found" for a real file** → run it by path (`./tool`) or ensure its dir is on
  `$PATH`.

### Intermediate
- **Wrong/missing interpreter** ("bad interpreter") → check the shebang (`head -1 <file>`);
  or just run it with the right one: `bash script.sh` / `python3 script.py`.
- **Windows line endings (CRLF)** break scripts → `file <script>` mentions "CRLF"; fix with
  `sudo apt install dos2unix && dos2unix <script>`.

### Extensive
- **Mounted `noexec`** (common on some `/tmp`/USB mounts) → you can't exec from there; move
  the file to a normal location or remount without `noexec`.
- Architecture/lib mismatch for a downloaded binary (`file <bin>`, missing `.so` via `ldd`).

---

## 10. S7 — Special bits (SUID/SGID/sticky) & immutable files

### Basic
- **Reading them:** an `s` in the owner/group exec slot = SUID/SGID; a `t` on others = sticky
  (e.g., `/tmp`). `ls -l` shows them.
- **"Operation not permitted" even as root** when changing a file → it may be **immutable**:
  `lsattr <file>` (look for `i`); clear with `sudo chattr -i <file>`, then modify.

### Intermediate
- Set/clear special bits deliberately: `chmod u+s` / `g+s` / `+t` — explained with *why you
  rarely should* on arbitrary files.

### Extensive
- **Auditing SUID binaries** (security learning): `find / -perm -4000 -type f 2>/dev/null` —
  why these matter (privilege escalation surface). For authorized review only.

---

## 11. S8 — "Read-only filesystem"

### Basic
- Often a **safety remount after an error.** Check why first: `dmesg | tail` (look for I/O
  or filesystem errors).
- Temporary remount read-write: `sudo mount -o remount,rw /` (or the affected mountpoint).
  *Verify:* you can write.

### Intermediate / Extensive
- **Recurring read-only = a filesystem or disk problem.** Filesystem check (`fsck`) must run
  on an **unmounted** target. **⚠ Running `fsck` on a mounted/in-use filesystem can destroy
  data** — for the root fs, do it from recovery/live media; warned, and routed to the
  rare/hard-case boot module.
- Failing disk (SMART) → cross-ref hardware/rare cases.

---

## 12. When known steps are exhausted (§6B applied)

**Unresolved Issue Log — permissions/fs fields:**
- symptom + triage (exact path + error, system vs USB, file ownership);
- outputs run: `ls -l`/`ls -ld`, `id`, `lsblk -f`, relevant `dmesg`/`getfacl`/`lsattr`,
  the failing command verbatim;
- environment: Kali version, filesystem type, mount options (`mount | grep <mp>`).
- *(No secrets — redact file contents/paths the user considers sensitive.)*

**Curated trusted links:**
- Kali docs / forums; Debian wiki — Permissions / fstab / Mount
- Arch Wiki — File permissions and attributes / fstab / mount (excellent)
- Unix & Linux Stack Exchange
- On-system: `man chmod`, `man chown`, `man mount`, `man fstab`, `man find`, `man chattr`

---

## 13. Glossary (shipped with this module)

- **permissions (rwx)** — read/write/execute, set separately for owner, group, others.
- **owner / group** — the user and group a file belongs to (`ls -l` columns).
- **chmod / chown** — change permissions / change owner+group.
- **umask** — the default permissions mask for newly created files.
- **sudo / group_membership** — run as root when permitted; the `sudo` group grants it.
- **mount / fstab** — attach a filesystem; `fstab` defines automatic mounts at boot.
- **SUID/SGID/sticky** — special bits: run-as-owner / run-as-group / restrict-deletion.
- **immutable** — a file that can't be changed until `chattr -i` clears the bit.
- **ACL** — fine-grained per-user/group permissions beyond classic rwx.

---

## 14. Design, safety, audit

- **Tokens:** commands in `--font-mono`; "did it work?" gate green/red; the **high-danger**
  steps — `chmod -R 777`, `chown -R` on system paths, editing `/etc/fstab` or `/etc/sudoers`,
  `fsck` on mounted fs — as `--status-critical` callouts with "what this does / risk / how to
  recover" **and the safe narrow alternative shown first.**
- **Generate-only:** all commands shown for the user to run; nothing executed.
- **Audit (no secrets):** symptom, tier reached, fix applied?, resolved?
- **Cross-links:** boot/recovery + disk health → rare/hard-case module; output-path
  confusion → tool modules; `man`/glossary inline; exhaustion → §12.

---

## 15. Why this matters

"Permission denied" is one of the most common beginner walls, and the dangerous "fixes"
people copy from the internet (`chmod -R 777`, `chown -R /`) are exactly what this module
steers them away from — teaching them to read `ls -l`/`id` and fix the *specific* thing.
That's both safer and genuinely educational.

*End of Module T04 (Permissions, sudo & Filesystem) spec v1.*
