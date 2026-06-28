import logging
from app.application.ports import DocumentLoaderPort
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from app.domain.documents import DocumentType
from pathlib import Path
from app.domain.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class LangChainDocumentLoader(DocumentLoaderPort):
    def __init__(self) -> None:
        super().__init__()

    def load(self, path: str) -> str:
        filename = Path(path).name
        
        match DocumentType.from_filename(filename=filename):
            case DocumentType.MD:
                with open(path, encoding="utf-8") as f:
                    return f.read()
            case DocumentType.PDF:
                docs = PyMuPDF4LLMLoader(path, mode="single").load()
                if not docs:
                    raise ExternalServiceError(f"PyMuPDF returned no content for {path}")
                return docs[0].page_content

