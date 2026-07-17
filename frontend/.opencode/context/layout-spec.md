# Vector Vault — Layout Specification

*Generated from brandkit run. Source of truth for all layout decisions.*

---

## Design Philosophy

The interface should feel like reading in a library, not navigating a dashboard. Generous whitespace, restrained density, and an editorial-quality grid. Content is king — the chrome recedes.

---

## Grid System

### Brand Board Grid (Reference)
- 3×3 grid with 12px gutters (`--spacing-lg`)
- 16:9 aspect ratio
- Max width: 1440px
- Max height: min(90vh, 810px)

### Application Grid
- Single-column centered layout for chat content
- Max content width: 720px (comfortable reading measure)
- No sidebar by default (future: document sidebar at 280px)

---

## Breakpoints

| Name | Width | Usage |
|------|-------|-------|
| **Mobile** | < 500px | Single column, full-width panels |
| **Tablet** | 500px – 900px | Two-column grid, reduced type sizes |
| **Desktop** | > 900px | Three-column grid, full type scale |

### Media Query Snippets

```css
/* Tablet: 2-column */
@media (max-width: 900px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

/* Mobile: 1-column */
@media (max-width: 500px) {
  .grid { grid-template-columns: 1fr; }
}
```

---

## Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--spacing-xs` | 4px | Tight internal padding |
| `--spacing-sm` | 6px | Input padding, icon gaps, theme toggle |
| `--spacing-md` | 8px | Swatch gaps, browser chrome padding |
| `--spacing-lg` | 12px | Grid gutters, panel padding |
| `--spacing-xl` | 16px | Section gaps, accent line margins |
| `--spacing-2xl` | 20px | Logo-to-wordmark gap |
| `--spacing-3xl` | 24px | Page padding |

---

## Component Dimensions

| Component | Width | Height | Notes |
|-----------|-------|--------|-------|
| Logo mark (lg) | 80px | 80px | For brand moments, hero sections |
| Logo mark (default) | 56px | 56px | Standard logo display |
| Logo mark (sm) | 32px | 32px | Navbar, cards |
| Logo mark (xs) | 20px | 20px | Browser tabs, favicon-sized |
| Color swatch | 32px | 32px | Brand board color chips |

---

## Panel & Card Design

### Panel
- Border radius: 6px (`--radius-xl`)
- Border: 1px solid (light: `--color-bg-tertiary`, dark: `rgba(255,255,255,0.06)`)
- Overflow: hidden
- Position: relative (for corner labels)

### Message Bubbles (Chat UI)
- User: sand background (`--color-bg-tertiary`), 4px radius
- Assistant: transparent with 2px amber left border (marginalia style)
- Padding: 6px 8px
- Font size: 11px (`--font-size-base`)

### Document Cards
- Parchment background
- 4px border radius
- Subtle shadow (`--shadow-md`)
- Interior padding: 8px 12px

---

## Layout Rules

1. **Single-column reading.** Chat content should never exceed 720px wide. If the viewport is wider, center the content column.

2. **No full-width content blocks.** Even document lists should respect the 720px reading measure.

3. **Panel labels go top-left.** Micro-labels (9px, uppercase, 0.08em letter-spacing) positioned absolutely at `top: 10px; left: 12px`.

4. **Panel numbers go bottom-right.** Small numeric indicators (10px) at `bottom: 10px; right: 12px`.

5. **The amber accent is a punctuation mark.** Use it for borders, underlines, dots — thin horizontal elements. Never large blocks of amber.

6. **Body padding is 24px.** The page body should have 24px padding on all sides to give content breathing room.

7. **Dark mode panels have no visible borders** — they use `rgba(255,255,255,0.06)` which reads as a subtle separation, not a hard line.
