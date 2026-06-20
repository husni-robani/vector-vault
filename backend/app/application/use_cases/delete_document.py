import logging

from app.application.ports import (
    DocumentRepositoryPort,
    VectorStorePort,
    FileStoragePort,
)
from app.domain.documents import Document
from app.domain.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class DeleteDocumentUseCase:
    def __init__(
        self,
        document_repo: DocumentRepositoryPort,
        vector_store: VectorStorePort,
        file_storage: FileStoragePort,
    ) -> None:
        self._document_repo: DocumentRepositoryPort = document_repo
        self._vector_store: VectorStorePort = vector_store
        self._file_storage: FileStoragePort = file_storage

    def execute(self, doc_id: str):
        document: Document | None = self._document_repo.find_by_id(doc_id)
        if document is None:
            logger.warning("Delete failed: document %s not found", doc_id)
            raise NotFoundError(f"Document {doc_id} not found")

        # delete data in sqlite
        self._document_repo.delete(document.id)

        # delete all related chunks in chromadb
        self._vector_store.delete_by_document(document.id)

        # delete the file
        self._file_storage.delete(document.file_path)
