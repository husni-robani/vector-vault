# FRONTEND PLAN — Phase 2: Chat Interface (Core RAG)

*Layer 1 — Architecture Plan. Read after AGENTS.md and FRONTEND_ROADMAP.md.*

---

## Phase Overview

**Phase 2** makes the chat functional. Users type messages, see token-by-token streaming responses from the backend RAG pipeline, and view source citations. All of this is driven by the `useChat` composable wiring the static shell from Phase 1 to the `streamChat()` API client.

### Phase Deliverables

| # | Deliverable | Owner | Status |
|---|------------|-------|--------|
| 1 | `src/composables/useChat.ts` | ui-component-builder | 🔲 Pending |
| 2 | `src/composables/useConversationId.ts` | ui-component-builder | 🔲 Pending |
| 3 | Update `ChatView.vue` — wire composable, auto-scroll, empty state | ui-component-builder | 🔲 Pending |
| 4 | Update `ChatMessage.vue` — real data binding, streaming cursor live | ui-component-builder | 🔲 Pending |
| 5 | Update `ChatInput.vue` — submit wired to composable, disabled during stream | ui-component-builder | 🔲 Pending |
| 6 | Error handling — SSE drops, timeouts, retry UX | ui-component-builder | 🔲 Pending |
| 7 | Verification — test against real backend | webapp-testing | 🔲 Pending |

---

## 1. Route Architecture

No changes from Phase 1. Single-page app:

```
/          →  redirect to /chat
/chat      →  ChatView.vue  (now functional)
```

---

## 2. Component Hierarchy

### Updated Tree (Phase 2)

```
App.vue
 └── ChatView.vue                          ← wires useChat, useConversationId
      ├── <aside class="sidebar">          ← still static placeholder (Phase 3)
      │    └── (hardcoded document cards)
      └── <main class="chat-panel">
           ├── <header> (brand wordmark)
           ├── <div class="chat-messages">  ← v-for from composable
           │    ├── ChatMessage.vue          ← user: right-aligned bubble
           │    ├── ChatMessage.vue          ← assistant: left, with cursor if streaming
           │    └── <empty state>            ← shown when messages[] is empty
           └── ChatInput.vue                 ← emits submit → useChat.sendMessage()
```

### Component Responsibilities (Phase 2 Changes)

| Component | Phase 1 | Phase 2 |
|-----------|---------|---------|
| `ChatView.vue` | Static shell with hardcoded messages | **Wires `useChat` composable.** Renders `v-for` over `messages`, watches for scroll-to-bottom, shows empty state / error banner. |
| `ChatMessage.vue` | All states already coded | **No structural changes needed.** Already handles `isStreaming`, `sources`, `loading`, `hasError`. Just receives real data now. |
| `ChatInput.vue` | `@submit` emit already coded, disabled prop exists | **No structural changes needed.** Already has Enter handler, disabled prop, `@submit` emit. Just wired to composable. |
| Sidebar (in `ChatView.vue`) | Hardcoded document cards | **Unchanged.** Phase 3 work. Leave static cards. |

### Key Insight: ChatMessage and ChatInput are Phase-2-Ready

Both components were built in Phase 1 with their full prop/emit contracts anticipating functional wiring. Phase 2 is primarily about:
1. Building the `useChat` composable
2. Wiring it into `ChatView.vue`
3. The streaming token accumulation animation

---

## 3. State Management Strategy

### 3.1 `useChat.ts` — Core Chat State

**File:** `src/composables/useChat.ts`

```typescript
// Interface (conceptual — builder writes actual code)
export function useChat() {
  // State
  const messages: readonly Ref<ChatMessage[]>       // accumulated messages
  const isStreaming: readonly Ref<boolean>           // true while SSE active
  const error: readonly Ref<string | null>           // last error message
  const lastEvent: readonly Ref<SSEEvent | null>     // last SSE event received

  // Computed
  const messageCount: ComputedRef<number>            // derived from messages.length
  const lastMessage: ComputedRef<ChatMessage | null> // latest in messages array

  // Actions
  sendMessage(text: string): Promise<void>           // POST → consume SSE → update messages
  clearMessages(): void                              // reset everything
  retryLastMessage(): Promise<void>                  // re-send last user message on error
}
```

