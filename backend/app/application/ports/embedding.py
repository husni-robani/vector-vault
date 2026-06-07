from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """Convert text into numerical vector representations (embeddings)."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts.

        Args:
            texts: One or more text strings to embed.

        Returns:
            A list of embedding vectors, one per input text, each as a list of floats.
        """
        pass
