"""Health check route."""

from fastapi import APIRouter
from src.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "research_ready": bool(settings.nim_api_key and settings.tavily_api_key),
        "nim_configured": bool(settings.nim_api_key),
        "tavily_configured": bool(settings.tavily_api_key),
    }