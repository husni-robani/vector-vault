import pytest
from app.infrastructure.vector_store.chromadb_adapter import ChromaDBVectorStore
from app.domain.chunks import Chunk, MetaData
from app.domain.exceptions import ExternalServiceError

@pytest.fixture
def vector_store(tmp_path: str):
    return ChromaDBVectorStore(
        persist_directory=tmp_path, 
        collection_name="asdf"
    )

def test_add_chunks_successfully(vector_store):
    chunks: list[Chunk] = [
        Chunk(
            id="1",
            text="Text 1",
            vector=[0.1, 0.2],
            metadata=MetaData(document_id="document_1", chunk_index=1, title="Document 1")
        ),
        Chunk(
            id="2",
            text="Text 2",
            vector=[0.1, 0.3],
            metadata=MetaData(document_id="document_1", chunk_index=2, title="Document 1")
        )
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
            metadata=MetaData(document_id="document_1", chunk_index=2, title="Document 1")
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
