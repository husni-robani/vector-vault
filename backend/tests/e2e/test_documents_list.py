class TestListDocuments:
    def test_list_empty_returns_empty_array(self, client):
        response = client.get("/api/documents")

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Documents retrieved successfully"
        assert body["data"]["documents"] == []
        assert body["data"]["total"] == 0
        assert body["data"]["page"] == 1
        assert body["data"]["limit"] == 50

    def test_list_returns_single_uploaded_document(self, client, sample_md_bytes):
        files = {
            "document": ("notes.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": "My Notes"}
        upload_resp = client.post("/api/documents", files=files, data=data)
        assert upload_resp.status_code == 200
        doc_id = upload_resp.json()["data"]["document_id"]

        response = client.get("/api/documents")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["total"] == 1
        assert len(body["data"]["documents"]) == 1

        doc = body["data"]["documents"][0]
        assert doc["id"] == doc_id
        assert doc["title"] == "My Notes"
        assert doc["filename"] == "notes.md"
        assert doc["status"] == "processed"

    def test_list_document_fields_match_upload(self, client, sample_md_bytes):
        files = {
            "document": ("fields.md", sample_md_bytes, "text/markdown"),
        }
        data = {"title": "Field Check"}
        upload_resp = client.post("/api/documents", files=files, data=data)
        assert upload_resp.status_code == 200

        response = client.get("/api/documents")
        doc = response.json()["data"]["documents"][0]

        assert doc["file_type"] == ".md"
        assert doc["chunks_count"] > 0
        assert doc["size_bytes"] == len(sample_md_bytes)
        assert doc["status"] == "processed"
        assert doc["created_at"] is not None

    def test_list_returns_multiple_documents(self, client, sample_md_bytes):
        client.post(
            "/api/documents",
            files={"document": ("first.md", sample_md_bytes, "text/markdown")},
            data={"title": "First"},
        )
        client.post(
            "/api/documents",
            files={"document": ("second.md", sample_md_bytes, "text/markdown")},
            data={"title": "Second"},
        )

        response = client.get("/api/documents")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["total"] == 2
        assert len(body["data"]["documents"]) == 2

        titles = {d["title"] for d in body["data"]["documents"]}
        assert titles == {"First", "Second"}

    def test_pagination_first_page(self, client, sample_md_bytes):
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

        response = client.get("/api/documents", params={"page": 1, "limit": 1})

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]["documents"]) == 1
        assert body["data"]["total"] == 2
        assert body["data"]["page"] == 1
        assert body["data"]["limit"] == 1

    def test_pagination_second_page(self, client, sample_md_bytes):
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

        response = client.get("/api/documents", params={"page": 2, "limit": 1})

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]["documents"]) == 1
        assert body["data"]["total"] == 2
        assert body["data"]["page"] == 2
        assert body["data"]["limit"] == 1

        first_page = client.get("/api/documents", params={"page": 1, "limit": 1})
        first_ids = {d["id"] for d in first_page.json()["data"]["documents"]}
        second_ids = {d["id"] for d in body["data"]["documents"]}

        assert first_ids.isdisjoint(second_ids)

    def test_pagination_empty_page_beyond_range(self, client, sample_md_bytes):
        client.post(
            "/api/documents",
            files={"document": ("only.md", sample_md_bytes, "text/markdown")},
            data={"title": "Only"},
        )

        response = client.get("/api/documents", params={"page": 5, "limit": 10})

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["documents"] == []
        assert body["data"]["total"] == 1
        assert body["data"]["page"] == 5
        assert body["data"]["limit"] == 10

    def test_default_pagination_values_in_response(self, client, sample_md_bytes):
        client.post(
            "/api/documents",
            files={"document": ("default.md", sample_md_bytes, "text/markdown")},
            data={"title": "Default"},
        )

        response = client.get("/api/documents")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["page"] == 1
        assert body["data"]["limit"] == 50
        assert body["data"]["total"] == 1
