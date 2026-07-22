# FRONTEND PLAN — Phase 3: Document Management

*Layer 1 — Architecture Plan. Read after AGENTS.md and FRONTEND_ROADMAP.md.*

*Version 3.0 — Replaces Phase 2 plan (now archived).*

---

## Phase Overview

**Phase 3** makes the sidebar functional. Users can upload `.md` and `.pdf` documents, see their document library with real data, and delete documents. The sidebar transitions from static placeholder to a fully wired document management panel. All data flows through the `useDocuments` composable driving real API calls through `fetchDocuments()`, `uploadDocument()`, and `deleteDocument()` — all of which were already implemented in Phase 1.

The chat panel (Phase 2) remains untouched and fully operational.

### Phase Deliverables

| # | Deliverable | Owner | Status |
|---|------------|--------|--------|
| 1 | `src/composables/useDocuments.ts` — full document state management | ui-component-builder | 🔲 Pending |
| 2 | `src/components/DocumentUpload.vue` — drag-and-drop upload zone | ui-component-builder | 🔲 Pending |
| 3 | `src/components/DocumentList.vue` — document cards with all states | ui-component-builder | 🔲 Pending |
| 4 | Update `ChatView.vue` — wire sidebar to real components | ui-component-builder | 🔲 Pending |
| 5 | Verification — test against real backend | webapp-testing | 🔲 Pending |

---

## 1. Route Architecture

No changes from Phase 2. Single-page app:

```
/          →  redirect to /chat
/chat      →  ChatView.vue  (sidebar now functional)
```

---

## 2. Component Hierarchy

### Updated Tree (Phase 3)

```
App.vue
 └── ChatView.vue                              ← wires useChat + useDocuments
      ├── <aside class="sidebar">
      │    ├── DocumentUpload.vue               ← NEW: drag-and-drop + file picker
      │    │    └── (hidden <input type="file">, drop overlay, validation)
      │    ├── <span class="sidebar__section-label">Documents</span>
      │    ├── DocumentList.vue                 ← NEW: replaces hardcoded cards
      │    │    ├── [loading] Skeleton cards (shimmer animation)
      │    │    ├── [empty]  "No documents yet..." with upload CTA
      │    │    ├── [error]  Error message + retry button
      │    │    ├── [populated] doc-card × N + delete with confirmation
      │    │    └── [pagination] "Load more" button (if hasMore)
      │    └── <delete confirmation inline>     ← shown on delete click
      └── <main class="chat-panel">             ← UNCHANGED from Phase 2
           ├── ChatMessage.vue
           ├── <empty state>
           ├── <error banner>
           └── ChatInput.vue
```

### Component Responsibilities (Phase 3)

| Component | Phase 2 | Phase 3 |
|-----------|---------|---------|
| `ChatView.vue` | Sidebar with hardcoded cards | **Sidebar now renders `<DocumentUpload>` + `<DocumentList>`.** Chat panel unchanged. |
| `DocumentUpload.vue` | Doesn't exist | **New.** Upload button, hidden file input, drag-and-drop overlay, file type/size validation, upload progress, error messages. |
| `DocumentList.vue` | Doesn't exist (hardcoded in ChatView) | **New.** Fetches documents on mount via `useDocuments`. Renders four states: loading (skeletons), empty (message + CTA), error (message + retry), populated (document cards). Handles delete with inline confirmation. Pagination via "Load more". |
| Chat panel components | Fully functional | **Untouched.** |

### Key Design Decision: Keep It in the Sidebar

The existing `ChatView.vue` sidebar already has all the CSS for document cards (`doc-card`, `doc-card__badge`, `doc-card__name`, `doc-card__meta`, `doc-card__delete`). `DocumentList.vue` will reuse these exact CSS classes. The sidebar CSS structure is:

```css
.sidebar                    /* 280px, warm ivory, border-right */
  .sidebar__upload-btn      /* becomes DocumentUpload component */
  .sidebar__section-label   /* "Documents" label (unchanged) */
  .sidebar__documents       /* becomes DocumentList component */
  .sidebar-empty            /* empty state (moved into DocumentList) */
```

---

## 3. State Management Strategy

### 3.1 `useDocuments.ts` — Document Lifecycle State

**File:** `src/composables/useDocuments.ts`

