# Vector Vault — Frontend Rules & Conventions

*Version 1.0 — Layer 0 Documentation. Read this first.*

---

## 1. Project Identity

**Vector Vault** is a personal knowledge management application powered by RAG (Retrieval-Augmented Generation). It runs locally on localhost. The frontend provides a chat-based interface for querying personal documents, with document upload and management capabilities.

**Core principles:**
- Local-first, privacy-respecting
- Lightweight — no unnecessary dependencies
- Clean, trustworthy, calm aesthetic
- Accessible to technical users managing personal documents

---

## 2. Tech Stack

| Layer | Choice | Version | Notes |
|-------|--------|---------|-------|
| Framework | Vue 3 | ^3.x | Composition API only (`<script setup>`) |
| Build | Vite | ^5.x | Fast HMR, native ESM |
| Language | TypeScript | ^5.x | Strict mode enabled |
| Styling | Plain CSS | — | CSS custom properties for theming. No Tailwind, no UnoCSS, no CSS-in-JS, no preprocessors. |
| State | Vue composables | — | `ref`, `reactive`, `computed`, `watch`. No Pinia, no Vuex. |
| HTTP | Native `fetch` | — | No Axios, no other HTTP libraries. |
| Routing | Vue Router | ^4.x | Hash mode or history mode — TBD per setup |

### Banned Dependencies

These are **explicitly disallowed** to keep the frontend light:

- Tailwind CSS, UnoCSS, WindiCSS (any utility CSS framework)
- Styled Components, Emotion, CSS Modules (any CSS-in-JS)
- Pinia, Vuex (any state management library)
- Axios, ky, got (any HTTP library — use native `fetch`)
- SCSS, Less, Stylus (any CSS preprocessor)
- UI component libraries (Vuetify, Element Plus, PrimeVue, etc.)

If a task seems to require one of these, report to the architect — do not install it.

---

## 3. Directory Structure

