# Vector Vault — Frontend Development Roadmap

*Version 1.0. Persistent master plan — survives across all phases and sessions.*

---

## Current Status

| Attribute | Value |
|-----------|-------|
| **Active Phase** | Phase 3 — Document Management |
| **Phase 1 Status** | ✅ Complete (2026-07-17) |
| **Phase 2 Status** | ✅ Complete (2026-07-17) |
| **Design Mockup** | [Preview URL](http://127.0.0.1:7456/api/projects/vector-vault-chat-mockup-e5d4/raw/index.html) |
| **Design System** | "The Scholar's Study" — warm light theme (parchment `#faf8f5`, amber accent `#c4952e`, navy text `#1B2A3A`) |
| **Design Baseline** | Complete — 6 files in `.opencode/context/` |
| **Last Updated** | 2026-07-17 |
| **Mockup Alignment** | ✅ Complete (2026-07-17) — all components now match mockup CSS |

---

## Phase Overview

| Phase | Name | Status | Core Deliverable |
|-------|------|--------|------------------|
| **1** | Foundation & Design Baseline | ✅ Complete | Scaffold, tokens, static shell |
| **2** | Chat Interface (Core RAG) | ✅ Complete | Working chat with SSE streaming |
| **3** | Document Management | ⬜ Pending | Upload, list, delete documents |
| **4** | Integration & Polish | ⬜ Pending | Error states, responsive, health check |

---

## Phase 1 — Foundation & Design Baseline

**Goal:** Establish the frontend scaffold, design system, and API integration layer. A static chat shell renders with all design tokens wired in — no functionality yet.

### Completed

- [x] `AGENTS.md` — project rules and conventions (Layer 0)
- [x] `FRONTEND_PLAN.md` — Phase 1 architecture plan (Layer 1)
- [x] `FRONTEND_ROADMAP.md` — this file (persistent master plan)
- [x] Design mockup generated via Open Design ("The Scholar's Study" warm theme)
- [x] Design token extraction from mockup → `.opencode/context/design-tokens.css`
- [x] Supporting design docs: `color-palette.md`, `typography.md`, `layout-spec.md`, `DesignSpec.md`
- [x] Vite + Vue 3 + TypeScript scaffold (`npm create vite`, vue-router install)
- [x] `src/types/index.ts` — all 18 backend types mirrored
- [x] `src/api/client.ts` — typed fetch wrappers (streamChat, uploadDocument, fetchDocuments, deleteDocument, checkHealth)
- [x] Token sync: `.opencode/context/design-tokens.css` → `src/assets/styles/tokens.css`
- [x] `src/assets/styles/main.css` — global resets, base typography
- [x] `App.vue` — root layout with `<RouterView>`
- [x] `ChatView.vue` — two-column static shell (sidebar + chat panel)
- [x] `ChatMessage.vue` — static message bubbles (user + assistant variants, source chips)
- [x] `ChatInput.vue` — static input bar (non-functional textarea + send button)
- [x] `npm run dev` starts without errors, build completes clean
- [x] All component styles consume CSS custom properties from `tokens.css`

### Phase 1 Completion Criteria

```
[x] npm run dev starts without TypeScript errors
[x] Browser at localhost:5173 shows static chat shell
[x] Design tokens are visibly applied (colors, fonts, spacing match mockup)
[x] ChatMessage renders user + assistant bubbles with hardcoded data
[x] ChatInput shows textarea + send button (non-functional)
[x] All CSS values come from var(--token-name) — zero hardcoded values
```

---

## Phase 2 — Chat Interface (Core RAG)

**Goal:** Make the chat functional. Users can type messages, see streaming responses from the backend, and view source citations. This is the core RAG experience.

### Components to Implement

| Component | Key Requirements |
|-----------|------------------|
| `useChat.ts` composable | Manages messages array, streaming state, SSE parsing, error handling |
| `ChatView.vue` | Wires composable to view, scroll-to-bottom on new messages |
| `ChatMessage.vue` | Real data from composable, streaming animation on last message, source chips with clickable links (future: document preview) |
| `ChatInput.vue` | Submit on Enter, disabled during streaming, clears on send |

### SSE Streaming Integration

The `useChat.ts` composable must handle the SSE protocol from `POST /api/chats`:

```
Event sequence: 0..N token events → 1 sources event → 1 done event (or 1 error event)
```

| SSE Event | Behavior |
|-----------|----------|
| `token` | Append content to the growing assistant message in-place (streaming effect) |
| `sources` | Store source citations, attach to the completed assistant message |
| `done` | Mark streaming complete, finalize message, store conversation_id |
| `error` | Show error banner, stop streaming, offer retry |

### States to Handle

| State | Behavior |
|-------|----------|
| **Empty chat** | Show intro message from assistant ("Hello! I'm your Vector Vault assistant...") |
| **Streaming** | Disable input, show blinking cursor on last message, auto-scroll |
| **Error** | Show error message inline, keep previous messages, allow retry |
| **No documents** | Assistant message adapts: "You haven't uploaded any documents yet. Upload some to get started." |

### Pending Tasks

- [x] `src/composables/useChat.ts` — full composable with SSE stream parsing
- [x] `src/composables/useConversationId.ts` — persist conversation_id in localStorage
- [x] Update `ChatView.vue` — wire useChat, auto-scroll, empty state
- [x] Update `ChatMessage.vue` — real data binding, streaming cursor, source chips
- [x] Update `ChatInput.vue` — submit handler, Enter key, disabled state
- [x] Error handling for SSE connection drops, timeouts
- [ ] Verify with real backend: send message, see streaming response, see sources

### Phase 2 Completion Criteria

```
[ ] User types message, presses Enter, message appears in chat
[ ] Assistant response streams token-by-token in real time
[ ] Source citation chip appears below assistant response
[ ] Input disabled during streaming, re-enabled on done/error
[ ] Chat auto-scrolls to bottom on new tokens
[ ] Error banner appears on connection failure with retry button
[ ] Empty state shows intro message when no conversation history
```

---

## Phase 3 — Document Management

**Goal:** Full document lifecycle — upload, list, delete. The sidebar becomes functional. Users can manage their knowledge base.

### Components to Implement

| Component | Key Requirements |
|-----------|------------------|
| `useDocuments.ts` composable | Manage document list, upload state, delete, pagination |
| `DocumentUpload.vue` | Drag-and-drop zone or file picker, file type validation (.md/.pdf), size validation (50MB max), upload progress |
| `DocumentList.vue` | Render document cards from composable, empty state, loading skeleton, delete confirmation |
| Update `ChatView.vue` | Integrate document components into sidebar |

### Key Behaviors

| Feature | Behavior |
|---------|----------|
| **Upload** | Drag .md/.pdf file onto zone or click to browse. Validate type and size before sending. Show progress bar. On success, add to list. On error, show message. |
| **File type validation** | Accept only `.md` and `.pdf`. Show error for blocked types. |
| **Size validation** | Max 50MB. Show error with file size displayed. |
| **List** | Fetch on mount, show skeleton while loading, empty state if 0 documents |
| **Delete** | Click delete icon → confirmation dialog → DELETE request → remove from list |
| **Pagination** | Load more button or infinite scroll if many documents |

### States to Handle

| State | Behavior |
|-------|----------|
| **Loading** | Skeleton cards with shimmer animation in sidebar |
| **Empty** | "No documents yet. Upload your first document to start." with prominent upload CTA |
| **Error (list)** | Error message + retry button in sidebar |
| **Error (upload)** | Inline error on upload zone: "Upload failed: File too large (52MB > 50MB limit)" |
| **Uploading** | Progress bar on the uploading document card, disabled input |
| **Deleting** | Document card fades out, removed from list on success |

### Pending Tasks

- [ ] `src/composables/useDocuments.ts` — full composable
- [ ] `src/components/DocumentUpload.vue` — drag-and-drop zone
- [ ] `src/components/DocumentList.vue` — document cards list
- [ ] Update `ChatView.vue` sidebar to use real components
- [ ] File type and size validation
- [ ] Upload progress tracking
- [ ] Delete confirmation flow
- [ ] Pagination support

### Phase 3 Completion Criteria

```
[ ] User can drag-and-drop a .md or .pdf file onto the upload zone
[ ] User can click to browse and select a file
[ ] Invalid file types show clear error message
[ ] Files over 50MB show size error
[ ] Uploaded document appears in sidebar list immediately
[ ] Document list shows loading skeleton while fetching
[ ] Empty sidebar shows helpful message with upload CTA
[ ] Delete click shows confirmation, then removes document from list
[ ] Chat still works — streaming and source citations intact
```

---

## Phase 4 — Integration & Polish

**Goal:** Production-ready robustness. Error handling everywhere, responsive design, health monitoring, empty states perfected.

### Deliverables

| Deliverable | Details |
|-------------|---------|
| **Health Status Indicator** | Green/red dot in header reflects `GET /api/health`. Click shows detailed panel (Ollama status, ChromaDB status, model info). |
| **Error Boundaries** | Every component that fetches data shows inline errors with retry. Global error banner for catastrophic failures. |
| **Empty States** | Every list/collection has a polished empty state with illustration + CTA. Not just "no items" text. |
| **Responsive Layout** | Chat works on narrow screens. Sidebar becomes a toggle/drawer. Message width adapts. Touch-friendly inputs. |
| **Loading Skeletons** | Consistent shimmer skeletons across all data-fetching components. |
| **Network Resilience** | Reconnection logic for SSE drops. Offline detection banner. |
| **Accessibility** | Keyboard navigation, ARIA labels, focus management, screen reader support. |
| **Performance** | Virtual scrolling for long chat histories (if needed). Lazy loading for document list. |

### Pending Tasks

- [ ] Header health status indicator (green/red dot + tooltip)
- [ ] Health check polling (every 30s)
- [ ] Global error boundary component
- [ ] Responsive sidebar (drawer/toggle on mobile)
- [ ] Touch-friendly sizing for mobile
- [ ] ARIA labels and keyboard navigation
- [ ] Offline detection
- [ ] SSE reconnection on connection drop
- [ ] Final visual QA pass against design mockup
- [ ] End-to-end test with real backend

### Phase 4 Completion Criteria

```
[ ] Health dot in header updates in real-time (green/red)
[ ] Every component shows appropriate error state when backend is down
[ ] Every empty state has helpful message + CTA
[ ] Chat works on mobile devices (sidebar collapsible)
[ ] Keyboard-only navigation works end-to-end
[ ] SSE reconnects automatically on connection loss
[ ] All component styles still reference CSS custom properties
[ ] Zero hardcoded colors, spacings, or font sizes
```

---

## Architecture Decisions (Persistent)

These decisions apply across all phases. They do not change.

### Tech Stack

| Layer | Choice | Constraints |
|-------|--------|-------------|
| Framework | Vue 3 (Composition API) | `<script setup>` only |
| Build | Vite 5 | — |
| Language | TypeScript 5 (strict) | No `any`, mirror backend schemas |
| Styling | Plain CSS | CSS custom properties only. No Tailwind, no preprocessors. |
| State | Vue composables | `ref`, `reactive`, `computed`. No Pinia, no Vuex. |
| HTTP | Native `fetch` | No Axios, no libraries. |
| Routing | Vue Router 4 | Hash or history mode |

### Banned Dependencies (All Phases)

- ❌ Tailwind CSS, UnoCSS, WindiCSS
- ❌ CSS-in-JS (Styled Components, Emotion)
- ❌ SCSS, Less, Stylus
- ❌ Pinia, Vuex
- ❌ Axios, ky, got
- ❌ UI component libraries (Vuetify, Element Plus, etc.)

### Documentation Layers

```
Layer 0: AGENTS.md              ← Tech stack, conventions (all agents read first)
Layer 1: FRONTEND_PLAN.md       ← Per-phase plan (architect writes, agents read)
Layer 2: .opencode/context/     ← Design source of truth (ui-designer writes)
Layer 3: src/                   ← Implementation (ui-component-builder writes)
```

### Backend Contract (Critical for All Phases)

| Concern | Code Value (authoritative) |
|---------|---------------------------|
| Chat endpoint | `POST /api/chats` (plural) |
| Pagination param | `page` (not `skip`) |
| Upload field name | `document` (not `file`) |
| `conversation_id` | Required `str` |
| `DocumentInfo.file_type` | Extension string: `".md"` / `".pdf"` |
| `DocumentUploadResponse.file_type` | MIME: `"text/markdown"` / `"application/pdf"` |

---

## Design Decisions (Persistent)

### Current Design System

| Decision | Value |
|----------|-------|
| **Theme** | "The Scholar's Study" — warm light theme |
| **Canvas** | `#faf8f5` (warm parchment) |
| **Sidebar** | `#faf9f5` (ivory surface) |
| **Accent** | `#c4952e` (warm amber) |
| **Font Display** | EB Garamond (brand moments) |
| **Font Body** | Inter (UI, messages) |
| **Sidebar width** | 280px |
| **Max content width** | 720px (chat), 1440px (app wrapper) |
| **Responsive breakpoint** | 900px (tablet), 500px (mobile) |

### If These Change

When design decisions change, they must be updated here AND in the Layer 2 files (`.opencode/context/`). The ui-component-builder syncs from Layer 2 to `src/assets/styles/tokens.css`.

---

## Session Recovery Checklist

When starting a new session, read these files in order:

```
1. AGENTS.md                   ← Rules and conventions
2. FRONTEND_ROADMAP.md         ← THIS FILE (where are we, what's next)
3. FRONTEND_PLAN.md            ← Current phase detailed plan
4. .opencode/context/          ← Current design tokens
```

From this roadmap, identify:
- **Active phase:** Check the "Current Status" table
- **What's done:** Checked boxes in the active phase section
- **Next action:** First unchecked box in the active phase section

---

*End of Roadmap. Update the "Current Status" table at the top after each session's progress.*
