from unittest.mock import patch

from app.domain.exceptions import ExternalServiceError
from app.application.use_cases.answer_question import AnswerQuestionUseCase


class TestChat:
    def test_chat_response_is_sse(self, client):
        response = client.post(
            "/api/chats", json={"message": "Hello world", "conversation_id": "test-sse"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

    def test_chat_returns_token_sources_and_done_events(self, client, sample_md_bytes):
        files = {"document": ("knowledge.md", sample_md_bytes, "text/markdown")}
        client.post("/api/documents", files=files, data={"title": "AI Knowledge"})

        from tests.e2e.conftest import parse_sse_events

        response = client.post(
            "/api/chats",
            json={
                "message": "What is machine learning?",
                "conversation_id": "conv-123",
            },
        )

        events = parse_sse_events(response)
        event_types = {e["data"]["type"] for e in events}

        assert len(events) > 0
        assert "token" in event_types
        assert "sources" in event_types
        assert "done" in event_types

    def test_chat_token_content_matches_stub(self, client, sample_md_bytes):
        files = {"document": ("knowledge.md", sample_md_bytes, "text/markdown")}
        client.post("/api/documents", files=files, data={"title": "AI Knowledge"})

        from tests.e2e.conftest import parse_sse_events

        response = client.post(
            "/api/chats",
            json={
                "message": "What is machine learning?",
                "conversation_id": "conv-123",
            },
        )

        events = parse_sse_events(response)
        tokens = [e["data"]["content"] for e in events if e["data"]["type"] == "token"]

        assert tokens == ["This", " is", " a", " stub", " answer."]

    def test_chat_sources_reference_uploaded_document(self, client, sample_md_bytes):
        files = {"document": ("knowledge.md", sample_md_bytes, "text/markdown")}
        upload_resp = client.post(
            "/api/documents", files=files, data={"title": "AI Knowledge"}
        )
        doc_id = upload_resp.json()["data"]["document_id"]

        from tests.e2e.conftest import parse_sse_events

        response = client.post(
            "/api/chats",
            json={
                "message": "What is machine learning?",
                "conversation_id": "conv-123",
            },
        )

        events = parse_sse_events(response)
        sources_events = [e for e in events if e["data"]["type"] == "sources"]

        assert len(sources_events) == 1
        sources = sources_events[0]["data"]["sources"]
        assert len(sources) > 0

        for source in sources:
            assert source["title"] == "knowledge"
            assert source["chunk_index"] is not None
            assert source["distance"] is not None
            assert source["snippet"] is not None

    def test_chat_sources_empty_with_no_documents(self, client):
        from tests.e2e.conftest import parse_sse_events

        response = client.post(
            "/api/chats",
            json={
                "message": "What is machine learning?",
                "conversation_id": "conv-empty",
            },
        )

        events = parse_sse_events(response)
        sources_events = [e for e in events if e["data"]["type"] == "sources"]

        assert sources_events[0]["data"]["sources"] == []

    def test_chat_done_event_echoes_conversation_id(self, client, sample_md_bytes):
        files = {"document": ("knowledge.md", sample_md_bytes, "text/markdown")}
        client.post("/api/documents", files=files, data={"title": "AI Knowledge"})

        from tests.e2e.conftest import parse_sse_events

        response = client.post(
            "/api/chats",
            json={
                "message": "What is machine learning?",
                "conversation_id": "custom-conv-42",
            },
        )

        events = parse_sse_events(response)
        done_events = [e for e in events if e["data"]["type"] == "done"]

        assert len(done_events) == 1
        assert done_events[0]["data"]["conversation_id"] == "custom-conv-42"

    def test_chat_error_yields_sse_error_event(self, client):
        async def failing_execute(self, input):
            raise ExternalServiceError("LLM generation failed")

        with patch.object(AnswerQuestionUseCase, "execute", failing_execute):
            from tests.e2e.conftest import parse_sse_events

            response = client.post(
                "/api/chats",
                json={
                    "message": "What is machine learning?",
                    "conversation_id": "conv-error",
                },
            )

            events = parse_sse_events(response)
            error_events = [e for e in events if e["data"]["type"] == "error"]

            assert len(error_events) == 1
            assert error_events[0]["data"]["message"] == "LLM generation failed"
