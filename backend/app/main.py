from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.dependencies import build
from app.interfaces.api.router import api_router
from app.interfaces.api.exception_handlers import register_exception_handlers


def create_app(settings=None) -> FastAPI:
    if settings is None:
        settings = get_settings()

    container = build(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        container.close()

    app = FastAPI(lifespan=lifespan)

    app.state.container = container

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


api_app = create_app()
