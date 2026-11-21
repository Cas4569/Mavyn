"""Review analysis route."""

from fastapi import APIRouter, HTTPException

from src.routes.research_errors import research_http_exception
from src.schemas.review import ReviewAnalysis, ReviewInput
from src.services.market_research import GeminiResearchError, market_research
from src.services.review_analyzer import ReviewAnalyzer

router = APIRouter(prefix="/reviews", tags=["reviews"])
analyzer = ReviewAnalyzer()


@router.post("/analyze", response_model=ReviewAnalysis)
async def analyze_reviews(input_data: ReviewInput):
    """Analyze provided reviews or live, cited review excerpts for a product."""
    if input_data.reviews:
        return analyzer.analyze(input_data, source="user")

    try:
        detail = await market_research.get_product_detail(input_data.product_id)
    except GeminiResearchError as exc:
        raise research_http_exception(exc) from exc
    if detail is None:
        raise HTTPException(status_code=404, detail="Product not found in the live catalog.")

    return analyzer.analyze(
        ReviewInput(
            product_id=input_data.product_id,
            reviews=[review.text for review in detail.reviews],
            competitor_ids=input_data.competitor_ids,
        ),
        source="api",
        sources=detail.sources,
    )
