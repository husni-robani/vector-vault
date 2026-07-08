import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.domain.exceptions import (
    VectorVaultError,
    ExternalServiceError,
    FileAlreadyExistsError,
    NotFoundError,
    UnsupportedFileTypeError
)

logger = logging.getLogger(__name__)

def register_exception_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"message": str(exc)})
    @app.exception_handler(FileAlreadyExistsError)
    async def file_exists_handler(request: Request, exc: FileAlreadyExistsError):
        return JSONResponse(status_code=400, content={"message": str(exc)})
    @app.exception_handler(UnsupportedFileTypeError)
    async def unsupported_type_handler(request: Request, exc: UnsupportedFileTypeError):
        return JSONResponse(status_code=400, content={"message": str(exc)})
    @app.exception_handler(ExternalServiceError)
    async def external_service_handler(request: Request, exc: ExternalServiceError):
        return JSONResponse(status_code=502, content={"message": str(exc)})
    @app.exception_handler(VectorVaultError)
    async def vector_vault_error_handler(request: Request, exc: VectorVaultError):
        return JSONResponse(status_code=500, content={"message": "Internal server error"})
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception")       # log with traceback
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )