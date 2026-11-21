"""Schema package exports."""

from src.schemas.category import Category, CategoryList
from src.schemas.product import Product, ProductList, Competitor, ProductDetail
from src.schemas.review import (
    ReviewInput,
    ReviewAnalysis,
    SentimentBreakdown,
    Theme,
)
from src.schemas.strategy import SWOT, MarketGap, Trend, Opportunity, StrategyPanel
from src.schemas.content import (
    ContentRequest,
    ContentResponse,
    AdCopy,
    ProductDescription,
    ListingContent,
    AdScript,
    StoryboardFrame,
    VideoConcept,
)

__all__ = [
    # Category
    "Category",
    "CategoryList",
    # Product
    "Product",
    "ProductList",
    "Competitor",
    "ProductDetail",
    # Review
    "ReviewInput",
    "ReviewAnalysis",
    "SentimentBreakdown",
    "Theme",
    # Strategy
    "SWOT",
    "MarketGap",
    "Trend",
    "Opportunity",
    "StrategyPanel",
    # Content
    "ContentRequest",
    "ContentResponse",
    "AdCopy",
    "ProductDescription",
    "ListingContent",
    "AdScript",
    "StoryboardFrame",
    "VideoConcept",
]