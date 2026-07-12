from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

from app.application import use_cases
from app.application.ports import (
    DocumentLoaderPort,
    DocumentRepositoryPort,
    EmbeddingPort,
    FileStoragePort,
    LLMPort,
    TextSplitterPort,
    VectorStorePort,
)
from app.config import Settings
from app.infrastructure import (
    ChromaDBVectorStore,
    LangChainDocumentLoader,
    LangChainTextSplitter,
    LocalFileStorage,
    OllamaLLM,
    SentenceTransformerEmbedding,
    SQLiteDocumentRepository,
)


@dataclass(frozen=True)
class Container:
    """Factory functions for every use case, plus a close() hook."""

    ingest_document_usecase: Callable[[], use_cases.IngestDocumentUseCase]
    answer_question_usecase: Callable[[], use_cases.AnswerQuestionUseCase]
    list_documents_usecase: Callable[[], use_cases.ListDocumentsUseCase]
    delete_document_usecase: Callable[[], use_cases.DeleteDocumentUseCase]
    health_check_usecase: Callable[[], use_cases.HealthCheckUseCase]
    document_repo: Callable[[], DocumentRepositoryPort]
    vector_store: Callable[[], VectorStorePort]
    file_storage: Callable[[], FileStoragePort]
    embedder: Callable[[], EmbeddingPort]
    llm: Callable[[], LLMPort]
    document_loader: Callable[[], DocumentLoaderPort]
    text_splitter: Callable[[], TextSplitterPort]
    close: Callable[[], None]


def build(s: Settings) -> Container:
    """Pure function — zero side effects, zero framework imports.
    Every call returns an independent, fully-wired Container."""

    # ------------------------------------------------------------------
    # Adapter singletons (shared across use cases in THIS container)
    # ------------------------------------------------------------------

    @lru_cache
    def _get_document_repo() -> SQLiteDocumentRepository:
        return SQLiteDocumentRepository(s.sqlite_db_path)

    @lru_cache
    def _get_embedder() -> SentenceTransformerEmbedding:
        return SentenceTransformerEmbedding(s.embedding_model)

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
    def _get_llm() -> OllamaLLM:
        return OllamaLLM(
            base_url=s.ollama_base_url,
            model=s.ollama_model,
        )

    @lru_cache
    def _get_document_loader() -> LangChainDocumentLoader:
        return LangChainDocumentLoader()

    @lru_cache
    def _get_text_splitter() -> LangChainTextSplitter:
        return LangChainTextSplitter()

    # ------------------------------------------------------------------
    # Use case factories
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Shutdown helper
    # ------------------------------------------------------------------

    def close() -> None:
        for factory in [_get_document_repo]:
            if factory.cache_info().misses > 0:
                instance = factory()
                if hasattr(instance, "close"):
                    instance.close()

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
