from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator
from app.config import get_settings
from app.domain.documents import DocumentType, DocumentStatus

class DocumentUploadRequest(BaseModel):
    title: str = Field(default="", max_length=100)
    document: UploadFile
    model_config = {"extra": "forbid"}

    @field_validator('document', mode='after')
    @classmethod
    def document_validation(cls, value: UploadFile):
        # empty filename validation
        if value.filename is None:
            raise ValueError("Empty filename")
        
        # max file size validation
        max_size = get_settings().max_upload_size_mb * 1024 * 1024

        if value.size is None:
            raise ValueError("Unable to determine file size")
        if value.size > max_size:
            raise ValueError(f"File exceeds {get_settings().max_upload_size_mb} MB limit")
        return value

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: DocumentType
    title: str | None
    status: DocumentStatus