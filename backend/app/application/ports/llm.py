from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from app.application.dto import LLMHealth


class LLMPort(ABC):
    """Generate text responses from a language model given a prompt."""

    @abstractmethod
    def generate(self, prompt: str) -> AsyncIterator[str]:
        """Stream a response from the LLM token by token.

        Args:
            prompt: The full prompt string to send to the model.

        Returns:
            An async iterator yielding response tokens as strings.
        """
        pass

    @abstractmethod
    def health_check(self) -> LLMHealth:
        """Verify the LLM service is reachable and the configured model is available.

        Adapters should probe the LLM API (e.g. GET /api/tags on Ollama)
        to confirm connectivity and check if the configured model is downloaded.
        Return LLMHealth(connected=True, model=<name>, model_loaded=<bool>)
        on success, or connected=False with an error message on failure.
        """
        pass
