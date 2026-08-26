# Vector Vault — Project Plan

## 1. Overview

**Vector Vault** is a personal knowledge management application powered by RAG (Retrieval-Augmented Generation). It runs entirely locally on a laptop, keeping private data private, and uses lightweight models suitable for consumer hardware.

**Core Principle:** MVP is a local web app (localhost). Desktop packaging (Tauri) is a future milestone.

---

## 2. Architecture Decisions

| Layer | Decision | Rationale |
|-------|----------|-----------|
| Architecture | Clean Architecture (Ports & Adapters) | Independent of frameworks, testable, swappable infrastructure |
| Runtime | Local web app (localhost) | Avoids WSL+Electron friction; Tauri wrap later |
| Backend | Python 3.11+ / FastAPI | Best RAG ecosystem, async, auto-docs |
| LLM Runtime | Ollama | Simple setup, REST API, quantized model support |
| LLM Model | Llama 3.1 8B (Q4_K_M) | Best quality/size ratio, ~5-6GB RAM |
| Vector Store | ChromaDB (embedded mode) | No separate server, pure Python, built-in metadata |
| Embedding Model | all-MiniLM-L6-v2 | 80MB, fast, solid English quality |
| Frontend | Vue 3 + Vite | Approachable, good for smaller apps |
| UI Paradigm | Chat-based RAG (MVP) | Simplest to build; hybrid UI later |
| External Libraries | LangChain primitives (wrapped in adapters) | LangChain lives only in infrastructure layer; swappable |
| Data Sources | Markdown (.md), PDF (.pdf) | No OCR pipeline needed for MVP |

---

## 3. Project Structure (Clean Architecture)

```
vector-vault/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # Composition root: wires DI, starts uvicorn
│   │   ├── config.py                   # Settings (pydantic-settings)
│   │   ├── dependencies.py             # FastAPI DI providers (get_use_case)
│   │   │
│   │   ├── domain/                     # LAYER 0: Entities — zero deps
│   │   │   ├── __init__.py
│   │   │   ├── documents.py            # Document, DocumentType, DocumentStatus
│   │   │   ├── chunks.py               # Chunk, SearchResult, MetaData
│   │   │   ├── conversations.py        # Conversation, Message (Phase 2)
│   │   │   └── exceptions.py           # VectorVaultError hierarchy
│   │   │
│   │   ├── application/                # LAYER 1: Business logic — depends on domain
│   │   │   ├── __init__.py
│   │   │   ├── ports/                  # Abstract interfaces (what we need)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vector_store.py     # VectorStorePort
│   │   │   │   ├── embedding.py        # EmbeddingPort
│   │   │   │   ├── llm.py              # LLMPort
│   │   │   │   ├── document_repo.py    # DocumentRepositoryPort
│   │   │   │   ├── file_storage.py     # FileStoragePort
│   │   │   │   ├── document_loader.py  # DocumentLoaderPort
│   │   │   │   └── text_splitter.py    # TextSplitterPort
│   │   │   ├── dto/                    # Use case input/output objects (@dataclass)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py
│   │   │   │   └── documents.py
│   │   │   │   └── health.py
│   │   │   └── use_cases/              # Single-responsibility orchestrators
│   │   │       ├── __init__.py
│   │   │       ├── ingest_document.py  # IngestDocumentUseCase
│   │   │       ├── answer_question.py  # AnswerQuestionUseCase
│   │   │       ├── list_documents.py   # ListDocumentsUseCase
│   │   │       ├── delete_document.py  # DeleteDocumentUseCase
│   │   │       └── check_health.py     # HealthCheckUseCase
│   │   │
│   │   ├── infrastructure/             # LAYER 2: Adapters — depends on application ports
│   │   │   ├── __init__.py
│   │   │   ├── vector_store/
│   │   │   │   ├── __init__.py
│   │   │   │   └── chromadb_adapter.py # ChromaDBVectorStore : VectorStorePort
│   │   │   ├── embedding/
│   │   │   │   ├── __init__.py
│   │   │   │   └── hf_sentence_adapter.py # SentenceTransformerEmbedding : EmbeddingPort
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   └── ollama_adapter.py   # OllamaLLM : LLMPort
│   │   │   ├── document_repo/
│   │   │   │   ├── __init__.py
│   │   │   │   └── sqlite_repository.py   # SQLiteDocumentRepository : DocumentRepositoryPort
│   │   │   ├── file_storage/
│   │   │   │   ├── __init__.py
│   │   │   │   └── local_storage.py    # LocalFileStorage : FileStoragePort
│   │   │   ├── document_loaders/
│   │   │   │   ├── __init__.py
│   │   │   │   └── langchain_loader.py # LangChainDocumentLoader : DocumentLoaderPort
│   │   │   └── text_splitter/
│   │   │       ├── __init__.py
│   │   │       └── langchain_splitter.py # LangChainTextSplitter : TextSplitterPort
│   │   │
│   │   └── interfaces/                 # LAYER 3: Delivery — depends on application
│   │       ├── __init__.py
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   ├── router.py           # Aggregated API router
│   │       │   ├── chat.py             # POST /api/chat (thin controller)
│   │       │   ├── documents.py        # POST/GET/DELETE /api/documents
│   │       │   └── health.py           # GET /api/health
│   │       └── schemas/            # HTTP boundary models (Pydantic)
│   │           ├── __init__.py
│   │           ├── chat.py     # ChatRequest, ChatResponse
│   │           └── documents.py # DocumentUpload, DocumentInfo
│   │
│   ├── data/
│   │   ├── chroma_db/                  # ChromaDB persistence
│   │   └── uploads/                    # Raw uploaded files
│   ├── tests/
│   │   ├── domain/                     # Unit tests — pure entities, no mocks needed
│   │   ├── application/                # Unit tests — use cases with mocked ports
│   │   ├── infrastructure/             # Integration tests — real adapters
│   │   └── interfaces/                 # E2E tests — FastAPI TestClient
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── ChatMessage.vue
│   │   │   ├── ChatInput.vue
│   │   │   ├── DocumentUpload.vue
│   │   │   └── DocumentList.vue
│   │   ├── views/
│   │   │   └── ChatView.vue
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── assets/
│   │       └── styles/
│   │           └── main.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
└── docs/
    ├── API.md
    └── SETUP.md
```

