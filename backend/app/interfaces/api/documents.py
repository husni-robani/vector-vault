import logging
from fastapi import APIRouter, Form, Query
from typing import Annotated
from app.application.dto import (
    IngestDocumentInput,
    ListDocumentsInput,
    ListDocumentsOutput,
)
from app.domain.documents import DocumentType
from app.interfaces.schemas import (
    SuccessResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    DocumentInfo,
    DocumentListResponse,
)
from app.interfaces.dependencies import ContainerDep
from app.application.use_cases import (
    IngestDocumentUseCase,
    ListDocumentsUseCase,
    DeleteDocumentUseCase,
)

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()


@router.get("/documents")
def list_documents(
    container: ContainerDep,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    list_usecase: ListDocumentsUseCase = container.list_documents_usecase()
    input_dto = ListDocumentsInput(page=page, limit=limit)
    result: ListDocumentsOutput = list_usecase.execute(input_dto)

    return SuccessResponse(
        message="Documents retrieved successfully",
        data=DocumentListResponse(
            documents=[DocumentInfo.model_validate(doc) for doc in result.documents],
            total=result.total,
            page=result.page,
            limit=result.limit,
        ),
    )


@router.post("/documents")
def upload_document(
    body: Annotated[DocumentUploadRequest, Form()], container: ContainerDep
):
    ingest_document_usecase: IngestDocumentUseCase = container.ingest_document_usecase()

    file_bytes: bytes = body.document.file.read()

    assert body.document.filename is not None

    document_data = IngestDocumentInput(
        filename=body.document.filename,
        title=body.title,
        content=file_bytes,
        content_type=DocumentType(DocumentType.from_filename(body.document.filename)),
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


@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: str,
    container: ContainerDep,
):
    delete_usecase: DeleteDocumentUseCase = container.delete_document_usecase()
    delete_usecase.execute(doc_id)
    return SuccessResponse(message="Document deleted successfully")
