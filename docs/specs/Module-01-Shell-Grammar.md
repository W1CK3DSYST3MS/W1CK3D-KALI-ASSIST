# Module 01 — Shell Grammar (Fundamentals Lesson)

**Type:** Lesson module · **Status:** Starter module spec (v1) · **For:** base app v1
**Companion to:** Tool Wizard Blueprint v1.1 + Coverage Map v1.0
**Last updated:** 2026-06-21

> This is the **first releasable module** and the worked template for all future
> lessons. It teaches the shell command grammar — which *is* the slot model the whole
> product is built on — and along the way defines every glossary term the user flagged
> as a gap (program, flag, option, argument, global option, placeholder, slot).
>
> It is written two ways at once:
> 1. As a **spec** a build service can implement directly (manifest + LessonSpec + steps).
> 2. As **real lesson content** (the actual text shown to the learner), so it doubles as
>    a content sample and is testable by Hunter immediately in a terminal.
>
> **Reminder:** the app never executes anything. Each step shows a command for the
> learner to type **in their own terminal**, then asks "did it work?" — the adaptive
> stepper branches on the answer.

---

## 1. Module manifest

```yaml
module_id: fundamentals.shell_grammar
name: "Shell Grammar — How a Linux command is built"
version: 1.0.0
type: lesson
requires:
  base_api: ">=1.0"
  modules: []                      # no dependencies — this is the foundation
provides:
  lessons: [lesson.shell_grammar]
  glossary_terms: [program, flag, option, argument, global_option, placeholder, slot, pipe, redirection]
content:
  lesson: registry/lessons/shell_grammar.yaml
  glossary: explain/glossary/shell_grammar.yaml
source: "authored (original) + examples seeded from tldr-pages (CC-BY 4.0)"
license: "project-proprietary lesson text; example commands CC-BY 4.0 attributed"
provenance: "Module 01, starter"
checksum: "<filled at build>"
```

---

## 2. LessonSpec (overview)

```yaml
lesson_id: lesson.shell_grammar
title: "Shell Grammar — How a Linux command is built"
topic_tags: [fundamentals, shell, cli, slots]
audience: beginner
prerequisites: none
goal: >
  Understand that every command follows the same ordered structure (the SLOTS),
  and be able to identify the program, options/flags, arguments, and output parts
  of any command — so you stop guessing at order and syntax.
intro: >
  Every Linux command — from `ls` to `nmap` — is built from the same ordered pieces.
  Learn those pieces once and you can read and build any command. We call those pieces
  SLOTS. This lesson walks them one at a time. Type each command in your own terminal,
  then tell the wizard whether it worked.
steps: [s1, s2, s3, s4, s5, s6, s7]
completion_criteria: "learner reaches s7 and can map a command into slots"
```

The lesson uses a simplified, beginner-facing subset of the 8 slots from the blueprint:

| Teaching slot | Blueprint slot | Plain meaning |
|---------------|----------------|---------------|
| **Program** | PROGRAM | the command name you run |
| **Options/Flags** | GLOBAL_OPTIONS + ACTION_OPTIONS | switches that change behavior |
| **Target/Argument** | TARGET_PIVOT + POSITIONAL_ARGS | the thing the command acts on |
| **Output** | OUTPUT_OPTIONS | where results go (intro only) |

---

## 3. Step model used here (recap of the adaptive stepper)

Each `StepSpec` carries:

- `concept` — short, true, precise: *what* this piece is and *why* it exists.
- `slot_mapping` — which slot this step is teaching.
- `try_this` — the exact command the learner types in their own terminal.
- `expected` / `success_criteria` — what they should see if it worked.
- `did_it_work` gate — **Yes →** next step; **No →** show `alternatives`.
- `alternatives[]` — for the "No" path: likely cause + what to check + a fix to retry.
- `glossary_refs` — terms surfaced inline on first use.

---

## 4. Steps (full content)

### Step s1 — The Program (the command itself)

- **slot_mapping:** Program
- **glossary_refs:** program
- **concept:** "The first word on the line is the **program** — the tool you're running.
  It decides how everything after it is read. Right now, that's all we type."
- **try_this:** `whoami`
- **expected:** "It prints your username (e.g., `kali`)."
- **success_criteria:** a single line of output appears.
- **did_it_work?**
  - **Yes →** s2
  - **No → alternatives:**
    - *`command not found`* → "Check spelling. The program name must be exact and
      lowercase. Retry `whoami`."
    - *nothing happens / cursor hangs* → "Press Enter; if still stuck, press `Ctrl+C`
      to cancel and retype."

---

### Step s2 — Arguments (the thing the command acts on)

- **slot_mapping:** Target/Argument
- **glossary_refs:** argument, target
- **concept:** "An **argument** is a value you give the program to act on — often the
  *target*. It is **not** preceded by a dash. Here, `/etc` is the argument telling `ls`
  *which folder* to list."
- **try_this:** `ls /etc`
- **expected:** "A list of files/folders inside `/etc`."
- **success_criteria:** multiple names print (e.g., `passwd`, `hostname`).
- **did_it_work?**
  - **Yes →** s3
  - **No → alternatives:**
    - *`No such file or directory`* → "The argument is a path that must exist. Try
      `ls /` first to confirm, then `ls /etc`."
    - *`Permission denied`* → "You can list `/etc`; if denied, you likely typed a
      different path. Re-check the argument."

---

### Step s3 — Flags / options (switches that change behavior)

- **slot_mapping:** Options/Flags
- **glossary_refs:** flag, option
- **concept:** "A **flag** (or **option**) is a switch starting with a dash that changes
  *how* the program behaves. `-l` means 'long format'. The program is the same; the flag
  changes the output."
