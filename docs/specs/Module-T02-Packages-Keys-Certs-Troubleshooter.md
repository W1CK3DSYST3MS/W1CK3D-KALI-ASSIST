# Module T02 — Packages, Keys & Certificates Troubleshooter

**Project:** W1CK3D'S KALI ASSIST · **Type:** Troubleshooter module · **os_profile: kali**
**Status:** spec v1 · **Companion to:** `Troubleshooter-Subsystem.md`, `Module-T01`, Blueprint v1.8
**Last updated:** 2026-06-22

> The second complete troubleshooter — and the **integral-Kali-functions showcase**:
> `apt`, repository trust (GPG keys + `signed-by`), TLS certificates / CA authority, and
> installing tools from git. Built to the T01 template: **symptom-first** → triage →
> one-command-at-a-time diagnosis → verified fix → if exhausted, **Unresolved Issue Log** +
> curated trusted links. **Generate-only, self-contained, no AI.** Three tiers
> (Basic → Intermediate → Extensive).

---

## 1. Manifest

```yaml
module_id: troubleshoot.packages
name: "Packages, Keys & Certificates Troubleshooter"
version: 1.0.0
type: troubleshooter
os_profile: kali
requires: { base_api: ">=1.0" }
recommends: { modules: [fundamentals.shell_grammar, fundamentals.setup_and_securing.kali] }
provides:
  symptoms: [update_errors, pubkey_signature, broken_deps, dpkg_lock, third_party_repo, cert_tls, git_install]
  glossary_terms: [repository, package, apt_vs_dpkg, gpg_key, keyring, signed_by, signature, ca_certificate, certificate_authority, dependency, held_package, pep668]
content:
  flows: registry/troubleshoot/packages_*.yaml
  resources: registry/resources/packages_links.yaml
  glossary: explain/glossary/packages.yaml
theme: theme.w1ck3d_systems
source: "authored; verified against apt/dpkg/gpg/update-ca-certificates man pages + Kali/Debian docs"
license: "project-proprietary"
```

---

## 2. Symptom router (entry)

| # | Symptom (plain language) | Routes to |
|---|--------------------------|-----------|
| S1 | "apt update / upgrade throws errors" | §3 |
| S2 | "NO_PUBKEY / signature / 'not signed' errors" | §4 |
| S3 | "broken / unmet / held-back dependencies" | §5 |
| S4 | "could not get lock / dpkg was interrupted" | §6 |
| S5 | "I want a tool that isn't installed / add another repo safely" | §7 |
| S6 | "certificate / TLS 'verify failed' errors" | §8 |
| S7 | "install a tool from a git repo (clone + build)" | §9 |

**Triage (asked once):**
- What is the **exact error line**? (copy it — apt's errors are precise and point straight
  at the cause.)
- Did this start after an update, adding a repo, or on a fresh install?
- Is the repo/tool **official Kali** or **third-party**?

> **Kali rule of thumb (stated up front):** on Kali, **do not add third-party repos to the
> base system** unless you understand the risk — mixing repos can break the rolling
> distro. Prefer the Kali repos; use git/pipx/containers for one-off tools (§7/§9).

---

## 3. S1 — apt update / upgrade errors (general)

### Basic
- **Read the error first** — the fix depends on it. Re-run `sudo apt update` and note which
  line fails (network? signature? release-info?).
- **The correct Kali sequence:** `sudo apt update` then `sudo apt full-upgrade`
  (`full-upgrade` handles the dependency changes a rolling distro constantly makes).
- **Network/DNS failure** (`Could not resolve` / `Failed to fetch`) → this is a networking
  problem, not apt → hand to **T01 Networking** (Issue Log carries over).

### Intermediate
- **"Repository changed its Codename/Suite/Origin"** prompt → review it's expected, then
  `sudo apt update --allow-releaseinfo-change`.
- **One mirror failing intermittently** → retry shortly; do **not** "fix" it by editing
  sources/adding mirrors on Kali.
- **Partial/`apt upgrade` left things back** → use `full-upgrade` (see Basic).

### Extensive
- Rolling-release breakage from a half-finished upgrade → `sudo dpkg --configure -a` then
  `sudo apt --fix-broken install` then `sudo apt full-upgrade` (cross-ref S3/S4).
- Disk full breaking apt → `df -h`; clear with `sudo apt clean` / prune old kernels.
- Time skew breaking signature/cert validation → see S6 (`timedatectl`).

---

## 4. S2 — NO_PUBKEY / signature / "not signed"

### Basic (official Kali)
- **`NO_PUBKEY` on a Kali repo** → refresh Kali's keyring (the canonical fix):
  `sudo apt install kali-archive-keyring` then `sudo apt update`.
  *Verify:* update completes with no signature error.

