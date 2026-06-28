import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from ollama import ResponseError as OllamaResponseError

from app.domain.exceptions import ExternalServiceError
from app.infrastructure.llm.ollama_adapter import OllamaLLM


class MockGenerateChunk:
    def __init__(self, response, done=False):
        self.response = response
        self.done = done


async def _async_gen(items):
    for item in items:
        yield item


@pytest.fixture
def adapter():
    with (
        patch("app.infrastructure.llm.ollama_adapter.AsyncClient") as mock_async_cls,
        patch("app.infrastructure.llm.ollama_adapter.Client") as mock_sync_cls,
    ):
        mock_async_instance = AsyncMock()
        mock_sync_instance = MagicMock()
        mock_async_cls.return_value = mock_async_instance
        mock_sync_cls.return_value = mock_sync_instance
        mock_async_instance.generate = AsyncMock()
        adapter = OllamaLLM(base_url="http://localhost:11434", model="llama3.1")
        yield adapter


class TestGenerate:
    @pytest.mark.asyncio
    async def test_yields_tokens_from_stream(self, adapter):
        chunks = [
            MockGenerateChunk("Hello"),
            MockGenerateChunk(" world"),
            MockGenerateChunk("!"),
        ]
        adapter._async_client.generate.return_value = _async_gen(chunks)

        tokens = []
        async for token in adapter.generate(prompt="What is AI?"):
            tokens.append(token)

        assert tokens == ["Hello", " world", "!"]

    @pytest.mark.asyncio
    async def test_skips_chunks_with_empty_response(self, adapter):
        chunks = [
            MockGenerateChunk("Hello"),
            MockGenerateChunk(""),
            MockGenerateChunk(" world"),
            MockGenerateChunk(None),
            MockGenerateChunk("!"),
        ]
        adapter._async_client.generate.return_value = _async_gen(chunks)

        tokens = []
        async for token in adapter.generate(prompt="test"):
            tokens.append(token)

        assert tokens == ["Hello", " world", "!"]

    @pytest.mark.asyncio
    async def test_raises_on_ollama_response_error(self, adapter):
        adapter._async_client.generate.side_effect = OllamaResponseError(
            "model not found"
        )

        with pytest.raises(ExternalServiceError) as exc_info:
            async for _ in adapter.generate(prompt="test"):
                pass

        assert "Ollama generate response failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_raises_on_connect_error(self, adapter):
        adapter._async_client.generate.side_effect = httpx.ConnectError(
            "connection refused"
        )

        with pytest.raises(ExternalServiceError) as exc_info:
            async for _ in adapter.generate(prompt="test"):
                pass

        assert "Cannot connect to Ollama" in str(exc_info.value)


class TestHealthCheck:
    def test_connected_and_model_loaded(self, adapter):
        mock_model = MagicMock()
        mock_model.model = "llama3.1"
        mock_resp = MagicMock()
        mock_resp.models = [mock_model]
        adapter._sync_client.list.return_value = mock_resp

        result = adapter.health_check()

        assert result.connected is True
        assert result.model == "llama3.1"
        assert result.model_loaded is True
        assert result.error is None

    def test_connected_but_model_not_loaded(self, adapter):
        mock_model = MagicMock()
        mock_model.model = "mistral"
        mock_resp = MagicMock()
        mock_resp.models = [mock_model]
        adapter._sync_client.list.return_value = mock_resp

        result = adapter.health_check()

        assert result.connected is True
        assert result.model == "llama3.1"
        assert result.model_loaded is False
        assert result.error is None

    def test_connect_error_returns_disconnected(self, adapter):
        adapter._sync_client.list.side_effect = httpx.ConnectError("connection refused")

        result = adapter.health_check()

        assert result.connected is False
        assert result.model == "llama3.1"
        assert result.model_loaded is False
        assert "connection refused" in result.error

    def test_response_error_returns_disconnected(self, adapter):
        adapter._sync_client.list.side_effect = OllamaResponseError("internal error")

        result = adapter.health_check()

        assert result.connected is False
        assert result.model == "llama3.1"
        assert result.model_loaded is False
        assert "internal error" in result.error
