import math

import pytest

from app.infrastructure.vector_store.chromadb_adapter import ChromaDBVectorStore
from app.domain.chunks import Chunk, MetaData
from app.domain.exceptions import ExternalServiceError


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(x * x for x in vector))
    return [x / magnitude for x in vector]


@pytest.fixture
def vector_store(tmp_path: str):
    return ChromaDBVectorStore(persist_directory=tmp_path, collection_name="asdf")


def test_add_chunks_successfully(vector_store):
    chunks: list[Chunk] = [
        Chunk(
            id="1",
            text="Text 1",
            vector=[0.1, 0.2],
            metadata=MetaData(
                document_id="document_1", chunk_index=1, title="Document 1"
            ),
        ),
        Chunk(
            id="2",
            text="Text 2",
            vector=[0.1, 0.3],
            metadata=MetaData(
                document_id="document_1", chunk_index=2, title="Document 1"
            ),
        ),
    ]

    vector_store.add_chunks(chunks=chunks)
    result = vector_store.collection.get(ids=["1", "2"])

    assert len(result["ids"]) == 2
    assert "Text 1" in result["documents"]
    assert "Text 2" in result["documents"]


def test_add_chunks_error(vector_store, monkeypatch):
    chunk = Chunk(
        id="2",
        text="Text 2",
        vector=[0.1, 0.3],
        metadata=MetaData(document_id="document_1", chunk_index=2, title="Document 1"),
    )

    # Simulate a catastrophic failure in the external library (ChromaDB)
    # We use pytest's monkeypatch to force the underlying .add() method to crash
    def mock_add_crash(*args, **kwargs):
        raise RuntimeError("Simulated out-of-memory or database crash")

    monkeypatch.setattr(vector_store.collection, "add", mock_add_crash)

    # 2 & 3. Act & Assert: Verify that our adapter catches the RuntimeError
    # and raises our specific domain exception instead.
    with pytest.raises(ExternalServiceError) as exc_info:
        vector_store.add_chunks(chunks=[chunk])

    # Verify the error message contains the expected domain context
    assert "Failed to store chunks in vector database" in str(exc_info.value)


def test_delete_data_successfully(vector_store):
    # 1. Arrange: Add a chunk first
    chunk = Chunk(
        id="chunk_to_delete",
        text="Text to be deleted",
        vector=[0.5, 0.6],
        metadata=MetaData(document_id="document_1", chunk_index=1, title="Doc"),
    )
    vector_store.add_chunks(chunks=[chunk])

    # Verify the chunk exists before deletion
    result_before = vector_store.collection.get(ids=["chunk_to_delete"])
    assert len(result_before["ids"]) == 1

    # 2. Act: Delete the chunk
    vector_store.delete_by_document(document_id="chunk_to_delete")

    # 3. Assert: Verify the chunk is gone
    result_after = vector_store.collection.get(ids=["chunk_to_delete"])
    assert len(result_after["ids"]) == 0


def test_delete_data_error(vector_store, monkeypatch):
    chunk = Chunk(
        id="3",
        text="Text 3",
        vector=[0.7, 0.8],
        metadata=MetaData(document_id="document_1", chunk_index=3, title="Doc"),
    )
    vector_store.add_chunks(chunks=[chunk])

    def mock_delete_crash(*args, **kwargs):
        raise RuntimeError("Simulated database crash")

    monkeypatch.setattr(vector_store.collection, "delete", mock_delete_crash)

    with pytest.raises(ExternalServiceError) as exc_info:
        vector_store.delete_by_document(document_id="3")

    assert "Failed to delete data from collection" in str(exc_info.value)


def test_search_data_successfully(vector_store):
    relevant_chunks = [
        Chunk(
            id="chunk-rag-1",
            text="Vector Vault uses Clean Architecture with ports and adapters to decouple business logic from infrastructure.",
            vector=_normalize([0.85, 0.75, 0.10, 0.10]),
            metadata=MetaData(
                document_id="doc-arch", chunk_index=0, title="Architecture Overview"
            ),
        ),
        Chunk(
            id="chunk-rag-2",
            text="The AnswerQuestionUseCase embeds the user question and searches ChromaDB for the most similar document chunks.",
            vector=_normalize([0.80, 0.70, 0.10, 0.10]),
            metadata=MetaData(
                document_id="doc-rag", chunk_index=0, title="RAG Pipeline"
            ),
        ),
        Chunk(
            id="chunk-rag-3",
            text="ChromaDB stores document chunks as vector embeddings and supports cosine similarity search for retrieval.",
            vector=_normalize([0.78, 0.72, 0.15, 0.10]),
            metadata=MetaData(
                document_id="doc-rag", chunk_index=1, title="RAG Pipeline"
            ),
        ),
    ]

    irrelevant_chunks = [
        Chunk(
            id="chunk-setup-1",
            text="To install dependencies, run pip install -r requirements.txt in the backend directory.",
            vector=_normalize([0.10, 0.10, 0.85, 0.75]),
            metadata=MetaData(
                document_id="doc-setup", chunk_index=0, title="Getting Started"
            ),
        ),
        Chunk(
            id="chunk-setup-2",
            text="The frontend is built with Vue 3 and Vite, providing a responsive single-page application interface.",
            vector=_normalize([0.10, 0.10, 0.80, 0.70]),
            metadata=MetaData(
                document_id="doc-frontend", chunk_index=0, title="Frontend Setup"
            ),
        ),
    ]

    all_chunks = relevant_chunks + irrelevant_chunks
    vector_store.add_chunks(chunks=all_chunks)

    query_vector = _normalize([0.85, 0.75, 0.10, 0.10])

    results = vector_store.search(embedding=query_vector, k=3)

    assert len(results) == 3

    for i in range(len(results) - 1):
        assert results[i].distance <= results[i + 1].distance

    result_ids = {r.chunk.id for r in results}
    relevant_ids = {c.id for c in relevant_chunks}
    assert result_ids == relevant_ids

    for r in results:
        assert r.distance < 0.01, (
            f"Expected distance < 0.01 for {r.chunk.id}, got {r.distance}"
        )
        assert isinstance(r.distance, float)

    for r in results:
        original = next(c for c in all_chunks if c.id == r.chunk.id)
        assert r.chunk.text == original.text
        assert r.chunk.metadata.document_id == original.metadata.document_id
        assert r.chunk.metadata.chunk_index == original.metadata.chunk_index
        assert r.chunk.metadata.title == original.metadata.title


def test_search_data_error(vector_store, monkeypatch):
    chunk = Chunk(
        id="1",
        text="Text 1",
        vector=[0.1, 0.2],
        metadata=MetaData(document_id="document_1", chunk_index=1, title="Doc 1"),
    )
    vector_store.add_chunks(chunks=[chunk])

    def mock_query_crash(*args, **kwargs):
        raise RuntimeError("Simulated database crash")

    monkeypatch.setattr(vector_store.collection, "query", mock_query_crash)

    with pytest.raises(ExternalServiceError) as exc_info:
        vector_store.search(embedding=[0.1, 0.2])

    assert "ChromaDB failed to search" in str(exc_info.value)
