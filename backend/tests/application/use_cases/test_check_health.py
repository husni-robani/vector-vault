from app.application.use_cases.check_health import HealthCheckUseCase
from app.application.dto import LLMHealth, VectorStoreHealth, EmbeddingHealth


class TestCheckHealth:
    def test_execute_all_healthy(self, mock_llm, mock_vector_store, mock_embedder):
        mock_llm.health_check.return_value = LLMHealth(
            connected=True, model="llama3.1", model_loaded=True
        )
        mock_vector_store.health_check.return_value = VectorStoreHealth(
            connected=True, collections_count=1
        )
        mock_embedder.health_check.return_value = EmbeddingHealth(
            connected=True, model_name="all-MiniLM-L6-v2"
        )

        uc = HealthCheckUseCase(mock_llm, mock_vector_store, mock_embedder)
        result = uc.execute()

        assert result.status == "healthy"
        assert result.llm.connected is True
        assert result.llm.model == "llama3.1"
        assert result.vector_store.connected is True
        assert result.vector_store.collections_count == 1
        assert result.embedding.connected is True

    def test_execute_llm_down_returns_unhealthy(
        self, mock_llm, mock_vector_store, mock_embedder
    ):
        mock_llm.health_check.side_effect = RuntimeError("Connection refused")
        mock_vector_store.health_check.return_value = VectorStoreHealth(
            connected=True, collections_count=1
        )
        mock_embedder.health_check.return_value = EmbeddingHealth(
            connected=True, model_name="all-MiniLM-L6-v2"
        )

        uc = HealthCheckUseCase(mock_llm, mock_vector_store, mock_embedder)
        result = uc.execute()

        assert result.status == "unhealthy"
        assert result.llm.connected is False
        assert result.llm.error == "Connection refused"
        assert result.vector_store.connected is True
        assert result.embedding.connected is True

    def test_execute_vector_store_down_returns_unhealthy(
        self, mock_llm, mock_vector_store, mock_embedder
    ):
        mock_llm.health_check.return_value = LLMHealth(
            connected=True, model="llama3.1", model_loaded=True
        )
        mock_vector_store.health_check.side_effect = RuntimeError("Timeout")
        mock_embedder.health_check.return_value = EmbeddingHealth(
            connected=True, model_name="all-MiniLM-L6-v2"
        )

        uc = HealthCheckUseCase(mock_llm, mock_vector_store, mock_embedder)
        result = uc.execute()

        assert result.status == "unhealthy"
        assert result.llm.connected is True
        assert result.vector_store.connected is False
        assert result.vector_store.error == "Timeout"
        assert result.embedding.connected is True

    def test_execute_embedding_down_returns_unhealthy(
        self, mock_llm, mock_vector_store, mock_embedder
    ):
        mock_llm.health_check.return_value = LLMHealth(
            connected=True, model="llama3.1", model_loaded=True
        )
        mock_vector_store.health_check.return_value = VectorStoreHealth(
            connected=True, collections_count=1
        )
        mock_embedder.health_check.side_effect = RuntimeError("Model not found")

        uc = HealthCheckUseCase(mock_llm, mock_vector_store, mock_embedder)
        result = uc.execute()

        assert result.status == "unhealthy"
        assert result.llm.connected is True
        assert result.vector_store.connected is True
        assert result.embedding.connected is False
        assert result.embedding.error == "Model not found"

    def test_execute_multiple_services_down_returns_unhealthy(
        self, mock_llm, mock_vector_store, mock_embedder
    ):
        mock_llm.health_check.side_effect = RuntimeError("Connection refused")
        mock_vector_store.health_check.side_effect = RuntimeError("Timeout")
        mock_embedder.health_check.return_value = EmbeddingHealth(
            connected=True, model_name="all-MiniLM-L6-v2"
        )

        uc = HealthCheckUseCase(mock_llm, mock_vector_store, mock_embedder)
        result = uc.execute()

        assert result.status == "unhealthy"
        assert result.llm.connected is False
        assert result.vector_store.connected is False
        assert result.embedding.connected is True