---

## 4. Data Flow (Clean Architecture)

### 4.1 Chat Flow (AnswerQuestionUseCase)

```
┌──────────────────────────────────────────────────────────────────┐
│ INTERFACES (FastAPI Controller)                                   │
│                                                                   │
│  Post /api/chat  →  chat.py                                      │
│    │  parse ChatRequest Pydantic schema                           │
│    │  build AnswerQuestionInput DTO                               │
│    ▼                                                              │
│  calls AnswerQuestionUseCase.execute(input)                       │
│  returns StreamingResponse                                        │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│ APPLICATION (Use Case)                                             │
│                                                                   │
│  AnswerQuestionUseCase.execute(input)                              │
│    1. embedding: EmbeddingPort.embed([input.message])             │
│    2. vector_store: VectorStorePort.search(embedding, k=5)        │
│    3. Build prompt from retrieved chunks                          │
│    4. llm: LLMPort.generate(prompt) → async iterator              │
│    Returns: AsyncIterator[AnswerQuestionOutput]                    │
└──────┬──────────────────┬──────────────────┬─────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│ INFRASTRUCTURE│ │ INFRASTRUCTURE│ │ INFRASTRUCTURE    │
│ EmbeddingPort │ │ VectorStorPort│ │ LLMPort           │
│ (HuggingFace) │ │ (ChromaDB)   │ │ (Ollama)          │
│               │ │               │ │                   │
│ embed(texts)  │ │ search(embed) │ │ generate(prompt)  │
│ → 384-dim vec │ │ → top-k chunks│ │ → NDJSON tokens   │
└──────────────┘ └──────────────┘ └──────────────────┘
```

### 4.2 Document Ingestion Flow (IngestDocumentUseCase)

