import logging
from fastapi import APIRouter, Form
from typing import Annotated
from app.application.dto import IngestDocumentInput
from app.domain.documents import DocumentType
from app.interfaces.schemas import SuccessResponse, DocumentUploadRequest, DocumentUploadResponse 
from app.interfaces.dependencies import ContainerDep
from app.application.use_cases import IngestDocumentUseCase

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()


@router.post("/documents")
def upload_document(
    body: Annotated[DocumentUploadRequest, Form()], 
    container: ContainerDep
):
    ingest_document_usecase: IngestDocumentUseCase = container.ingest_document_usecase()

    file_bytes: bytes = body.document.file.read()

    assert body.document.filename is not None

    document_data = IngestDocumentInput(
        filename=body.document.filename,
        title=body.title,
        content=file_bytes,
        content_type=DocumentType(body.document.content_type),
    )

    result = ingest_document_usecase.execute(document_dto=document_data)

    return SuccessResponse(
        message="Upload document success",
        data=DocumentUploadResponse(
            document_id=result.id,
            filename=result.filename,
            file_type=result.file_type,
            title=result.title,
            status=result.status,
        ),
    )
