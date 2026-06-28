import logging

import httpx
from ollama import AsyncClient, Client
from ollama import ResponseError as OllamaResponseError

from app.application.dto.health import LLMHealth
from app.application.ports import LLMPort
from app.domain.exceptions import ExternalServiceError
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class OllamaLLM(LLMPort):
    def __init__(self, base_url: str, model: str) -> None:
        self._async_client = AsyncClient(host=base_url)
        self._sync_client = Client(host=base_url)
        self._model: str = model
        self._base_url: str = base_url

    async def generate(self, prompt: str) -> AsyncIterator[str]:

        try:
            stream = await self._async_client.generate(
                model=self._model, prompt=prompt, stream=True, raw=True
            )
        except httpx.ConnectError as e:
            # Ollama process not running, wrong port, network down
            raise ExternalServiceError(
                f"Cannot connect to Ollama at {self._base_url}"
            ) from e
        except OllamaResponseError as e:
            logger.exception("Ollama generate response failed")
            raise ExternalServiceError("Ollama generate response failed") from e

        async for chunk in stream:
            if chunk.response:
                yield chunk.response

    def health_check(self) -> LLMHealth:
        try:
            resp = self._sync_client.list()
        except httpx.ConnectError as e:
            return LLMHealth(
                connected=False, model=self._model, model_loaded=False, error=str(e)
            )
        except OllamaResponseError as e:
            return LLMHealth(
                connected=False, model=self._model, model_loaded=False, error=str(e)
            )
        names = [m.model for m in resp.models]
        return LLMHealth(
            connected=True, model=self._model, model_loaded=self._model in names
        )
