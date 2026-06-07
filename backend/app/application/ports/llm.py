from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


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