```typescript
// Interface (conceptual — builder writes actual code)
export function useDocuments() {
  // ── State ──
  const documents: Ref<DocumentInfo[]>         // fetched document list
  const isLoading: Ref<boolean>               // fetching list
  const isUploading: Ref<boolean>             // uploading file
  const error: Ref<string | null>            // last error (list or upload)
  const uploadError: Ref<string | null>      // upload-specific error (separate from list error)
  const currentPage: Ref<number>             // current page (1-indexed)
  const totalDocuments: Ref<number>          // total across all pages
  const deletingIds: Ref<Set<string>>        // track which docs are being deleted (for fade-out)

  // ── Computed ──
  const hasMore: ComputedRef<boolean>        // documents.length < totalDocuments
  const isEmpty: ComputedRef<boolean>        // !isLoading && documents.length === 0

  // ── Actions ──
  async function loadDocuments(page?: number): Promise<void>     // fetchDocuments()
  async function loadNextPage(): Promise<void>                   // loadDocuments(currentPage + 1)
  async function uploadDocument(file: File, title?: string): Promise<void>  // uploadDocument()
  async function deleteDocument(id: string): Promise<void>       // deleteDocument(), remove from list
  function dismissError(): void                                  // clear error state

  // ── Return ──
  return {
    documents: readonly(documents),
    isLoading: readonly(isLoading),
    isUploading: readonly(isUploading),
    error: readonly(error),
    uploadError: readonly(uploadError),
    deletingIds: readonly(deletingIds),
    hasMore,
    isEmpty,
    loadDocuments,
    loadNextPage,
    uploadDocument,
    deleteDocument,
    dismissError,
  }
}
```

### 3.2 State Machine — Document List

```
┌──────────────┐
│   LOADING    │  ← isLoading=true. Show skeleton cards.
│ (on mount)   │
└──────┬───────┘
       │ fetch succeeds
       ▼
┌──────────────┐     documents.length === 0     ┌──────────────┐
│  POPULATED   │ ──────────────────────────────→│    EMPTY     │
│  (show list) │                                │ (message+CTA)│
└──────┬───────┘                                └──────────────┘
       │ fetch fails
       ▼
┌──────────────┐
│    ERROR     │  ← Show error message + retry button.
│ (show banner)│      Retry calls loadDocuments() again.
└──────────────┘
```

### 3.3 State Machine — Upload Flow

```
┌──────────────┐     file selected/dropped
│    IDLE      │ ──────────────────────────┐
│ (upload btn) │                           ▼
└──────────────┘              ┌──────────────────────┐
                              │    VALIDATING         │
                              │ (check type, size)   │
                              └──────┬───────────────┘
                                     │ valid
                                     ▼
                              ┌──────────────────────┐
                              │    UPLOADING          │
                              │ (progress bar, btn    │
                              │  disabled)            │
                              └──────┬───────────────┘
                                     │ success
                                     ▼
                              ┌──────────────────────┐
                              │    DONE               │
                              │ (doc added to list,   │
                              │  upload zone resets)  │
                              └──────────────────────┘
                              
                              ┌──────────────────────┐
                              │    VALIDATION ERROR   │  ← wrong type, too large
                              │ (inline error msg)    │
                              └──────────────────────┘
                              
                              ┌──────────────────────┐
                              │    UPLOAD ERROR       │  ← network/server failure
                              │ (error msg + retry)   │
                              └──────────────────────┘
```

---

## 4. Backend Contract Map

All API functions already exist in `src/api/client.ts`. No changes needed.

| Frontend Action | API Call | Request | Response Wrapper |
|----------------|----------|---------|------------------|
| `loadDocuments()` | `fetchDocuments(page, limit)` | `GET /api/documents?page=1&limit=50` | `SuccessResponse<DocumentListResponse>` |
| `uploadDocument()` | `uploadDocument(file, title?)` | `POST /api/documents` (multipart form) | `SuccessResponse<DocumentUploadResponse>` |
| `deleteDocument()` | `deleteDocument(id)` | `DELETE /api/documents/{id}` | `SuccessResponse<null>` |

### Validation Constraints (Applied Client-Side + Handled Server-Side)

| Constraint | Value | Frontend Handling |
|------------|-------|-------------------|
| **Accepted file types** | `.md`, `.pdf` | Validate before upload. Show error for blocked types. |
| **Max file size** | 50 MB | Validate before upload. Show error with file size. |
| **Title max length** | 100 chars | Trim. Silently truncate or let backend validate. |
| **Page** | ≥1, default 1 | Handled by composable. |
| **Limit** | 1-100, default 50 | Fixed at 20 per page for sidebar UX. |

### Error Response Handling

Error responses from the backend are flat JSON: `{ "message": "..." }`. The `client.ts` functions already handle this by reading `response.text()` on non-ok statuses. The composable should parse the error message from the thrown Error.

---

## 5. Component Specifications

### 5.1 `DocumentUpload.vue`

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `disabled` | `boolean` | `false` | Disable upload while another upload is in progress |

**Emits:**
| Event | Payload | Description |
|-------|---------|-------------|
| `upload` | `{ file: File, title?: string }` | User has selected/dropped a valid file |

