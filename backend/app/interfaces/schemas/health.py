from pydantic import BaseModel


class OllamaHealthResponse(BaseModel):
    connected: bool
    model: str
    model_loaded: bool
    error: str | None = None


class ChromadbHealthResponse(BaseModel):
    connected: bool
    collections_count: int
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    ollama: OllamaHealthResponse
    chromadb: ChromadbHealthResponse
    embedding_model: str
