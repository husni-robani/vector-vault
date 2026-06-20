from dataclasses import dataclass

@dataclass
class MetaData:
    document_id: str | None # uuid
    chunk_index: int | None
    title: str | None

@dataclass
class Chunk:
    id: str
    text: str | None
    vector: list[float] | None
    metadata: MetaData

@dataclass
class SearchResult:
    chunk: Chunk
    distance: float