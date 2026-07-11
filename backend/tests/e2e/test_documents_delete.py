from pathlib import Path


class TestDeleteDocument:
    def test_delete_existing_document_returns_success(self, client, sample_md_bytes):
        upload = client.post(
            "/api/documents",
            files={"document": ("to-delete.md", sample_md_bytes, "text/markdown")},
            data={"title": "Delete Me"},
        )
        doc_id = upload.json()["data"]["document_id"]

        response = client.delete(f"/api/documents/{doc_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Document deleted successfully"
        assert body["data"] is None

    def test_delete_removes_db_record(self, client, sample_md_bytes):
        upload = client.post(
            "/api/documents",
            files={"document": ("gone.md", sample_md_bytes, "text/markdown")},
            data={"title": "Gone"},
        )
        doc_id = upload.json()["data"]["document_id"]

        client.delete(f"/api/documents/{doc_id}")

        container = client.app.state.container
        assert container.document_repo().find_by_id(doc_id) is None

    def test_delete_removes_file_from_disk(self, client, sample_md_bytes):
        upload = client.post(
            "/api/documents",
            files={"document": ("rm-me.md", sample_md_bytes, "text/markdown")},
            data={"title": "Remove"},
        )
        doc_id = upload.json()["data"]["document_id"]

        container = client.app.state.container
        file_path = container.document_repo().find_by_id(doc_id).file_path

        client.delete(f"/api/documents/{doc_id}")

        assert not Path(file_path).exists()

    def test_delete_removes_chunks_from_vector_store(self, client, sample_md_bytes):
        upload = client.post(
            "/api/documents",
            files={"document": ("chunked.md", sample_md_bytes, "text/markdown")},
            data={"title": "Chunked"},
        )
        doc_id = upload.json()["data"]["document_id"]

        client.delete(f"/api/documents/{doc_id}")

        container = client.app.state.container
        collection = container.vector_store().collection
        result = collection.get(where={"document_id": doc_id})
        assert len(result["ids"]) == 0

    def test_delete_nonexistent_document_returns_404(self, client):
        response = client.delete("/api/documents/nonexistent-id")

        assert response.status_code == 404

    def test_deleted_document_not_in_list(self, client, sample_md_bytes):
        client.post(
            "/api/documents",
            files={"document": ("a.md", sample_md_bytes, "text/markdown")},
            data={"title": "A"},
        )
        client.post(
            "/api/documents",
            files={"document": ("b.md", sample_md_bytes, "text/markdown")},
            data={"title": "B"},
        )

        docs = client.get("/api/documents").json()["data"]["documents"]
        doc_b_id = next(d["id"] for d in docs if d["title"] == "B")

        client.delete(f"/api/documents/{doc_b_id}")

        remaining = client.get("/api/documents").json()["data"]["documents"]
        assert len(remaining) == 1
        assert remaining[0]["title"] == "A"
