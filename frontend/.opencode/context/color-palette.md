# Vector Vault — Color Palette

*Generated from brandkit run. Source of truth for all color decisions.*

---

## Design Philosophy

"The Scholar's Study" — warm, contemplative, intimate. Colors evoke a private library, annotated books, warm lamplight. The palette is grounded in warm neutrals with a single amber/gold accent. No cool blues, no tech gradients, no corporate grays.

---

## Light Mode Palette

| Token | Hex | Description | Usage |
|-------|-----|-------------|-------|
| `--color-bg-primary` | `#faf8f5` | Warm parchment off-white | Page background, main canvas |
| `--color-bg-secondary` | `#faf9f5` | Ivory surface | Cards, panels, elevated surfaces |
| `--color-bg-tertiary` | `#e8e6dc` | Warm sand | Hover states, separators, user message bubbles |
| `--color-text-primary` | `#1B2A3A` | Deep navy | Primary headings, body text |
| `--color-text-secondary` | `#5e5d59` | Olive gray | Muted text, captions, metadata |
| `--color-text-tertiary` | `#8b8980` | Muted warm gray | Placeholder text, disabled states |

## Accent Colors

| Token | Hex | Description | Usage |
|-------|-----|-------------|-------|
| `--color-accent` | `#c4952e` | Warm amber | Primary accent, logo mark, emphasis |
| `--color-accent-bright` | `#d4a43e` | Brighter amber | Hover states, active elements, dark mode accent |
| `--color-accent-bg` | `rgba(196,149,46,0.12)` | Amber tint | Chips, badges, subtle highlights |

## Dark Mode Palette

| Token | Hex | Description | Usage |
|-------|-----|-------------|-------|
| `--color-dark-bg` | `#1a1c22` | Warm charcoal | Dark mode background |
| `--color-dark-surface` | `#262420` | Warm dark surface | Dark mode cards, panels |
| `--color-dark-text` | `#f0ece4` | Warm off-white | Dark mode primary text |
| `--color-dark-muted` | `#8b8980` | Muted gray | Dark mode secondary text |

## Semantic Colors

| Token | Hex | Description |
|-------|-----|-------------|
| `--color-success` | `#6cb56c` | Success / positive actions |
| `--color-warning` | `#d4a43e` | Warnings (same as accent-bright) |
| `--color-error` | `#e06c6c` | Errors / destructive actions |
| `--color-info` | `#1B2A3A` | Informational (same as text-primary) |

## Usage Rules

1. **Amber accent must be used sparingly.** Maximum 2–3 visible accent uses per screen. Overusing gold cheapens its effect.

2. **Never use cool grays.** All grays are warm-toned (`#5e5d59`, `#8b8980`). Never `#666`, `#888`, or `#999`.

3. **No indigo.** `#6366f1` and similar AI-tool indigos are banned. This is a scholarly product, not a generic SaaS.

4. **No purple-blue gradients.** No trust gradients, no tech gradients. The palette is warm, grounded, and analog.

5. **Dark mode is warm charcoal**, not cool dark (#1a1c22 has a subtle warm undertone vs pure #1a1a1a).

6. **Paper texture.** The parchment background (#faf8f5) is intentionally slightly warm/creamy, not pure white (#ffffff).

7. **Contrast check.** Navy on parchment (#1B2A3A on #faf8f5) passes WCAG AAA for normal text. Amber on charcoal (#d4a43e on #1a1c22) passes WCAG AA for large text.
