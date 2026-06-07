from dataclasses import dataclass
from enum import StrEnum

class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    id: str # uuid
    conversation_id: str # uuid
    role: MessageRole
    content: str
    source_document_ids: list[str] # RAG citation (which docs grounded this answer)
    created_at: str

@dataclass
class Conversation:
    id: str # uuid
    title: str
    created_at: str