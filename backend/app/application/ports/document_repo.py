from abc import ABC, abstractmethod
from app.domain.documents import Document


class DocumentRepositoryPort(ABC):
    """Persist and retrieve document metadata records."""

    @abstractmethod
    def save(self, doc: Document):
        """Create or update a document record.

        Args:
            doc: The document entity to persist.
        """
        pass

    @abstractmethod
    def find_all(
        self, page: int | None = None, limit: int = 50
    ) -> tuple[list[Document], int]:
        """List documents with optional pagination.

        Args:
            page: 1-indexed page number. None returns all documents.
            limit: Page size (ignored when page is None).

        Returns:
            Tuple of (documents, total_count).
        """
        pass

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Document | None:
        """Look up a single document by its unique ID.

        Args:
            id: The document UUID.

        Returns:
            The matching document entity.
        """
        pass

    @abstractmethod
    def find_by_filename(self, filename: str) -> Document | None:
        """Look up a single document by filename.

        Args: 
            filename: document filename.

        Returns: 
            The matching document entity.
        """

    @abstractmethod
    def delete(self, doc_id: str):
        """Remove a document record by ID.

        Args:
            id: The document UUID to delete.
        """
        pass

    @abstractmethod
    def close(self):
        pass
