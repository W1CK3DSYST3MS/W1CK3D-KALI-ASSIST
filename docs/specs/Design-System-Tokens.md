# W1CK3D SYSTEMS — Brand Design System & Tokens

**Brand/Group:** **W1CK3D SYSTEMS** (the organization) · **Applied to project:**
**W1CK3D'S KALI ASSIST** · **Type:** Theme module reference
**Source:** extracted from the user's exported design (`W1CK3D Tool Wizard.html`)
**Companion to:** Blueprint §14 (Design system) · **Last updated:** 2026-06-21

> Note: **W1CK3D SYSTEMS is the group/brand name, not the project name.** This is the
> group's brand identity, applied as the theme for the Tool Wizard project.

> The canonical visual identity. The build service implements the UI against **these
> tokens** so layout/components stay consistent and don't conflict as modules are added.
> Aesthetic: **dark cyber/military "terminal"** — layered near-black surfaces, purple
> neon accent, metallic gold/silver edges, stencil + monospace type.

---

## 1. Color tokens

### 1.1 Backgrounds (darkest → lightest)
| Token | Hex | Use |
|-------|-----|-----|
| `--bg-void` | `#030405` | deepest base / app backdrop |
| `--bg-base` | `#06080b` | primary background |
| `--bg-inset` | `#07090c` | sunken areas (e.g. command/terminal pane) |
| `--bg-surface` | `#0b0e13` | cards / panels |
| `--bg-raised` | `#11151b` | elevated cards, popovers |
| `--bg-hover` | `#181d25` | hover state for surfaces |

Gradients: `--grad-void` (radial top glow into void), `--grad-purple-haze` (purple corner haze).

### 1.2 Text
| Token | Alias | Hex | Use |
|-------|-------|-----|-----|
| `--text-strong` | `--text-1` | `#eef1f5` | headings / primary |
| `--text-body` | `--text-2` | `#c2c8d2` | body copy |
| `--text-muted` | `--text-3` | `#8b93a1` | secondary / labels |
| `--text-faint` | `--text-4` | `#5a626f` | disabled / hints |
| `--text-invert` | — | `#06080b` | text on light/accent fills |

### 1.3 Accent (primary = purple)
| Token | Hex | Use |
|-------|-----|-----|
| `--purple` / `--accent` | `#561593` | primary accent, active step, focus border |
| `--purple-glow` / `--accent-hover` | `#9a3eff` | hover, neon glow |
| `--purple-deep` / `--accent-press` | `#320a63` | pressed/active deep |

### 1.4 Status / category palette (drives tabs AND stepper states)
| Semantic token | Color | Hex | Maps to category | Maps to stepper |
|----------------|-------|-----|------------------|-----------------|
| `--status-recon` | purple | `#561593` | Reconnaissance | active/primary |
| `--status-secure` | green | `#0f9446` | Protect/Detect | **"did it work? YES"** |
| `--status-warning` | orange | `#ee5a04` | (caution flows) | **alternative / retry** |
| `--status-critical` | red | `#e51f1f` | Exploitation/destructive | **"did it work? NO" / error** |
| `--status-info` | blue | `#147ec2` | Forensics/info | neutral info |

Each status has `-deep` and `-glow` variants + a matching `--glow-*` (neon box-shadow) and
`--text-glow-*` (text shadow): e.g. `--green-glow #3df085`, `--red-deep #7e1212`,
`--blue-glow #4fbdf5`, `--orange-glow #ff8a3d`.

### 1.5 Metallic edges (premium framing)
- Gold: `--gold #c5a45a` (hi `#f0dca0`, lo `#6e5824`) → `--emboss-gold`, `--edge-gold`.
- Silver: `--silver #c2c7cf` (hi `#f4f6f9`, lo `#6a7079`) → `--emboss-silver`, `--edge-silver`.
- Use sparingly for hero framing (login wordmark, key CTAs, badges).

### 1.6 Lines / borders
| Token | Hex | Use |
|-------|-----|-----|
| `--line-faint` | `#1b1f26` | subtle dividers |
| `--line` | `#262c35` | default card border |
| `--line-strong` | `#353c47` | emphasized border |
| `--border-focus` | `var(--purple)` | focus ring |

---

## 2. Typography

| Role | Token | Stack |
|------|-------|-------|
| Display (wordmark/hero) | `--font-display` | "Black Ops One", "Orbitron", Impact |
| Heading | `--font-heading` | "Orbitron", "Oxanium", "Chakra Petch" |
| Body | `--font-body` | "Chakra Petch", "Oxanium", sans-serif |
| **Mono (commands/slots)** | `--font-mono` | "JetBrains Mono", "Share Tech Mono" |
| Terminal (preview pane) | `--font-term` | "Share Tech Mono", "JetBrains Mono" |

