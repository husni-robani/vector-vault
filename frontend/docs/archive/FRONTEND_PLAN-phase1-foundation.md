# FRONTEND PLAN — Phase 1: Foundation & Design Baseline

*Layer 1 — Architecture Plan. Read after AGENTS.md.*

---

## Phase Overview

**Phase 1** establishes the frontend scaffold, design system baseline, and API integration layer. No interactive functionality is built — that comes in Phase 2 (Chat) and Phase 3 (Documents). The goal of this phase is to have a running Vite dev server rendering a static chat shell with the design tokens fully wired.

### Phase Deliverables

| # | Deliverable | Owner | Status |
|---|------------|-------|--------|
| 1 | `AGENTS.md` — project rules & conventions | Architect | ✅ Done |
| 2 | Design baseline in `.opencode/context/` | ui-designer | 🔲 Pending |
| 3 | Vite + Vue 3 + TypeScript scaffold | ui-component-builder | 🔲 Pending |
| 4 | `src/types/index.ts` — mirrored backend schemas | ui-component-builder | 🔲 Pending |
| 5 | `src/api/client.ts` — typed fetch wrappers | ui-component-builder | 🔲 Pending |
| 6 | Token sync `.opencode/context/` → `src/assets/styles/tokens.css` | ui-component-builder | 🔲 Pending |
| 7 | `src/assets/styles/main.css` — global resets & base | ui-component-builder | 🔲 Pending |
| 8 | `App.vue` + `ChatView.vue` — static shell | ui-component-builder | 🔲 Pending |

---

## 1. Route Architecture

Single-page application with Vue Router. Only one route in Phase 1 (scaffold shell):

```
/ (redirects to /chat)
/chat  →  ChatView.vue
```

All other routes (document management, settings) are Phase 3+. The router is configured in `src/main.ts`.

```
App.vue
 └── <RouterView />
      └── ChatView.vue  (static shell only in Phase 1)
```

---

## 2. Component Hierarchy

### Full Tree (Phases 1-3 target)

```
App.vue
 └── ChatView.vue
      ├── DocumentList.vue          (sidebar, Phase 3)
      ├── <div class="chat-panel">
      │    ├── ChatMessage.vue      (repeated, Phase 2)
      │    ├── ChatMessage.vue
      │    └── ...
      ├── ChatInput.vue             (Phase 2)
      └── DocumentUpload.vue        (inline or modal, Phase 3)
```

### Phase 1 Components

Only static shells — no data, no events, no composables:

| Component | Phase 1 Responsibility | Phase 2+ Adds |
|-----------|----------------------|---------------|
| `App.vue` | Layout shell with `<RouterView>`, imports global CSS | Router links, sidebar toggle |
| `ChatView.vue` | Two-column layout: document sidebar (empty) + chat panel (empty) | ChatMessage render loop, ChatInput, SSE |
| `ChatMessage.vue` | ✅ Create static component (hardcoded props). Shows user bubble + assistant bubble with fake text. Handles loading/empty/populated/error states. | Real data, streaming animation |
| `ChatInput.vue` | ✅ Create static component (non-functional textarea + send button). | Real submit, disable during streaming |
| `DocumentList.vue` | ❌ Not created yet (Phase 3) | Document CRUD |
| `DocumentUpload.vue` | ❌ Not created yet (Phase 3) | Drag-and-drop upload |

### Component Props (Phase 1 contract)

```typescript
// ChatMessage.vue
interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
  sources?: ChatSource[]
}

// ChatInput.vue
interface ChatInputProps {
  disabled?: boolean
  placeholder?: string
}
interface ChatInputEmits {
  (e: 'submit', value: string): void
}
```

---

## 3. State Management Strategy

### Phase 1: No state yet

No composables needed in Phase 1. Components are purely presentational with hardcoded props.

### Phase 2 Composables (DESIGN ONLY — implementation in Phase 2)

```
src/composables/
├── useChat.ts         ← messages[], isStreaming, sendMessage(), clearMessages()
└── useDocuments.ts    ← documents[], uploadDocument(), deleteDocument()
```

**`useChat.ts` design:**

