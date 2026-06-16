from dataclasses import dataclass
from collections.abc import AsyncIterator

@dataclass
class SourceInfo:
    title: str
    chunk_index: int
    score: float
    snippet: str

@dataclass
class AnswerQuestionOutput:
    token_stream: AsyncIterator[str]
    sources: list[SourceInfo]
