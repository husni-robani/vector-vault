from dataclasses import dataclass
from app.domain.documents import DocumentType, DocumentStatus
@dataclass
class IngestDocumentInput:
    filename: str
    title: str
    content: bytes
    content_type: DocumentType

@dataclass
class IngestDocumentOutput:
    id: str     # document id
    filename: str
    file_type: DocumentType
    title: str
    status: DocumentStatus 
