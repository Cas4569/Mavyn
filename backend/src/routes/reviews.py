"""Reviews analysis route."""

from fastapi import APIRouter, HTTPException
from src.schemas.review import ReviewInput, ReviewAnalysis
from src.services.review_analyzer import ReviewAnalyzer
from src.data.samples import get_sample_reviews

router = APIRouter(prefix="/reviews", tags=["reviews"])

analyzer = ReviewAnalyzer()


@router.post("/analyze", response_model=ReviewAnalysis)
async def analyze_reviews(input_data: ReviewInput):
    """
    Analyze customer reviews for a product.

    If `reviews` is not provided, uses sample reviews for the product.
    """
    # If no reviews provided, use sample reviews
    if not input_data.reviews:
        sample_reviews = get_sample_reviews(input_data.product_id)
        if not sample_reviews:
            raise HTTPException(
                status_code=404,
                detail=f"No sample reviews found for product {input_data.product_id}. Provide reviews in request."
            )
        input_data.reviews = sample_reviews

    # Run analysis
    analysis = analyzer.analyze(input_data)
    return analysis