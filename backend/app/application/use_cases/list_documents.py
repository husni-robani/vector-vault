from ports import DocumentRepositoryPort
from domain.documents import Document
class ListDocumentUseCase:
    def __init__(self, document_repo: DocumentRepositoryPort) -> None:
        self._document_repo: DocumentRepositoryPort = document_repo

    def execute(self) -> list[Document]: 

        documents: list[Document] = self._document_repo.find_all()

        return documents