from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """Application settings — read from environment variables / .env file."""
    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

_settings: Settings | None = None

def get_settings() -> Settings:
    """Singleton — creates Settings once, caches forever."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings