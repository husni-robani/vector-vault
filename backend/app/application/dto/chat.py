from dataclasses import dataclass
from collections.abc import AsyncIterator

@dataclass
class SourceInfo:
    title: str | None
    chunk_index: int | None
    distance: float | None
    snippet: str | None

@dataclass
class AnswerQuestionOutput:
    token_stream: AsyncIterator[str]
    sources: list[SourceInfo]

@dataclass
class AnswerQuestionInput:
    question: str
