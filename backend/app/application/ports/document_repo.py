from abc import ABC, abstractmethod
from domain.documents import Document


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
    def find_all(self) -> list[Document]:
        """List all stored documents.

        Returns:
            All document records currently in the repository.
        """
        pass

    @abstractmethod
    def find_by_id(self, id: str) -> Document:
        """Look up a single document by its unique ID.

        Args:
            id: The document UUID.

        Returns:
            The matching document entity.
        """
        pass

    @abstractmethod
    def delete(self, id: str):
        """Remove a document record by ID.

        Args:
            id: The document UUID to delete.
        """
        pass
