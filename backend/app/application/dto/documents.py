from dataclasses import dataclass
from app.domain.documents import Document, DocumentType, DocumentStatus


@dataclass
class IngestDocumentInput:
    filename: str
    title: str
    content: bytes
    content_type: DocumentType


@dataclass
class IngestDocumentOutput:
    id: str  # document id
    filename: str
    file_type: DocumentType
    title: str
    status: DocumentStatus


@dataclass
class ListDocumentsInput:
    page: int = 1
    limit: int = 50


@dataclass
class ListDocumentsOutput:
    documents: list[Document]
    total: int
    page: int
    limit: int
