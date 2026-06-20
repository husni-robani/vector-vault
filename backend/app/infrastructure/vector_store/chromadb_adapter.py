import chromadb
import logging
from app.application.ports import VectorStorePort
from app.domain.chunks import Chunk, SearchResult
from app.application.dto.health import VectorStoreHealth
from app.domain.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class ChromaDBVectorStore(VectorStorePort):
    def __init__(self, persist_directory: str, collection_name: str):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(self, chunks: list[Chunk]):
        
        ids = []
        vectors = []
        texts = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk.id)
            vectors.append(chunk.vector)
            texts.append(chunk.text)
            metadatas.append(chunk.metadata.__dict__)

        try: 
            self.collection.add(
                ids=ids,
                embeddings=vectors,
                documents=texts,
                metadatas=metadatas
            )
        except Exception as e:
            logger.exception("ChromaDB failed to insert chunks")
            raise ExternalServiceError("Failed to store chunks in vector database") from e
        
    def search(self, embedding: list[float], k: int = 5) -> list[SearchResult]:
        return []
    
    def delete_by_document(self, document_id: str):
        return
    
    def health_check(self) -> VectorStoreHealth:
        return VectorStoreHealth(connected=True, collections_count=1, error="")
    