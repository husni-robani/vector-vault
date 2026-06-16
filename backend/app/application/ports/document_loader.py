from abc import ABC, abstractmethod


class DocumentLoaderPort(ABC):
    """Extract raw text content from a document file."""

    @abstractmethod
    def load(self, path: str) -> str:
        """Read a file and return its full text content.

        Args:
            path: Filesystem path to the document (.md, .pdf, etc.).

        Returns:
            The extracted plain-text content of the file.
        """
        pass
