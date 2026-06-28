from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings — read from environment variables / .env file."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # Vector Store
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_name: str = "vector_vault_chunks"
    distance_threshold: float = 0.7
    top_k: int = 5

    # Document Repository
    sqlite_db_path: str = "./data/vault.db"

    # File Storage
    upload_dir: str = "./data/uploads"

    # Text Splitter
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Upload
    max_upload_size_mb: int = 50

    # Frontend
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Singleton — creates Settings once, caches forever."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