| State | Type | Notes |
|-------|------|-------|
| `messages` | `readonly Ref<ChatMessage[]>` | Accumulated messages |
| `isStreaming` | `readonly Ref<boolean>` | True while SSE stream is active |
| `error` | `readonly Ref<string \| null>` | Last error message |
| `messageCount` | `ComputedRef<number>` | Derived count |

| Action | Signature | Description |
|--------|-----------|-------------|
| `sendMessage(text: string)` | `async ()` | POST to `/api/chats`, parse SSE, update messages |
| `clearMessages()` | `sync ()` | Reset messages array |

### Phase 3 Composable (DESIGN ONLY)

**`useDocuments.ts` design:**

| State | Type | Notes |
|-------|------|-------|
| `documents` | `readonly Ref<DocumentInfo[]>` | Current page of documents |
| `loading` | `readonly Ref<boolean>` | Fetch in progress |
| `error` | `readonly Ref<string \| null>` | Last error |
| `pagination` | `reactive({ page, limit, total })` | Pagination metadata |

| Action | Signature | Description |
|--------|-----------|-------------|
| `fetchDocuments(page?, limit?)` | `async ()` | GET `/api/documents` |
| `uploadDocument(file, title?)` | `async ()` | POST multipart `/api/documents` |
| `deleteDocument(id)` | `async ()` | DELETE `/api/documents/{id}` |

---

## 4. Backend Contract Map

### Frontend Type ↔ Backend Schema Mapping

Every frontend type in `src/types/index.ts` must mirror a backend schema 1:1:

| Frontend Type | Backend Source | Purpose |
|---------------|---------------|---------|
| `ChatRequest` | `backend/app/interfaces/schemas/chat.py:ChatRequest` | POST body for chat |
| `DeliveryEventData` | `backend/app/interfaces/schemas/chat.py:DeliveryEventData` | SSE token chunk |
| `SourcesEventData` | `backend/app/interfaces/schemas/chat.py:SourcesEventData` | SSE sources |
| `SourceInfo` | `backend/app/application/dto/chat.py:SourceInfo` | Individual source |
| `DoneEventData` | `backend/app/interfaces/schemas/chat.py:DoneEventData` | SSE completion |
| `ErrorEventData` | `backend/app/interfaces/schemas/chat.py:ErrorEventData` | SSE error |
| `ChatSource` | *(derived from SourceInfo)* | Frontend display type |
| `DocumentUploadRequest` | `backend/app/interfaces/schemas/documents.py:DocumentUploadRequest` | Form fields |
| `DocumentUploadResponse` | `backend/app/interfaces/schemas/documents.py:DocumentUploadResponse` | Upload result |
| `DocumentInfo` | `backend/app/interfaces/schemas/documents.py:DocumentInfo` | Document in list |
| `DocumentListResponse` | `backend/app/interfaces/schemas/documents.py:DocumentListResponse` | List wrapper |
| `DocumentType` | `backend/app/domain/documents.py:DocumentType` | `'.md' \| '.pdf'` |
| `DocumentStatus` | `backend/app/domain/documents.py:DocumentStatus` | `'pending' \| 'processed' \| 'error'` |
| `HealthResponse` | `backend/app/interfaces/schemas/health.py:HealthResponse` | Health check |
| `OllamaHealthResponse` | `backend/app/interfaces/schemas/health.py:OllamaHealthResponse` | Ollama status |
| `ChromadbHealthResponse` | `backend/app/interfaces/schemas/health.py:ChromadbHealthResponse` | ChromaDB status |
| `SuccessResponse<T>` | `backend/app/interfaces/schemas/response.py:SuccessResponse` | Generic wrapper |
| `ErrorResponse` | `backend/app/interfaces/schemas/response.py:ErrorResponse` | Error body |

### Critical Backend Discrepancies (Code wins over docs)

| Concern | Code Value | Frontend Must Use |
|---------|-----------|-------------------|
| Chat endpoint | `POST /api/chats` | `/api/chats` not `/api/chat` |
| List pagination | `page` param | `page` not `skip` |
| Upload field name | `document` | `formData.append("document", file)` not `"file"` |
| `conversation_id` | Required `str` | Always send it |
| `DocumentInfo.file_type` | Extension string | `".md"` / `".pdf"` |

### API Client Functions (`src/api/client.ts`)

