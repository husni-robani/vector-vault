import logging

from app.application.dto import ListDocumentsInput, ListDocumentsOutput
from app.application.ports import DocumentRepositoryPort
from app.domain.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class ListDocumentsUseCase:
    def __init__(self, document_repo: DocumentRepositoryPort) -> None:
        self._document_repo: DocumentRepositoryPort = document_repo

    def execute(self, input_dto: ListDocumentsInput) -> ListDocumentsOutput:
        try:
            docs, total = self._document_repo.find_all(
                page=input_dto.page,
                limit=input_dto.limit,
            )
        except Exception as e:
            logger.exception("Failed to list documents")
            raise ExternalServiceError("Failed to list documents") from e

        return ListDocumentsOutput(
            documents=docs,
            total=total,
            page=input_dto.page,
            limit=input_dto.limit,
        )
