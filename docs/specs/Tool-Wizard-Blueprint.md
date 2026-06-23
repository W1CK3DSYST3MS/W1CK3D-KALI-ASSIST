# W1CK3D'S KALI ASSIST — Project Blueprint

*A **W1CK3D SYSTEMS** project — standalone Kali Linux interactive support & education tool.*

**Version:** 1.8 (free build = self-contained no-AI; editions + closed distribution)
**Status:** Blueprint / reference spec — for handoff to a build service
**Last updated:** 2026-06-21

> **CURRENT SCOPE — Kali Linux only.** The product is now focused as a **standalone Kali
> Linux interactive support & education tool**. Parrot OS is **parked** (deferred) due to
> its sandboxing / managed-access-control complexity, which needs dedicated testing to
> teach safely. The OS-profile architecture (§15) is retained specifically so Parrot — or
> any other distro — can be added later as its own module **without reworking the Kali
> product.** Where this document still mentions Parrot, treat it as *future/parked* unless
> noted otherwise.

> This document is the single source of truth for the project. It consolidates the
> original brainstorming transcript into one organized specification. It defines
> **what** the product is and **how** it should be structured. It does **not** write
> the implementation code — a dedicated build service will do that, using this map.

---

## 1. Product vision

A **guided, generate-only learning companion** for **Kali Linux** — its security tooling
and the OS itself. (Parrot and other distros are a future, parked expansion; see scope
banner above and §15.) It teaches the user the correct usage of CLI tools —
syntax, flags, arguments, environment setup, and OS-specific quirks — through an
adaptive step-by-step wizard, while also serving as a fast "get the info I need"
reference.

The product is **one unified system** with three faces that share a single brain:

1. **Tool Wizard** — guided, slot-based construction of correct command structures
   for individual tools (e.g., `nmap`, `gvm-start`, `amass`).
2. **OS Learning Companion** — guided lessons on Kali/Parrot features, services,
   permissions, networking, package management, and the quirks that separate these
   distros from generic Linux.
3. **Self-help Troubleshooter** — symptom-first guided diagnosis with **no live
   assistant**; when authored flows are exhausted it produces an Issue Log + trusted links
   for self-directed search. See §15B / `Troubleshooter-Subsystem.md`.

### Guiding principles

- **Simple to use, complete in depth.** The two pillars, held together, not traded off.
  Every flow has an easy on-ramp (pick a profile, answer a couple of prompts) *and*
  complete coverage underneath (every flag, state, and option explained for those who go
  deeper). A beginner is never overwhelmed; an advanced user is never shortchanged.
- **Generate-only. Never execute.** The app shows and explains commands; it never
  runs them. Safety comes from accountability (login + audit log), not from
  withholding information that is freely available online.
- **Learn-as-you-ask.** Every answer doubles as a lesson. The user should come away
  understanding *what / why / where*, not just copying a string.
- **Repetition builds memory.** The same grammar, the same slot model, and the same
  explanation format appear every time, so patterns stick.
- **Grows with the user.** Adding tools, flows, lessons, and OS topics is a matter of
  adding data (specs/knowledge), not rewriting the UI.
- **Adaptive, not linear.** The wizard verifies progress at each step and branches to
  alternatives when something doesn't work (see §4).

### Explicit non-goals

- No command execution, scanning, or exploitation from within the app.
- Not a replacement for `man` pages or online docs — it organizes and teaches them.
- Not a vulnerability scanner, payload generator, or attack framework.

### Editions & distribution

- **Free Standalone edition (current target):** fully **self-contained, no AI/model
  layer.** Runs for anyone, offline, with no hardware or subscription barrier. This is what
  ships first; all help is pre-authored (flows, explanations, glossary) + the Unresolved
  Issue Log fallback.
- **Enterprise / retail edition (future option):** adds **AI assistance** — a local LLM
  for free on-device help where hardware allows, and/or a paid portal-LLM tier. Optional
  and monetizable; never required for the core tool to work.
- **Distribution model:** released via **GitHub as a built tool file only.** The **source
  code and these blueprints are NOT published** — keeping the build closed preserves the
  option to offer a paid Enterprise edition later.
- **Implication:** these blueprint/spec documents are **internal, private design assets**,
  not shipped artifacts.

---

## 2. Platforms & packaging

Two editions, one shared core (`wizard-core`, see §6).

### 2.1 Desktop edition (Kali) — standalone executable app

