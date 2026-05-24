# Vector Vault — Project Plan

## 1. Overview

**Vector Vault** is a personal knowledge management application powered by RAG (Retrieval-Augmented Generation). It runs entirely locally on a laptop, keeping private data private, and uses lightweight models suitable for consumer hardware.

**Core Principle:** MVP is a local web app (localhost). Desktop packaging (Tauri) is a future milestone.

---

## 2. Architecture Decisions

| Layer | Decision | Rationale |
|-------|----------|-----------|
| Runtime | Local web app (localhost) | Avoids WSL+Electron friction; Tauri wrap later |
| Backend | Python 3.11+ / FastAPI | Best RAG ecosystem, async, auto-docs |
| LLM Runtime | Ollama | Simple setup, REST API, quantized model support |
| LLM Model | Llama 3.1 8B (Q4_K_M) | Best quality/size ratio, ~5-6GB RAM |
| Vector Store | ChromaDB (embedded mode) | No separate server, pure Python, built-in metadata |
| Embedding Model | all-MiniLM-L6-v2 | 80MB, fast, solid English quality |
| Frontend | Vue 3 + Vite | Approachable, good for smaller apps |
| UI Paradigm | Chat-based RAG (MVP) | Simplest to build; hybrid UI later |
| RAG Pipeline | LangChain primitives | Component reuse without framework lock-in |
| Data Sources | Markdown (.md), PDF (.pdf) | No OCR pipeline needed for MVP |

---

## 3. Project Structure

```
vector-vault/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py               # Settings (pydantic-settings)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py           # Aggregated API router
│   │   │   ├── chat.py             # POST /api/chat
│   │   │   ├── documents.py         # POST/GET/DELETE /api/documents
│   │   │   └── health.py           # GET /api/health
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ingestion.py         # Document loading, chunking, embedding
│   │   │   ├── retrieval.py         # Query embedding, vector search
│   │   │   ├── generation.py        # LLM call via Ollama
│   │   │   └── rag_pipeline.py      # Orchestrates retrieval + generation
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── chat.py              # ChatRequest, ChatResponse
│   │       └── documents.py          # DocumentUpload, DocumentInfo
│   ├── data/
│   │   ├── chroma_db/              # ChromaDB persistence directory
│   │   └── uploads/                # Raw uploaded files
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── api/
│   │   │   └── client.ts           # Axios/fetch wrapper
│   │   ├── components/
│   │   │   ├── ChatMessage.vue      # Single message bubble
│   │   │   ├── ChatInput.vue        # Message input bar
│   │   │   ├── DocumentUpload.vue   # Drag & drop upload
│   │   │   └── DocumentList.vue     # List uploaded documents
│   │   ├── views/
│   │   │   └── ChatView.vue        # Main chat page
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript interfaces
│   │   └── assets/
│   │       └── styles/
│   │           └── main.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
└── docs/
    ├── API.md                      # API design document
    └── SETUP.md                    # Setup & configuration guide
```

---

## 4. Data Flow

```
User Message
    │
    ▼
┌─────────────────┐
│  FastAPI POST    │
│  /api/chat       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  Embed query     │────▶│  ChromaDB search  │
│  (MiniLM)        │     │  (top-k chunks)   │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │  Build prompt:        │
                    │  system + context +   │
                    │  question             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Ollama LLM call      │
                    │  (Llama 3.1 8B)       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Stream response      │
                    │  to frontend          │
                    └──────────────────────┘
```

```
Document Upload
    │
    ▼
┌─────────────────┐
│  FastAPI POST    │
│  /api/documents  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save file to    │
│  data/uploads/   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Load document   │  (LangChain loaders: UnstructuredMarkdownLoader, PyMuPDFLoader)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Split chunks    │  (RecursiveCharacterTextSplitter, ~512 tokens, 50 overlap)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Embed chunks    │  (all-MiniLM-L6-v2, batch embed)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Store in        │
│  ChromaDB         │  (with metadata: source, page, chunk_idx)
└─────────────────┘
```

---

## 5. RAG Pipeline Details

### 5.1 Document Ingestion

| Step | Tool | Parameters |
|------|------|------------|
| Load Markdown | `UnstructuredMarkdownLoader` | - |
| Load PDF | `PyMuPDFLoader` (via `langchain-community`) | - |
| Split chunks | `RecursiveCharacterTextSplitter` | `chunk_size=512`, `chunk_overlap=50` |
| Embed | `HuggingFaceEmbeddings` | `model_name="all-MiniLM-L6-v2"` |
| Store | ChromaDB `add_texts()` | `ids=[hash]`, `metadatas=[{source, page, chunk_idx}]` |

### 5.2 Retrieval

| Step | Tool | Parameters |
|------|------|------------|
| Embed query | `HuggingFaceEmbeddings` | Same model as ingestion |
| Search | ChromaDB `similarity_search()` | `k=5` (top 5 chunks) |
| Score threshold | ChromaDB `similarity_search_with_relevance_score()` | `score_threshold=0.7` |