### Internal `ChatMessage` Type (Frontend Display)

The composable uses a display-oriented message type that wraps what comes from the API:

```typescript
interface ChatMessage {
  id: string                    // uuid for v-for key
  role: 'user' | 'assistant'
  content: string               // accumulated text
  sources: SourceInfo[]         // populated on sources event
  isStreaming: boolean          // true for the in-flight assistant message
  error: string | null          // set on error event
}
```

This is **NOT** a backend schema type. It's a frontend-only display model. The backend types (`DeliveryEventData`, `SourcesEventData`, etc.) feed into building this.

### 3.2 `useConversationId.ts` — Persistent Conversation State

**File:** `src/composables/useConversationId.ts`

```typescript
export function useConversationId() {
  const conversationId: Ref<string>   // current conversation_id (from localStorage or new)
  newConversation(): void             // generate fresh UUID, clear localStorage
}
```

**Behavior:**
- On first load: generate a new UUID, store in `localStorage`
- On subsequent loads: read from `localStorage`
- On `done` SSE event with a new `conversation_id`: update both ref and localStorage
- On `newConversation()`: generate fresh UUID, clear localStorage, caller also clears messages

**Storage key:** `vector-vault-conversation-id`

### 3.3 SSE Stream Processing Flow

The critical loop inside `sendMessage()`. This is the heart of Phase 2:

```
sendMessage(text)
  │
  ├─ 1. Push user ChatMessage to messages[]
  ├─ 2. Push empty assistant ChatMessage (isStreaming: true) to messages[]
  ├─ 3. Set isStreaming = true, error = null
  ├─ 4. Disable input (via isStreaming)
  │
  ├─ 5. Call streamChat({ message: text, conversation_id })
  │       │
  │       ├── for each SSE event:
  │       │   ├── type === "token":
  │       │   │     append event.content to last assistant message's content
  │       │   │     → Vue reactivity triggers re-render
  │       │   │     → scroll-to-bottom fires
  │       │   │
  │       │   ├── type === "sources":
  │       │   │     replace last assistant message's sources[] with event.sources
  │       │   │
  │       │   ├── type === "done":
  │       │   │     mark last assistant message isStreaming = false
  │       │   │     if event.conversation_id: update conversation_id
  │       │   │     set isStreaming = false
  │       │   │
  │       │   └── type === "error":
  │       │         set last assistant message error = event.message
  │       │         mark isStreaming = false
  │       │         set error = event.message
  │       │
  │       └── on fetch/stream exception:
  │             set isStreaming = false
  │             set error = "Connection lost. Please try again."
  │             mark last assistant message as errored
  │
  └─ 6. Re-enable input (isStreaming = false, regardless of success/failure)
```

### 3.4 State Transitions

```
                              ┌──────────────┐
                              │  Empty Chat  │
                              │ (no messages)│
                              └──────┬───────┘
                                     │ user sends message
                                     ▼
                              ┌──────────────┐
                              │  Streaming   │
                              │ isStreaming  │
                              │ == true      │
                              └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              done event       error event       network error
                    │                │                │
                    ▼                ▼                ▼
              ┌──────────┐   ┌──────────┐    ┌──────────────┐
              │Populated │   │  Error   │    │  Error       │
              │(complete)│   │ (inline) │    │ (connection) │
              └──────────┘   └────┬─────┘    └──────┬───────┘
                                  │                  │
                                  │ user clicks retry│
                                  └──────────────────┘
                                           │
                                           ▼
                                    re-send last user msg
```

---

## 4. Composable ↔ Component Wiring

### ChatView.vue

