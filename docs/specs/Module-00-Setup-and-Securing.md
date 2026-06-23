# Module 00 — First Setup & Securing (Router)

**Type:** Lesson module group (router) · **Status:** spec v3 — Kali-only (Parrot parked)
**Companion to:** Tool Wizard Blueprint v1.3 (§15 OS profiles)
**Last updated:** 2026-06-21

> **Current scope: Kali only.** The router currently resolves to the **Kali edition**.
> The Parrot edition is **parked** (deferred) — see `Module-00-Parrot-Setup-and-Securing.md`,
> which now holds field notes for whoever picks Parrot up later. The router pattern is
> kept so re-adding Parrot is just re-enabling a route — no rework of the Kali product.

---

## 1. Router manifest

```yaml
module_id: fundamentals.setup_and_securing
name: "First Setup & Securing"
version: 3.0.0
type: lesson_router
requires:
  base_api: ">=1.0"
provides:
  router: lesson.setup_and_securing
routes:
  - when: { os_profile: kali }
    load: fundamentals.setup_and_securing.kali     # Module-00-Kali (ACTIVE)
  # - when: { os_profile: parrot }                 # PARKED — re-enable when ready
  #     load: fundamentals.setup_and_securing.parrot
  - when: { os_profile: not_kali }
    action: notify_unsupported                     # tell user this build targets Kali
os_targets: [kali]
```

## 2. Routing logic (current)

1. Read `/etc/os-release` to detect the distro.
2. If `kali` → load the **Kali edition** (`Module-00-Kali-Setup-and-Securing`).
3. If **not** Kali → inform the user this build supports Kali only (don't apply Kali
   steps to another distro).

> To re-add Parrot later: finalize the parked Parrot edition, uncomment its route, add
> `parrot` to `os_targets`. No change to the Kali edition required.

## 3. Editions

- **Kali edition (ACTIVE)** — `Module-00-Kali-Setup-and-Securing.md`
- **Parrot edition (PARKED)** — `Module-00-Parrot-Setup-and-Securing.md` (field notes only)

*End of Module 00 router spec v2.*