```
frontend/
├── AGENTS.md                          ← THIS FILE. Read first.
├── docs/
│   ├── FRONTEND_PLAN.md               ← Current phase architecture plan
│   └── archive/                       ← Completed phase plans
├── .opencode/
│   ├── context/                       ← Layer 2: DESIGN SOURCE OF TRUTH
│   │   ├── design-tokens.css          ← CSS custom properties
│   │   ├── color-palette.md           ← Color system documentation
│   │   ├── typography.md              ← Font stack and type scale
│   │   ├── layout-spec.md             ← Breakpoints, grid, dimensions
│   │   └── DesignSpec.md              ← High-level visual identity
│   └── agent/                         ← Agent definitions
├── src/
│   ├── main.ts                        ← App entry, router setup, token import
│   ├── App.vue                        ← Root component
│   ├── api/
│   │   └── client.ts                  ← API functions (native fetch wrappers)
│   ├── composables/                   ← Shared state & logic (Vue composables)
│   │   ├── useChat.ts                 ← Chat state + SSE streaming
│   │   └── useDocuments.ts            ← Document upload/list/delete state
│   ├── components/                    ← Reusable UI components
│   │   ├── ChatMessage.vue
│   │   ├── ChatInput.vue
│   │   ├── DocumentUpload.vue
│   │   └── DocumentList.vue
│   ├── views/                         ← Page-level route components
│   │   └── ChatView.vue
│   ├── types/
│   │   └── index.ts                   ← Mirrored backend schemas
│   └── assets/
│       └── styles/
│           ├── tokens.css             ← SYNCED COPY from .opencode/context/
│           └── main.css               ← Global styles, resets, base
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### Directory Rules

- `src/components/` — Reusable, presentational or semi-smart components. One component per file.
- `src/views/` — Route-level page components. One per route.
- `src/composables/` — Shared reactive state and logic. Export composable functions (`useXxx`).
- `src/api/` — HTTP client functions. One module per resource domain.
- `src/types/` — TypeScript interfaces/types mirroring backend schemas 1:1.
- `src/assets/styles/` — Global styles and synced token copy. Component styles go in `<style scoped>`.
- `.opencode/context/` — **Do not edit directly unless you are `ui-designer`.** Read-only for other agents.

---

## 4. Naming Conventions

### Files

| Type | Convention | Example |
|------|-----------|---------|
| Vue components | PascalCase `.vue` | `ChatMessage.vue` |
| Composables | camelCase `useXxx.ts` | `useChat.ts` |
| Type definitions | camelCase or `index.ts` | `index.ts` |
| API modules | camelCase `.ts` | `client.ts` |
| CSS files | kebab-case `.css` | `tokens.css` |
| Markdown docs | SCREAMING_SNAKE_CASE `.md` | `FRONTEND_PLAN.md` |

### Code

| Element | Convention | Example |
|---------|-----------|---------|
| Components | PascalCase | `<ChatMessage />`, `import ChatMessage` |
| Composables | camelCase, `use` prefix | `useChat()`, `useDocuments()` |
| Props | camelCase | `messageId`, `isStreaming` |
| Events | kebab-case | `@message-sent`, `@document-deleted` |
| CSS classes | kebab-case | `.chat-message`, `.document-card` |
| CSS custom properties | kebab-case, `--` prefix | `--color-primary`, `--spacing-md` |
| TypeScript types | PascalCase interfaces | `ChatMessage`, `DocumentInfo` |
| API functions | camelCase, verb prefix | `sendMessage()`, `uploadDocument()` |

---

## 5. Styling Rules

### CSS Approach

**Plain CSS only.** No utility frameworks. No preprocessors. No CSS-in-JS.

1. **Component styles** go in `<style scoped>` blocks in `.vue` SFCs.
2. **Global styles** go in `src/assets/styles/main.css`.
3. **Design tokens** come from `src/assets/styles/tokens.css` (synced from `.opencode/context/design-tokens.css`).

### Token Consumption

Every component must reference CSS custom properties — never hardcode values:

```css
/* ✅ CORRECT */
.chat-message {
  color: var(--color-text-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  font-family: var(--font-sans);
}

/* ❌ WRONG */
.chat-message {
  color: #333333;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
}
```

### Token Source of Truth

```
.opencode/context/design-tokens.css    ← SOURCE OF TRUTH (ui-designer owns this)
        │
        │  ui-component-builder syncs verbatim
        ▼
src/assets/styles/tokens.css           ← CONSUMABLE COPY (imported by app)
```

- Never edit `.opencode/context/` files (unless you are `ui-designer`).
- Never create tokens in `src/` that don't exist in the source of truth.
- If you need a new token, request it through the architect → `ui-designer`.

### Responsive Design

Use native CSS media queries referencing breakpoints defined in `.opencode/context/layout-spec.md`:

```css
@media (max-width: 768px) {
  .sidebar { display: none; }
}
```

### Typography

Use the font stack and type scale from `.opencode/context/typography.md`. Never set `font-family` to a specific font without referencing the token.

---

## 6. State Management

### Vue Composables Only

All state management uses Vue 3 composables (`ref`, `reactive`, `computed`, `watch`, `watchEffect`). No Pinia. No Vuex.

### Composable Structure

Each composable in `src/composables/` is a self-contained module:

```typescript
// src/composables/useChat.ts
import { ref, computed } from 'vue'
import type { ChatMessage } from '@/types'

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  const messageCount = computed(() => messages.value.length)

  async function sendMessage(text: string): Promise<void> {
    // native fetch + SSE stream parsing
  }

  function clearMessages(): void {
    messages.value = []
  }

  return {
    // State (readonly)
    messages: readonly(messages),
    isStreaming: readonly(isStreaming),
    error: readonly(error),
    // Computed
    messageCount,
    // Actions
    sendMessage,
    clearMessages,
  }
}
```

### Rules

1. **Shared state** → `src/composables/`. Export a composable function.
2. **Component-local state** → `ref`/`reactive` inside `<script setup>`.
3. **No global singletons.** Composables return fresh instances. Components that need shared state call the same composable.
4. **Expose readonly** for state that should not be mutated externally. Use `readonly()`.
5. **Actions, not mutations.** Composables expose functions that modify state internally.

---

## 7. API Integration

### HTTP Client

Use **native `fetch`**. Wrap in typed functions in `src/api/client.ts`:

```typescript
// src/api/client.ts
const API_BASE = 'http://localhost:8000/api'

