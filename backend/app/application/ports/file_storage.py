from abc import ABC, abstractmethod
from pathlib import Path

class FileStoragePort(ABC):
    """Store and delete raw uploaded files on disk."""

    @abstractmethod
    def save(self, name: str, content: bytes) -> str:
        """Persist a file and return its storage path.

        Raises:
            FileAlreadyExistsError: If a file with this name already exists
            ExternalServiceError: If the storage backend fails (disk, network, permissions)

        Args:
            name: The filename to use when saving.
            content: Raw binary content of the file.

        Returns:
            The absolute or relative path where the file was written.
        """
        pass

    @abstractmethod
    def delete(self, path: Path):
        """Remove a previously saved file.

        Args:
            path: The file path returned by a prior save() call.
        """
        pass
