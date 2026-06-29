import logging
from pathlib import Path
from app.domain.exceptions import FileAlreadyExistsError, ExternalServiceError

logger = logging.getLogger(__name__)

class LocalFileStorage:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path: Path =  storage_path

    def save(self, name: str, content: bytes) -> str:
        target_file = self.storage_path / name

        self.storage_path.mkdir(parents=True, exist_ok=True)

        try: 
            with open(target_file, "xb") as file:
                file.write(content)

            final_absoulte_path = target_file.resolve()
            logger.info(f"file saved successfully: {target_file}")

            return str(final_absoulte_path)
        except FileExistsError as e:
            logger.exception(f"file {target_file} already exists")
            raise FileAlreadyExistsError("file already exists") from e
        except Exception as e:
            logger.exception(f"Failed to save file {target_file}")
            raise ExternalServiceError("Failed to save file") from e
    
    def delete(self, path: Path):
        try: 
            path.unlink(missing_ok=True)
        except FileNotFoundError:
            logger.warning(f"'{path}' not found")
        
        logger.info(f"'{path}' has been deleted (or was already gone)")