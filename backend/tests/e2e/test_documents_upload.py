from pathlib import Path

import pytest


class TestUploadDocument:
    def test_upload_md_success(self, client, sample_md_bytes):
        files = {
            "document": ("test.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": "My Document"}

        response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Upload document success"
        assert body["data"]["document_id"] is not None
        assert body["data"]["filename"] == "test.md"
        assert body["data"]["title"] == "My Document"
        assert body["data"]["file_type"] == "text/markdown"
        assert body["data"]["status"] == "processed"

    def test_upload_empty_title_defaults_to_filename_stem(
        self, client, sample_md_bytes
    ):
        files = {
            "document": ("my-notes.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": ""}

        response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["title"] == "my-notes"

    def test_upload_file_persisted_on_disk(self, client, sample_md_file):
        with open(sample_md_file, "rb") as f:
            files = {"document": (sample_md_file.name, f, "text/markdown")}
            data = {"title": "Disk Test"}
            response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 200
        doc_id = response.json()["data"]["document_id"]

        container = client.app.state.container
        doc = container.document_repo().find_by_id(doc_id)
        assert doc is not None

        saved_path = Path(doc.file_path)
        assert saved_path.exists()
        assert saved_path.read_bytes() == sample_md_file.read_bytes()

    def test_upload_creates_db_record(self, client, sample_md_bytes):
        files = {
            "document": ("notes.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": "DB Record"}

        response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 200
        doc_id = response.json()["data"]["document_id"]

        container = client.app.state.container
        doc = container.document_repo().find_by_id(doc_id)

        assert doc is not None
        assert doc.filename == "notes.md"
        assert doc.title == "DB Record"
        assert doc.file_type == "text/markdown"
        assert doc.status == "processed"
        assert doc.chunks_count > 0
        assert doc.size_bytes == len(sample_md_bytes)

    def test_upload_creates_vector_store_entries(self, client, sample_md_bytes):
        files = {
            "document": ("chunked.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": "Chunk Test"}

        response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 200
        doc_id = response.json()["data"]["document_id"]

        container = client.app.state.container
        collection = container.vector_store().collection

        result = collection.get(where={"document_id": doc_id})

        assert len(result["ids"]) > 0

    def test_upload_empty_filename_rejected(self, client):
        files = {
            "document": ("", b"content", "text/markdown"),
        }
        data = {"title": "Empty"}

        response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 422

    def test_upload_oversized_file_rejected(self, client_small_max_upload):
        content = b"x" * 2000
        files = {
            "document": ("big.md", content, "text/markdown"),
        }
        data = {"title": "Too Big"}

        response = client_small_max_upload.post(
            "/api/documents", files=files, data=data
        )

        assert response.status_code == 422

    def test_upload_unsupported_file_type_rejected(self, client):
        files = {
            "document": ("notes.txt", b"plain text", "text/plain"),
        }
        data = {"title": "Unsupported"}

        response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 400
        assert response.json()["message"] == "Unsupported file type: .txt"

    def test_upload_duplicate_filename_rejected(self, client, sample_md_bytes):
        files = {
            "document": ("unique.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": "First"}

        response = client.post("/api/documents", files=files, data=data)
        assert response.status_code == 200

        response = client.post("/api/documents", files=files, data=data)
        assert response.status_code == 400
        assert response.json()["message"] == "file already exists"

    def test_upload_stores_mime_content_type_in_db(self, client, sample_md_bytes):
        files = {
            "document": ("doc.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": "MIME Check"}

        response = client.post("/api/documents", files=files, data=data)

        assert response.status_code == 200
        doc_id = response.json()["data"]["document_id"]

        container = client.app.state.container
        doc = container.document_repo().find_by_id(doc_id)

        assert doc is not None
        assert doc.file_type == "text/markdown"