- **Form factor:** a self-contained **desktop application / executable program**,
  not a website and not a browser app. The user launches it like any other GUI app.
- **GUI stack:** Python + **PySide6** (recommended) or PyQt6 — tabbed UI, wizard
  pages, live command-preview pane.
- **Packaging:** bundled into a single distributable executable with a tool such as
  **PyInstaller** (or `briefcase`/`AppImage` for a portable Linux binary). Ships with
  the bundled knowledge base so it works offline.
- **Target OS:** Kali Linux desktop (Debian-based); should also run on a standard Ubuntu
  desktop. (Parrot parked — future module.)

### 2.2 Android / Termux edition — headless TUI

- **Form factor:** a text UI / CLI program that runs inside **Termux** on an Android
  device, including the **proot / Ubuntu venv** setups the user runs.
- **Style:** menu-driven stepper (select category → tool → flow → step prompts),
  rendering the same explanations and command previews as the desktop edition.
- **Packaging:** a Python package/script installable in Termux; same `wizard-core`
  dependency, no GUI libraries.

> Both editions consume the identical registry + knowledge base + builders. Command
> and teaching logic is **never** duplicated between front-ends.

---

## 3. The core teaching model — CLI "slots"

The biggest learning problem this product solves: vague placeholder templates like
`tool [global options] [action options] [args] [defs]` are unmemorable and easy to
get wrong, and the CLI often fails silently on bad ordering. The fix is to teach
**every** command as the same ordered set of **slots**.

### 3.1 The universal slot order

| # | Slot | What goes here | Example (nmap) |
|---|------|----------------|----------------|
| 1 | `PROGRAM` | the executable name | `nmap` |
| 2 | `GLOBAL_OPTIONS` | flags affecting the whole run (timing, DNS, verbosity) | `-n -Pn -T4` |
| 3 | `TARGET_PIVOT` | the scope: hosts / CIDR / domains / URLs / files | `192.168.1.0/24` |
| 4 | `ACTION_OPTIONS` | what the tool does to the targets | `-sV -p 22,80,443` |
| 5 | `OUTPUT_OPTIONS` | output formats + destinations | `-oX ./out/scan.xml` |
| 6 | `POSITIONAL_ARGS` | required positional values (tool-defined, if any) | — |
| 7 | `ENV/INTERFACE_CONFIG` | interface / capture / proxy / host-binding | (e.g. capture iface) |
| 8 | `EXTRA_FILES` | wordlists, certs, script files | `-w rockyou.txt` |

Not every tool/flow uses every slot. A flow declares which slots it uses; the builder
always assembles them in this fixed order, so **the user never reorders anything**.

### 3.2 Each input maps to exactly one slot

In the wizard, a single user input maps to a single slot. "Ports" always fills
ACTION_OPTIONS; "Targets" always fills TARGET_PIVOT; "Output path" always fills
OUTPUT_OPTIONS. The command is then generated in correct order every time.

### 3.3 Three synchronized views, shown every time

For any command the wizard shows:

- **A) Skeleton (numbered slots):** the shape of the command with placeholders.
- **B) Filled (slot-ordered):** the same command with the user's real values.
- **C) Why-this-goes-here:** one short, true, precise sentence per slot.

Example for an nmap basic scan:

```
Skeleton:   nmap [global] {targets} [action] [output]
Filled:     nmap -n -Pn -T4 192.168.1.0/24 -sV -p 22,80,443 -oX ./out/scan.xml
Why:        global = behavior for the whole run | {targets} = the scope/pivot |
            action = what to probe | output = where results are written
```

### 3.4 Profiles to reduce decision load

Each flow offers **profiles** that pre-fill the harder slots so beginners pick only
targets + output:

- **Discovery** — minimal, low-noise.
- **Service** — adds service/version detection behavior.
- **Aggressive** — adds scripting/timing.

Profiles are a teaching scaffold, not execution presets — they still only generate
and explain.

---

## 4. The adaptive verify-and-branch stepper *(core interaction model)*

This is the defining interaction pattern of the product. Instead of a linear
"next, next, next" wizard, each step is a **test-and-confirm loop**:

```
        ┌─────────────────────────────────────────────┐
        │  STEP N                                       │
        │  • Show: instruction + slot explanation       │
        │  • Show: exact command/structure to try       │
        │  • Ask:  "Did this step work?  [Yes] / [No]"  │
        └───────────────┬───────────────┬──────────────┘
                        │Yes            │No
                        ▼               ▼
                 ┌────────────┐   ┌───────────────────────────┐
                 │  STEP N+1  │   │  Offer alternative for     │
                 └────────────┘   │  STEP N (branch):          │
                                  │  • different approach/flag  │
                                  │  • likely cause + fix       │
                                  │  • which log/output to check│
                                  └───────────┬───────────────┘
                                              │ retry → ask again
                                              ▼
                                     (loop until Yes, or
                                      exhausted → Issue Log + links)
```

### 4.1 Behavior

1. **Scenario input.** The user states what they want to accomplish (free text or a
   picked flow). This seeds the relevant lesson/flow.
2. **One step at a time.** The wizard presents **Step 1** — what to do, the slot
   explanation, and the exact structure to test.
3. **Confirmation gate.** The user reports **Yes / No** (did it work?).
   - **Yes →** advance to the next step.
   - **No →** the wizard offers an **alternative step** (a different flag/approach),
     the likely root cause, and which log/output to inspect — then re-asks.
4. **Exhaustion (no live help).** If alternatives are exhausted, the tool generates an
   **Unresolved Issue Log** (steps tried + error output) and offers curated trusted links
   for self-directed search (§7, `Troubleshooter-Subsystem.md` §6B). No assistant/service.

### 4.2 Why this matters

It directly fixes the user's "hours chasing my tail" problem: progress is verified
incrementally, errors are caught at the step that caused them, and the user learns
*why* a step failed — not just that it did.

### 4.3 Data needed per step to support branching

Each `StepSpec` (see §6.3) carries: the primary instruction, the slot mapping, a
`success_criteria` description ("what success looks like"), and an ordered list of
`alternatives[]` (each with its own instruction, cause hypothesis, and
verification/log hint).

---

## 5. Knowledge backend — how the wizard gets its content

The explanations, syntax, OS quirks, and troubleshooting branches all need a source.
Three options were considered; a **hybrid** is recommended.

### 5.1 Option A — Curated static library

A hand-built / sourced knowledge base in YAML/JSON: per-tool flows, slot mappings,
explanation text, OS-quirk lessons.

- **Pros:** most accurate and predictable; fully offline; no model resources; safe
  (nothing invented).
- **Cons:** labor-intensive to author; slow to scale toward "all tools"; troubleshooting
  branches must be anticipated and written by hand.

### 5.2 Option B — Small local LLM / RAG

A small language model answers and explains, retrieving from curated data
(retrieval-augmented generation) so it stays grounded.

- **Pros:** scales to many tools quickly; flexible free-text Q&A; natural "helpdesk"
  feel; can generate alternative steps on the fly.
- **Cons:** needs guardrails for accuracy (hallucination risk on exact flags is
  dangerous in security tooling); heavier device resources (challenging on the Termux
  edition); harder to keep deterministic.

### 5.3 Option C — Hybrid *(recommended)*

A **curated knowledge base as the ground truth**, with a **small model + RAG layer on
top** for explanation phrasing, free-text Q&A, and generating troubleshooting
alternatives — always constrained to retrieved facts.

- **Command structures and exact flags come only from the curated registry/builders**
  (deterministic, verifiable). The model never invents a flag.
- **The model handles natural language**: rephrasing explanations to the user's level,
  answering "what is a global option?", and proposing branch alternatives drawn from
  the curated troubleshooting data.
- **Graceful degradation:** the Termux edition can run **curated-only** (no model) and
  still be fully functional; the desktop edition can enable the model layer where
  resources allow.

**Recommendation (revised per editions decision):** the **Free Standalone edition is
curated-only — no model layer at all** (Option A), so it runs for everyone offline with no
hardware/subscription barrier. Still design the data so a RAG/model layer *could* be added
without re-architecting — but that **hybrid/model layer is reserved for the future
Enterprise edition** (see §1 Editions), not the free build.

### 5.4 Candidate source material to seed the curated library

Man pages (`man`/`--help` output), `tldr` pages, the Kali Tools documentation, Parrot
docs, official tool docs (e.g., Greenbone/GVM docs for `gvm-start`), and reputable
wiki-style CLI references. Authoring workflow: extract → restructure into slots →
write the *what/why/where* explanations → review for accuracy.

