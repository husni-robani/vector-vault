# Vector Vault — Typography

*Generated from brandkit run. Source of truth for all typographic decisions.*

---

## Design Philosophy

Two-typeface system pairing a literary serif (warmth, scholarship, trust) with a clean humanist sans-serif (readability, UI clarity). The serif conveys the "scholar's study" aesthetic — annotated books, private libraries, contemplative reading. The sans-serif keeps the interface clean and functional.

---

## Font Stack

| Role | Font Family | Fallback | Usage |
|------|------------|----------|-------|
| **Display** | `EB Garamond` | `Georgia`, serif | Headings, wordmark, brand moments, large type |
| **Body** | `Inter` | `system-ui`, `-apple-system`, sans-serif | UI text, messages, labels, body copy |
| **Mono** | `JetBrains Mono` | `Fira Code`, monospace | Code blocks, technical details (future) |

### Google Fonts Import

```html
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### CSS Custom Properties

```css
--font-display: 'EB Garamond', 'Georgia', serif;
--font-body: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

---

## Type Scale

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `--font-size-xs` | 9px (0.5625rem) | — | 400 | Micro-labels, panel labels, uppercase badges |
| `--font-size-sm` | 10px (0.625rem) | — | 400 | Small labels, construction notes |
| `--font-size-base` | 12px (0.75rem) | 1.55 | 400 | Body copy, UI text, message content |
| `--font-size-md` | 14px (0.875rem) | 1.5 | 400 | Enhanced body, list items |
| `--font-size-lg` | 18px (1.125rem) | 1 | 500 | Small wordmark (`wordmark-sm`) |
| `--font-size-xl` | 24px (1.5rem) | 1.1 | 500 | Type specimen heading |
| `--font-size-2xl` | 26px (1.625rem) | 1.25 | 400 | Brand essence text |
| `--font-size-3xl` | 28px (1.75rem) | 1 | 500 | Medium wordmark (`wordmark-md`) |
| `--font-size-4xl` | 42px (2.625rem) | 1 | 500 | Large wordmark (`wordmark-lg`) |

---

## Font Weights

| Token | Value | Usage |
|-------|-------|-------|
| `--font-weight-normal` | 400 | Body text, most UI labels |
| `--font-weight-medium` | 500 | Headings, wordmark, emphasis |
| `--font-weight-semibold` | 600 | Strong emphasis (rarely used) |

---

## Letter Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--letter-spacing-tight` | `-0.01em` | Wordmark, brand moments (EB Garamond) |
| `--letter-spacing-normal` | `0` | Body text (Inter) |
| `--letter-spacing-wide` | `0.02em` | Tagline, subtle emphasis |
| `--letter-spacing-wider` | `0.06em` | Color labels, metadata |
| `--letter-spacing-widest` | `0.08em` | Uppercase micro-labels, panel labels |

---

## Line Heights

| Token | Value | Usage |
|-------|-------|-------|
| `--line-height-tight` | 1.1 | Type specimens, display text |
| `--line-height-snug` | 1.25 | Brand essence, pull quotes |
| `--line-height-normal` | 1.5 | Most UI text, messages |
| `--line-height-relaxed` | 1.55 | Body text, long-form reading |

---

## Typographic Rules

1. **EB Garamond is for brand moments only.** Use sparingly for headings, the wordmark, and the occasional pull quote. Never use it for body text or UI labels.

2. **Inter is the workhorse.** All UI text, messages, buttons, inputs, labels, and body content use Inter.

3. **No faux italic.** EB Garamond has true italics. Use the italic style variant, not `font-style: italic` on the regular weight.

4. **Uppercase sparingly.** Only for micro-labels (panel labels, section headers) at 9-10px with `letter-spacing: 0.08em`.

5. **The wordmark is sacred.** "Vector Vault" in EB Garamond 500 should be handled with care — generous spacing, never compressed, always at display sizes (28px+).

6. **Type pairing test phrase:** Display: "Vector Vault" in EB Garamond 500 + Body: "Your personal knowledge, searchable and conversational" in Inter 400. If this pairing looks off, the typography is broken.
