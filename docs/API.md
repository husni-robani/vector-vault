# Vector Vault — API Design

Base URL: `http://localhost:8000/api`

> **Backend Architecture:** The API implementation follows Clean Architecture. Controllers live in `app/interfaces/api/`, request/response schemas in `app/interfaces/serializers/`. Controllers are thin delegates — they parse HTTP input into use case DTOs, call the appropriate use case, and serialize the response. No business logic lives in the controller layer.

All request/response bodies are JSON. Chat response uses Server-Sent Events for streaming.

---

## Endpoints

### POST /api/chat

Send a message and receive a streamed RAG response.

**Request:**

```json
{
  "message": "What did I write about machine learning in my notes?",
  "conversation_id": "optional-uuid-string"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | yes | User's question |
| `conversation_id` | string | no | Thread conversation for multi-turn (future phase) |

**Response:** Server-Sent Events (SSE) stream

Each event is a chunk of the generated response:

```
event: token
data: {"content": "Based on"}

event: token
data: {"content": " your notes,"}

event: token
data: {"content": " you wrote about..."}

event: done
data: {"sources": [{"title": "ml_notes.md", "chunk_index": 3, "score": 0.87}]}
```

| SSE Event | Data Shape | Description |
|-----------|------------|-------------|
| `token` | `{"content": string}` | Partial response text chunk |
| `done` | `{"sources": Source[]}` | Final event with source citations |

**Source object:**

```json
{
  "title": "ml_notes.md",
  "chunk_index": 3,
  "score": 0.87,
  "snippet": "relevant text preview..."
}
```

**Error responses:**

| Status | Condition |
|--------|-----------|
| 400 | Empty message |
| 503 | Ollama not reachable |
| 500 | Internal processing error |

---

### POST /api/documents

Upload a document (.md or .pdf) for ingestion.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | yes | .md or .pdf file |
| `title` | string | no | Custom title (defaults to filename) |

**Example (curl):**

```bash
curl -X POST http://localhost:8000/api/documents \
  -F "file=@/path/to/notes.md"
```

**Response (201 Created):**

```json
{
  "id": "doc_abc123",
  "filename": "notes.md",
  "file_type": ".md",
  "title": "notes",
  "status": "processed"
}
```

**Error responses:**

| Status | Condition |
|--------|-----------|
| 400 | Unsupported file type |
| 409 | Document with same hash already exists |
| 413 | File exceeds size limit (50MB) |
| 500 | Ingestion processing failed |

---

### GET /api/documents

List all uploaded documents.

**Query parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 50 | Max results per page |
| `file_type` | string | null | Filter: "md" or "pdf" |

**Response (200 OK):**

```json
{
  "documents": [
    {
      "id": "doc_abc123",
      "title": "notes.md",
      "filename": "notes.md",
      "file_type": ".md",
      "chunks_count": 12,
      "created_at": "2025-01-15T10:30:00Z",
      "status": "processed",
      "size_bytes": 4520
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

### DELETE /api/documents/{doc_id}

Delete a document and all its embedded chunks.

**Response (200 OK):**

```json
{
  "id": "doc_abc123",
  "title": "notes.md",
  "status": "deleted"
}
```

**Error responses:**

| Status | Condition |
|--------|-----------|
| 404 | Document not found |

---

### GET /api/health

Check system health: Ollama connectivity and ChromaDB status.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "ollama": {
    "connected": true,
    "model": "llama3.1",
    "model_loaded": true
  },
  "chromadb": {
    "connected": true,
    "collections_count": 1,
  },
  "embedding_model": "all-MiniLM-L6-v2"
}
```

**Error response (503 Service Unavailable):**

```json
{
  "status": "unhealthy",
  "ollama": {
    "connected": false,
    "error": "Connection refused at localhost:11434"
  },
  "chromadb": {
    "connected": true
  }
}
```

---

## Exception Hierarchy

Custom exceptions defined in `domain/exceptions.py` map to HTTP status codes at the interface layer:

| Exception | HTTP Status | Typical Condition |
|-----------|-------------|-------------------|
| `NotFoundError` | 404 | Document or resource not found |
| `UnsupportedFileTypeError` | 400 | Uploaded file is not .md or .pdf |
| `DocumentProcessingError` | 500 | Failure during ingestion or processing |
| `ExternalServiceError` | 503 | Ollama, ChromaDB, or embedding service unreachable |
| `VectorVaultError` | 500 | Catch-all base exception |

---

## Frontend → Backend Integration

### CORS Configuration

Backend allows `http://localhost:5173` (Vite dev server) by default.

### SSE Streaming (Frontend)

Use `EventSource` or `fetch` with readable stream:

```typescript
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userInput }),
});

const reader = response.body!.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  // Parse SSE events and render tokens
}
```

### File Upload (Frontend)

```typescript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/documents', {
  method: 'POST',
  body: formData,
});
```

---

## Future API Extensions (Phase 2+)

| Endpoint | Description | Phase |
|----------|-------------|-------|
| `GET /api/chat/history` | List conversation history | 2 |
| `GET /api/chat/{conversation_id}` | Get full conversation | 2 |
| `DELETE /api/chat/{conversation_id}` | Delete conversation | 2 |
| `POST /api/documents/reindex/{doc_id}` | Re-index a document | 2 |
| `GET /api/documents/{doc_id}/chunks` | View chunks for a document | 4 |
| `GET /api/search?q=` | Direct semantic search (no LLM) | 4 |