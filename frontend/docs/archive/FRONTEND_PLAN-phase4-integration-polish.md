# FRONTEND PLAN — Phase 4: Integration & Polish

*Layer 1 — Architecture Plan. Read after AGENTS.md and FRONTEND_ROADMAP.md.*

*Version 4.0 — Replaces Phase 3 plan (now archived).*

---

## Phase Overview

**Phase 4** makes Vector Vault production-ready. The core functionality (chat, documents) is complete. Now we add robustness: health monitoring, responsive layout, offline resilience, SSE reconnection, keyboard accessibility, and a global error boundary. The app transitions from "works on desktop" to "works everywhere, handles failure gracefully."

All existing functionality (chat streaming, document upload/list/delete) remains untouched.

### Phase Deliverables

| # | Deliverable | Owner | Complexity |
|---|------------|--------|------------|
| 1 | `src/composables/useHealth.ts` — health polling composable | ui-component-builder | Small |
| 2 | `App.vue` — wire health indicator, add expandable detail panel | ui-component-builder | Medium |
| 3 | `src/composables/useOnline.ts` — online/offline detection | ui-component-builder | Small |
| 4 | `App.vue` — offline detection banner + global error boundary | ui-component-builder | Small |
| 5 | `ChatView.vue` — responsive sidebar with hamburger toggle + mobile overlay | ui-component-builder | Medium |
| 6 | `useChat.ts` — SSE reconnection with exponential backoff | ui-component-builder | Medium |
| 7 | Keyboard navigation & ARIA polish across all components | ui-component-builder | Medium |
| 8 | Visual QA — token compliance, dark mode smoothness, touch-friendly sizing | ui-component-builder + testing | Small |
| 9 | Verification — test against real backend | webapp-testing | Small |

---

## 1. Route Architecture

No changes. Still single-page:

```
/          →  redirect to /chat
/chat      →  ChatView.vue
```

---

## 2. Component Hierarchy (Phase 4)

### Updated Tree

```
App.vue                                    ← NEW: useHealth, useOnline, error boundary, offline banner
 ├── <header>
 │    ├── <brand>                           (unchanged)
 │    ├── <theme-toggle>                    (unchanged)
 │    ├── <health-indicator>                ← NEW: reactive green/red dot, click to expand panel
 │    │    └── <health-detail-panel>        ← NEW: expandable card showing Ollama/ChromaDB/Embedding status
 │    ├── <offline-banner>                  ← NEW: shown when navigator.onLine === false
 │    └── <sidebar-toggle>                  ← NEW: hamburger button (visible ≤500px)
 │
 └── <main>
      └── ChatView.vue                      ← UPDATED: sidebar toggle integration
           ├── <aside class="sidebar">      ← UPDATED: overlay on mobile, Escape to close
           │    ├── DocumentUpload.vue       (unchanged)
           │    └── DocumentList.vue         (unchanged)
           │
           └── <main class="chat-panel">
                ├── <reconnecting-banner>    ← NEW: shown during SSE reconnection
                ├── <error-banner>           (unchanged)
                ├── <empty-state>            (unchanged)
                ├── ChatMessage.vue          ← UPDATED: ARIA live region for streaming
                └── ChatInput.vue            ← UPDATED: keyboard shortcut, touch tweaks
```

### Component Changes Summary

| Component | Phase 3 | Phase 4 |
|-----------|---------|---------|
| `App.vue` | Static health dot, no online/offline, no error boundary | **Wired health indicator + detail panel, offline banner, error boundary** |
| `ChatView.vue` | Sidebar `display:none` at 500px | **Hamburger toggle, sidebar overlay on mobile** |
| `useChat.ts` | One-shot SSE, no retry | **Exponential backoff reconnection** |
| `ChatMessage.vue` | No ARIA live region | **ARIA live region for streaming** |
| `ChatInput.vue` | Basic input | **`/` key shortcut to focus, touch tweaks** |
| `useHealth.ts` | Doesn't exist | **NEW** |
| `useOnline.ts` | Doesn't exist | **NEW** |
| Other components | Fully functional | **Unchanged** |

---

## 3. New Composables

### 3.1 `useHealth.ts` — Health Polling

**File:** `src/composables/useHealth.ts`

