from enum import StrEnum
from dataclasses import dataclass

class DocumentType(StrEnum):
    MD = ".md"
    PDF = ".pdf"

class DocumentStatus(StrEnum): 
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"

@dataclass
class Document:
    id: str # uuid
    title: str
    filename: str
    file_type: DocumentType
    status: DocumentStatus
    created_at: str
    updated_at: str