export interface ChatRequest {
  message: string
  conversation_id?: string
}

export interface ChatResponseChunk {
  token: string
  done: boolean
}

export async function* streamChat(
  request: ChatRequest
): AsyncGenerator<ChatResponseChunk> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`)
  }

  // Parse SSE/NDJSON stream
  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  // ... streaming logic
}
```

### Backend Endpoints

| Method | Endpoint | Purpose | Frontend Module |
|--------|----------|---------|-----------------|
| `POST` | `/api/chat` | Send message, receive SSE stream | `useChat.ts`, `api/client.ts` |
| `POST` | `/api/documents` | Upload document (multipart) | `useDocuments.ts`, `api/client.ts` |
| `GET` | `/api/documents` | List all documents | `useDocuments.ts`, `api/client.ts` |
| `DELETE` | `/api/documents/{id}` | Delete a document | `useDocuments.ts`, `api/client.ts` |
| `GET` | `/api/health` | Health check (Ollama + ChromaDB) | `useHealth.ts` (optional) |

### SSE Streaming

Chat responses use Server-Sent Events (SSE) / NDJSON. Each line is a JSON object with a `token` field. The stream ends with `{"done": true}`.

Handle errors, connection drops, and partial chunks. Show a loading indicator during streaming.

---

## 8. Component Architecture

### Component Rules

1. **Every component handles all states:** loading, empty, populated, error, edge cases.
2. **Props are typed.** Use TypeScript `interface` for props.
3. **Emits are typed.** Use TypeScript for emit payloads.
4. **Scoped styles only.** No global style leakage from components.
5. **No direct DOM manipulation.** Use Vue's reactive system.
6. **Accessible.** Use semantic HTML, proper ARIA labels where needed.

### State Pattern

Every data-fetching component must handle:

```
┌──────────┐
│ LOADING  │ ← Show skeleton/spinner. Initial state.
└────┬─────┘
     │ fetch succeeds
     ▼
┌──────────┐     fetch fails     ┌──────────┐
│POPULATED │ ──────────────────→ │  ERROR   │ ← Show error message + retry button.
└────┬─────┘                     └──────────┘
     │ data is empty array/list
     ▼
┌──────────┐
│  EMPTY   │ ← Show helpful empty state message with CTA.
└──────────┘
```

### Props Contract

```typescript
interface Props {
  message: ChatMessage       // Required: the data to render
  isStreaming?: boolean      // Optional: streaming indicator
  onRetry?: () => void       // Optional: retry callback
}
```

---

## 9. Type System

### Backend Schema Mirroring

All frontend types must mirror backend schemas 1:1. The source of truth is `../backend/app/interfaces/schemas/`. When a backend type changes, the frontend type must be updated.

```typescript
// Example: mirrors backend/app/interfaces/schemas/chat.py
export interface ChatRequest {
  message: string
  conversation_id?: string
}

export interface ChatResponse {
  answer: string
  sources: ChatSource[]
  conversation_id: string
}

export interface ChatSource {
  document_id: string
  document_name: string
  chunk_index: number
  relevance_score: number
}
```

### Rules

1. Types go in `src/types/index.ts` (or split by domain if it grows beyond ~100 lines).
2. Prefer `interface` over `type` for object shapes.
3. Use `readonly` for properties that should not be mutated.
4. Export all types — they may be consumed by multiple components.
5. Never use `any`. Use `unknown` if the type is genuinely unknown, then narrow it.

---

## 10. Documentation System

The project uses a **four-layer documentation system** plus a persistent roadmap. Every agent must know which layer to read for what.

| Layer | Name | Location | Owner | Who Reads |
|-------|------|----------|-------|-----------|
| **0** | Project Rules | `./AGENTS.md` | Architect | All agents (first read) |
| **0a** | Roadmap | `./docs/FRONTEND_ROADMAP.md` | Architect | All agents (second read — "where are we?") |
| **1** | Architecture Plan | `./docs/FRONTEND_PLAN.md` | Architect | Builder, Designer |
| **2** | Design Baseline | `./opencode/context/` | ui-designer | Builder (tokens), Designer (for iteration) |
| **3** | Implementation | `./src/` | ui-component-builder | Builder (during work), Tester (during verify) |

