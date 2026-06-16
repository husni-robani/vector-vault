from enum import StrEnum
from dataclasses import dataclass
from pathlib import Path

class DocumentType(StrEnum):
    MD = ".md"
    PDF = ".pdf"

    @classmethod
    def from_filename(cls, filename: str) -> "DocumentType":
        ext = Path(filename).suffix.lower()
        try:
            return cls(ext)
        except ValueError as e:
            raise ValueError(f"Unsupported file type: {ext}") from e

class DocumentStatus(StrEnum): 
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"

@dataclass
class Document:
    id: str # uuid
    title: str
    filename: str
    file_path: str
    file_type: DocumentType
    status: DocumentStatus
    created_at: str
    updated_at: str