from fastapi import APIRouter
from app.interfaces.api.documents import router as document_router

api_router = APIRouter(prefix="/api")

api_router.include_router(document_router)