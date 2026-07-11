import sqlite3

import pytest

from app.infrastructure.document_repo.sqlite_repository import SQLiteDocumentRepository
from app.domain.documents import Document, DocumentStatus, DocumentType
from app.domain.exceptions import ExternalServiceError


@pytest.fixture
def repo(tmp_path):
    db_path = tmp_path / "test.db"
    repository = SQLiteDocumentRepository(database_file=str(db_path))
    repository.initialize_tables()
    yield repository
    repository.close()


@pytest.fixture
def sample_doc():
    return Document(
        id="doc-123",
        title="Test Document",
        filename="test.md",
        file_path="/data/uploads/test.md",
        file_type=DocumentType.MD,
        status=DocumentStatus.PROCESSED,
        chunks_count=3,
        size_bytes=1024,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00",
    )


def test_initialize_tables_creates_documents_table(repo):
    cursor = repo.conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
    )
    assert cursor.fetchone() is not None


def test_save_inserts_document(repo, sample_doc):
    repo.save(sample_doc)

    result = repo.find_by_id(sample_doc.id)

    assert result is not None
    assert result.id == sample_doc.id
    assert result.title == sample_doc.title
    assert result.filename == sample_doc.filename
    assert result.file_path == sample_doc.file_path
    assert result.file_type == sample_doc.file_type
    assert result.status == sample_doc.status
    assert result.chunks_count == sample_doc.chunks_count
    assert result.size_bytes == sample_doc.size_bytes
    assert result.created_at == sample_doc.created_at
    assert result.updated_at == sample_doc.updated_at


def test_save_upserts_on_duplicate_id(repo, sample_doc):
    repo.save(sample_doc)

    updated_doc = Document(
        id=sample_doc.id,
        title="Updated Title",
        filename=sample_doc.filename,
        file_path=sample_doc.file_path,
        file_type=sample_doc.file_type,
        status=DocumentStatus.ERROR,
        chunks_count=99,
        size_bytes=sample_doc.size_bytes,
        created_at=sample_doc.created_at,
        updated_at="2025-06-01T00:00:00",
    )
    repo.save(updated_doc)

    result = repo.find_by_id(sample_doc.id)

    assert result.title == "Updated Title"
    assert result.status == DocumentStatus.ERROR
    assert result.chunks_count == 99
    assert result.updated_at == "2025-06-01T00:00:00"


def test_find_all_returns_all_documents(repo, sample_doc):
    doc2 = Document(
        id="doc-456",
        title="Second Document",
        filename="second.md",
        file_path="/data/uploads/second.md",
        file_type=DocumentType.PDF,
        status=DocumentStatus.PENDING,
        chunks_count=0,
        size_bytes=2048,
        created_at="2025-02-01T00:00:00",
        updated_at="2025-02-01T00:00:00",
    )

    repo.save(sample_doc)
    repo.save(doc2)

    results, total = repo.find_all()
    assert total == 2
    assert len(results) == 2
    ids = {d.id for d in results}
    assert ids == {sample_doc.id, doc2.id}


def test_find_by_id_returns_none_for_missing_id(repo):
    result = repo.find_by_id("nonexistent-id")
    assert result is None


def test_delete_removes_document(repo, sample_doc):
    repo.save(sample_doc)

    repo.delete(sample_doc.id)

    result = repo.find_by_id(sample_doc.id)
    assert result is None


def test_delete_non_existent_does_not_raise(repo):
    repo.delete("nonexistent-id")


def test_find_all_empty_database_returns_empty_list(repo):
    results, total = repo.find_all()
    assert results == []
    assert total == 0


class _CrashingCursor:
    def execute(self, *args, **kwargs):
        raise sqlite3.OperationalError("database is locked")


class _CrashingConnection:
    def cursor(self):
        return _CrashingCursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def test_save_raises_external_service_error_on_db_failure(
    repo, sample_doc, monkeypatch
):
    monkeypatch.setattr(repo, "conn", _CrashingConnection())

    with pytest.raises(ExternalServiceError, match="failed to insert document"):
        repo.save(sample_doc)


def test_find_by_id_raises_external_service_error_on_db_failure(
    repo, sample_doc, monkeypatch
):
    repo.save(sample_doc)

    monkeypatch.setattr(repo, "conn", _CrashingConnection())

    with pytest.raises(ExternalServiceError, match="failed to get document by id"):
        repo.find_by_id(sample_doc.id)
