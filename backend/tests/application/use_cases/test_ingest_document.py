from unittest.mock import call
from app.application.use_cases.ingest_document import IngestDocumentUseCase
from app.application.dto import IngestDocumentInput
from app.domain.documents import DocumentStatus


class TestIngestDocument:
    def test_execute_happy_path_returns_processed_status(
        self,
        mock_file_storage,
        mock_document_loader,
        mock_text_splitter,
        mock_embedder,
        mock_vector_store,
        mock_document_repo,
    ):
        uc = IngestDocumentUseCase(
            mock_document_loader,
            mock_document_repo,
            mock_embedder,
            mock_file_storage,
            mock_text_splitter,
            mock_vector_store,
        )
        dto = IngestDocumentInput(filename="test.md", content=b"file content bytes")

        result = uc.execute(dto)

        assert result.status == DocumentStatus.PROCESSED
        assert result.filename == "test.md"
        assert result.id is not None

    def test_execute_calls_all_ports(
        self,
        mock_file_storage,
        mock_document_loader,
        mock_text_splitter,
        mock_embedder,
        mock_vector_store,
        mock_document_repo,
    ):
        uc = IngestDocumentUseCase(
            mock_document_loader,
            mock_document_repo,
            mock_embedder,
            mock_file_storage,
            mock_text_splitter,
            mock_vector_store,
        )
        dto = IngestDocumentInput(filename="test.md", content=b"file content bytes")
        uc.execute(dto)

        mock_file_storage.save.assert_called_once()
        mock_document_loader.load.assert_called_once()
        mock_text_splitter.split.assert_called_once()
        mock_embedder.embed.assert_called_once()
        mock_vector_store.add_chunks.assert_called_once()
        mock_document_repo.save.assert_called_once()

    def test_execute_saves_file_with_correct_args(
        self,
        mock_file_storage,
        mock_document_loader,
        mock_text_splitter,
        mock_embedder,
        mock_vector_store,
        mock_document_repo,
    ):
        uc = IngestDocumentUseCase(
            mock_document_loader,
            mock_document_repo,
            mock_embedder,
            mock_file_storage,
            mock_text_splitter,
            mock_vector_store,
        )
        dto = IngestDocumentInput(filename="test.md", content=b"file content bytes")
        uc.execute(dto)

        mock_file_storage.save.assert_called_once_with("test.md", b"file content bytes")

    def test_execute_embeds_and_stores_chunks(
        self,
        mock_file_storage,
        mock_document_loader,
        mock_text_splitter,
        mock_embedder,
        mock_vector_store,
        mock_document_repo,
    ):
        mock_text_splitter.split.return_value = ["chunk a", "chunk b"]
        mock_embedder.embed.return_value = [[0.1, 0.2], [0.3, 0.4]]

        uc = IngestDocumentUseCase(
            mock_document_loader,
            mock_document_repo,
            mock_embedder,
            mock_file_storage,
            mock_text_splitter,
            mock_vector_store,
        )
        dto = IngestDocumentInput(filename="test.md", content=b"file content bytes")
        uc.execute(dto)

        mock_embedder.embed.assert_called_once_with(["chunk a", "chunk b"])
        mock_vector_store.add_chunks.assert_called_once()
        added_chunks = mock_vector_store.add_chunks.call_args[1]["chunks"]
        added_vectors = mock_vector_store.add_chunks.call_args[1]["vectors"]
        assert len(added_chunks) == 2
        assert len(added_vectors) == 2

    def test_execute_splitter_error_sets_error_status(
        self,
        mock_file_storage,
        mock_document_loader,
        mock_text_splitter,
        mock_embedder,
        mock_vector_store,
        mock_document_repo,
    ):
        mock_text_splitter.split.side_effect = RuntimeError("split failed")

        uc = IngestDocumentUseCase(
            mock_document_loader,
            mock_document_repo,
            mock_embedder,
            mock_file_storage,
            mock_text_splitter,
            mock_vector_store,
        )
        dto = IngestDocumentInput(filename="test.md", content=b"file content bytes")

        result = uc.execute(dto)

        assert result.status == DocumentStatus.ERROR
        mock_document_repo.save.assert_called_once()
        saved_doc = mock_document_repo.save.call_args[0][0]
        assert saved_doc.status == DocumentStatus.ERROR

    def test_execute_embedding_error_sets_error_status(
        self,
        mock_file_storage,
        mock_document_loader,
        mock_text_splitter,
        mock_embedder,
        mock_vector_store,
        mock_document_repo,
    ):
        mock_embedder.embed.side_effect = RuntimeError("embed failed")

        uc = IngestDocumentUseCase(
            mock_document_loader,
            mock_document_repo,
            mock_embedder,
            mock_file_storage,
            mock_text_splitter,
            mock_vector_store,
        )
        dto = IngestDocumentInput(filename="test.md", content=b"file content bytes")

        result = uc.execute(dto)

        assert result.status == DocumentStatus.ERROR
        mock_document_repo.save.assert_called_once()

    def test_execute_vector_store_error_sets_error_status(
        self,
        mock_file_storage,
        mock_document_loader,
        mock_text_splitter,
        mock_embedder,
        mock_vector_store,
        mock_document_repo,
    ):
        mock_vector_store.add_chunks.side_effect = RuntimeError("store failed")

        uc = IngestDocumentUseCase(
            mock_document_loader,
            mock_document_repo,
            mock_embedder,
            mock_file_storage,
            mock_text_splitter,
            mock_vector_store,
        )
        dto = IngestDocumentInput(filename="test.md", content=b"file content bytes")

        result = uc.execute(dto)

        assert result.status == DocumentStatus.ERROR
        mock_document_repo.save.assert_called_once()