> **Accuracy is the hard problem.** Whatever backend is chosen, every command
> structure must be verifiable against an authoritative source before it ships. The
> curated layer is the contract; the model is a presenter, never an authority on
> exact syntax.

---

## 6. Shared engine — `wizard-core`

The UI-agnostic brain both editions depend on. Spec-driven so coverage grows by adding
data, not code.

### 6.1 Suggested project layout

```
wizard-core/
  registry/
    tools.yaml                # ToolSpecs + FlowSpec metadata
    flows/                    # per-tool flow specs
      nmap_basic.yaml
      gvm_start.yaml
      amass_basic.yaml
    lessons/                  # OS Learning Companion topics (Kali/Parrot quirks)
      kali_services.yaml
      parrot_anonsurf.yaml
      package_management.yaml
  schema/
    slots.py                  # the 8 CLI slot definitions
    steps.py                  # Step types (targets, interface, output dir, etc.)
    validation.py             # input validation rules (Pydantic)
  command_builders/
    nmap_builder.py
    gvm_start_builder.py
    common.py                 # shell-escaping, quoting, path handling, slot joiner
  explain/
    templates.py              # consistent what/why/where rendering per slot
    glossary.py               # beginner glossary (see §9), shown inline first-use
  knowledge/
    store.py                  # curated KB access; optional RAG/model adapter
  output/
    manifests.py              # planned artifact naming/paths (PLAN ONLY, no writing)
  audit/
    logger.py                 # on-device audit logging interface (UI-agnostic)
  auth/
    login_policy.py           # local login-gate rules (UI-agnostic)

wizard-desktop/               # PySide6 GUI app → packaged as an executable
  ui/ (main_window, login_window, tab_view, wizard_pages, command_preview_panel)
  app.py

wizard-android-termux/        # headless TUI
  tui/ (main, forms)
  app.py
```

### 6.2 Core data objects

- **ToolSpec** — `tool_id`, `display_name`, `binary_candidates` (for install
  detection), `categories[]` (tab tags), `flows[]`.
- **FlowSpec** — `flow_id`, `title`, `slots[]` (which slots this flow uses),
  `steps[]`, `command_builder_id`, `output_manifest` (planned artifacts).
- **StepSpec** — `step_id`, `title`, `slot_target` (one of the 8 slots),
  `field_schema[]`, `explanation { what_it_is, why_it_is_here, where_it_goes }`,
  `requiredness`, **`success_criteria`**, **`alternatives[]`** (for §4 branching).
- **FieldSchema** — `field_id`, `label`, `type` (string/int/bool/choice/path/list/
  range), `constraints` (regex/min/max/enums), `default`, `validation_rules`.
- **CommandPlan** (internal) — `program`, `slot_values` (structured), `render_mode`
  (bash preview string + optional array form).
- **CommandBuilder** — `build(validated_inputs) -> CommandPlan`.
- **LessonSpec** — `lesson_id`, `title`, `topic_tags`, `steps[]` (same adaptive
  step model), for the OS Learning Companion.

### 6.3 Why structured builders (not string concatenation)

Each argument is represented as `(flag, value, format_rule)`. Quoting is handled by a
robust shell-escaping function. The builder produces both a **bash preview string**
(slot-ordered, copyable) and an **array form** (`["nmap", "-sV", ...]`) for display.
This guarantees correct syntax and avoids any injection/escaping bugs — and since
nothing is executed, the array form is purely illustrative.

---

## 7. Help model — self-contained (no live assistant)

The free build has **no live assistant and no AI/model layer.** All help is **pre-authored**
and grounded in the curated knowledge base — there is no "ask anything" service answering
in the background.

- **Within a flow:** the adaptive stepper's branches provide the help (try → did it work?
  → cause/fix), authored at three depths (see §15B and `Troubleshooter-Subsystem.md`).
- **When flows are exhausted:** the tool generates an **Unresolved Issue Log** (steps tried
  + actual error output) and offers curated, trustworthy external links so the user can
  search themselves — see `Troubleshooter-Subsystem.md` §6B. The tool never fetches or
  answers; the user goes to those resources themselves.
- **Why self-contained:** the tool must run for everyone, offline, with no hardware or
  subscription barrier. **AI assistance is deferred to the future Enterprise edition**
  (see Editions, §1).

---

## 8. Accounts, onboarding & compliance (local-only)

### 8.1 Login / disclaimer gate

On first run / each open, a login screen blocks the wizard until completed:

