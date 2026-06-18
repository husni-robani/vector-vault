from app.application.ports import DocumentRepositoryPort
from app.domain.documents import Document


class ListDocumentsUseCase:
    def __init__(self, document_repo: DocumentRepositoryPort) -> None:
        self._document_repo: DocumentRepositoryPort = document_repo

    def execute(self) -> list[Document]:

        documents: list[Document] = self._document_repo.find_all()

        return documents
