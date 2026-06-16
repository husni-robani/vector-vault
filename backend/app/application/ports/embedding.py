from abc import ABC, abstractmethod
from app.application.dto import EmbeddingHealth


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

    @abstractmethod
    def health_check(self) -> EmbeddingHealth:
        """Verify the embedding model is loaded and operational.

        Since embedding models run in-process, adapters can simply
        report the model name and connected=True. Optionally, embed a
        trivial test string to validate the pipeline is working.
        Return EmbeddingHealth(connected=True, model_name=<name>) on
        success, or connected=False with an error message on failure.
        """
        pass