```
API_BASE = 'http://localhost:8000/api'

streamChat(request: ChatRequest) → AsyncGenerator<SSEEvent>
  POST /api/chats
  Content-Type: application/json
  Response: ReadableStream (SSE)
  Yields: token | sources | done | error events

uploadDocument(file: File, title?: string) → Promise<SuccessResponse<DocumentUploadResponse>>
  POST /api/documents
  Content-Type: multipart/form-data
  Field "document" = file, Field "title" = title

fetchDocuments(page?: number, limit?: number) → Promise<SuccessResponse<DocumentListResponse>>
  GET /api/documents?page=1&limit=50

deleteDocument(id: string) → Promise<SuccessResponse<null>>
  DELETE /api/documents/{id}

checkHealth() → Promise<HealthResponse>
  GET /api/health
```

---

## 5. Design Baseline Requirements

### What ui-designer must produce

The `ui-designer` sub-agent is responsible for generating the complete visual design system. It must produce these files in `.opencode/context/`:

| File | Contents |
|------|----------|
| `design-tokens.css` | CSS custom properties: color palette, spacing scale, border radii, shadows, transitions, z-indices |
| `color-palette.md` | Named colors with HEX/OKLCH values, semantic role mapping (primary=buttons, accent=links, danger=delete, etc.), light/dark variants |
| `typography.md` | Font stack (system fonts preferred), type scale (xs → 4xl), weight hierarchy, line-height rules |
| `layout-spec.md` | App max-width, sidebar width (280-320px), chat panel width, responsive breakpoints (mobile/tablet/desktop), spacing grid |
| `DesignSpec.md` | High-level visual identity document: mood board description, design principles, component anatomy references |

### Design Constraints Passed to ui-designer

1. **Tech stack:** Vue 3 + Vite + plain CSS (CSS custom properties only — no Tailwind, no utility classes)
2. **Product:** Personal knowledge management, local-first, privacy-respecting, RAG chat interface
3. **Tone:** Clean, trustworthy, intelligent, calm — not flashy, not startup-vibrant
4. **Must design for these components:**
   - Chat view (two-column: document sidebar + chat panel)
   - Chat message bubbles (user: right-aligned, assistant: left-aligned)
   - Chat input bar (textarea + send button, bottom of chat panel)
   - Document list sidebar (file cards with type icon, name, date, delete button)
   - Document upload area (drag-and-drop zone or upload button)
5. **Must design all states:** loading (skeleton), empty (helpful message), populated, error (retry)
6. **Design system recommendation:** Prefer Linear, Notion, or Clean for a knowledge-management aesthetic. Claude is also suitable for AI-chat interface patterns.

---

## 6. Implementation Task Order

Once the design baseline is produced and you sign off, the `ui-component-builder` will execute tasks in this order:

1. **Scaffold project** — `npm create vite@latest`, configure TypeScript strict, install vue-router
2. **Create `src/types/index.ts`** — all types from §4
3. **Create `src/api/client.ts`** — all functions from §4
4. **Sync tokens** — copy `.opencode/context/design-tokens.css` → `src/assets/styles/tokens.css`
5. **Create `src/assets/styles/main.css`** — global resets, base typography, import tokens
6. **Create `src/main.ts`** — mount app, import router
7. **Create `App.vue`** — root layout, `<RouterView />`
8. **Create `ChatView.vue`** — two-column static shell
9. **Create `ChatMessage.vue`** — static message bubbles with all states
10. **Create `ChatInput.vue`** — static input bar (non-functional)
11. **Verify** — `npm run dev` starts without errors, static shell renders

---

## 7. Phase 1 Completion Criteria

- [ ] `AGENTS.md` exists and is accurate
- [ ] `npm run dev` starts the Vite dev server without errors
- [ ] Browser at `localhost:5173` shows the static chat shell
- [ ] Design tokens are visibly applied (colors, fonts, spacing match the design baseline)
- [ ] ChatMessage component renders user and assistant bubbles with hardcoded data
- [ ] ChatInput component shows textarea + send button (no functionality)
- [ ] All CSS values come from `var(--tokens)` — no hardcoded values
- [ ] TypeScript compiles with strict mode, no errors
- [ ] All backend types are mirrored in `src/types/index.ts`

---

*Plan created — awaiting user sign-off before spawning sub-agents.*
