# Changelog

All notable changes to Vector Vault will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.5.0] - 2026-07-12

### Added
- Interface layer: all API controllers and schemas (Phase 4)
  - `interfaces/api/chat.py` — thin controller delegating to AnswerQuestionUseCase
  - `interfaces/api/documents.py` — thin controllers for document upload, list, and delete
  - `interfaces/api/health.py` — health check endpoint
  - `interfaces/api/router.py` — aggregated `/api` router
  - `interfaces/api/exception_handlers.py` — domain exception → HTTP status mapping
  - `interfaces/schemas/` — Pydantic request/response schemas (chat, documents, health, response)
- Composition root (`main.py`) wiring adapters → use cases → DI → uvicorn
- FastAPI DI container (`dependencies.py`) with lazy service factory pattern
- E2E tests with FastAPI TestClient using stub LLM/embedder and real SQLite/ChromaDB/file storage
- `Makefile` for common dev tasks (run, test, lint, clean)

## [v0.4.0] - 2026-06-28

### Added
- Infrastructure layer: all 7 adapter implementations (Phase 3)
  - `ChromaDBVectorStore` — embedded vector store via ChromaDB PersistentClient
  - `SentenceTransformerEmbedding` — text embedding via all-MiniLM-L6-v2
  - `OllamaLLM` — LLM generation via Ollama REST API with SSE streaming
  - `LangChainDocumentLoader` — file loading routed by extension (.md, .pdf)
  - `LangChainTextSplitter` — recursive character text splitting
  - `LocalFileStorage` — local filesystem storage in `data/uploads/`
  - `SQLiteDocumentRepository` — document metadata persistence via sqlite3
- Integration tests for all infrastructure adapters

## [v0.3.0] - 2026-06-15

### Added
- Application layer: all 7 abstract port interfaces (Phase 2)
- All 5 use case classes with constructor DI
- Input/output DTO dataclasses for each use case
- Unit tests for use cases with mocked ports

## [v0.2.0] - 2026-06-08

### Added
- Domain layer: entities and value objects (Phase 1)
  - `Document` entity, `DocumentType` and `DocumentStatus` enums
  - `Chunk` entity, `SearchResult` value object
  - `Conversation` and `Message` skeleton
- Custom exception hierarchy

## [v0.1.0] - 2026-06-02

### Added
- Project scaffold (directory structure, configuration, dependencies)