- Fields: **username**, **password**, **disclaimer acknowledgment checkbox**.
- The wizard is inaccessible until the disclaimer is acknowledged.
- Rules live in `auth/login_policy.py` (UI-agnostic); both editions enforce them.

### 8.2 Onboarding guide

First-run checklist: how to set a base output directory, how to read the command
preview and slot views, and a clear reminder: *"reference guide only — does not run
commands."*

The **recommended first guided experience** after onboarding is the **First Setup &
Securing** module (Module 00) — an interactive starter guide that walks a new user
through setting up and securing a fresh Kali/Parrot system, exposing the core OS flows
(updates, accounts/privilege, firewall, services, privacy, backups). It pairs with the
**Shell Grammar** module (Module 01), which teaches the slot model itself.

### 8.3 On-device audit log

For compliance / reference, kept locally (suggested format: JSON Lines, with
size/date rotation):

- **Log:** timestamp; username (or local pseudonym); category/tool/flow or lesson
  selected; step-completion milestones; "command preview generated" events.
- **Never log:** passwords; optionally hash/truncate full target strings if considered
  sensitive.
- **Purpose:** a local accountability trail — if misuse is ever flagged, the log
  identifies activity. This is the project's chosen safety model (accountability over
  censorship).

---

## 9. Beginner glossary (shown inline on first use)

Short, true, precise definitions surfaced the first time each term appears in a step.

- **Program** — the executable you're running (e.g., `nmap`). Determines how the rest
  of the line is parsed.
- **Flag / option** — a switch that turns a feature on/off or sets a value
  (`-p 80`, `--threads=10`).
- **Global option** — a flag that affects the whole run (timing, DNS, verbosity),
  read early regardless of targets.
- **Argument (positional arg)** — a value that must appear in a specific position and
  is *not* preceded by a `-flag` (e.g., the target itself).
- **Target / pivot** — the thing the tool operates on (host, CIDR, URL, domain, file);
  the scope of the run.
- **Action option** — a flag controlling *what the tool does* to the targets (scan
  type, version detection, scripts).
- **Output option** — a flag setting output format and destination (`-oX file`).
- **Placeholder** — a symbol in an example (`{targets}`, `{ports}`) standing in for a
  value you provide; each maps to a wizard field.
- **Slot** — one of the 8 ordered positions a command is built from (§3.1).

---

## 10. Categories & tool mapping

Categories are just **filters** over the registry (your headers): Wireless Tools,
Reconnaissance, Resource Development, Forensics, Protect, Detect, Recover, Respond,
etc. Each tool carries category tags; a category tab shows the tools/flows tagged for
it. Optionally show only installed tools (via `binary_candidates` detection), with a
grayed "install hint" for empty categories.

---

## 11. Extension mechanism — growing to "all tools" + all OS topics

**Add a tool:** add a `ToolSpec` to the registry → add each `FlowSpec` (steps,
field schemas, explanations, success criteria, alternatives) → implement/register a
command builder per flow → optionally add install-detection and output-manifest
templates.

**Add an OS lesson:** add a `LessonSpec` under `registry/lessons/` using the same
adaptive step model.

**Adjust explanations:** they live in the specs (`StepSpec.explanation`); the UI
renders them generically — no UI changes needed.

This is why the slot model + spec-driven design matter: the UI is written once;
coverage is pure data growth.

### 11.4 Module system & release / packaging *(incremental growth model)*

The product ships as a **small releasable base** plus **modules** added over time as
updates or optional add-ons. This is the practical mechanism behind "start small, grow."

- **Base app** = the engine (`wizard-core`) + UI shell (desktop executable / Termux TUI)
  + login/audit/onboarding + a stable `wizard-core` API. Ships small and is useful on
  its own with one or two core modules.
- **A module** = a **versioned bundle** the base discovers and loads at runtime. Types:
  - **Lesson module** — one or more `LessonSpec`s (OS fundamentals, Kali/Parrot quirks).
  - **Tool module** — `ToolSpec` + `FlowSpec`s + command builder(s) + explanations.
  - **Troubleshooter module** — symptom-first flows for the self-help troubleshooter.
  - **Knowledge/data module** — an ingested KB slice (e.g., a tldr-pages snapshot).
  - **Theme module** — the design system / visual identity (see §14).
