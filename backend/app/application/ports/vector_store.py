from abc import ABC, abstractmethod
from app.domain.chunks import Chunk, SearchResult
from app.application.dto import VectorStoreHealth


class VectorStorePort(ABC):
    """Store and search vector embeddings for document chunks."""

    @abstractmethod
    def add_chunks(self, chunks: list[Chunk], vectors: list[list[float]]):
        """Index chunks with their corresponding embedding vectors.

        Args:
            chunks: Chunk entities containing text and metadata.
            vectors: Embedding vectors, one per chunk in the same order.
        """
        pass

    @abstractmethod
    def search(self, embedding: list[float], k: int = 5) -> list[SearchResult]:
        """Find the top-k most similar chunks for a query embedding.

        Args:
            embedding: The query vector to compare against.
            k: Number of results to return.

        Returns:
            Ranked search results with chunk and similarity score.
        """
        pass

    @abstractmethod
    def delete_by_document(self, document_id: str):
        """Remove all chunks belonging to a document.

        Args:
            document_id: The document whose chunks should be deleted.
        """
        pass

    @abstractmethod
    def health_check(self) -> VectorStoreHealth:
        """Verify the vector store is operational.

        Adapters should call the store's built-in health endpoint
        (e.g. ChromaDB's client.heartbeat()) and report the current
        number of collections. Return VectorStoreHealth(connected=True,
        collections_count=<int>) on success, or connected=False with an
        error message on failure.
        """
        pass
