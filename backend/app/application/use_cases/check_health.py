from ports import EmbeddingPort, LLMPort, VectorStorePort
from dto import HealthCheckResult, LLMHealth, VectorStoreHealth, EmbeddingHealth


class HealthCheckUseCase:
    def __init__(
        self,
        llm: LLMPort,
        vector_store: VectorStorePort,
        embedder: EmbeddingPort,
    ) -> None:
        self._llm: LLMPort = llm
        self._vector_store: VectorStorePort = vector_store
        self._embedder: EmbeddingPort = embedder

    def execute(self) -> HealthCheckResult:
        try:
            llm_health = self._llm.health_check()
        except Exception as e:
            llm_health = LLMHealth(
                connected=False, model="unknown", model_loaded=False, error=str(e)
            )

        try:
            vs_health = self._vector_store.health_check()
        except Exception as e:
            vs_health = VectorStoreHealth(
                connected=False, collections_count=0, error=str(e)
            )

        try:
            emb_health = self._embedder.health_check()
        except Exception as e:
            emb_health = EmbeddingHealth(
                connected=False, model_name="unknown", error=str(e)
            )

        overall = (
            "healthy"
            if all(
                [
                    llm_health.connected,
                    vs_health.connected,
                    emb_health.connected,
                ]
            )
            else "unhealthy"
        )

        return HealthCheckResult(
            status=overall,
            llm=llm_health,
            vector_store=vs_health,
            embedding=emb_health,
        )