```
┌──────────────────────────────────────────────────────────────────┐
│ INTERFACES (FastAPI Controller)                                   │
│                                                                   │
│  POST /api/documents  →  documents.py                             │
│    │  parse multipart/form-data                                   │
│    │  build IngestDocumentInput DTO                               │
│    ▼                                                              │
│  calls IngestDocumentUseCase.execute(input)                       │
│  returns DocumentUploadResponse schema                            │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│ APPLICATION (Use Case)                                            │
│                                                                   │
│  IngestDocumentUseCase.execute(input)                             │
│    1. file_storage: FileStoragePort.save(filename, content)       │
│    2. loader: DocumentLoaderPort.load(path) → str                 │
│    3. splitter: TextSplitterPort.split(text) → list[str]          │
│    4. embedding: EmbeddingPort.embed(chunks) → list[vector]       │
│    5. vector_store: VectorStorePort.add_chunks(chunks)   │
│    6. doc_repo: DocumentRepositoryPort.save(Document entity)      │
│    Returns: IngestDocumentOutput                                  │
└──────┬─────────┬──────────┬──────────┬──────────┬────────────────┘
       │         │          │          │          │
       ▼         ▼          ▼          ▼          ▼
┌──────────┐ ┌──────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐
│FileStore │ │Loader│ │Splitter│ │Embedding │ │Vector Store  │
│(Local)   │ │(LC)  │ │(LC)    │ │(HF)       │ │(ChromaDB)   │
└──────────┘ └──────┘ └────────┘ └──────────┘ └──────────────┘
```

### 4.3 Dependency Rule Visualization

```
                     ┌─────────────────┐
                     │   interfaces/   │  ← Controllers, schemas
                     │  (FastAPI DTOs) │     depends on application
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │  application/   │  ← Use Cases, Ports
                     │  (business      │     depends on domain only
                     │   logic)        │
                     └──┬──────────┬───┘
                        │          │
            ┌───────────▼──┐  ┌────▼───────────┐
            │   domain/    │  │ infrastructure/ │  ← Adapters
            │  (entities)  │  │ (ChromaDB,      │     implements ports
            │  zero deps   │  │  Ollama, etc.)  │     from application
            └──────────────┘  └────────────────┘

Dependency direction: interfaces → application → domain ← infrastructure
(Infrastructure implements ports defined in application)
```

---

## 5. Port, Adapter & Use Case Map

### 5.1 Ports (Abstract Interfaces — `application/ports/`)

Each port defines what the application needs. Defined as an abstract class with `@abstractmethod`.

| Port | Responsibility | Key Methods | Default Adapter |
|------|---------------|-------------|-----------------|
| `EmbeddingPort` | Convert text(s) to vectors | `embed(texts) → list[list[float]]`, `health_check()` | `SentenceTransformerEmbedding` |
| `LLMPort` | Generate text from prompt | `generate(prompt) → AsyncIterator[str]`, `health_check()` | `OllamaLLM` |
| `VectorStorePort` | Store and search embeddings | `add_chunks()`, `search()`, `delete_by_document()`, `health_check()` | `ChromaDBVectorStore` |
| `DocumentLoaderPort` | Load file into raw text | `load(path) → str` | `LangChainDocumentLoader` |
| `TextSplitterPort` | Split text into chunks | `split(text) → list[str]` | `LangChainTextSplitter` |
| `FileStoragePort` | Save/delete raw files | `save(name, bytes) → path`, `delete(path)` | `LocalFileStorage` |
| `DocumentRepositoryPort` | Persist document metadata | `save(doc)`, `find_all()`, `find_by_id(id)`, `delete(id)` | `SQLiteDocumentRepository` |

### 5.2 Adapters (Concrete Implementations — `infrastructure/`)

LangChain lives **only** in the infrastructure layer, wrapped behind ports:

| Adapter | Implements | Wraps | Notes |
|---------|-----------|-------|-------|
| `ChromaDBVectorStore` | `VectorStorePort` | `chromadb.PersistentClient` | Embedded, no separate server |
| `SentenceTransformerEmbedding` | `EmbeddingPort` | `sentence_transformers` | all-MiniLM-L6-v2, 384-dim vectors |
| `OllamaLLM` | `LLMPort` | HTTP calls to `localhost:11434` | Streaming via NDJSON |
| `LangChainDocumentLoader` | `DocumentLoaderPort` | `UnstructuredMarkdownLoader`, `PyMuPDFLoader` | Routes by file extension |
| `LangChainTextSplitter` | `TextSplitterPort` | `RecursiveCharacterTextSplitter` | chunk_size=512, overlap=50 |
| `LocalFileStorage` | `FileStoragePort` | `pathlib`, `shutil` | Saves to `data/uploads/` |
| `SQLiteDocumentRepository` | `DocumentRepositoryPort` | `sqlite3` (stdlib) | Embedded, zero deps, relational integrity |

### 5.3 Use Cases (`application/use_cases/`)

Each use case is a class with dependencies injected via constructor. Only orchestrates port calls — zero infrastructure imports.

| Use Case | Dependencies (ports) | Orchestrates |
|----------|---------------------|-------------|
| `IngestDocumentUseCase` | FileStorage + DocLoader + TextSplitter + Embedding + VectorStore + DocRepo | Upload → Load → Split → Embed → Store |
| `AnswerQuestionUseCase` | Embedding + VectorStore + LLM | Embed → Search → Prompt → Generate |
| `ListDocumentsUseCase` | DocumentRepository | List all indexed documents |
| `DeleteDocumentUseCase` | VectorStore + DocRepo + FileStorage | Delete chunks + metadata + file |
| `HealthCheckUseCase` | LLM + VectorStore + Embedding | Verify all adapters healthy |

### 5.4 Prompt Template

```
You are Vector Vault, a personal knowledge assistant. Answer the user's question based only on the following context from their personal documents. If the context doesn't contain enough information, say so honestly.

Context:
{context}

Question: {question}

Answer:
```

### 5.5 LangChain Isolation Strategy

LangChain is a framework dependency — in Clean Architecture, frameworks belong in the infrastructure layer only. All LangChain code is wrapped behind ports so the business logic never imports it.

```
✅ CORRECT — LangChain only in infrastructure
  application/ports/document_loader.py  →  DocumentLoaderPort (abstract)
  infrastructure/document_loaders/langchain_loader.py  →  LangChainDocumentLoader (concrete)

  # Use case code:
  def __init__(self, loader: DocumentLoaderPort):  # knows nothing about LangChain
      self._loader = loader

❌ WRONG — LangChain leaking into application
  application/use_cases/ingest_document.py  →  from langchain import PyMuPDFLoader
```

**Why this matters:**
- Swap LangChain for something else (naive loaders, custom PDF parser) without touching use cases
- Unit test use cases with a fake loader that returns canned text
- LangChain's version upgrades affect only the infrastructure adapter

---

## 6. API Design Summary

(See `docs/API.md` for full details.)

The REST contract is unchanged by Clean Architecture — only the internal implementation structure changes. Controllers live in `interfaces/api/` and are thin delegates to use cases.

| Method | Endpoint | Description | Interface Controller |
|--------|----------|-------------|---------------------|
| POST | `/api/chat` | Send message, get streamed RAG response | `interfaces/api/chat.py` |
| POST | `/api/documents` | Upload a document (.md, .pdf) | `interfaces/api/documents.py` |
| GET | `/api/documents` | List all uploaded documents | `interfaces/api/documents.py` |
| DELETE | `/api/documents/{doc_id}` | Delete a document and its embeddings | `interfaces/api/documents.py` |
| GET | `/api/health` | Health check (Ollama + ChromaDB status) | `interfaces/api/health.py` |

---

## 7. Configuration

All config via environment variables (with `.env` file support):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3.1` | Model name in Ollama |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | ChromaDB storage path |
| `CHROMA_COLLECTION_NAME` | `vector_vault_chunks` | Collection for vector chunks |
| `SQLITE_DB_PATH` | `./data/vault.db` | SQLite database path |
| `UPLOAD_DIR` | `./data/uploads` | Uploaded files storage |
| `CHUNK_SIZE` | `512` | Text splitter chunk size |
| `CHUNK_OVERLAP` | `50` | Text splitter overlap |
| `TOP_K` | `5` | Number of chunks to retrieve |
| `DISTANCE_THRESHOLD` | `0.7` | Minimum similarity distance |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum file upload size |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |

---

## 8. Dependencies

### Backend (`pyproject.toml`)

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

## 9. Dependency Injection & Composition Root

The `main.py` and `dependencies.py` files form the **composition root** — the single place where objects are created and wired together. This follows the "assemble at the boundaries, inject inward" principle.

### 9.1 Wiring Pattern

```python
# main.py — Composition Root
from app.config import get_settings
from app.infrastructure.vector_store.chromadb_adapter import ChromaDBVectorStore
from app.infrastructure.embedding.hf_sentence_adapter import SentenceTransformerEmbedding
from app.infrastructure.llm.ollama_adapter import OllamaLLM
from app.application.use_cases.ingest_document import IngestDocumentUseCase
from app.application.use_cases.answer_question import AnswerQuestionUseCase
# ... other imports

