import math

import pytest

from app.infrastructure.embedding.hf_sentence_adapter import (
    SentenceTransformerEmbedding,
)

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_EMBEDDING_DIM = 384


@pytest.fixture(scope="module")
def embedder():
    return SentenceTransformerEmbedding(embedding_model=_MODEL_NAME)


def test_embed_returns_correct_dimensions(embedder):
    texts = ["first sentence", "second sentence"]

    vectors = embedder.embed(texts)

    assert len(vectors) == 2
    for v in vectors:
        assert len(v) == _EMBEDDING_DIM
        assert all(isinstance(x, float) for x in v)


def test_embed_normalizes_vectors(embedder):
    texts = ["test normalization"]

    vectors = embedder.embed(texts)

    v = vectors[0]
    magnitude = math.sqrt(sum(x * x for x in v))
    assert abs(magnitude - 1.0) < 1e-5


def test_embed_empty_list(embedder):
    vectors = embedder.embed([])

    assert vectors == []


def test_health_check_success(embedder):
    result = embedder.health_check()

    assert result.connected is True
    assert result.model_name == _MODEL_NAME
    assert result.error is None


def test_health_check_error(embedder, monkeypatch):
    def mock_encode_crash(*args, **kwargs):
        raise RuntimeError("Simulated model inference failure")

    monkeypatch.setattr(embedder.model, "encode", mock_encode_crash)

    result = embedder.health_check()

    assert result.connected is False
    assert result.model_name == _MODEL_NAME
    assert "Simulated model inference failure" in result.error
