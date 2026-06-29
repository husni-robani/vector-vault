from abc import ABC, abstractmethod
from app.domain.documents import DocumentType

class TextSplitterPort(ABC):
    """Break long text into smaller overlapping chunks for indexing."""

    @abstractmethod
    def split(self, text: str, *, document_type: DocumentType) -> list[str]:
        """Split a document's text into chunks. Strategy is dispatched based on document_type

        Args:
            text: The full plain-text content of a document.
            document_type: file type of document that siplitted

        Returns:
            A list of text chunks, typically with configurable size and overlap.
        """
        pass
