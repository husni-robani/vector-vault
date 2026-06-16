import pytest
from unittest.mock import MagicMock
from app.application.ports import (
    DocumentRepositoryPort,
    EmbeddingPort,
    FileStoragePort,
    LLMPort,
    VectorStorePort,
    TextSplitterPort,
    DocumentLoaderPort,
)
from app.domain.documents import Document, DocumentStatus, DocumentType
from app.domain.chunks import Chunk, MetaData, SearchResult


@pytest.fixture
def mock_file_storage():
    m = MagicMock(spec=FileStoragePort)
    m.save.return_value = "/data/uploads/test.md"
    return m


@pytest.fixture
def mock_document_loader():
    m = MagicMock(spec=DocumentLoaderPort)
    m.load.return_value = "This is the document content for testing."
    return m


@pytest.fixture
def mock_text_splitter():
    m = MagicMock(spec=TextSplitterPort)
    m.split.return_value = ["chunk one text", "chunk two text", "chunk three text"]
    return m


@pytest.fixture
def mock_embedder():
    m = MagicMock(spec=EmbeddingPort)
    m.embed.return_value = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
    return m


@pytest.fixture
def mock_vector_store():
    return MagicMock(spec=VectorStorePort)


@pytest.fixture
def mock_document_repo():
    return MagicMock(spec=DocumentRepositoryPort)


@pytest.fixture
def mock_llm():
    m = MagicMock(spec=LLMPort)
    m.generate.return_value = _async_mock_iterator(["Based", " on", " the", " context"])
    return m


@pytest.fixture
def sample_document():
    return Document(
        id="doc-123",
        title="test",
        filename="test.md",
        file_path="/data/uploads/test.md",
        file_type=DocumentType.MD,
        status=DocumentStatus.PROCESSED,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00",
    )


@pytest.fixture
def sample_search_results():
    return [
        SearchResult(
            chunk=Chunk(
                id="c1",
                document="context text one",
                metadata=MetaData(document_id="doc-1", chunk_index=0),
            ),
            score=0.92,
        ),
        SearchResult(
            chunk=Chunk(
                id="c2",
                document="context text two",
                metadata=MetaData(document_id="doc-1", chunk_index=1),
            ),
            score=0.87,
        ),
    ]


def _async_mock_iterator(values):
    async def gen():
        for v in values:
            yield v

    return gen()
