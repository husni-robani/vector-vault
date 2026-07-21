from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    origins = [
        "http://localhost:5173"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.state.container = container

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


api_app = create_app()
