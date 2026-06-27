from app.application.ports import TextSplitterPort
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from app.domain.documents import DocumentType


class LangChainTextSplitter(TextSplitterPort):
    def __init__(self, chunk_size: int = 512, overlap: int = 30) -> None:
        md_headers_to_split_on = [("#", "H1"), ("##", "H2"), ("###", "H3")]
        self._header_splitter = MarkdownHeaderTextSplitter(
            md_headers_to_split_on, strip_headers=True
        )

        self._char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", " ", ""],
        )

        self._chunk_size = chunk_size

    def split(self, text: str, *, document_type: DocumentType) -> list[str]:
        if document_type == DocumentType.MD:
            return self._split_markdown(text=text)

        return self._split_pdf(text=text)

    def _split_markdown(self, text: str) -> list[str]:
        header_splits = self._header_splitter.split_text(text=text)

        chunks: list[str] = []

        for section in header_splits:
            header_metadata = self._build_header_path(section.metadata)

            if len(section.page_content) <= self._chunk_size:
                prefix = f"{header_metadata}\n\n" if header_metadata else ""
                chunks.append(f"{prefix}{section.page_content}")
            else:
                sub_chunks = self._char_splitter.split_text(section.page_content)
                prefix = f"{header_metadata}\n\n" if header_metadata else ""
                chunks.extend(f"{prefix}{sub}" for sub in sub_chunks)
        return chunks

    def _split_pdf(self, text: str) -> list[str]:
        return self._char_splitter.split_text(text=text)

    @staticmethod
    def _build_header_path(metadata: dict) -> str:
        """Build a breadcrumb like '## Kubernetes > Networking' from header metadata."""
        parts = []
        for key in ("H1", "H2", "H3"):
            if key in metadata and metadata[key]:
                level = int(key[1])  # H1 → 1, H2 → 2
                parts.append(f"{'#' * level} {metadata[key]}")
        return " > ".join(parts) if parts else ""
