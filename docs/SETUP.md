# Vector Vault — Setup & Configuration Guide

> **Architecture:** The backend follows Clean Architecture (Ports & Adapters). Layers from inner to outer: `domain/` (entities) → `application/` (use cases, ports) → `infrastructure/` (adapters) → `interfaces/` (API controllers). The entry point `main.py` is the composition root where all dependencies are wired together. See `PROJECT_PLAN.md` for the full architecture guide.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | `sudo apt install python3.11` |
| Node.js | 18+ | `nvm install 18` or `sudo apt install nodejs` |
| Ollama | Latest | See below |
| Git | 2.40+ | `sudo apt install git` |

---

## 1. Install Ollama

### Option A: Run Ollama on Windows (recommended for WSL users)

1. Download from [ollama.com](https://ollama.com) and install on **Windows**
2. Ollama starts as a Windows service on port 11434
3. From WSL, it's accessible at `http://localhost:11434` (WSL2 port forwarding)
4. Pull the model:

```bash
# Run this in WSL — it will reach Ollama on Windows
curl http://localhost:11434/api/pull -d '{"name":"llama3.1"}'
```

Or open PowerShell on Windows and run:

```powershell
ollama pull llama3.1
```

5. Verify from WSL:

```bash
curl http://localhost:11434/api/tags
```

### Option B: Run Ollama inside WSL

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.1
```

### Troubleshooting WSL ↔ Ollama Connectivity

If `localhost:11434` doesn't work from WSL:

```bash
# Find Windows host IP from WSL
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
# Use that IP, e.g.:
# http://172.x.x.x:11434
```

Set this in your `.env` file:

```
OLLAMA_BASE_URL=http://172.x.x.x:11434
```

---

## 2. Backend Setup

```bash
cd vector-vault/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/chroma_db data/uploads

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### `.env.example`

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ChromaDB Configuration
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=vector_vault_chunks
CHROMA_META_COLLECTION=vector_vault_docs

# Upload Configuration
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE_MB=50

# RAG Configuration
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
SCORE_THRESHOLD=0.7

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173

# First run will download the embedding model (~80MB)
```

### Run the backend

```bash
# Development (with hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Project Layer Reference

When navigating the codebase, use this map:

| Directory | What lives here | Depends on |
|-----------|----------------|------------|
| `app/domain/` | Document, Chunk entities | Nothing |
| `app/application/ports/` | Abstract interfaces (ABCs) | domain |
| `app/application/use_cases/` | Business logic orchestrators | ports + domain |
| `app/application/dto/` | Use case input/output (dataclasses) | Nothing |
| `app/infrastructure/` | Concrete adapters (ChromaDB, Ollama, LangChain) | ports (implements them) |
| `app/interfaces/api/` | FastAPI route handlers (thin controllers) | use_cases |
| `app/interfaces/serializers/` | Pydantic request/response schemas | Nothing |
| `app/main.py` | Composition root (DI assembly) | Everything |
| `app/dependencies.py` | FastAPI DI providers | use_cases |
| `tests/domain/` | Entity unit tests | domain |
| `tests/application/` | Use case tests (mock ports) | use_cases |
| `tests/infrastructure/` | Adapter integration tests | adapters |
| `tests/interfaces/` | E2E API tests | FastAPI app |

### Running Tests by Layer

```bash
cd vector-vault/backend
pip install pytest pytest-asyncio

# Unit tests (domain) — no external deps, always fast
pytest tests/domain/

# Unit tests (application) — mock all ports, fast
pytest tests/application/

# Integration tests (infrastructure) — needs real ChromaDB & Ollama
pytest tests/infrastructure/

# E2E tests (interfaces) — full FastAPI test client
pytest tests/interfaces/

# Run all
pytest
```

The API docs will be available at: `http://localhost:8000/docs` (Swagger UI)

---

## 3. Frontend Setup

```bash
cd vector-vault/frontend

# Install dependencies
npm install

# Development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

## 4. Verify Everything Works

### Check backend health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "ollama": { "connected": true, "model": "llama3.1", "model_loaded": true },
  "chromadb": { "connected": true },
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### Upload a test document

```bash
curl -X POST http://localhost:8000/api/documents \
  -F "file=@test.md"
```

### Send a test chat message

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is in my documents?"}'
```

The `-N` flag disables buffering so you see streamed tokens.

---

## 5. Configuration Details

### Embedding Model

The `all-MiniLM-L6-v2` model downloads automatically on first use (~80MB). It produces 384-dimensional vectors.

Alternative models (change `EMBEDDING_MODEL` in `.env`):

| Model | Dimensions | Size | Context | Notes |
|-------|-----------|------|---------|-------|
| all-MiniLM-L6-v2 | 384 | 80MB | 256 | Default, fast, good quality |
| all-mpnet-base-v2 | 768 | 420MB | 384 | Higher quality, slower |
| nomic-embed-text | 768 | 270MB | 8192 | Best for long documents |

If you change the embedding model, you **must** re-index all documents (delete ChromaDB data and re-upload).

### LLM Model

Change `OLLAMA_MODEL` in `.env` to any model available in Ollama:

```bash
# List available models
ollama list

# Pull a different model
ollama pull mistral
```

Recommended 8B-class models:

| Model | RAM (Q4) | Quality | Notes |
|-------|----------|---------|-------|
| llama3.1 | ~5GB | Best | Default recommendation |
| mistral | ~4.5GB | Good | Fast, good instruction following |
| qwen2.5:7b | ~4.5GB | Good | Strong multilingual |
| phi3:mini | ~2.5GB | Decent | If RAM constrained |

### Chunking Parameters

- `CHUNK_SIZE=512`: Number of characters per chunk. Smaller = more precise retrieval but less context per chunk. Larger = more context but noisier retrieval.
- `CHUNK_OVERLAP=50`: Characters overlapping between chunks. Prevents losing context at chunk boundaries.
- `TOP_K=5`: Number of chunks retrieved per query. More = more context but slower and noisier.
- `SCORE_THRESHOLD=0.7`: Minimum similarity score. Lower = more results but less relevant.

---

## 6. WSL-Specific Tips

### File Storage Performance

Keep the `data/` directory inside the WSL filesystem (**not** under `/mnt/c/`). WSL filesystem I/O is significantly faster than cross-filesystem access.

```
✅ /home/bani/dev/projects/vector-vault/backend/data/
❌ /mnt/c/Users/.../vector-vault/backend/data/
```

### Running Both Servers

Use two terminal tabs/sessions:

```bash
# Terminal 1 — Backend
cd vector-vault/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd vector-vault/frontend
npm run dev
```

### GPU Acceleration (Optional)

If you have an NVIDIA GPU and want faster inference:

1. Install CUDA on Windows: [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
2. Ollama on Windows automatically uses GPU if available
3. For embedding model GPU support in WSL:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| `ConnectionRefusedError` to Ollama | Check Ollama is running; verify URL in `.env`; check WSL networking |
| Embedding model download fails | Check internet; `pip install sentence-transformers` manually |
| ChromaDB permission error | `chmod -R 755 data/chroma_db` |
| Out of memory during LLM call | Switch to smaller model or reduce `TOP_K` |
| PDF parsing errors | Ensure `pymupdf` is installed: `pip install pymupdf` |
| Frontend can't reach backend | Check CORS config; verify both servers running |