All are Google Fonts (free). The logo wordmark is a heavy military stencil (per the
design's webfont note). **All command/slot/preview text uses the mono/term fonts** — this
is essential for the teaching views.

**Type scale:** `--fs-2xs 11` · `--fs-xs 12` · `--fs-sm 13` · `--fs-base 15` · `--fs-md 17`
· `--fs-lg 20` · `--fs-xl 25` · `--fs-2xl 32` · `--fs-3xl 42` · `--fs-4xl 56` · `--fs-5xl 76` (px).

**Weights:** regular 400 · medium 500 · semibold 600 · bold 700 · black 800.

**Line height:** tight 1.05 · snug 1.25 · normal 1.5 · loose 1.7.

**Letter spacing:** tight −0.01em · normal 0 · wide 0.04em · wider 0.12em · widest 0.28em
(use wide/widest for stencil headings and labels — the techno look).

---

## 3. Spacing, radius, sizing

**Spacing (4px base):** `--sp-1 4` · `2 8` · `3 12` · `4 16` · `5 20` · `6 24` · `8 32`
· `10 40` · `12 48` · `16 64` · `20 80` · `24 96` (px). Default gutter = `--sp-6` (24px).

**Radius:** `--r-xs 2` · `sm 3` · `md 5` · `lg 8` · `xl 12` · `pill 999` · `none 0` (px) —
generally low radius (sharp, technical feel).

**Control heights:** `--ctl-sm 30` · `--ctl-md 38` · `--ctl-lg 46` (px). Container max
`--container 1200px`.

---

## 4. Elevation & motion

**Shadows:** `--shadow-sm/md/lg` (deep blacks) + `--shadow-inset`. **Neon glows:**
`--glow-purple/green/red/orange/blue` for active/status emphasis.

**Motion:** durations `--dur-fast 110ms` · `--dur-mid 200ms` · `--dur-slow 360ms`;
eases `--ease-out` `cubic-bezier(.2,.7,.3,1)`, `--ease-in-out` `cubic-bezier(.6,0,.3,1)`.

---

## 5. Token → UI component mapping (the important part)

How the identity applies to the product's recurring components (blueprint §3/§4):

- **Login / disclaimer screen:** `--grad-void` backdrop; wordmark in `--font-display`
  with gold/silver edge; disclaimer body in `--font-body` `--text-body`; primary CTA in
  `--accent` with `--glow-purple` on focus.
- **Category tabs:** each tab tinted by its `--status-*` color (recon=purple, secure=green,
  etc.) — visual category coding is built in.
- **Wizard stepper:** active step uses `--accent` + `--glow-purple`; completed steps
  `--status-secure` (green); step titles in `--font-heading` with `--ls-wide`.
- **Slot cards (the 3 views):** `--bg-surface` card, `--line` border, `--border-focus` on
  active; slot labels `--font-heading`/`--text-muted`; **command text `--font-mono`**;
  the "why this goes here" note in `--text-body`.
- **Command preview / terminal pane:** `--bg-inset` or `--bg-void`; `--font-term`; a
  valid/complete command gets `--text-glow-green`; placeholders in `--text-faint`.
- **Adaptive "did it work?" gate:** **YES** button = `--status-secure` (green) +
  `--glow-green`; **NO** button = `--status-critical` (red) / `--status-warning`
  (orange) for the "show alternative" path.
- **Validation messages:** errors `--status-critical`; warnings `--status-warning`;
  success `--status-secure`.
- **Helpdesk / info callouts:** `--status-info` (blue).

---

## 6. Packaging as a theme module

Per blueprint §11.4, ship this as the base **theme module** (`theme.w1ck3d_systems`):

```yaml
module_id: theme.w1ck3d_systems
name: "W1CK3D SYST3MS theme"
version: 1.0.0
type: theme
provides: { theme: w1ck3d_systems }
content:
  tokens: theme/w1ck3d/tokens.css        # the :root CSS variables (source of truth)
  fonts:  theme/w1ck3d/fonts.css         # Google Fonts imports / bundled webfonts
assets:
  logo: theme/w1ck3d/logo.*              # ⬅ still needed (see §7)
license: "fonts: Google Fonts (OFL/Apache); design: project-owned"
```

The raw `:root` CSS variable block from the export is the **source of truth** — extract it
verbatim into `tokens.css` so values never drift from your design.

---

## 7. Still needed to complete the theme

- **Logo / wordmark as a FILE:** the W1CK3D SYSTEMS logo (bronze shield + raven on skull
  + stencil wordmark) has been *seen* but only as an in-chat image — no asset file came
  through the export. To bundle it, upload the actual **SVG (preferred) or PNG** file.
- **"Page tags" / page settings did NOT export cleanly:** the HTML is a compiled/minified
  bundle, so any page-level tags/settings configured in the design tool are not present as
  readable, integrable data. Only the CSS design tokens and the page `<title>`
  ("W1CK3D — Tool Wizard") came through usefully. If specific page tags matter, re-state
  them here in text and they'll be captured directly.
- **Confirm font licensing/bundling:** all stacks are Google Fonts substitutes — fine to
  bundle (OFL/Apache), but confirm you want the substitutes vs. any custom logo font.
- **Any screens/mockups** showing intended layout (so component placement matches your
  vision, not just the tokens).
- **Confirm the project name** (under the W1CK3D SYSTEMS group).

*End of W1CK3D SYST3MS tokens v1.*