```typescript
export function useHealth(pollIntervalMs: number = 30000) {
  // ── State ──
  const status: Ref<'healthy' | 'unhealthy' | 'loading'> = ref('loading')
  const ollama: Ref<OllamaHealthResponse | null> = ref(null)
  const chromadb: Ref<ChromadbHealthResponse | null> = ref(null)
  const embeddingModel: Ref<string | null> = ref(null)
  const lastChecked: Ref<Date | null> = ref(null)
  const error: Ref<string | null> = ref(null)

  // ── Computed ──
  const isHealthy: ComputedRef<boolean> = computed(() => status.value === 'healthy')
  const isDetailOpen = ref(false)

  // ── Actions ──
  async function checkNow(): Promise<void>    // Immediate health check
  function toggleDetail(): void               // Toggle detail panel
  function startPolling(): void               // setInterval
  function stopPolling(): void                // clearInterval

  // Starts polling on creation, stops on scope disposal (onScopeDispose)
}
```

### 3.2 `useOnline.ts` — Offline Detection

**File:** `src/composables/useOnline.ts`

```typescript
export function useOnline() {
  const isOnline = ref(navigator.onLine)
  // Listen for 'online' and 'offline' events on window
  // Return readonly isOnline
}
```

---

## 4. Backend Contract Map

All API functions already exist. Only `checkHealth()` is newly wired.

| Frontend Action | API Call | Request | Response |
|----------------|----------|---------|----------|
| `checkNow()` | `checkHealth()` | `GET /api/health` | `HealthResponse` |
| Polling (every 30s) | `checkHealth()` | `GET /api/health` | `HealthResponse` |

### Health Response Shape (already typed in `types/index.ts`)

```typescript
interface HealthResponse {
  status: string                       // "healthy" | "unhealthy"
  ollama: OllamaHealthResponse         // { connected, model, model_loaded, error }
  chromadb: ChromadbHealthResponse     // { connected, collections_count, error }
  embedding_model: string              // e.g. "all-MiniLM-L6-v2"
}
```

---

## 5. Detailed Specifications

### 5.1 Health Status Indicator (App.vue)

**Replaces the static** `<div class="header__health">` in App.vue's template.

**States:**

| State | Visual |
|-------|--------|
| **Loading** (initial) | Gray dot, "Checking..." label |
| **Healthy** | Green dot with glow (`--color-success`), "System Healthy" label |
| **Unhealthy** | Red dot (`--color-error`), "Service Issue" label |

**Expanded Detail Panel:**

Clicking the health indicator expands an inline card below the header:

```
┌─────────────────────────────────────────────────────────────┐
│ System Status                                  [✕]         │
│                                                             │
│ Ollama          ● Connected      llama3.2        loaded    │
│ ChromaDB        ● Connected      3 collections              │
│ Embedding       ● Ready          all-MiniLM-L6-v2           │
│                                                             │
│ Last checked: 12 seconds ago                                │
└─────────────────────────────────────────────────────────────┘
```

- Each row shows a green/red dot + service name + detail
- Click outside or ✕ closes the panel
- Panel uses existing CSS tokens: `--color-surface-card`, `--color-border-prominent`, `--shadow-card`
- Renders inside the `<header>` as an absolutely-positioned dropdown

### 5.2 Offline Banner (App.vue)

