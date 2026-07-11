import shutil
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.dto import EmbeddingHealth, LLMHealth
from app.application.ports import EmbeddingPort, LLMPort
from app.config import Settings
from app.dependencies import Container
from app.infrastructure import (
    ChromaDBVectorStore,
    LangChainDocumentLoader,
    LangChainTextSplitter,
    LocalFileStorage,
    SQLiteDocumentRepository,
)
from app.interfaces.api.router import api_router
from app.interfaces.api.exception_handlers import register_exception_handlers

# ===========================================================================
# Stubs — replace external services so E2E tests need zero network / models
# ===========================================================================


class StubEmbedder(EmbeddingPort):
    """Returns fixed 384-dim vectors.  No model download, no GPU."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.01 * (i + j) for j in range(384)] for i in range(len(texts))]

    def health_check(self) -> EmbeddingHealth:
        return EmbeddingHealth(connected=True, model_name="stub-embedder", error=None)


class StubLLM(LLMPort):
    """Returns a trivial token stream.  No Ollama server needed."""

    async def generate(self, prompt: str) -> AsyncIterator[str]:
        for word in ["This", " is", " a", " stub", " answer."]:
            yield word

    def health_check(self) -> LLMHealth:
        return LLMHealth(
            connected=True, model="stub-llm", model_loaded=True, error=None
        )


# ===========================================================================
# Test container builder — mirrors production build() but uses stubs
# ===========================================================================


def _build_test_container(s: Settings) -> Container:
    """
    Same shape as production `build()`, but OLlama and SentenceTransformer
    are replaced with in-process stubs.  SQLite, ChromaDB, and file storage
    run against real temp directories — so the full I/O pipeline is exercised.
    """

    @lru_cache
    def _get_document_repo() -> SQLiteDocumentRepository:
        return SQLiteDocumentRepository(s.sqlite_db_path)

    @lru_cache
    def _get_embedder() -> StubEmbedder:
        return StubEmbedder()

    @lru_cache
    def _get_file_storage() -> LocalFileStorage:
        return LocalFileStorage(Path(s.upload_dir))

    @lru_cache
    def _get_vector_store() -> ChromaDBVectorStore:
        return ChromaDBVectorStore(
            persist_directory=s.chroma_persist_dir,
            collection_name=s.chroma_collection_name,
        )

    @lru_cache
    def _get_llm() -> StubLLM:
        return StubLLM()

    @lru_cache
    def _get_document_loader() -> LangChainDocumentLoader:
        return LangChainDocumentLoader()

    @lru_cache
    def _get_text_splitter() -> LangChainTextSplitter:
        return LangChainTextSplitter()

    from app.application import use_cases

    def get_ingest_document_use_case() -> use_cases.IngestDocumentUseCase:
        return use_cases.IngestDocumentUseCase(
            doc_loader=_get_document_loader(),
            doc_repo=_get_document_repo(),
            embedder=_get_embedder(),
            file_storage=_get_file_storage(),
            splitter=_get_text_splitter(),
            vector_store=_get_vector_store(),
        )

    def get_answer_question_use_case() -> use_cases.AnswerQuestionUseCase:
        return use_cases.AnswerQuestionUseCase(
            embedder=_get_embedder(),
            llm=_get_llm(),
            vector_store=_get_vector_store(),
        )

    def get_list_documents_use_case() -> use_cases.ListDocumentsUseCase:
        return use_cases.ListDocumentsUseCase(
            document_repo=_get_document_repo(),
        )

    def get_delete_document_use_case() -> use_cases.DeleteDocumentUseCase:
        return use_cases.DeleteDocumentUseCase(
            document_repo=_get_document_repo(),
            vector_store=_get_vector_store(),
            file_storage=_get_file_storage(),
        )

    def get_health_check_use_case() -> use_cases.HealthCheckUseCase:
        return use_cases.HealthCheckUseCase(
            llm=_get_llm(),
            vector_store=_get_vector_store(),
            embedder=_get_embedder(),
        )

    def close() -> None:
        if _get_document_repo.cache_info().misses > 0:
            _get_document_repo().close()

    return Container(
        ingest_document_usecase=get_ingest_document_use_case,
        answer_question_usecase=get_answer_question_use_case,
        list_documents_usecase=get_list_documents_use_case,
        delete_document_usecase=get_delete_document_use_case,
        health_check_usecase=get_health_check_use_case,
        document_repo=_get_document_repo,
        vector_store=_get_vector_store,
        file_storage=_get_file_storage,
        embedder=_get_embedder,
        llm=_get_llm,
        document_loader=_get_document_loader,
        text_splitter=_get_text_splitter,
        close=close,
    )


# ===========================================================================
# App builder — shared by all client fixtures
# ===========================================================================


def _build_app(container: Container) -> FastAPI:
    """Assemble a FastAPI app wired to *container*, with lifespan & routes."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        container.close()

    app = FastAPI(lifespan=lifespan)
    app.state.container = container

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def client():
    """
    Return a TestClient wired to a fully isolated FastAPI app.

    Every test gets:
      - its own temporary directory
      - its own SQLite database   (real, temp)
      - its own ChromaDB instance (real, temp)
      - its own file storage      (real, temp)
      - stubbed LLM & embedder    (no network / no model downloads)

    When the test finishes, everything is torn down automatically.
    """
    tmp = Path(tempfile.mkdtemp())

    test_settings = Settings(
        sqlite_db_path=str(tmp / "test.db"),
        chroma_persist_dir=str(tmp / "chroma"),
        chroma_collection_name="e2e_test_collection",
        upload_dir=str(tmp / "uploads"),
        chunk_size=256,
        chunk_overlap=25,
    )

    container = _build_test_container(test_settings)
    app = _build_app(container)

    with TestClient(app) as c:
        yield c

    container.close()
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def client_small_max_upload():
    """
    Same as `client` but max upload size is effectively zero bytes.

    Uses a separate temp directory and patches the schema module's
    get_settings() so the Pydantic validator rejects any non-empty file.
    """
    from unittest.mock import patch

    tmp = Path(tempfile.mkdtemp())

    test_settings = Settings(
        sqlite_db_path=str(tmp / "test.db"),
        chroma_persist_dir=str(tmp / "chroma"),
        chroma_collection_name="e2e_test_collection_small",
        upload_dir=str(tmp / "uploads"),
        chunk_size=256,
        chunk_overlap=25,
        max_upload_size_mb=0,
    )

    container = _build_test_container(test_settings)
    app = _build_app(container)

    with patch(
        "app.interfaces.schemas.documents.get_settings",
        return_value=test_settings,
    ):
        with TestClient(app) as c:
            yield c

    container.close()
    shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# Sample file fixtures
# ===========================================================================

_MINIMAL_PDF_CONTENT = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
    b"/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
    b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    b"5 0 obj<</Length 44>>stream\n"
    b"BT /F1 12 Tf 100 700 Td (Hello PDF) Tj ET\n"
    b"endstream endobj\n"
    b"xref 0 6\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"0000000247 00000 n \n"
    b"0000000326 00000 n \n"
    b"trailer<</Size 6/Root 1 0 R>>\n"
    b"startxref\n414\n%%EOF"
)


@pytest.fixture
def sample_md_bytes():
    return b"# Hello\n\nThis is a test document.\n\n## Section\n\nContent here."


@pytest.fixture
def sample_md_file(sample_md_bytes, tmp_path):
    path = tmp_path / "sample.md"
    path.write_bytes(sample_md_bytes)
    return path


@pytest.fixture
def sample_pdf_bytes():
    return _MINIMAL_PDF_CONTENT


@pytest.fixture
def sample_pdf_file(sample_pdf_bytes, tmp_path):
    path = tmp_path / "sample.pdf"
    path.write_bytes(sample_pdf_bytes)
    return path
