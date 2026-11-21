"""Content generation route."""

from fastapi import APIRouter, HTTPException
from src.schemas.content import ContentRequest, ContentResponse
from src.services.content_generator import ContentGenerator

router = APIRouter(prefix="/content", tags=["content"])

generator = ContentGenerator()


@router.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """
    Generate marketing content for a product based on strategy insights.

    Optional: provide strategy_id to use a specific strategy panel.
    Optional: specify platforms and content_types to limit generation.
    """
    try:
        response = generator.generate(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")