settings = get_settings()

# 1. Instantiate infrastructure (adapters)
vector_store = ChromaDBVectorStore(settings.chroma_persist_dir, settings.chroma_collection_name)
embedder = SentenceTransformerEmbedding(settings.embedding_model)
llm = OllamaLLM(settings.ollama_base_url, settings.ollama_model)
doc_repo = SQLiteDocumentRepository(settings.sqlite_db_path)
file_storage = LocalFileStorage(settings.upload_dir)
loader = LangChainDocumentLoader()
splitter = LangChainTextSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)

# 2. Instantiate use cases (inject adapters)
ingest_use_case = IngestDocumentUseCase(doc_repo, file_storage, loader, splitter, embedder, vector_store)
answer_use_case = AnswerQuestionUseCase(embedder, vector_store, llm)
list_use_case = ListDocumentsUseCase(doc_repo)
delete_use_case = DeleteDocumentUseCase(vector_store, doc_repo, file_storage)
health_use_case = HealthCheckUseCase(llm, vector_store, embedder)

# 3. Inject into FastAPI app
app = create_app(
    ingest_use_case, answer_use_case, list_use_case, delete_use_case, health_use_case
)
```

### 9.2 FastAPI DI Pattern

```python
# dependencies.py — FastAPI dependency providers

from typing import Callable, TypeVar, cast

_use_cases: dict[str, object] = {}

def register_use_cases(**kwargs) -> None:
    _use_cases.update(kwargs)

def get_use_case(use_case_class):
    """Returns a FastAPI Depends callable for a given use case class."""
    async def dependency():
        return _use_cases[use_case_class.__name__]
    return dependency

