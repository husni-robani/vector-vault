import pytest
from app.infrastructure.document_loader.langchain_loader import LangChainDocumentLoader
from app.domain.exceptions import ExternalServiceError, UnsupportedFileTypeError
from langchain_pymupdf4llm import PyMuPDF4LLMLoader


def _make_minimal_pdf(text: str = "Hello PDF World") -> bytes:
    header = b"%PDF-1.4\n"

    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    obj2 = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    obj3 = (
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
        b"endobj\n"
    )
    content = f"BT /F1 12 Tf 100 700 Td ({text}) Tj ET".encode()
    obj4 = (
        b"4 0 obj\n<< /Length %d >>\nstream\n" % len(content)
        + content
        + b"\nendstream\nendobj\n"
    )
    obj5 = b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"

    body_parts = [obj1, obj2, obj3, obj4, obj5]
    body = header
    xref_table = ""
    for obj in body_parts:
        xref_table += f"{len(body):010d} 00000 n \n"
        body += obj

    xref_offset = len(body)
    xref = f"xref\n0 6\n0000000000 65535 f \n{xref_table}".encode()
    trailer = (
        f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )

    return body + xref + trailer


@pytest.fixture
def loader():
    return LangChainDocumentLoader()


def test_load_md_returns_content(loader, tmp_path):
    md_path = tmp_path / "test.md"
    md_path.write_text("# Hello Markdown\n\nSome content here.")

    content = loader.load(str(md_path))

    assert content == "# Hello Markdown\n\nSome content here."


def test_load_md_utf8_encoding(loader, tmp_path):
    md_path = tmp_path / "utf8.md"
    md_path.write_text("日本語\némojis 🚀\n")

    content = loader.load(str(md_path))

    assert content == "日本語\némojis 🚀\n"


def test_load_pdf_returns_content(loader, tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(_make_minimal_pdf("Hello PDF World"))

    content = loader.load(str(pdf_path))

    assert len(content) > 0
    assert "Hello PDF World" in content


def test_load_pdf_empty_content_raises(loader, tmp_path, monkeypatch):
    pdf_path = tmp_path / "empty.pdf"
    pdf_path.write_bytes(_make_minimal_pdf())

    def mock_load_empty(*args, **kwargs):
        return []

    monkeypatch.setattr(PyMuPDF4LLMLoader, "load", mock_load_empty)

    with pytest.raises(ExternalServiceError, match="PyMuPDF returned no content"):
        loader.load(str(pdf_path))


def test_load_unsupported_file_type_raises(loader, tmp_path):
    bad_path = tmp_path / "test.xyz"
    bad_path.write_text("whatever")

    with pytest.raises(UnsupportedFileTypeError):
        loader.load(str(bad_path))


def test_load_nonexistent_file_raises(loader):
    with pytest.raises(FileNotFoundError):
        loader.load("/nonexistent/path/doc.md")


def test_load_pdf_external_error_raises(loader, tmp_path, monkeypatch):
    pdf_path = tmp_path / "crash.pdf"
    pdf_path.write_bytes(_make_minimal_pdf())

    def mock_load_crash(*args, **kwargs):
        raise RuntimeError("Simulated PDF parsing failure")

    monkeypatch.setattr(PyMuPDF4LLMLoader, "load", mock_load_crash)

    with pytest.raises(RuntimeError, match="Simulated PDF parsing failure"):
        loader.load(str(pdf_path))
