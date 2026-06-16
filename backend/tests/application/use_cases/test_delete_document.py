import pytest
from unittest.mock import call
from app.application.use_cases.delete_document import DeleteDocumentUseCase


class TestDeleteDocument:
    def test_execute_happy_path_deletes_from_all_stores(
        self, mock_document_repo, mock_vector_store, mock_file_storage, sample_document
    ):
        mock_document_repo.find_by_id.return_value = sample_document

        uc = DeleteDocumentUseCase(
            mock_document_repo, mock_vector_store, mock_file_storage
        )
        uc.execute(sample_document.id)

        mock_document_repo.find_by_id.assert_called_once_with(sample_document.id)
        mock_document_repo.delete.assert_called_once_with(sample_document.id)
        mock_vector_store.delete_by_document.assert_called_once_with(sample_document.id)
        mock_file_storage.delete.assert_called_once_with(sample_document.file_path)

    def test_execute_calls_delete_in_correct_order(
        self, mock_document_repo, mock_vector_store, mock_file_storage, sample_document
    ):
        mock_document_repo.find_by_id.return_value = sample_document
        call_order = []

        mock_document_repo.delete.side_effect = lambda doc_id: call_order.append("repo")
        mock_vector_store.delete_by_document.side_effect = lambda doc_id: (
            call_order.append("vector")
        )
        mock_file_storage.delete.side_effect = lambda path: call_order.append("storage")

        uc = DeleteDocumentUseCase(
            mock_document_repo, mock_vector_store, mock_file_storage
        )
        uc.execute(sample_document.id)

        assert call_order == ["repo", "vector", "storage"]

    def test_execute_document_not_found_raises_value_error(
        self, mock_document_repo, mock_vector_store, mock_file_storage
    ):
        mock_document_repo.find_by_id.return_value = None

        uc = DeleteDocumentUseCase(
            mock_document_repo, mock_vector_store, mock_file_storage
        )

        with pytest.raises(ValueError, match="doc-missing"):
            uc.execute("doc-missing")

    def test_execute_document_not_found_does_not_call_delete(
        self, mock_document_repo, mock_vector_store, mock_file_storage
    ):
        mock_document_repo.find_by_id.return_value = None

        uc = DeleteDocumentUseCase(
            mock_document_repo, mock_vector_store, mock_file_storage
        )

        with pytest.raises(ValueError):
            uc.execute("doc-missing")

        mock_document_repo.delete.assert_not_called()
        mock_vector_store.delete_by_document.assert_not_called()
        mock_file_storage.delete.assert_not_called()
