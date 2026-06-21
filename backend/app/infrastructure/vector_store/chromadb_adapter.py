import chromadb
import logging
from app.application.ports import VectorStorePort
from app.domain.chunks import Chunk, SearchResult
from app.application.dto.health import VectorStoreHealth
from app.domain.exceptions import ExternalServiceError
from app.domain.chunks import MetaData
from typing import cast

logger = logging.getLogger(__name__)


class ChromaDBVectorStore(VectorStorePort):
    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        distance_function: str = "cosine",
    ):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": distance_function}
        )

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
                ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas
            )
        except Exception as e:
            logger.exception("ChromaDB failed to insert chunks")
            raise ExternalServiceError(
                "Failed to store chunks in vector database"
            ) from e

    def search(self, embedding: list[float], k: int = 5) -> list[SearchResult]:

        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=k,
                include=["documents", "metadatas", "embeddings", "distances"],
            )
        except Exception as e:
            logger.exception("ChromaDB failed to search")
            raise ExternalServiceError("ChromaDB failed to search") from e

        search_results: list[SearchResult] = []

        ids = results.get("ids")
        if not ids or not ids[0]:
            return []

        documents = results.get("documents")
        metadatas = results.get("metadatas")
        embeddings = results.get("embeddings")
        distances = results.get("distances")

        for i in range(len(ids[0])):
            chunk = Chunk(
                id=ids[0][i],
                text=documents[0][i] if documents else None,
                vector=cast("list[float] | None", embeddings[0][i])
                if embeddings
                else None,
                metadata=MetaData(
                    document_id=cast("str | None", metadatas[0][i].get("document_id"))
                    if metadatas
                    else None,
                    chunk_index=cast("int | None", metadatas[0][i].get("chunk_index"))
                    if metadatas
                    else None,
                    title=cast("str | None", metadatas[0][i].get("title"))
                    if metadatas
                    else None,
                ),
            )
            search_results.append(
                SearchResult(chunk=chunk, distance=distances[0][i] if distances else 1)
            )

        return search_results

    def delete_by_document(self, document_id: str):
        try:
            result = self.collection.delete(where={"document_id": document_id})
            logger.info(f"total chunks deleted: {result['deleted']}")
        except Exception as e:
            logger.exception("ChromaDB failed to delete data")
            raise ExternalServiceError("Failed to delete data from collection") from e

    def health_check(self) -> VectorStoreHealth:
        try:
            self.client.heartbeat()
            collections_count = len(self.client.list_collections())
            return VectorStoreHealth(
                connected=True, collections_count=collections_count, error=None
            )
        except Exception as e:
            logger.exception("ChromaDB health check failed")
            return VectorStoreHealth(connected=False, collections_count=0, error=str(e))