Shown between header and main content when `isOnline === false`:

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠ You are offline. Changes will sync when connection        │
│   is restored.                                              │
└─────────────────────────────────────────────────────────────┘
```

- Uses `--color-accent-soft` background + `--color-accent` text
- Appears/disappears with CSS transition
- Auto-hides when `online` event fires
- Does NOT prevent user from reading cached content

### 5.3 Responsive Sidebar (ChatView.vue + App.vue)

**Breakpoint:** ≤500px width

**Desktop (width > 500px):** No changes. Sidebar is always visible at `var(--sidebar-width)`.

**Mobile (width ≤ 500px):**

1. **Hamburger button** appears in the App header (next to theme toggle). Only visible at ≤500px.
2. **Sidebar is hidden by default.** Slides in from the left as an overlay (`transform: translateX(-100%)` → `translateX(0)`).
3. **Backdrop** appears behind sidebar (semi-transparent black). Clicking backdrop closes sidebar.
4. **Escape key** closes sidebar.
5. **Focus trap:** when sidebar is open, Tab/Shift+Tab cycle within sidebar only.
6. **Sidebar takes full height** of viewport and sits above the chat panel.
7. **Opening sidebar closes the health detail panel** (and vice versa) to avoid overlapping overlays.

**CSS Implementation:**

```css
@media (max-width: 500px) {
  .sidebar {
    position: fixed;
    top: var(--header-height);
    left: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
    box-shadow: var(--shadow-card-hover);
  }

  .sidebar--open {
    transform: translateX(0);
  }

  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: 99;
    opacity: 0;
    transition: opacity var(--transition-normal);
    pointer-events: none;
  }

  .sidebar-backdrop--visible {
    opacity: 1;
    pointer-events: auto;
  }
}
```

**Hamburger button:**

```
┌───┐
│ ≡ │  (three-line icon, 34×34px, matches theme-toggle dimensions)
└───┘
```

- Same style as the existing `.theme-toggle` button
- `aria-label="Toggle sidebar"`, `aria-expanded` reflects state

### 5.4 SSE Reconnection (useChat.ts)

**Current behavior:** `streamChat()` throws on connection failure → catch block shows error banner. User must retry manually.

**New behavior:**

1. `sendMessage()` wraps the SSE stream in a retry loop
2. **Connection failure during streaming** → set a "reconnecting" state, don't remove messages
3. **Exponential backoff:** wait 1s → 2s → 4s → 8s → max 30s between retries
4. **Max 3 retries** → then show error banner (existing behavior)
5. **During reconnection:** show a subtle banner above chat input: "Reconnecting..." with animated dots
6. **On successful reconnection:** re-send the last user message, replace the partial assistant response
7. **New user messages are blocked** during reconnection (same as during streaming)

**State machine:**

```
IDLE → STREAMING → (error) → RECONNECTING → (success) → STREAMING
                                    ↓ (max retries)
                                  ERROR (existing banner)
```

**Implementation approach:**

The retry logic lives in `useChat.ts`'s `sendMessage()` method. On SSE failure, it increments a `retryCount`, waits via `setTimeout` wrapped in a promise, then calls `sendMessage()` again (recursively via a private `_sendMessageWithRetry`). The public `sendMessage()` resets `retryCount` to 0.

### 5.5 Keyboard Navigation & ARIA

| Feature | Implementation | Where |
|---------|---------------|-------|
| **`/` key to focus input** | `keydown` listener on `document`, focuses `ChatInput` textarea | `ChatInput.vue` via `onMounted`/`onUnmounted` |
| **Escape to close overlays** | Priority: health panel → sidebar → confirmation dialogs | `App.vue` (`keydown` listener) |
| **ARIA live region** | `aria-live="polite"` on streaming assistant message bubble | `ChatMessage.vue` (when `isStreaming`) |
| **Focus trap** | When sidebar is open on mobile, Tab cycles within sidebar | `ChatView.vue` (focus trap logic in `onMounted`) |
| **Skip link** | "Skip to chat" link at top of page, visible on focus | `App.vue` |
| **`aria-expanded`** | On hamburger button, health indicator | `App.vue` |
| **`aria-label`** | All icon-only buttons already have them — audit for completeness | All components |

### 5.6 Global Error Boundary (App.vue)

Vue doesn't have React-style error boundaries, but we can use `onErrorCaptured`:

```typescript
// App.vue <script setup>
import { onErrorCaptured, ref } from 'vue'

const globalError = ref<string | null>(null)

onErrorCaptured((err: Error, instance, info) => {
  console.error('Global error:', err, info)
  globalError.value = err.message || 'An unexpected error occurred.'
  return false // Prevent propagation
})
```

When `globalError` is set, replace `<RouterView>` with a fallback:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                     Something went wrong                     │
│                                                             │
│            An unexpected error occurred.                     │
│                                                             │
│                     [ Reload App ]                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.7 Touch-Friendly Polish

| Issue | Fix |
|-------|-----|
| **Small tap targets on mobile** | Ensure all interactive elements ≥ 44×44px at ≤500px (ChatInput send button is already 36px, bump to 44px on mobile) |
| **Virtual keyboard hides input** | `ChatInput.vue` listens for `visualViewport` resize, adjusts padding at bottom |
| **Long press context menu** | `-webkit-touch-callout: none` on interactive elements, `user-select: none` on non-text content |

---

## 6. Data Flow

### Health Polling Flow

```
App.vue mounts
  → useHealth() created
  → checkNow() called immediately
    → GET /api/health
    → Populate status, ollama, chromadb, embeddingModel
  → setInterval every 30s → checkNow()
  → App.vue header dot reflects isHealthy
  → Click dot → toggleDetail() → expand panel

