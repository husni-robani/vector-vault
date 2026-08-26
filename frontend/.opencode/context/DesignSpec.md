# Vector Vault — Design Specification

*Visual identity document. Read alongside `design-tokens.css`, `color-palette.md`, `typography.md`, and `layout-spec.md`.*

---

## 1. Mood & Identity

**The Scholar's Study.** Vector Vault is a personal knowledge management application, but it does not look like one. It evokes the quiet warmth of a private library: annotated books stacked on a wooden desk, warm lamplight pooling on parchment, marginalia traced in faded ink. The interface should feel like a place you want to linger in — contemplative, unhurried, intellectually generous — not a productivity dashboard you race through.

The palette is anchored in warm parchment (`--color-bg-primary: #faf8f5`) and deep navy text (`--color-text-primary: #1B2A3A`), a combination that echoes fine book printing. A single amber accent (`--color-accent: #c4952e`) runs through the interface like a gilded page edge or a brass bookmark — always thin, always deliberate, never garish. There are no cool grays, no indigo hues, no purple-blue gradients. Every surface is warm, grounded, and analog in spirit.

Typography does the heavy lifting of atmosphere. EB Garamond (`--font-display`) carries the brand's literary DNA — it appears in the wordmark, empty-state headings, and the rare pull quote — while Inter (`--font-body`) keeps the interface clean and readable at every size. The two voices are distinct but harmonious: the serif whispers "scholarship," the sans-serif says "utility."

---

## 2. Design Principles

- **Amber as Punctuation.** `--color-accent` is never a large block. It appears as thin borders, underlines, dots, and the send button — always a mark, never a field. Maximum two or three accent touches per screen. Overuse cheapens the effect.

- **Content is King.** The chrome recedes. Panels, borders, and structural elements use warm low-contrast neutrals (`--color-bg-secondary`, `--color-bg-tertiary`, `--border-color-light`). Nothing competes with the user's documents and conversation.

- **Editorial Measure.** Reading content — chat messages, document previews, empty-state prose — respects a 720px maximum width. This is not an arbitrary constraint; it is the measure of a well-set book. Wider viewports simply center the column in generous whitespace (`--spacing-3xl` body padding).

- **Warm Neutrals Only.** Every gray in the system has a warm undertone: `#5e5d59`, `#8b8980`, `#e8e6dc`. Cool grays (`#666`, `#888`, `#999`) are banned. Dark mode backgrounds are warm charcoal (`#1a1c22`), not steely blue-blacks. No indigo. No trust gradients. This is a scholarly product, not a generic SaaS.

- **Two Voices, One Register.** EB Garamond (`--font-display`) is reserved for brand moments — the wordmark, empty-state headings, ceremonial type at `--font-size-xl` and above. Inter (`--font-body`) handles everything else: messages, labels, inputs, metadata, buttons. The pairing is deliberate and never mixed mid-sentence.

---

## 3. Component Visual Identity

### Chat View
The primary interface is a two-panel layout on desktop: a narrow document sidebar (280px, future phase) and a centered chat column (720px max). On mobile, the sidebar collapses and the chat column fills the viewport. Both panels float on the parchment background with `--spacing-3xl` body padding, giving the entire interface the breathing room of a reading desk.

### User Message Bubble
The user's messages sit on a warm sand background (`--color-bg-tertiary`) with `--radius-md` rounded corners, right-aligned in the chat column. The bubble feels tactile — like a note card resting on the desk — with subtle `--shadow-sm` elevation. Text uses `--font-size-base` in `--color-text-primary`, set at `--line-height-normal`.

### Assistant Message Bubble
The assistant's responses are the centerpiece of the reading experience. They have no background fill — the text floats directly on the parchment canvas — but are marked by a 2px amber left border (`--color-accent`) at `--border-width-thick`. This "marginalia" treatment draws the eye without adding visual weight. Source citations appear as amber-tinted chips (`--color-accent-bg`) below the response. The overall effect is an annotated page, not a chat log.

### Chat Input
The input area anchors to the bottom of the chat column. It is a single-line text field with a subtle bottom border (`--border-color-light`), expanding naturally as the user types. The send button is a small amber circle or rounded pill (`--color-accent`), positioned to the right of the input. On hover, it brightens to `--color-accent-bright`. The entire input row uses `--spacing-lg` padding and sits within the 720px content column — it never stretches edge-to-edge on desktop.

### Document Cards
Each document appears as a parchment card: `--color-bg-secondary` background, `--radius-md` border radius, and a faint `--shadow-md` that suggests a sheet of paper resting on a stack. Interior padding follows `--spacing-md` horizontally and `--spacing-lg` vertically. Card metadata (file type, date, size) uses `--font-size-xs` in `--color-text-tertiary` with `--letter-spacing-wide`. The card's hover state lifts gently with `--shadow-lg` — a physical, analog gesture.

### Source Chips
When the assistant cites a document, each source appears as a small amber-tinted pill: `--color-accent-bg` background, `--radius-full` border radius, and `--font-size-xs` type in `--color-text-primary`. The chip's interior padding is `--spacing-xs` horizontal and `--spacing-sm` vertical. On hover, the amber tint deepens slightly, inviting inspection.

---

## 4. State Design

### Loading
Loading states use a skeleton shimmer pattern on `--color-bg-tertiary` surfaces. For chat messages, a placeholder bubble appears — a rounded rectangle in `--color-bg-tertiary` with a gentle opacity pulse (`--transition-normal`). For document cards, a card-shaped skeleton with the same treatment. No spinner dominates the view; the skeleton suggests content is arriving without demanding attention.

### Empty
Empty states are treated as brand moments. A centered heading in EB Garamond (`--font-display`) at `--font-size-2xl` or `--font-size-3xl` carries the primary message in `--color-text-primary`. Below it, a single line of Inter body text (`--font-size-base`, `--color-text-secondary`) offers a warm, human instruction — never a cold "No results found." The entire block sits centered in the 720px column with generous vertical whitespace, inviting the user to begin.

### Error
Errors appear as a compact notification panel near the relevant content, not a full-screen takeover. The panel uses a `--color-error` left border (`--border-width-thick`) against a transparent or `--color-bg-secondary` background. The error message is set in Inter at `--font-size-base` in `--color-text-primary`, with a retry action rendered as an amber button or link (`--color-accent`). The tone is calm and corrective, not alarming.

### Populated
When content is present, the interface settles into a clean typographic hierarchy. Message text uses `--font-size-base` at `--line-height-relaxed` for comfortable reading. Document metadata and timestamps sit at `--font-size-xs` in `--color-text-tertiary`, visually subordinate to the content. The overall effect is a well-set page — content breathes, chrome recedes, and the amber accent punctuation marks the reading path through the conversation.

---

*End of DesignSpec.md — For implementation, reference tokens in `design-tokens.css` and detailed rules in `color-palette.md`, `typography.md`, and `layout-spec.md`.*
