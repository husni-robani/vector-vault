import pytest
from app.infrastructure.text_splitter.langchain_splitter import LangChainTextSplitter
from app.domain.documents import DocumentType


@pytest.fixture
def splitter():
    return LangChainTextSplitter()


@pytest.fixture
def splitter_large_chunks():
    return LangChainTextSplitter(chunk_size=2048, overlap=100)


@pytest.fixture
def splitter_tiny_chunks():
    return LangChainTextSplitter(chunk_size=50, overlap=0)


class TestLangChainTextSplitterPdf:
    def test_split_plain_text_returns_chunks(self, splitter):
        text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three."

        chunks = splitter.split(text, document_type=DocumentType.PDF)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        assert all(isinstance(c, str) for c in chunks)
        assert "paragraph one" in chunks[0]

    def test_split_empty_text_returns_empty_list(self, splitter):
        chunks = splitter.split("", document_type=DocumentType.PDF)

        assert chunks == []

    def test_split_single_short_text_returns_single_chunk(self, splitter):
        text = "short text"

        chunks = splitter.split(text, document_type=DocumentType.PDF)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_long_text_produces_multiple_chunks(self, splitter_tiny_chunks):
        text = " ".join(f"sentence number {i}" for i in range(200))

        chunks = splitter_tiny_chunks.split(text, document_type=DocumentType.PDF)

        assert len(chunks) > 1

    def test_honors_chunk_size(self, splitter_tiny_chunks):
        text = "A" * 200

        chunks = splitter_tiny_chunks.split(text, document_type=DocumentType.PDF)

        for chunk in chunks:
            assert len(chunk) <= 50


class TestLangChainTextSplitterMarkdown:
    def test_split_markdown_with_headers_produces_header_breadcrumbs(self, splitter):
        text = "# Title\nIntro content under the title.\n\n## Section One\nDetails about section one."

        chunks = splitter.split(text, document_type=DocumentType.MD)

        assert len(chunks) >= 2
        assert "# Title" in chunks[0]
        assert "## Section One" in chunks[1]

    def test_split_markdown_preserves_header_hierarchy(self, splitter):
        text = (
            "# H1 Title\nIntro.\n\n"
            "## H2 Section\nMore content.\n\n"
            "### H3 Subsection\nDeep content here."
        )

        chunks = splitter.split(text, document_type=DocumentType.MD)

        assert len(chunks) >= 3
        assert "# H1 Title > ## H2 Section > ### H3 Subsection" in chunks[2]

    def test_split_markdown_long_section_gets_sub_split(self, splitter_tiny_chunks):
        text = "# Title\n" + ("A" * 200)

        chunks = splitter_tiny_chunks.split(text, document_type=DocumentType.MD)

        assert len(chunks) > 1
        for chunk in chunks:
            assert "# Title" in chunk

    def test_split_markdown_empty_returns_empty_list(self, splitter):
        chunks = splitter.split("", document_type=DocumentType.MD)

        assert chunks == []

    def test_split_markdown_no_headers_still_works(self, splitter):
        text = "Just plain text without any markdown headers."

        chunks = splitter.split(text, document_type=DocumentType.MD)

        assert len(chunks) >= 1
        assert "Just plain text" in chunks[0]


class TestLangChainTextSplitterRouting:
    def test_md_type_routes_to_markdown_splitter(self, splitter):
        text = "# Header\nContent here."

        md_chunks = splitter.split(text, document_type=DocumentType.MD)
        pdf_chunks = splitter.split(text, document_type=DocumentType.PDF)

        assert md_chunks != pdf_chunks

    def test_custom_chunk_size_is_respected(self):
        small = LangChainTextSplitter(chunk_size=32, overlap=0)
        large = LangChainTextSplitter(chunk_size=2048, overlap=0)

        text = "A" * 512

        small_chunks = small.split(text, document_type=DocumentType.PDF)
        large_chunks = large.split(text, document_type=DocumentType.PDF)

        assert len(small_chunks) > len(large_chunks)
