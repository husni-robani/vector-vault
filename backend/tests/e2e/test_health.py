class TestHealthCheck:
    def test_health_returns_healthy_when_all_services_up(self, client):
        response = client.get("/api/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"

    def test_health_response_keys_match_api_spec(self, client):
        response = client.get("/api/health")

        body = response.json()
        assert set(body.keys()) == {"status", "ollama", "chromadb", "embedding_model"}

        ollama = body["ollama"]
        assert ollama["connected"] is True
        assert isinstance(ollama["model"], str)
        assert isinstance(ollama["model_loaded"], bool)

        chromadb = body["chromadb"]
        assert chromadb["connected"] is True
        assert isinstance(chromadb["collections_count"], int)

        assert isinstance(body["embedding_model"], str)
