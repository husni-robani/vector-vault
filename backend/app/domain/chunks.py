from dataclasses import dataclass

@dataclass
class MetaData:
    document_id: str # uuid
    chunk_index: int

@dataclass
class Chunk:
    id: str
    document: str
    metadata: MetaData

@dataclass
class SearchResult:
    chunk: Chunk
    score: float