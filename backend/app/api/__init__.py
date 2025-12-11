# API Package
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.files import router as files_router

__all__ = [
    "documents_router",
    "search_router",
    "chat_router",
    "files_router"
]

