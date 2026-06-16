from app.application.use_cases.list_documents import ListDocumentUseCase


class TestListDocuments:
    def test_execute_returns_documents(self, mock_document_repo, sample_document):
        mock_document_repo.find_all.return_value = [sample_document]

        uc = ListDocumentUseCase(mock_document_repo)
        result = uc.execute()

        assert result == [sample_document]
        assert len(result) == 1
        mock_document_repo.find_all.assert_called_once()

    def test_execute_returns_empty_list_when_no_documents(self, mock_document_repo):
        mock_document_repo.find_all.return_value = []

        uc = ListDocumentUseCase(mock_document_repo)
        result = uc.execute()

        assert result == []
        mock_document_repo.find_all.assert_called_once()
