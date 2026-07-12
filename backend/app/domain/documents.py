from enum import StrEnum
from dataclasses import dataclass
from pathlib import Path

from app.domain.exceptions import UnsupportedFileTypeError


class DocumentType(StrEnum):
    MD = "text/markdown"
    PDF = "application/pdf"

    @classmethod
    def from_filename(cls, filename: str) -> "DocumentType":
        ext = Path(filename).suffix.lower()

        match ext:
            case ".pdf":
                return cls.PDF
            case ".md":
                return cls.MD
            case _:
                raise UnsupportedFileTypeError(f"Unsupported file type: {ext}")

    @property
    def extension(self) -> str:
        match self:
            case DocumentType.MD:
                return ".md"
            case DocumentType.PDF:
                return ".pdf"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"


@dataclass
class Document:
    id: str  # uuid
    title: str
    filename: str
    file_path: str
    file_type: DocumentType
    status: DocumentStatus
    chunks_count: int
    size_bytes: int
    created_at: str
    updated_at: str
