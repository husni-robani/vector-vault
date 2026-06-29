import logging

from app.application.ports import EmbeddingPort
from app.application.dto.health import EmbeddingHealth
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedding(EmbeddingPort):
    def __init__(self, embedding_model: str) -> None:
        self._model_name = embedding_model
        self.model = SentenceTransformer(model_name_or_path=embedding_model)
        super().__init__()

    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def health_check(self) -> EmbeddingHealth:
        try:
            self.model.encode(["health check"], normalize_embeddings=True)
            return EmbeddingHealth(
                connected=True, model_name=self._model_name, error=None
            )
        except Exception as e:
            logger.exception("Embedding health check failed")
            return EmbeddingHealth(
                connected=False, model_name=self._model_name, error=str(e)
            )