**States:**
| State | Visual |
|-------|--------|
| **Idle** | Upload button (amber, full width) with plus icon + "Upload Document" text |
| **Dragging over** | Visual feedback on the upload button or sidebar area (subtle amber border glow) |
| **Uploading** | Button shows spinner or progress text, disabled |
| **Error** | Error text below button: "Only .md and .pdf files are supported" or "File exceeds 50MB limit" |
| **Disabled** | Button is grayed out, cursor not-allowed |

**Behavior:**
1. Click button → triggers hidden `<input type="file" accept=".md,.pdf">`
2. Drag anywhere on sidebar → highlight upload button, accept drop
3. On file selection → validate type (`.md`, `.pdf`) and size (≤ 50MB)
4. On validation pass → emit `upload` with File + optional title (extracted from filename)
5. On validation fail → show inline error, don't emit
6. After successful upload → reset file input so same file can be re-uploaded

**CSS:** Reuses existing `.sidebar__upload-btn` styles from `ChatView.vue`. Additional styles for drag-over glow and error text.

### 5.2 `DocumentList.vue`

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `documents` | `DocumentInfo[]` | `[]` | The document list |
| `isLoading` | `boolean` | `false` | Show skeleton |
| `error` | `string \| null` | `null` | Show error message |
| `hasMore` | `boolean` | `false` | Show "Load more" |
| `deletingIds` | `Set<string>` | `new Set()` | Docs currently being deleted |

**Emits:**
| Event | Payload | Description |
|-------|---------|-------------|
| `delete` | `string` (document ID) | User confirmed delete |
| `retry` | — | User clicked retry after error |
| `load-more` | — | User clicked "Load more" |
| `upload` | — | User clicked CTA from empty state |

**States:**
| State | Visual |
|-------|--------|
| **Loading** | 3 skeleton card placeholders with shimmer animation |
| **Empty** | Centered message: "No documents yet. Upload your first document to get started." with a small upload button below |
| **Error** | Error icon + message + "Retry" button |
| **Populated** | Document cards (reuse `.doc-card` CSS from ChatView) |
| **Deleting** | Card fades to 0.5 opacity with spinner replacing delete icon |

**Document Card (populated state):**
```
┌──────────────────────────────────────────────┐
│ [.md]  quarterly-notes.md                  [✕]│
│        2 days ago · 12 chunks · 4 KB         │
└──────────────────────────────────────────────┘
```

Each card shows:
- **Badge**: file type (`.md` or `.pdf`) — colored per type
- **Filename**: truncated with ellipsis
- **Meta line**: relative time (e.g., "2 days ago") · chunks count · file size (human-readable)
- **Delete button**: trash icon, appears on hover. Click shows inline confirmation.

**Delete Confirmation (inline):**
```
┌──────────────────────────────────────────────┐
│ Delete "quarterly-notes.md"?                 │
│ [Cancel]                              [Delete]│
└──────────────────────────────────────────────┘
```

Replaces the card content with confirmation text and two buttons. Cancel returns to card. Delete emits `delete` event.

**Pagination:**
```
┌──────────────────────────────────────────────┐
│           [ Load 20 more documents ]          │
└──────────────────────────────────────────────┘
```

Shown below the last card when `hasMore` is true. On click emits `load-more`. While loading next page, button shows a small spinner.

**CSS:** All document card styles already exist in `ChatView.vue`'s scoped styles. `DocumentList.vue` must replicate them or we extract them to `src/assets/styles/main.css` as shared styles. **Decision:** Keep them scoped — `DocumentList.vue` duplicates the necessary CSS classes. This avoids polluting the global scope and keeps components self-contained.

---

## 6. Data Flow Diagram

```
User Action                 Composable                  API Client              Backend
───────────                 ──────────                  ──────────              ───────

[Page Load]
ChatView mounts ───────→ useDocuments.loadDocuments() ──→ fetchDocuments(1, 20) ──→ GET /api/documents
                     ←── documents.value updated     ←── SuccessResponse<DocumentListResponse>
                     ←── UI re-renders

[Upload File]
DocumentUpload ───────→ useDocuments.uploadDocument() ─→ uploadDocument(file) ────→ POST /api/documents
  emits 'upload'      ←── isUploading=true              ←── SuccessResponse<DocumentUploadResponse>
                     ←── new doc prepended to list
                     ←── totalDocuments incremented
                     ←── isUploading=false

[Delete Document]
DocumentList ─────────→ useDocuments.deleteDocument(id) ─→ deleteDocument(id) ────→ DELETE /api/documents/{id}
  emits 'delete'      ←── deletingIds.add(id)           ←── SuccessResponse<null>
                     ←── doc removed from list
                     ←── deletingIds.delete(id)

[Load More]
DocumentList ─────────→ useDocuments.loadNextPage() ────→ fetchDocuments(page+1, 20) ──→ GET /api/documents?page=2
  emits 'load-more'   ←── new docs appended to list     ←── SuccessResponse<DocumentListResponse>
```

