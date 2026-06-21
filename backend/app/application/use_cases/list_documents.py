import logging

from app.application.ports import DocumentRepositoryPort
from app.domain.documents import Document
from app.domain.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class ListDocumentsUseCase:
    def __init__(self, document_repo: DocumentRepositoryPort) -> None:
        self._document_repo: DocumentRepositoryPort = document_repo

    def execute(self) -> list[Document]:
        try:
            documents: list[Document] = self._document_repo.find_all()
        except Exception as e:
            logger.exception("Failed to list documents")
            raise ExternalServiceError("Failed to list documents") from e

        return documents