```typescript
const { messages, isStreaming, error, sendMessage, clearMessages } = useChat();
const { conversationId, newConversation } = useConversationId();

// Scrolling
const messagesContainer = ref<HTMLElement | null>(null);
watch(() => messages.value.length, scrollToBottom);
watch(() => lastMessage.value?.content, scrollToBottom); // scroll on each token

// Empty state
const isEmpty = computed(() => messages.value.length === 0);

// Submit handler
function onInputSubmit(text: string) {
  sendMessage(text);
}
```

### ChatInput.vue Binding

```html
<ChatInput
  :disabled="isStreaming"
  placeholder="Ask a question about your documents..."
  @submit="onInputSubmit"
/>
```

### ChatMessage.vue Binding (v-for)

```html
<ChatMessage
  v-for="msg in messages"
  :key="msg.id"
  :role="msg.role"
  :content="msg.content"
  :is-streaming="msg.isStreaming"
  :sources="msg.sources"
  :has-error="!!msg.error"
  :error-message="msg.error || ''"
/>
```

---

## 5. Empty State & Error UX

### Empty Chat (no messages)

When `messages.length === 0`, show a centered welcome card instead of message list:

```
┌──────────────────────────────────────┐
│                                      │
│    Vector Vault                      │
│    Your personal knowledge,          │
│    searchable and conversational     │
│                                      │
│    ┌────────────────────────────┐    │
│    │ Ask a question about your  │    │
│    │ document collection below. │    │
│    └────────────────────────────┘    │
│                                      │
│    [   Ask a question about...   ] [→]│
└──────────────────────────────────────┘
```

The header wordmark + tagline already exist. Add a friendly intro message card. On first load (no documents + no conversation), keep it warm and inviting.

### Error Banner

When `error` is non-null and not tied to a specific message, show a dismissible banner at the top of the chat panel:

```html
<div v-if="error" class="chat-error-banner" role="alert">
  <span class="chat-error-banner__icon">⚠</span>
  <span class="chat-error-banner__text">{{ error }}</span>
  <button @click="retryLastMessage()" class="chat-error-banner__retry">Retry</button>
  <button @click="error = null" class="chat-error-banner__dismiss">✕</button>
</div>
```

### Auto-Scroll

Scrolling must be smooth and reliable:
- User sends message → instant scroll to bottom (smooth)
- Each token arrives → scroll to bottom if user hasn't scrolled up manually
- If user scrolls up to read history → don't force-scroll (detect with scroll position)

---

## 6. Backend Contract Map (Phase 2 Focus)

Only the chat endpoint is consumed in Phase 2:

| Frontend Call | Endpoint | Request | Response | Notes |
|---------------|----------|---------|----------|-------|
| `streamChat()` | `POST /api/chats` | `{ message, conversation_id }` | SSE stream (NDJSON lines) | Already implemented in Phase 1 |

### SSE Event Sequence (Authoritative from Backend)

```
token → token → ... → token → sources → done
            OR
token → token → ... → error
```

| SSE Event | JSON | Composable Action |
|-----------|------|-------------------|
| `token` | `{"type":"token","content":"some text"}` | Append to assistant message content |
| `sources` | `{"type":"sources","sources":[{"title":...,"chunk_index":...,"distance":...,"snippet":...}]}` | Set assistant message sources |
| `done` | `{"type":"done","conversation_id":"uuid-or-null"}` | End streaming, store conversation_id |
| `error` | `{"type":"error","message":"error text"}` | End streaming, set error |

### `streamChat()` Already Built (Phase 1)

The API client in `src/api/client.ts` handles:
- POST to `/api/chats` with `Content-Type: application/json`
- NDJSON line parsing from `ReadableStream`
- Yielding typed `SSEEvent` objects via `AsyncGenerator`
- Error handling for non-2xx responses

**No API client changes needed in Phase 2.**

---

## 7. Types (Phase 2 Additions)

### New Frontend-Only Types

These go in `src/types/index.ts`. They are NOT backend schema mirrors — they are display models:

```typescript
// Frontend display model for a chat message
export interface ChatMessageModel {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: SourceInfo[];
  isStreaming: boolean;
  error: string | null;
}
```

All backend schema types already exist from Phase 1. No backend type changes needed.

