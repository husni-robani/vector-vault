import sqlite3
import logging
from app.domain.documents import Document
from app.domain.exceptions import ExternalServiceError, NotFoundError
from app.application.ports import DocumentRepositoryPort

logger = logging.getLogger(__name__)

class SQLiteDocumentRepository(DocumentRepositoryPort):
    def __init__(self, database_file: str) -> None:
        self.conn: sqlite3.Connection = sqlite3.connect(database=database_file)
        self.conn.row_factory = sqlite3.Row

    def initialize_tables(self):
        cursor = self.conn.cursor()

        try: 
            with self.conn:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        file_type TEXT NOT NULL CHECK (file_type IN ('.md', '.pdf')),
                        status TEXT NOT NULL CHECK (status IN ('pending', 'processed', 'error')),
                        chunks_count INTEGER NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                ''')
        except Exception as e: 
            logger.exception("initialize tables failed")
            raise ExternalServiceError("initialize tables failed") from e

    def save(self, doc: Document):    
        cursor: sqlite3.Cursor = self.conn.cursor()

        try:
            with self.conn:
                cursor.execute("INSERT OR REPLACE INTO documents (id, title, filename, file_path, file_type, status, chunks_count, size_bytes, created_at, updated_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (doc.id, doc.title, doc.filename, doc.file_path, doc.file_type, doc.status, doc.chunks_count, doc.size_bytes, doc.created_at, doc.updated_at))
        except Exception as e:
            logger.exception(f"failed to insert document {doc.filename} into database")
            raise ExternalServiceError("failed to insert document") from e
        
    def find_all(self) -> list[Document]:
        cursor: sqlite3.Cursor = self.conn.cursor()
        all_documents: list[Document] = []
        try:
            with self.conn:
                cursor.execute("SELECT * FROM documents")

                for row in cursor:
                    row_dict = dict(row)
                    document: Document = Document(**row_dict)
                    all_documents.append(document)

        except Exception as e: 
            logger.exception("failed to get all documents")
            raise ExternalServiceError("failed to get all documents") from e

        
        return all_documents
    
    def find_by_id(self, doc_id: str) -> Document | None:
        cursor: sqlite3.Cursor = self.conn.cursor()

        try:
            with self.conn:
                cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id, ))
            
            row = cursor.fetchone()
            if row:
                return Document(**dict(row))
            
            return None
        except Exception as e:
            logger.exception("failed to get document by id")
            raise ExternalServiceError("failed to get document by id") from e

    def delete(self, doc_id: str):
        cursor: sqlite3.Cursor = self.conn.cursor()

        try: 
            with self.conn:
                cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id, ))
            
            if cursor.rowcount > 0:
                logger.info(f"deleted {cursor.rowcount} document")
            else:
                logger.info(f"document {doc_id} is not found")
        except Exception as e:
            logger.exception(f"failed to delete document({doc_id})")
            raise ExternalServiceError(f"failed to delete document({doc_id})") from e
        
    def close(self):
        self.conn.close()