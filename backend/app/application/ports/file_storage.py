from abc import ABC, abstractmethod


class FileStoragePort(ABC):
    """Store and delete raw uploaded files on disk."""

    @abstractmethod
    def save(self, name: str, content: bytes) -> str:
        """Persist a file and return its storage path.

        Args:
            name: The filename to use when saving.
            content: Raw binary content of the file.

        Returns:
            The absolute or relative path where the file was written.
        """
        pass

    @abstractmethod
    def delete(self, path: str):
        """Remove a previously saved file.

        Args:
            path: The file path returned by a prior save() call.
        """
        pass
