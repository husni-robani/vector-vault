from dataclasses import dataclass

@dataclass
class MetaData:
    document_id: str # uuid
    chunk_index: int
    title: str

@dataclass
class Chunk:
    id: str
    text: str
    vector: list[float]
    metadata: MetaData

@dataclass
class SearchResult:
    chunk: Chunk
    score: float