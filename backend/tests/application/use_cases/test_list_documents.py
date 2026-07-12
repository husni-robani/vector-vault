from app.application.dto import ListDocumentsInput
from app.application.use_cases.list_documents import ListDocumentsUseCase


class TestListDocuments:
    def test_execute_returns_documents(self, mock_document_repo, sample_document):
        mock_document_repo.find_all.return_value = ([sample_document], 1)

        uc = ListDocumentsUseCase(mock_document_repo)
        result = uc.execute(ListDocumentsInput(page=1, limit=10))

        assert result.documents == [sample_document]
        assert result.total == 1
        assert result.page == 1
        assert result.limit == 10
        mock_document_repo.find_all.assert_called_once_with(page=1, limit=10)

    def test_execute_returns_empty_list_when_no_documents(self, mock_document_repo):
        mock_document_repo.find_all.return_value = ([], 0)

        uc = ListDocumentsUseCase(mock_document_repo)
        result = uc.execute(ListDocumentsInput(page=1, limit=10))

        assert result.documents == []
        assert result.total == 0
        assert result.page == 1
        assert result.limit == 10
        mock_document_repo.find_all.assert_called_once_with(page=1, limit=10)
