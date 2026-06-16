from ports import DocumentLoaderPort, DocumentRepositoryPort, EmbeddingPort, FileStoragePort, TextSplitterPort, VectorStorePort
from dto import IngestDocumentInput, IngestDocumentOutput
from domain.chunks import Chunk, MetaData
from domain.documents import Document, DocumentStatus, DocumentType
from uuid import uuid4
from datetime import datetime
from pathlib import Path

class IngestDocumentUseCase:
    def __init__(self,
                 doc_loader: DocumentLoaderPort,
                 doc_repo: DocumentRepositoryPort,
                 embedder: EmbeddingPort,
                 file_storage: FileStoragePort,
                 splitter: TextSplitterPort,
                 vector_store: VectorStorePort) -> None:
        self._doc_repo = doc_repo
        self._doc_loader = doc_loader
        self._embedder = embedder
        self._file_storage = file_storage
        self._splitter = splitter
        self._vector_store = vector_store

    def execute(self, document_dto: IngestDocumentInput) -> IngestDocumentOutput:
        # 1. save the file
        file_path: str = self._file_storage.save(document_dto.filename, document_dto.content)

        # 2. load file to get str contents
        content_str: str = self._doc_loader.load(file_path)

        # build document data
        document_data: Document = Document(
            id=str(uuid4()),
            title=Path(document_dto.filename).stem,
            filename=document_dto.filename,
            file_type=DocumentType.from_filename(document_dto.filename),
            status=DocumentStatus.PROCESSED,
            created_at=str(datetime.now()),
            updated_at=str(datetime.now())
        )

        # 3. Chunk Process
        try: 
            # split the file
            chunks_text: list[str] = self._splitter.split(content_str)

            # embedding process
            chunks_vector: list[list[float]] = self._embedder.embed(chunks_text)
            
            # build chunks
            chunks: list[Chunk] = [
                Chunk(
                    id=str(uuid4()),
                    document=chunk_text,
                    metadata=MetaData(
                        document_id=document_data.id,
                        chunk_index=i
                    )
                )   
                for i, chunk_text in enumerate(chunks_text)
            ]
            # store to chroma db
            self._vector_store.add_chunks(chunks=chunks, vectors=chunks_vector)
        except Exception:
            document_data.status = DocumentStatus.ERROR
            self._doc_repo.save(document_data)
            return IngestDocumentOutput(
                id=document_data.id,
                filename=document_data.filename,
                status=document_data.status
            )

        # 4. store document data to sqlite
        self._doc_repo.save(document_data)
        
        return IngestDocumentOutput(
            id=document_data.id,
            filename=document_data.filename,
            status=document_data.status
        ) 