- **Module manifest** (every module carries one):
  - `module_id`, `name`, `version` (semver), `type`
  - `requires`: minimum base/`wizard-core` API version + any other modules it depends on
  - `provides`: which specs/builders/lessons it registers
  - `content`: paths to the registry/spec/builder files it adds
  - `source`, `license`, `provenance`, `checksum` (for trust + license auditing)
- **Loading:** the base scans a modules directory, validates each manifest against its
  API version, and registers the contents into the registry — **no UI changes needed**.
- **Releases:** v1 = base + Module 01. Each later feature ships as a new module (update
  or add-on) without touching the base. Both editions consume the identical module
  format.
- **Compatibility rule:** the base exposes a stable `wizard-core` API version; modules
  declare the API they target, so old modules keep working across base updates.

---

## 12. Suggested build sequencing (for the build service)

Although the product is one unified system, a sane build order:

1. **`wizard-core` foundation** — slot definitions, schema/validation, builder
   pattern, explanation renderer, glossary, curated KB access.
2. **First fully-specified flow end-to-end** — e.g., `nmap` basic scan (targets +
   ports profile + XML/normal output) to prove the slot model + adaptive stepper.
3. **Desktop edition (executable)** — login gate, tabbed tool selection, adaptive
   wizard pages, command-preview pane; package with PyInstaller.
4. **Audit logging + onboarding.**
5. **Termux edition** — same core, TUI front-end, curated-only mode.
6. **OS Learning Companion lessons** (Kali/Parrot quirks).
7. **Troubleshooter subsystem** — symptom-first flows + Unresolved Issue Log + trusted
   links (§15B, `Troubleshooter-Subsystem.md`). Curated content only.
8. **Scale coverage** — add tools/flows/lessons/troubleshooter modules as data.
9. *(Future — Enterprise edition only)* **AI layer** — local LLM / paid portal assist,
   grounded in the curated KB. Not part of the free build.

---

## 13. Open questions / decisions still to make

These were not resolved in brainstorming and should be settled before/while building:

1. **GUI stack:** PySide6 (recommended) vs PyQt6 — licensing/styling preference?
2. **First flow to fully spec:** the transcript started on `gvm-start`; that needs the
   user's actual install layout (`which gvm-start`, `gvm-start --help`, install
   source) before its steps can be made accurate. A simpler first flow (nmap) may be a
   better proof-of-concept.
3. **Model choice for the hybrid layer:** which small local model, and minimum device
   specs for the desktop edition? (Termux stays curated-only.)
4. **Authoring pipeline & accuracy review:** who/what verifies each command structure
   against an authoritative source before it ships?
5. **Knowledge-base license/sourcing:** confirm reuse terms for any wiki/doc content
   seeded into the curated library.
6. **Audit-log sensitivity policy:** store, hash, or truncate target strings?

---

---

## 14. Design system (visual identity)

The visual identity is the **W1CK3D SYSTEMS brand** — *the group/organization, not the
project name* — applied as the theme for the Tool Wizard project. A dark cyber/military
"terminal" aesthetic from the user's exported design. **Full tokens live in
`Design-System-Tokens.md`** (the canonical reference); summary below.

- **Aesthetic:** layered near-black surfaces (`#030405`→`#11151b`), **purple** primary
  accent (`#561593`, neon glow `#9a3eff`), metallic gold/silver edge framing, stencil +
  monospace type.
- **Type:** display "Black Ops One"/"Orbitron"; headings "Orbitron"; body "Chakra Petch";
  **mono "JetBrains Mono"/"Share Tech Mono" for ALL command/slot/terminal views** (all
  Google Fonts).
- **Status palette doubles as category coding:** recon=purple, secure=green,
  warning=orange, critical=red, info=blue — these tint the **category tabs** *and* the
  **stepper / "did it work?" states** (green = Yes/success, red/orange = No/alternative).
- **Captured as a theme module** (`theme.w1ck3d_systems`, per §11.4): the raw `:root` CSS
  variable block from the export is the source of truth, versioned independently of logic.
- **Component mapping** (login, tabs, stepper, slot cards, command-preview pane, Yes/No
  gate, validation) is specified in `Design-System-Tokens.md` §5.

