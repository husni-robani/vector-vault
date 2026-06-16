from ports import DocumentRepositoryPort, VectorStorePort, FileStoragePort
from domain.documents import Document

class DeleteDocumentUseCase: 
    def __init__(self, document_repo: DocumentRepositoryPort, vector_store: VectorStorePort, file_storage: FileStoragePort) -> None:
        self._document_repo: DocumentRepositoryPort = document_repo
        self._vector_store: VectorStorePort = vector_store
        self._file_storage: FileStoragePort = file_storage
    
    def execute(self, doc_id:str):
        document: Document | None = self._document_repo.find_by_id(doc_id)
        if document is None:
            raise ValueError(f"Document {doc_id} not found")
        
        # delete data in sqlite
        self._document_repo.delete(document.id)

        # delete all related chunks in chromadb
        self._vector_store.delete_by_document(document.id)

        # delete the file
        self._file_storage.delete(document.file_path)