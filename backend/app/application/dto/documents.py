from dataclasses import dataclass

@dataclass
class IngestDocumentInput:
    filename: str
    content: bytes

@dataclass
class IngestDocumentOutput:
    id: str     # document id
    filename: str
    status: str