- **try_this:** `ls -l /etc`
- **expected:** "The same list, now one item per line with permissions, owner, size,
  date."
- **success_criteria:** output shows permission strings like `-rw-r--r--`.
- **did_it_work?**
  - **Yes →** s4
  - **No → alternatives:**
    - *output looks unchanged* → "Make sure it's a lowercase L (`-l`), not a one (`1`).
      Retry `ls -l /etc`."
    - *`invalid option`* → "Flags are case-sensitive and tool-specific. Confirm the
      flag with `ls --help`."

---

### Step s4 — Combining flags + short vs long form

- **slot_mapping:** Options/Flags
- **glossary_refs:** flag, option
- **concept:** "Flags can be combined (`-la` = `-l` + `-a`), and many have a long form
  (`-a` = `--all`). `-a` shows hidden files (names starting with `.`). Short forms are
  for speed; long forms are for readability."
- **try_this:** `ls -la /etc`   *(then optionally: `ls --all -l /etc`)*
- **expected:** "Same long list, now including hidden entries like `.` and `..`."
- **success_criteria:** entries beginning with `.` appear.
- **did_it_work?**
  - **Yes →** s5
  - **No → alternatives:**
    - *no hidden files show* → "Confirm you included `a`. Hidden files start with a dot;
      `/etc` should show at least `.` and `..`."

---

### Step s5 — Options that take a value

- **slot_mapping:** Options/Flags (with value)
- **glossary_refs:** option, argument, placeholder
- **concept:** "Some options take a **value** right after them. In `head -n 5 file`,
  `-n` is the option and `5` is its value (how many lines). In examples we write the
  value as a **placeholder** like `{n}` — a stand-in for what *you* choose."
- **try_this:** `head -n 5 /etc/passwd`
- **expected:** "Exactly the first 5 lines of the file print."
- **success_criteria:** 5 lines output.
- **did_it_work?**
  - **Yes →** s6
  - **No → alternatives:**
    - *`option requires an argument`* → "`-n` needs a number right after it. Retry
      `head -n 5 /etc/passwd`."
    - *too many/few lines* → "The value after `-n` controls the count — change `5` to
      test."

---

### Step s6 — Putting it together: reading a command as SLOTS

- **slot_mapping:** all (synthesis)
- **glossary_refs:** slot, global_option, output
- **concept:** "Every command is the same ordered slots. Read this one by slot:
  `ls -la /etc` → **Program** `ls` · **Options/Flags** `-la` · **Target/Argument**
  `/etc`. That order never changes in your head again — the wizard always assembles it
  for you."
- **try_this:** "(No new command.) Look at `ls -la /etc` and name each slot out loud."
- **expected:** "You can point to the program, the flags, and the target."
- **success_criteria:** learner self-confirms they can label each part.
- **did_it_work?**
  - **Yes →** s7
  - **No → alternatives:**
    - "Re-show the 3 synchronized views (Skeleton / Filled / Why) for `ls -la /etc` and
      walk each slot again."

---

### Step s7 — The most important skill: getting help

- **slot_mapping:** meta-skill
- **glossary_refs:** program, flag, option
- **concept:** "You never need to memorize every flag. Three commands reveal them:
  `man <program>` (full manual), `<program> --help` (quick list), and `tldr <program>`
  (plain examples). Learning to read these is the skill that makes every other tool
  learnable."
- **try_this:** `ls --help`   *(then try `man ls`; press `q` to quit the manual)*
- **expected:** "A list of `ls` options with one-line descriptions."
- **success_criteria:** the options list prints.
- **did_it_work?**
  - **Yes →** lesson complete.
  - **No → alternatives:**
    - *`man` opens a full-screen pager and you're stuck* → "Press `q` to quit."
    - *`tldr: command not found`* → "`tldr` may not be installed; that's fine — use
      `ls --help` or `man ls` instead. (Installing `tldr` can be a later lesson.)"

---

## 5. Inline glossary (shipped with this module)

Surfaced the first time each term appears (blueprint §9 wording, lesson-scoped):

- **Program** — the command you run; the first word; decides how the rest is read.
- **Flag / option** — a dash-prefixed switch that changes behavior (`-l`, `--all`).
- **Argument** — a value the command acts on, *not* dash-prefixed (often the target).
- **Global option** — a flag affecting the whole run; read early regardless of target.
- **Placeholder** — a stand-in in examples (`{n}`, `{targets}`) for a value you provide.
- **Slot** — one ordered position a command is built from (Program → Options → Target →
  Output).
- **Pipe / redirection** — sending one command's output into another (`|`) or into a
  file (`>`); previewed here, taught fully in a later module.

---

## 6. Completion → what unlocks next

On completion, the app suggests the next modules that build on this one:

- **Module 02 — Files, paths & permissions** (uses the argument/target idea).
- **Module 03 — Pipes & redirection** (the `|` and `>` previewed in s7's glossary).
- **First tool module — nmap basic scan** (now the learner can read its slots).

This is the module-driven growth path from the blueprint (§11.4) in action.

---

## 7. Why this is a good first release

- **Self-contained:** no dependencies, no risk; safe to ship as v1 with the base.
- **Tests the entire engine:** lesson loading, slot rendering, the 3 synchronized views,
  the adaptive Yes/No stepper with real branch content, and inline glossary — all on one
  small slice.
- **Directly fixes the stated gap:** by the end the learner can define and *point to*
  every term (program/flag/option/argument/global/placeholder/slot) that caused the
  "hours chasing my tail" problem.
- **Template for everything after:** every later lesson and tool flow is authored to
  this exact shape.

*End of Module 01 spec v1.*