---

## 7. Type Changes

**No changes needed.** All types in `src/types/index.ts` already mirror backend schemas perfectly:

- `DocumentType` — `".md" | ".pdf"` ✅
- `DocumentStatus` — `"pending" | "processed" | "error"` ✅
- `DocumentUploadResponse` — all fields correct ✅
- `DocumentInfo` — all fields correct ✅
- `DocumentListResponse` — all fields correct ✅

---

## 8. API Client Changes

**No changes needed.** All three document API functions in `src/api/client.ts` are fully implemented:

- `fetchDocuments(page, limit)` ✅
- `uploadDocument(file, title?)` ✅
- `deleteDocument(id)` ✅

The `useDocuments` composable will import these directly.

---

## 9. CSS Strategy

### 9.1 Existing Styles to Reuse

The following CSS classes already exist in `ChatView.vue` scoped styles and must be replicated in the new components:

```css
/* In ChatView.vue: these classes are scoped and NOT accessible from child components */
.sidebar               /* layout container */
.sidebar__upload-btn   /* upload button (becomes DocumentUpload) */
.sidebar__section-label/* "Documents" label */
.sidebar__documents    /* document list container */
.doc-card              /* individual card */
.doc-card__badge       /* file type badge */
.doc-card__badge--md   /* .md coloring */
.doc-card__badge--pdf  /* .pdf coloring */
.doc-card__info        /* name + meta container */
.doc-card__name        /* filename */
.doc-card__meta        /* timestamp + stats */
.doc-card__delete      /* delete button */
.sidebar-empty         /* empty state */
.sidebar-empty__text   /* empty state text */
```

### 9.2 Strategy: Scoped Duplication

Since Vue scoped styles don't leak to child components, each new component will carry its own `<style scoped>` block with the CSS it needs. The `ui-component-builder` should:

1. Extract the relevant CSS classes from `ChatView.vue` into `DocumentUpload.vue` and `DocumentList.vue`.
2. Remove the now-unused hardcoded card markup and CSS from `ChatView.vue` sidebar.
3. Keep `ChatView.vue`'s sidebar layout CSS (`.sidebar`, `.chat-panel`, `.chat-messages`, etc.) since it still owns the layout.

### 9.3 New CSS Tokens Needed?

**None.** All visual tokens already exist in `tokens.css`. The existing color palette, spacing scale, radius tokens, and font tokens cover all document management states. Skeleton shimmer animations will use existing `--color-surface-hover` and `--color-border-subtle`.

---

## 10. Component Dependencies

```
useDocuments.ts
  imports from: @/api/client (fetchDocuments, uploadDocument, deleteDocument)
  imports from: @/types (DocumentInfo, DocumentUploadResponse, DocumentListResponse)

DocumentUpload.vue
  imports from: (none — pure presentational, emits events)

DocumentList.vue
  imports from: @/types (DocumentInfo)
  imports from: (pure presentational, receives props, emits events)

ChatView.vue (updated)
  imports from: @/composables/useChat
  imports from: @/composables/useDocuments  ← NEW
  imports from: @/components/ChatMessage
  imports from: @/components/ChatInput
  imports from: @/components/DocumentUpload  ← NEW
  imports from: @/components/DocumentList    ← NEW
```

---

## 11. Implementation Order

The `ui-component-builder` should work in this order:

1. **`useDocuments.ts`** — Build the composable first. The components need it for their prop/emit contracts.
2. **`DocumentUpload.vue`** — Build the upload zone. Test in isolation (can be mounted standalone).
3. **`DocumentList.vue`** — Build the document list with all four states. Test with mock data.
4. **Update `ChatView.vue`** — Wire `useDocuments`, `DocumentUpload`, `DocumentList` into the sidebar. Remove hardcoded cards.

---

## 12. Phase 3 Completion Criteria

```
[ ] User can click "Upload Document" and select a .md or .pdf file
[ ] User can drag-and-drop a file onto the upload zone
[ ] Invalid file types show clear error message (e.g., ".docx not supported")
[ ] Files over 50MB show size error
[ ] Uploaded document appears in sidebar list immediately after success
[ ] Document list shows loading skeleton while fetching
[ ] Empty sidebar shows helpful message with upload CTA
[ ] Error state shows message + retry button
[ ] Delete click shows inline confirmation dialog
[ ] Confirmed delete removes document from list
[ ] "Load more" button appears when more documents exist beyond the first page
[ ] Chat functionality is unaffected (streaming and source citations still work)
[ ] All CSS values reference var(--token-name) — zero hardcoded values
[ ] npm run build completes without errors
```

---

*End of Phase 3 Plan. Present to user for sign-off before implementation.*