> **Still needed:** the **logo/wordmark image** (the stencil mark wasn't in the export),
> font-licensing confirmation, and any **layout mockups** so component placement matches
> the intended design. See `Design-System-Tokens.md` §7.

---

## 15. OS profiles & distro separation *(retained for future expansion)*

**Current build targets Kali only.** This section is retained because the OS-profile
model is the exact mechanism that lets Parrot (or any distro) be added **later** as its
own module without reworking the Kali product — and because it documents *why* distros
must never be merged.

Distros **diverge in ways that make a merged guide dangerous** — the same task can have
a different correct process on each, and applying the wrong one can break a system or
fail silently. Therefore content is **separated by distro** (each its own module
edition), not merged with inline "if Kali / if Parrot" asides.

**Parrot status: PARKED.** Its sandboxing (firejail) + mandatory-access-control means
some paths stay locked even to root, and elevated processes can write reports into paths
the normal user then can't read — behavior that needs dedicated testing before it can be
taught safely. Parked field notes live in `Module-00-Parrot-Setup-and-Securing.md`.

### 15.1 The OS-profile model

- Every `LessonSpec` / `FlowSpec` / `StepSpec` declares an **`os_profile`**:
  `kali`, `parrot`, or `agnostic` (truly identical on both, e.g., pure shell grammar).
- On first run the app **detects the distro** (`/etc/os-release`) and, if ambiguous,
  **asks once**. It then **only ever shows content matching that profile.**
- Where a task differs between distros, the two versions are authored as **separate
  step sets / separate module editions** — never as one step with branching notes that
  could be read out of context.
- `agnostic` content (e.g., what a flag is) is shared; **divergent processes are split.**

### 15.2 Confirmed Kali vs Parrot divergences (must stay separated)

| Area | Kali | Parrot |
|------|------|--------|
| **Update/upgrade** | `sudo apt update && sudo apt full-upgrade`; rolling (Debian testing); keyring fix via `kali-archive-keyring` | **`sudo parrot-upgrade`** (curated wrapper); repos managed by Parrot via `/etc/apt/sources.list.d/parrot.list`; **do not add/modify repos** |
| **Privilege / elevated commands** | default user `kali` in `sudo` group; non-root by default | uses sudo with a normal user; Parrot's elevated-command conventions differ — **follow Parrot docs; specifics to confirm per install** |
| **Filesystem / root access** | standard Debian behavior | **firejail sandboxing + AppArmor profiles by default** affect how processes access the filesystem/root areas |
| **Privacy stack** | add-ons (install as needed) | **AnonSurf + firejail preinstalled** |
| **Base/release model** | rolling, bleeding-edge | more curated/stable, vendor-checked mirrors |

### 15.3 Implication for modules

OS-specific modules ship as **per-distro editions** (e.g., Module 00 splits into a Kali
edition and a Parrot edition) behind a **distro router** that picks the right one. The
module manifest's `os_targets` already supports this; the router enforces it at runtime.

---

## 15B. Troubleshooter subsystem (the largest part)

The interactive **symptom-first assisted troubleshooter** — a **self-contained, self-paced
self-help tool** (no live assistant) that helps the user navigate Kali itself — is specified
in full in **`Troubleshooter-Subsystem.md`**. Summary:

- **Assisted template:** symptom entry → triage questions → guided diagnosis (the §4
  stepper runs one diagnostic at a time, user reports results) → verified fix → if
  exhausted, generate an **Unresolved Issue Log** + offer curated trusted links for
  self-directed search (no service/assistant).
- **Three depth tiers:** Basic (quick fixes) → Intermediate (multi-step diagnosis) →
  Extensive (deep decision trees, logs, rare faults). Simple to start, complete to finish.
- **Coverage:** networking/DNS/Wi-Fi, apt/packages, services/systemd, permissions/sudo/
  filesystem, **integral Kali functions** (git-repo installs, GPG repo-trust keys, TLS
  certificates & CA/authority handling), plus a rare/hard-case tier.
- **Engine reuse:** a troubleshooter flow is just a `StepSpec` stepper with a symptom +
  triage front-end and a fixes list — no new UI. Each area ships as its own module.

## 16. Open items added from distro review

- **Confirm Parrot's exact privilege/elevated-command behavior** per current edition
  (sudo config, any root-password defaults) before finalizing the Parrot setup module.
- **Confirm Parrot's filesystem/root-access specifics** (firejail/AppArmor effects on
  common tasks) so step guidance is precise.
- **Decide distro-detection UX:** auto-detect silently, or always confirm with the user.

---

*End of blueprint v1.2. This is a living document — update it as decisions in §13/§16 are
resolved and as flows/lessons/modules are specified.*