### Mandatory Reading Order

**For `ui-designer`:**
1. `./AGENTS.md` (Layer 0) — tech stack, styling rules
2. `./docs/FRONTEND_ROADMAP.md` (Layer 0a) — current phase, what's done, what's next
3. `./docs/FRONTEND_PLAN.md` (Layer 1) — current phase scope

**For `ui-component-builder`:**
1. `./AGENTS.md` (Layer 0) — tech stack, conventions, naming
2. `./docs/FRONTEND_ROADMAP.md` (Layer 0a) — current phase, what's done, what's next
3. `./docs/FRONTEND_PLAN.md` (Layer 1) — component hierarchy, data flow
4. `.opencode/context/design-tokens.css` (Layer 2) — CSS custom properties
5. `.opencode/context/color-palette.md` (Layer 2) — color usage rules
6. `.opencode/context/typography.md` (Layer 2) — font stack, type scale
7. `.opencode/context/layout-spec.md` (Layer 2) — breakpoints, dimensions

### Key Principle

**If a doc you need doesn't exist, report it — don't guess.**

---

## 11. Agent Roles

| Agent | Mode | Responsibility | Boundaries |
|-------|------|----------------|------------|
| `frontend-architect` | primary | Reads backend schemas, plans architecture, orchestrates sub-agents | Never writes code. Never designs visually. |
| `ui-designer` | subagent | Generates visual designs via Open Design MCP | Writes to `.opencode/context/` only. Never writes `.vue`/`.ts` files. |
| `ui-component-builder` | subagent | Writes Vue 3 + TypeScript + plain CSS code | Writes to `src/` only. Never edits `.opencode/context/`. Syncs tokens verbatim. |

### Communication Flow

```
User → frontend-architect → ui-designer (if new visuals needed)
                          → ui-component-builder (implementation)
                          → webapp-testing skill (verification)
                          → User (review & sign-off)
```

---

## 12. Development Phases

Frontend development is split into four phases. Each phase has its own `FRONTEND_PLAN.md` that is created, reviewed, implemented, and archived before the next phase begins.

| Phase | Name | Focus |
|-------|------|-------|
| **1** | Foundation & Design Baseline | Scaffold, conventions, design tokens |
| **2** | Chat Interface (Core RAG) | Chat view, messages, SSE streaming |
| **3** | Document Management | Upload, list, delete documents |
| **4** | Integration & Polish | Error handling, responsive, health check |

### Phase Workflow

1. Architect creates `docs/FRONTEND_PLAN.md` for the phase
2. User reviews and signs off
3. ui-designer generates design baseline (Phase 1) or updates it (later phases)
4. ui-component-builder implements components
5. webapp-testing verifies
6. Architect archives plan to `docs/archive/FRONTEND_PLAN-<phase-name>.md`
7. User approves phase completion → next phase begins

### Scope Discipline

Tasks stay within their phase. If a task spans phases, the architect splits it. No scope creep between phases.

---

## 13. Hard Constraints

1. **Lightweight:** No unnecessary dependencies. Justify every `npm install`.
2. **Plain CSS only:** No Tailwind, no UnoCSS, no SCSS, no CSS-in-JS. CSS custom properties for theming.
3. **Composables only:** No Pinia, no Vuex. Vue 3 Composition API only.
4. **Native fetch:** No Axios, no HTTP libraries.
5. **Type-safe:** Mirror backend schemas exactly. No `any`. Strict TypeScript.
6. **State coverage:** Every component handles loading, empty, populated, error states.
7. **Token discipline:** Consume CSS custom properties from `tokens.css`. Never hardcode design values.
8. **Read docs first:** Always read AGENTS.md, FRONTEND_PLAN.md, and Layer 2 tokens before writing code.
9. **Respect boundaries:** ui-designer writes to `.opencode/context/`. ui-component-builder writes to `src/`. Neither crosses into the other's domain.
10. **Phase scope:** Stay within the current phase. Report scope creep to the architect.

---

*End of AGENTS.md — This is the law. When in doubt, re-read this file.*
