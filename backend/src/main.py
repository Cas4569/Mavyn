"""MAVYN Backend — FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes import (
    health_router,
    categories_router,
    products_router,
    reviews_router,
    content_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"{settings.app_name} v{settings.app_version} starting up...")
    print(f"   CORS enabled for: {settings.cors_origins}")
    yield
    # Shutdown
    print(f"{settings.app_name} shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Market intelligence and marketing content platform for Dot & Key",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(reviews_router)
app.include_router(content_router)


# Root endpoint
@app.get("/")
async def root():
    """API root with basic info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Market intelligence and marketing content platform for Dot & Key",
        "endpoints": {
            "health": "/health",
            "categories": "/categories",
            "products": "/products",
            "reviews": "/reviews",
            "content": "/content",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )