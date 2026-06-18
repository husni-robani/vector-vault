from dataclasses import dataclass

@dataclass
class IngestDocumentInput:
    filename: str
    title: str
    content: bytes

@dataclass
class IngestDocumentOutput:
    id: str     # document id
    filename: str
    file_type: str
    title: str
    status: str