# Usage in controller:
# @router.post("/chat")
# async def chat(
#     body: ChatRequest,
#     answer_uc: AnswerQuestionUseCase = Depends(get_use_case(AnswerQuestionUseCase)),
# ):
#     ...
```

---

## 10. Development Phases

### Phase 0 — Scaffold

- [x] Project directory structure (all `__init__.py` files, package layout)
- [x] `config.py` with pydantic-settings
- [x] `pyproject.toml` dependencies with all packages added via uv add

### Phase 1 — Domain Layer (zero external deps)

- [x] `domain/documents.py` — Document entity, DocumentType enum, DocumentStatus enum
- [x] `domain/chunks.py` — Chunk entity, SearchResult value object
- [x] `domain/conversations.py` — Conversation, Message (skeleton for Phase 5)
- [x] `domain/exceptions.py` — Custom exception hierarchy (VectorVaultError, NotFoundError, etc.)

### Phase 2 — Application Layer (ports + use cases + DTOs)

- [x] `application/ports/` — All 7 abstract port interfaces
- [x] `application/dto/` — Input/output dataclasses for each use case
- [x] `application/use_cases/` — All 5 use case classes (constructor DI, no infrastructure imports)
- [x] **Unit tests for use cases** — mock all ports, verify orchestration logic

### Phase 3 — Infrastructure Layer (adapters)

- [x] `infrastructure/vector_store/chromadb_adapter.py` — ChromaDBVectorStore
- [x] `infrastructure/embedding/hf_sentence_adapter.py` — SentenceTransformerEmbedding
- [x] `infrastructure/llm/ollama_adapter.py` — OllamaLLM with SSE streaming
- [x] `infrastructure/document_loaders/langchain_loader.py` — LangChain wrapper
- [x] `infrastructure/text_splitter/langchain_splitter.py` — Text splitter wrapper
- [x] `infrastructure/file_storage/local_storage.py` — LocalFileStorage
- [x] `infrastructure/document_repo/sqlite_repository.py` — SQLiteDocumentRepository
- [x] **Integration tests for adapters** — verify real ChromaDB/Ollama connections

### Phase 4 — Interface Layer (controllers + schemas)

- [x] `interfaces/schemas/` — Pydantic request/response schemas (separate from domain)
- [x] `interfaces/api/chat.py` — Thin controller, delegates to AnswerQuestionUseCase
- [x] `interfaces/api/documents.py` — Thin controllers for upload/list/delete
- [x] `interfaces/api/health.py` — Health check endpoint
- [x] `interfaces/api/router.py` — Aggregated router
- [x] `dependencies.py` — FastAPI DI providers returning use case instances
- [x] `main.py` — Composition root: wire adapters → use cases → DI → start uvicorn
- [x] **E2E tests** — FastAPI TestClient with real adapters

### Phase 5 — Frontend

- [x] Vue 3 + Vite project scaffold
- [x] `api/client.ts` — Axios/fetch wrapper for backend
- [x] `components/ChatMessage.vue` — Single message bubble
- [x] `components/ChatInput.vue` — Message input bar with send
- [x] `components/DocumentUpload.vue` — Drag & drop file upload
- [x] `components/DocumentList.vue` — List uploaded documents
- [x] `views/ChatView.vue` — Main chat page
- [x] Streaming response rendering (parse SSE token by token)
- [x] Integration: End-to-end test with sample documents

### Phase 6 — Polish & Robustness

- [ ] Error handling and validation across all layers (exception definitions in `domain/exceptions.py` already in place)
- [ ] Document re-ingestion / update support
- [ ] Chat history persistence (SQLite or local JSON, via new `ConversationRepositoryPort`)
- [ ] Source citation in responses (which document/chunk, sent in SSE `done` event)
- [ ] Rate limiting / queue for LLM calls
- [ ] Dark mode / theming

### Phase 7 — Desktop App

- [ ] Tauri wrapper (Rust backend, webview frontend)
- [ ] System tray / background running
- [ ] Auto-start on login (optional)
- [ ] Native file dialogs via Tauri APIs

### Phase 8 — Hybrid UI (Document Browser)

- [ ] Document browser sidebar
- [ ] Document preview (markdown render, PDF viewer)
- [ ] Chunk highlighting in source documents
- [ ] Tag / folder organization for documents

---

## 11. WSL Development Notes

Since you're developing on WSL:

1. **Ollama** runs on the Windows side. Access it from WSL via `http://host.docker.internal:11434` or configure Ollama to listen on `0.0.0.0`.
2. **Frontend dev server** (Vite) runs fine on WSL. Access from Windows browser at `http://localhost:5173`.
3. **Backend** (FastAPI) runs fine on WSL. Access from Windows browser at `http://localhost:8000`.
4. **File storage**: Keep `data/` inside the WSL filesystem (not `/mnt/c/`) for performance.
5. **Hot reload**: Both Vite and uvicorn hot-reload work fine on WSL.

---

## 12. Key Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM quality too low for 8B model | Can swap to larger model; prompt engineering helps. Trivial to swap adapter. |
| ChromaDB doesn't scale to large corpus | ChromaDB handles 100K+ documents; behind `VectorStorePort`, switching to Qdrant means writing one new adapter. |
| Embedding model too small for domain | all-MiniLM is general-purpose; can swap to fine-tuned model by changing the adapter. |
| PDF parsing quality varies | PyMuPDF is best open-source option; `DocumentLoaderPort` allows fallback parsers. |
| WSL networking quirks with Ollama | Use `host.docker.internal` or run Ollama in WSL directly. `OllamaLLM` adapter takes a configurable URL. |
| Clean Architecture over-engineering for small app | The port/adapter abstraction adds files but prevents lock-in. MVP is small but the knowledge base grows; architecture stays solid. |
| LangChain API breaking changes | Only the `langchain_loader.py` and `langchain_splitter.py` adapters break. Use cases and domain are unaffected. |
| Sprint slowdown from extra abstraction | Each adapter is a thin wrapper (~30-50 lines). The real work is in use cases. Abstraction cost is low, refactoring cost avoided is high. |