from fastapi import APIRouter
from app.interfaces.api.documents import router as document_router
from app.interfaces.api.chat import router as chat_router
from app.interfaces.api.health import router as health_router

api_router = APIRouter(prefix="/api")

api_router.include_router(document_router)
api_router.include_router(chat_router)
api_router.include_router(health_router)
