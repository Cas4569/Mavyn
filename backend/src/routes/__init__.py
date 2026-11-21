"""Routes package exports."""

from src.routes.health import router as health_router
from src.routes.categories import router as categories_router
from src.routes.products import router as products_router
from src.routes.reviews import router as reviews_router
from src.routes.content import router as content_router

__all__ = [
    "health_router",
    "categories_router",
    "products_router",
    "reviews_router",
    "content_router",
]