from abc import ABC, abstractmethod


class TextSplitterPort(ABC):
    """Break long text into smaller overlapping chunks for indexing."""

    @abstractmethod
    def split(self, text: str) -> list[str]:
        """Split a document's text into manageable chunks.

        Args:
            text: The full plain-text content of a document.

        Returns:
            A list of text chunks, typically with configurable size and overlap.
        """
        pass
