from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.application.use_cases import HealthCheckUseCase
from app.application.dto import HealthCheckResult
from app.interfaces.dependencies import ContainerDep
from app.interfaces.schemas.health import (
    HealthResponse,
    OllamaHealthResponse,
    ChromadbHealthResponse,
)

router = APIRouter()


@router.get("/health")
def health_check(container: ContainerDep):
    usecase: HealthCheckUseCase = container.health_check_usecase()
    result: HealthCheckResult = usecase.execute()

    response = HealthResponse(
        status=result.status,
        ollama=OllamaHealthResponse(
            connected=result.llm.connected,
            model=result.llm.model,
            model_loaded=result.llm.model_loaded,
            error=result.llm.error,
        ),
        chromadb=ChromadbHealthResponse(
            connected=result.vector_store.connected,
            collections_count=result.vector_store.collections_count,
            error=result.vector_store.error,
        ),
        embedding_model=result.embedding.model_name,
    )

    status_code = 503 if result.status == "unhealthy" else 200
    return JSONResponse(content=response.model_dump(), status_code=status_code)
