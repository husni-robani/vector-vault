from app.application.ports import EmbeddingPort, LLMPort, VectorStorePort
from app.domain.chunks import SearchResult
from app.application.dto import AnswerQuestionOutput, SourceInfo
from collections.abc import AsyncIterator


class AnswerQuestionUseCase:
    _PROMPT_TEMPLATE = """You are Vector Vault, a personal knowledge assistant. Answer the user's question based only on the following context from their personal documents. If the context doesn't contain enough information, say so honestly.

    Context:
    {context}

    Question: {question}

    Answer:"""

    def __init__(
        self, embedder: EmbeddingPort, llm: LLMPort, vector_store: VectorStorePort
    ) -> None:
        self._embedder: EmbeddingPort = embedder
        self._llm: LLMPort = llm
        self._vector_store: VectorStorePort = vector_store

    async def execute(self, question: str) -> AnswerQuestionOutput:
        # embed question
        question_embeded: list[list[float]] = self._embedder.embed(texts=[question])

        # search
        search_results: list[SearchResult] = self._vector_store.search(
            embedding=question_embeded[0]
        )

        # build prompt
        prompt: str = self._build_prompt(
            question=question, search_results=search_results
        )

        # generate response from LLM
        token_stream: AsyncIterator[str] = self._llm.generate(prompt=prompt)

        # build sources metadata
        sources: list[SourceInfo] = [
            SourceInfo(
                title=result.chunk.metadata.document_id,
                chunk_index=result.chunk.metadata.chunk_index,
                score=result.score,
                snippet=result.chunk.document[:100],
            )
            for result in search_results
        ]

        return AnswerQuestionOutput(token_stream=token_stream, sources=sources)

    def _build_prompt(self, question: str, search_results: list[SearchResult]) -> str:
        context = "\n\n".join(result.chunk.document for result in search_results)
        return self._PROMPT_TEMPLATE.format(context=context, question=question)
