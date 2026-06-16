import pytest
from app.application.use_cases.answer_question import AnswerQuestionUseCase
from app.application.dto import AnswerQuestionOutput


class TestAnswerQuestion:
    @pytest.mark.asyncio
    async def test_execute_returns_answer_question_output(
        self, mock_embedder, mock_llm, mock_vector_store, sample_search_results
    ):
        mock_vector_store.search.return_value = sample_search_results
        mock_embedder.embed.return_value = [[0.5] * 384]

        uc = AnswerQuestionUseCase(mock_embedder, mock_llm, mock_vector_store)
        result = await uc.execute("What is machine learning?")

        assert isinstance(result, AnswerQuestionOutput)

    @pytest.mark.asyncio
    async def test_execute_embeds_question_and_searches(
        self, mock_embedder, mock_llm, mock_vector_store, sample_search_results
    ):
        mock_vector_store.search.return_value = sample_search_results
        mock_embedder.embed.return_value = [[0.5] * 384]

        uc = AnswerQuestionUseCase(mock_embedder, mock_llm, mock_vector_store)
        await uc.execute("What is machine learning?")

        mock_embedder.embed.assert_called_once_with(texts=["What is machine learning?"])
        mock_vector_store.search.assert_called_once_with(embedding=[0.5] * 384)

    @pytest.mark.asyncio
    async def test_execute_builds_prompt_with_context_and_question(
        self, mock_embedder, mock_llm, mock_vector_store, sample_search_results
    ):
        mock_vector_store.search.return_value = sample_search_results
        mock_embedder.embed.return_value = [[0.5] * 384]

        uc = AnswerQuestionUseCase(mock_embedder, mock_llm, mock_vector_store)
        await uc.execute("What is machine learning?")

        mock_llm.generate.assert_called_once()
        prompt_arg = mock_llm.generate.call_args[1]["prompt"]
        assert "What is machine learning?" in prompt_arg
        assert "context text one" in prompt_arg
        assert "context text two" in prompt_arg

    @pytest.mark.asyncio
    async def test_execute_returns_sources_from_search_results(
        self, mock_embedder, mock_llm, mock_vector_store, sample_search_results
    ):
        mock_vector_store.search.return_value = sample_search_results
        mock_embedder.embed.return_value = [[0.5] * 384]

        uc = AnswerQuestionUseCase(mock_embedder, mock_llm, mock_vector_store)
        result = await uc.execute("What is machine learning?")

        assert len(result.sources) == 2
        assert result.sources[0].title == "doc-1"
        assert result.sources[0].chunk_index == 0
        assert result.sources[0].score == 0.92
        assert result.sources[0].snippet == "context text one"
        assert result.sources[1].title == "doc-1"
        assert result.sources[1].chunk_index == 1
        assert result.sources[1].score == 0.87
        assert result.sources[1].snippet == "context text two"

    @pytest.mark.asyncio
    async def test_execute_empty_search_results_builds_empty_context(
        self, mock_embedder, mock_llm, mock_vector_store
    ):
        mock_vector_store.search.return_value = []
        mock_embedder.embed.return_value = [[0.5] * 384]

        uc = AnswerQuestionUseCase(mock_embedder, mock_llm, mock_vector_store)
        result = await uc.execute("What is machine learning?")

        assert result.sources == []
        prompt_arg = mock_llm.generate.call_args[1]["prompt"]
        assert "What is machine learning?" in prompt_arg

    @pytest.mark.asyncio
    async def test_execute_token_stream_yields_tokens(
        self, mock_embedder, mock_llm, mock_vector_store, sample_search_results
    ):
        mock_vector_store.search.return_value = sample_search_results
        mock_embedder.embed.return_value = [[0.5] * 384]

        uc = AnswerQuestionUseCase(mock_embedder, mock_llm, mock_vector_store)
        result = await uc.execute("What is machine learning?")

        tokens = []
        async for token in result.token_stream:
            tokens.append(token)

        assert tokens == ["Based", " on", " the", " context"]