### 5.3 Generation

| Step | Tool | Parameters |
|------|------|------------|
| Build prompt | Custom prompt template | See prompt template below |
| LLM call | `OllamaLLM` or raw HTTP to `http://localhost:11434/api/generate` | `model="llama3.1"`, `stream=True` |
| Stream | Server-Sent Events (SSE) via FastAPI `StreamingResponse` | - |

### 5.4 Prompt Template

```
You are Vector Vault, a personal knowledge assistant. Answer the user's question based only on the following context from their personal documents. If the context doesn't contain enough information, say so honestly.

Context:
{context}

Question: {question}

Answer:
```

---

## 6. API Design Summary

(See `docs/API.md` for full details)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message, get streamed RAG response |
| POST | `/api/documents` | Upload a document (.md, .pdf) |
| GET | `/api/documents` | List all uploaded documents |
| DELETE | `/api/documents/{doc_id}` | Delete a document and its embeddings |
| GET | `/api/health` | Health check (Ollama + ChromaDB status) |

---

## 7. Configuration

All config via environment variables (with `.env` file support):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3.1` | Model name in Ollama |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | ChromaDB storage path |
| `UPLOAD_DIR` | `./data/uploads` | Uploaded files storage |
| `CHUNK_SIZE` | `512` | Text splitter chunk size |
| `CHUNK_OVERLAP` | `50` | Text splitter overlap |
| `TOP_K` | `5` | Number of chunks to retrieve |
| `SCORE_THRESHOLD` | `0.7` | Minimum similarity score |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |

---

## 8. Dependencies

### Backend (`requirements.txt`)

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.9
pydantic-settings>=2.1.0
langchain>=0.1.0
langchain-community>=0.0.20
langchain-huggingface>=0.1.0
sentence-transformers>=2.3.0
chromadb>=0.4.22
pymupdf>=1.23.0
unstructured>=0.12.0
python-dotenv>=1.0.0
sse-starlette>=1.8.0
```

### Frontend (key packages)

```
vue@3
vite@5
typescript
axios or fetch wrapper
```

### System Requirements

| Requirement | Details |
|-------------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| Ollama | Latest, with `llama3.1` model pulled |
| RAM | 8GB minimum, 16GB recommended |
| Disk | ~1GB for models + ChromaDB |

---

## 9. Development Phases

### Phase 1 — MVP (Chat-based RAG)

- [ ] Backend: FastAPI skeleton + config
- [ ] Backend: Document upload endpoint + file storage
- [ ] Backend: Document ingestion pipeline (load → split → embed → store)
- [ ] Backend: Retrieval service (query embed → ChromaDB search)
- [ ] Backend: Generation service (Ollama integration)
- [ ] Backend: Chat endpoint with SSE streaming
- [ ] Backend: Health check endpoint
- [ ] Frontend: Vue 3 + Vite project scaffold
- [ ] Frontend: Chat UI (message list + input)
- [ ] Frontend: Document upload (drag & drop)
- [ ] Frontend: Document list view
- [ ] Frontend: Streaming response rendering
- [ ] Integration: End-to-end test with sample documents

### Phase 2 — Polish & Robustness

- [ ] Error handling and validation
- [ ] Document re-ingestion / update support
- [ ] Chat history persistence (SQLite or local JSON)
- [ ] Source citation in responses (which document/chunk)
- [ ] Rate limiting / queue for LLM calls
- [ ] Dark mode / theming

### Phase 3 — Desktop App

- [ ] Tauri wrapper (Rust backend, webview frontend)
- [ ] System tray / background running
- [ ] Auto-start on login (optional)
- [ ] Native file dialogs via Tauri APIs

### Phase 4 — Hybrid UI (Document Browser)

- [ ] Document browser sidebar
- [ ] Document preview (markdown render, PDF viewer)
- [ ] Chunk highlighting in source documents
- [ ] Tag / folder organization for documents

---

## 10. WSL Development Notes

Since you're developing on WSL:

1. **Ollama** runs on the Windows side. Access it from WSL via `http://host.docker.internal:11434` or configure Ollama to listen on `0.0.0.0`.
2. **Frontend dev server** (Vite) runs fine on WSL. Access from Windows browser at `http://localhost:5173`.
3. **Backend** (FastAPI) runs fine on WSL. Access from Windows browser at `http://localhost:8000`.
4. **File storage**: Keep `data/` inside the WSL filesystem (not `/mnt/c/`) for performance.
5. **Hot reload**: Both Vite and uvicorn hot-reload work fine on WSL.

---

## 11. Key Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM quality too low for 8B model | Can swap to larger model; prompt engineering helps |
| ChromaDB doesn't scale to large corpus | ChromaDB handles 100K+ documents; switch to Qdrant later if needed |
| Embedding model too small for domain | all-MiniLM is general-purpose; can swap to fine-tuned model |
| PDF parsing quality varies | PyMuPDF is best open-source option; add fallback parsers later |
| WSL networking quirks with Ollama | Use `host.docker.internal` or run Ollama in WSL directly |