---

## 8. CSS Token Usage

All new styles must consume existing tokens from `src/assets/styles/tokens.css`. No new tokens are expected in Phase 2, but if needed for error banner or empty state, the builder must request them through the architect → ui-designer path.

### Tokens Already Available

Refer to `.opencode/context/design-tokens.css` for the full set. Key tokens for Phase 2:

| Token | Purpose |
|-------|---------|
| `--color-error` | Error banner border, error text color |
| `--color-bg-tertiary` | Error banner background (low opacity variant) |
| `--color-accent` | Streaming cursor, send button |
| `--font-body` | All message text, input, errors |
| `--font-display` | Wordmark, welcome header |
| `--spacing-sm/md/lg/xl` | Padding, gaps |
| `--radius-md` | Error banner corners |
| `--transition-fast` | Cursor blink, opacity transitions |
| `--shadow-sm` | Welcome card elevation |

---

## 9. Implementation Task Order

The `ui-component-builder` executes tasks in this exact order:

1. **Create `src/composables/useConversationId.ts`**
   - UUID generation (crypto.randomUUID or simple fallback)
   - localStorage read/write
   - `newConversation()` to reset

2. **Create `src/types/index.ts` addition — `ChatMessageModel`**
   - Frontend display model for messages
   - Add to existing types file

3. **Create `src/composables/useChat.ts`**
   - Full composable with all states, actions, SSE processing
   - Import `streamChat` from `src/api/client.ts`
   - Import `useConversationId`
   - Handle all SSE event types
   - Error handling with try/catch around generator

4. **Update `ChatView.vue`**
   - Import and instantiate `useChat` and `useConversationId`
   - Replace hardcoded ChatMessage instances with `v-for`
   - Add empty state (welcome card when no messages)
   - Add error banner (dismissible, retry button)
   - Add auto-scroll logic (scroll to bottom on new messages, respect user scroll-up)
   - Wire `ChatInput` @submit to `sendMessage`
   - Pass `isStreaming` to `ChatInput :disabled`

5. **Update `ChatInput.vue`** — verify it works with real data (should need minimal changes since props/emits already correct)

6. **Update `ChatMessage.vue`** — verify streaming cursor renders during actual streaming (should already work)

7. **Verify** — `npm run dev` starts, TypeScript compiles with strict mode, no errors

---

## 10. Phase 2 Completion Criteria

```
[ ] User types message, presses Enter → message appears in chat
[ ] Assistant response streams token-by-token in real time
[ ] Blinking cursor visible on streaming assistant message
[ ] Source citation chips appear below completed assistant response
[ ] Input is disabled during streaming, re-enabled on done/error
[ ] Chat auto-scrolls to bottom on new tokens
[ ] Chat does NOT force-scroll if user scrolls up to read history
[ ] Error banner appears on SSE connection failure with retry + dismiss
[ ] Empty state shows welcome card when no conversation history
[ ] conversation_id persists across page reloads (localStorage)
[ ] TypeScript compiles with strict mode, zero errors
[ ] All CSS values reference var(--token-name) — zero hardcoded values
[ ] New 'New Conversation' button to reset chat + generate new conversation_id
```

---

## 11. Risk Items

| Risk | Mitigation |
|------|-----------|
| Backend SSE format differs from expected NDJSON | `streamChat()` in Phase 1 handles line-by-line parsing; if backend sends SSE with `data: ` prefix or `event: ` lines, it will need adjustment. Check first token from backend. |
| CORS issues with localhost:8000 | Vite dev server proxy may be needed. Configure `vite.config.ts` with proxy for `/api` → `http://localhost:8000` to avoid CORS. |
| Token accumulation too fast for smooth rendering | Vue's reactivity batches updates. Use `nextTick()` after each token append before scroll-to-bottom. |
| `crypto.randomUUID()` not available | Provide fallback: `Date.now().toString(36) + Math.random().toString(36).slice(2)` |

---

*Plan created — awaiting user sign-off before spawning sub-agents.*