### Intermediate (third-party repo)
- **`NO_PUBKEY` / "not signed" on a third-party repo** → the modern model: keys live in
  `/etc/apt/keyrings/` and each source declares its key with `signed-by=` (the old `apt-key`
  is **deprecated** — don't use it).
  1. `sudo install -m 0755 -d /etc/apt/keyrings`
  2. `curl -fsSL <repo>/key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/<name>.gpg`
  3. ensure the source line is
     `deb [signed-by=/etc/apt/keyrings/<name>.gpg] <url> <suite> <component>`
  4. `sudo apt update`
- **"repository is not signed"** → you omitted `signed-by=` (or the keyring path is wrong).

### Extensive
- Wrong key format (ASCII-armored vs binary) → that's what `--dearmor` fixes.
- Key expired/rotated → fetch the current key from the vendor.
- Legacy keys in `/etc/apt/trusted.gpg.d/` causing warnings → migrate to per-repo
  `signed-by`.

**Trust/authority note:** a repo key means you trust everything that repo ships, as root.
Only add keys/repos from sources you trust, fetched over HTTPS from the official origin.

---

## 5. S3 — broken / unmet / held-back dependencies

### Basic
- **Auto-repair:** `sudo apt --fix-broken install`.
- **Finish interrupted configures:** `sudo dpkg --configure -a`.
- **Then:** `sudo apt full-upgrade`. *Verify:* the failing install/upgrade now completes.

### Intermediate
- **Read what apt proposes** before confirming — note any package it wants to **remove**;
  on Kali a big removal list often means a partial-upgrade state, fixed by `full-upgrade`.
- **Held packages:** `apt-mark showhold` → unhold if intended: `sudo apt-mark unhold <pkg>`.
- **A single package unmet** → `sudo apt install <pkg>` and read the exact unmet line.

### Extensive
- Conflicting third-party packages pinning versions → remove the offending source/package.
- `aptitude` for interactive resolver suggestions (optional).
- Truly stuck dpkg states → targeted `sudo dpkg --remove --force-... ` **(⚠ destructive,
  last resort — warned, with what-it-does first)**.

---

## 6. S4 — "Could not get lock" / dpkg interrupted

### Basic
- **Something else is using apt** (an updater, another terminal, unattended-upgrades).
  Wait for it to finish. Locks: `/var/lib/dpkg/lock-frontend`, `/var/lib/apt/lists/lock`.
- **See what holds it:** `sudo lsof /var/lib/dpkg/lock-frontend` (or `ps aux | grep -i apt`).

### Intermediate
- **A previous apt crashed mid-run:** `sudo dpkg --configure -a` to finish it, then retry.

### Extensive
- **No apt process is actually running but the lock persists** (stale lock from a hard
  crash) → only then remove the lock files
  (`sudo rm /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock`) and run
  `sudo dpkg --configure -a`.
  **⚠ destructive/dangerous:** never remove locks while apt is genuinely running — it can
  corrupt the package database. The module shows this only after confirming no apt process
  exists, with the warning first.

---

## 7. S5 — Install a tool that isn't there / add a repo safely

### Basic
- **Is it already packaged?** `apt search <name>` (or `apt-cache search <keyword>`); install
  with `sudo apt install <pkg>`. Many Kali tools just aren't in your metapackage yet.
- **Pull more Kali tools:** e.g. `sudo apt install kali-linux-large` (bigger toolset) —
  still all official Kali.

### Intermediate (add a third-party repo — the right way)
- Use the **S2 Intermediate** key + `signed-by` procedure to add the repo's source, then
  `sudo apt update && sudo apt install <pkg>`.
- Keep each third-party source in its own file under `/etc/apt/sources.list.d/`.

### Extensive
- **Prefer isolation over base-system repos:** for one-off tools, `pipx install <tool>`
  (Python apps), a container, or git build (§9) avoids polluting the rolling base.
- `.deb` from a vendor → `sudo apt install ./file.deb` (apt resolves its deps; avoid raw
  `dpkg -i` which doesn't).

**Authority note again:** adding a repo = trusting it as root. On Kali, weigh whether you
need it in the base system at all.

---

## 8. S6 — Certificate / TLS "verify failed"

### Basic
- **Ensure the CA bundle is present/updated:**
  `sudo apt install ca-certificates && sudo update-ca-certificates`.
- **Check the clock** — a wrong date breaks TLS instantly: `timedatectl`
  (fix with `sudo timedatectl set-ntp true`). *Verify:* the HTTPS `apt`/`git` action works.

### Intermediate (trust a custom CA)
- Put the CA's PEM file (must end `.crt`) in `/usr/local/share/ca-certificates/`, then
  `sudo update-ca-certificates` (it links it into the system trust store).
  *Verify:* `curl -v https://<host>` no longer reports "self-signed/unknown issuer".

### Extensive
- **Per-app trust stores differ from the system store:** browsers and Python (`certifi`)
  keep their own — a cert can pass system checks but fail in an app (and vice-versa).
- Intercepting corporate proxy presenting its own CA → install that CA (above) only if you
  trust the network.
- `git` specifically: `git config --global http.sslCAInfo <path>` for a custom bundle
  (avoid `http.sslVerify false` — that disables security; **⚠ warned**).

**Authority concept (taught inline):** a CA vouches for a site's identity via a chain of
trust; trusting an unknown CA lets it impersonate any site to you — only add CAs you trust.

---

## 9. S7 — Install a tool from a git repo (clone + build)

### Basic
- `git clone <url>` → `cd <dir>` → **read its `README`/`INSTALL` first** (every project
  differs). Install listed dependencies via `sudo apt install <deps>`.
- **Git over HTTPS fails with a cert error** → that's S6.

### Intermediate (by project type)
- **Python project:** modern Kali blocks system-wide `pip install` (PEP 668,
  "externally-managed-environment"). Correct paths:
  - app/tool → `pipx install .` (isolated, on PATH); or
  - library/dev → a venv: `python3 -m venv .venv && source .venv/bin/activate && pip install .`
  - last resort `pip install --break-system-packages` **(⚠ can break system Python —
    warned, with what-it-does first)**.
- **C/C++ project:** `sudo apt install build-essential` then `make` (and `sudo make install`
  if intended — note it installs outside apt's tracking).
- **Go project:** `go build` / `go install` (binary lands in `~/go/bin`; ensure it's on PATH).

### Extensive
- Build fails on missing dev headers → install the `-dev` package the error names.
- Needs kernel headers (drivers/DKMS) → `sudo apt install linux-headers-$(uname -r)`.
- Where the binary went / PATH (`echo $PATH`); uninstalling source-built tools cleanly.
- **Authenticity:** only clone from the official repo; review what build scripts do —
  `make install`/`setup.py` run arbitrary code as you (or root).

---

## 10. When known steps are exhausted (§6B applied)

**Unresolved Issue Log — packages fields:**
- symptom + triage (exact error line, official vs third-party, when it started);
- commands run + outputs: the failing `apt`/`dpkg`/`gpg`/`git` line, `apt-mark showhold`,
  `timedatectl`, relevant `/etc/apt/sources.list.d/*` contents (redact tokens);
- environment: Kali version, `apt-cache policy` snippet, package + version in question.
- *(No secrets — repo tokens/credentials never logged.)*

**Curated trusted links:**
- Kali docs (kali.org/docs), forums, bug tracker
- Debian wiki — Apt / SecureApt / package management (wiki.debian.org)
- Arch Wiki — pacman/AUR pages are still great general dependency/repo concepts
- Unix & Linux Stack Exchange / Ask Ubuntu (Debian-family)
- The tool's own GitHub repo + issues
- On-system: `man apt`, `man apt-secure`, `man dpkg`, `man update-ca-certificates`

---

## 11. Glossary (shipped with this module)

- **repository** — an online source apt installs from (Kali's are curated).
- **package** — an installable software bundle (`.deb`); managed by apt/dpkg.
- **apt vs dpkg** — `apt` resolves dependencies + fetches; `dpkg` installs a single `.deb`
  and does *not* resolve deps.
- **gpg_key / keyring** — the cryptographic key proving a repo's packages are authentic;
  modern keys live in `/etc/apt/keyrings/`.
- **signed_by** — the per-source setting binding a repo to its key (replaces `apt-key`).
- **signature** — the cryptographic proof apt checks before trusting packages.
- **ca_certificate / certificate_authority** — the trust anchor that validates HTTPS
  identities; system store updated via `update-ca-certificates`.
- **dependency** — another package a package needs to work.
- **held_package** — a package pinned from upgrading (`apt-mark hold`).
- **pep668 / externally-managed** — why system-wide `pip` is blocked; use pipx/venv.

---

## 12. Design, safety, audit

- **Tokens:** commands in `--font-mono`; "did it work?" gate green/red; **destructive or
  trust-sensitive** steps (removing locks, `--break-system-packages`, `sslVerify false`,
  adding repos/keys/CAs) shown as `--status-critical` callouts with "what this does / risk /
  how to undo" first.
- **Generate-only:** everything shown for the user to run; nothing executed.
- **Audit (no secrets):** symptom, tier reached, fix applied?, resolved? — never tokens/keys.
- **Cross-links:** networking failures → T01; `man`/glossary inline; exhaustion → §10.

---

## 13. Notes for the build / authoring

- Modern apt trust (`signed-by` + `/etc/apt/keyrings`) and PEP 668 are current best
  practice as of authoring — flag for periodic re-verification, since apt/Python packaging
  conventions evolve.
- This module deliberately doubles as the home for the "integral Kali functions" Hunter
  called out (git installs, key/cert/authority handling).

*End of Module T02 (Packages, Keys & Certs) spec v1.*
