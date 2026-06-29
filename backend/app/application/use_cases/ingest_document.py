import logging

from app.application.ports import (
    DocumentLoaderPort,
    DocumentRepositoryPort,
    EmbeddingPort,
    FileStoragePort,
    TextSplitterPort,
    VectorStorePort,
)
from app.application.dto import IngestDocumentInput, IngestDocumentOutput
from app.domain.chunks import Chunk, MetaData
from app.domain.documents import Document, DocumentStatus, DocumentType
from uuid import uuid4
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class IngestDocumentUseCase:
    def __init__(
        self,
        doc_loader: DocumentLoaderPort,
        doc_repo: DocumentRepositoryPort,
        embedder: EmbeddingPort,
        file_storage: FileStoragePort,
        splitter: TextSplitterPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._doc_repo = doc_repo
        self._doc_loader = doc_loader
        self._embedder = embedder
        self._file_storage = file_storage
        self._splitter = splitter
        self._vector_store = vector_store

    def execute(self, document_dto: IngestDocumentInput) -> IngestDocumentOutput:
        # 1. save the file
        file_path: str = self._file_storage.save(
            document_dto.filename, document_dto.content
        )

        # 2. load file to get str contents
        content_str: str = self._doc_loader.load(file_path)

        # set default title as filename if custom title not included
        if document_dto.title == "":
            document_dto.title = Path(document_dto.filename).stem

        # build document data
        document_data: Document = Document(
            id=str(uuid4()),
            title=document_dto.title,
            filename=document_dto.filename,
            file_path=file_path,
            file_type=DocumentType.from_filename(document_dto.filename),
            status=DocumentStatus.PROCESSED,
            chunks_count=0,
            size_bytes=len(document_dto.content),
            created_at=str(datetime.now()),
            updated_at=str(datetime.now()),
        )

        # 3. Chunk Process & save document data
        try:
            # split the file
            chunks_text: list[str] = self._splitter.split(content_str, document_type=document_data.file_type)

            # embedding process
            chunks_vector: list[list[float]] = self._embedder.embed(chunks_text)

            # build chunks
            chunks: list[Chunk] = [
                Chunk(
                    id=str(uuid4()),
                    text=text,
                    vector=vector,
                    metadata=MetaData(
                        document_id=document_data.id,
                        chunk_index=i,
                        title=Path(document_dto.filename).stem,
                    ),
                )
                for i, (text, vector) in enumerate(zip(chunks_text, chunks_vector))
            ]
            # store to chroma db
            self._vector_store.add_chunks(chunks=chunks)

            # store document data to sqlite
            document_data.chunks_count = len(chunks_text)

            self._doc_repo.save(document_data)
        except Exception:
            logger.exception(
                "Document processing failed for '%s'", document_dto.filename
            )

            # delete the stored file
            self._file_storage.delete(Path(file_path))

            # set document_status as error
            document_data.status = DocumentStatus.ERROR

            self._doc_repo.save(document_data)
            
            raise

        return IngestDocumentOutput(
            id=document_data.id,
            filename=document_data.filename,
            status=document_data.status,
            file_type=document_data.file_type,
            title=document_data.title,
        )