App.vue unmounts (never happens in SPA)
  → onScopeDispose → clearInterval
```

### Offline Detection Flow

```
useOnline() created
  → isOnline = navigator.onLine
  → window.addEventListener('online', () => isOnline = true)
  → window.addEventListener('offline', () => isOnline = false)
  → App.vue watches isOnline → shows/hides offline banner
```

### SSE Reconnection Flow

```
User sends message
  → sendMessage("query")
    → _sendMessageWithRetry("query", retryCount=0)
      → streamChat({ message, conversation_id })
      → [SSE events stream normally] → done
      → [connection drops]
        → catch
          → retryCount < 3?
            → YES: wait(backoff(retryCount)), _sendMessageWithRetry("query", retryCount+1)
            → NO: show error banner
```

---

## 7. Type Changes

**No changes needed.** `src/types/index.ts` already contains `HealthResponse`, `OllamaHealthResponse`, `ChromadbHealthResponse`. The `useHealth` and `useOnline` composables use only `ref<string|null>` and `ref<boolean>` — no new types required.

---

## 8. API Client Changes

**No changes needed.** `checkHealth()` in `src/api/client.ts` is already implemented and typed.

---

## 9. CSS Strategy

### 9.1 New CSS Needed

| Component | New Styles |
|-----------|-----------|
| Health detail panel | `.health-detail` — absolutely-positioned card below header, `z-index: 200` |
| Offline banner | `.offline-banner` — fixed bar below header, `z-index: 50` |
| Sidebar overlay | `.sidebar-overlay` — fixed backdrop, `.sidebar` mobile transform |
| Hamburger button | `.sidebar-toggle` — matches `.theme-toggle` dimensions |
| Reconnecting banner | `.reconnecting-banner` — subtle bar above chat input |
| Global error fallback | `.global-error` — centered error page with reload button |

### 9.2 Existing Tokens Coverage

All new CSS will consume existing tokens. No new tokens required:
- Health colors: `--color-success`, `--color-error`, `--color-text-muted`
- Panel surfaces: `--color-surface-card`, `--color-bg-header`
- Borders: `--color-border-prominent`, `--color-border-subtle`
- Shadows: `--shadow-card-hover`
- Typography: `--font-body`, `--font-size-small`, `--font-size-caption`
- Spacing: `--spacing-sm` through `--spacing-2xl`
- No hardcoded values anywhere.

---

## 10. Implementation Order

The `ui-component-builder` should work in this order:

1. **`useHealth.ts`** — Build the composable first. The health indicator needs it.
2. **`useOnline.ts`** — Build the offline detection composable.
3. **`App.vue`** — Wire health indicator + detail panel, offline banner, error boundary, hamburger toggle, Escape handler.
4. **`ChatView.vue`** — Responsive sidebar overlay, backdrop, focus trap.
5. **`useChat.ts`** — SSE reconnection with exponential backoff, reconnecting banner state.
6. **`ChatMessage.vue`** — ARIA live region for streaming.
7. **`ChatInput.vue`** — `/` key shortcut, touch tweaks.
8. **Final visual QA** — Token audit, dark mode transitions, responsive verification.

---

## 11. Phase 4 Completion Criteria

```
[ ] Health dot in header updates in real-time (green = healthy, red = unhealthy)
[ ] Clicking health dot expands detail panel showing Ollama/ChromaDB/Embedding status
[ ] Health polls every 30 seconds
[ ] Offline detection banner appears when network is disconnected
[ ] Offline banner auto-hides when network returns
[ ] Hamburger toggle appears at ≤500px width
[ ] Sidebar slides in as overlay on mobile, backdrop dismisses it
[ ] Escape key closes sidebar and health panel
[ ] SSE reconnects automatically on connection drop (exponential backoff)
[ ] "Reconnecting..." banner shows during retry
[ ] Max 3 retries → error banner (existing behavior)
[ ] `/` key focuses the chat input
[ ] ARIA live region announces streaming content to screen readers
[ ] Focus trap works inside mobile sidebar
[ ] Skip link present at top of page
[ ] All component styles still reference CSS custom properties — zero hardcoded values
[ ] npm run build completes without errors
[ ] All existing functionality (chat, upload, delete) works correctly
```

---

*End of Phase 4 Plan. Implementation delegated to ui-component-builder.*
