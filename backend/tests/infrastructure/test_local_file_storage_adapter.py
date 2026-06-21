import pytest
from pathlib import Path
from app.infrastructure.file_storage.local_storage import LocalFileStorage
from app.domain.exceptions import FileAlreadyExistsError, ExternalServiceError


@pytest.fixture
def storage(tmp_path):
    return LocalFileStorage(storage_path=tmp_path)


def test_save_writes_file_and_returns_path(storage, tmp_path):
    result = storage.save("doc.md", b"# hello")

    expected_path = str((tmp_path / "doc.md").resolve())
    assert result == expected_path
    assert (tmp_path / "doc.md").read_bytes() == b"# hello"


def test_save_creates_missing_storage_path(tmp_path):
    nested = tmp_path / "deeply" / "nested" / "dir"
    storage = LocalFileStorage(storage_path=nested)

    storage.save("x.txt", b"data")

    assert (nested / "x.txt").exists()


def test_save_raises_file_already_exists(storage):
    storage.save("dup.md", b"first")

    with pytest.raises(FileAlreadyExistsError, match="file already exists"):
        storage.save("dup.md", b"second")


def test_save_raises_external_service_error_on_failure(storage, monkeypatch):
    def boom(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr("builtins.open", boom)

    with pytest.raises(ExternalServiceError, match="Failed to save file"):
        storage.save("x.md", b"data")


def test_save_with_empty_content(storage, tmp_path):
    result = storage.save("empty.txt", b"")

    assert result == str((tmp_path / "empty.txt").resolve())
    assert (tmp_path / "empty.txt").read_bytes() == b""


def test_delete_removes_existing_file(storage, tmp_path):
    saved_path = storage.save("to_delete.txt", b"remove me")

    storage.delete(Path(saved_path))

    assert not (tmp_path / "to_delete.txt").exists()


def test_delete_non_existent_file_no_error(storage, tmp_path):
    missing = tmp_path / "does_not_exist.txt"

    storage.delete(missing)

    assert True
