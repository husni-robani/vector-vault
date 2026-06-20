import logging

from app.application.ports import EmbeddingPort, LLMPort, VectorStorePort
from app.domain.chunks import SearchResult
from app.application.dto import AnswerQuestionOutput, SourceInfo, AnswerQuestionInput
from app.domain.exceptions import ExternalServiceError
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class AnswerQuestionUseCase:
    _PROMPT_TEMPLATE = """You are Vector Vault, a personal knowledge assistant. Answer the user's question based only on the following context from their personal documents. If the context doesn't contain enough information, say so honestly.

    Context:
    {context}

    Question: {question}

    Answer:"""

    def __init__(
        self, 
        embedder: EmbeddingPort, 
        llm: LLMPort, 
        vector_store: VectorStorePort,
    ) -> None:
        self._embedder: EmbeddingPort = embedder
        self._llm: LLMPort = llm
        self._vector_store: VectorStorePort = vector_store

    async def execute(self, input: AnswerQuestionInput) -> AnswerQuestionOutput:
        try:
            question_embeded: list[list[float]] = self._embedder.embed(
                texts=[input.question]
            )
        except Exception as e:
            logger.exception("Embedding service failed during question processing")
            raise ExternalServiceError("Embedding service failed") from e

        try:
            search_results: list[SearchResult] = self._vector_store.search(
                embedding=question_embeded[0]
            )
        except Exception as e:
            logger.exception("Vector store search failed")
            raise ExternalServiceError("Vector store search failed") from e

        # build prompt
        prompt: str = self._build_prompt(
            question=input.question, results=search_results
        )

        try:
            token_stream: AsyncIterator[str] = self._llm.generate(prompt=prompt)
        except Exception as e:
            logger.exception("LLM generation failed")
            raise ExternalServiceError("LLM generation failed") from e

        # build sources metadata
        sources: list[SourceInfo] = [
            SourceInfo(
                title=result.chunk.metadata.title,
                chunk_index=result.chunk.metadata.chunk_index,
                distance=result.distance,
                snippet=(result.chunk.text or "")[:100],
            )
            for result in search_results
        ]

        return AnswerQuestionOutput(token_stream=token_stream, sources=sources)

    def _build_prompt(self, question: str, results: list[SearchResult]) -> str:
        context = "\n\n".join(result.chunk.text or "" for result in results)
        return self._PROMPT_TEMPLATE.format(context=context, question=question)
