from dataclasses import dataclass


@dataclass
class LLMHealth:
    connected: bool
    model: str
    model_loaded: bool
    error: str | None = None


@dataclass
class VectorStoreHealth:
    connected: bool
    collections_count: int
    error: str | None = None


@dataclass
class EmbeddingHealth:
    connected: bool
    model_name: str
    error: str | None = None


@dataclass
class HealthCheckResult:
    status: str
    llm: LLMHealth
    vector_store: VectorStoreHealth
    embedding: EmbeddingHealth
