from pydantic import Field, BaseModel
from typing import Literal
from app.application.dto import SourceInfo

class ChatRequest(BaseModel):
    message: str = Field()
    conversation_id: str


# SSE response schemas
class DoneEventData(BaseModel):
    type: Literal["done"] = "done"
    conversation_id: str | None

class SourcesEventData(BaseModel):
    type: Literal["sources"] = "sources"
    sources: list[SourceInfo]

class DeliveryEventData(BaseModel):
    type: Literal["token"] = "token"
    content: str

class ErrorEventData(BaseModel):
    type: Literal["error"] = "error"
    message: str