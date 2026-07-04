from functools import lru_cache
from pathlib import Path

from app.application import use_cases
from app.config import get_settings
from app.infrastructure import (
    ChromaDBVectorStore,
    LangChainDocumentLoader,
    LangChainTextSplitter,
    LocalFileStorage,
    OllamaLLM,
    SentenceTransformerEmbedding,
    SQLiteDocumentRepository,
)

settings = get_settings()

# ---------------------------------------------------------------------------
# Adapter singletons (shared across use cases that need the same adapter)
# ---------------------------------------------------------------------------


@lru_cache
def _get_document_repo() -> SQLiteDocumentRepository:
    return SQLiteDocumentRepository(settings.sqlite_db_path)


@lru_cache
def _get_embedder() -> SentenceTransformerEmbedding:
    return SentenceTransformerEmbedding(settings.embedding_model)


@lru_cache
def _get_file_storage() -> LocalFileStorage:
    return LocalFileStorage(Path(settings.upload_dir))


@lru_cache
def _get_vector_store() -> ChromaDBVectorStore:
    return ChromaDBVectorStore(
        persist_directory=settings.chroma_persist_dir,
        collection_name=settings.chroma_collection_name,
    )


@lru_cache
def _get_llm() -> OllamaLLM:
    return OllamaLLM(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )


@lru_cache
def _get_document_loader() -> LangChainDocumentLoader:
    return LangChainDocumentLoader()


@lru_cache
def _get_text_splitter() -> LangChainTextSplitter:
    return LangChainTextSplitter()


# ---------------------------------------------------------------------------
# Use case factories (public API)
# ---------------------------------------------------------------------------


@lru_cache
def get_ingest_document_use_case() -> use_cases.IngestDocumentUseCase:
    return use_cases.IngestDocumentUseCase(
        doc_loader=_get_document_loader(),
        doc_repo=_get_document_repo(),
        embedder=_get_embedder(),
        file_storage=_get_file_storage(),
        splitter=_get_text_splitter(),
        vector_store=_get_vector_store(),
    )


@lru_cache
def get_answer_question_use_case() -> use_cases.AnswerQuestionUseCase:
    return use_cases.AnswerQuestionUseCase(
        embedder=_get_embedder(),
        llm=_get_llm(),
        vector_store=_get_vector_store(),
    )


@lru_cache
def get_list_documents_use_case() -> use_cases.ListDocumentsUseCase:
    return use_cases.ListDocumentsUseCase(
        document_repo=_get_document_repo(),
    )


@lru_cache
def get_delete_document_use_case() -> use_cases.DeleteDocumentUseCase:
    return use_cases.DeleteDocumentUseCase(
        document_repo=_get_document_repo(),
        vector_store=_get_vector_store(),
        file_storage=_get_file_storage(),
    )


@lru_cache
def get_health_check_use_case() -> use_cases.HealthCheckUseCase:
    return use_cases.HealthCheckUseCase(
        llm=_get_llm(),
        vector_store=_get_vector_store(),
        embedder=_get_embedder(),
    )
