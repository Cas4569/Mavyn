"""Schema package exports."""

from src.schemas.category import Category, CategoryList
from src.schemas.content import (
    AdCopy,
    AdScript,
    ContentRequest,
    ContentResponse,
    ListingContent,
    ProductDescription,
    StoryboardFrame,
    VideoConcept,
)
from src.schemas.product import (
    Competitor,
    CustomerReview,
    Product,
    ProductCatalog,
    ProductDetail,
    ProductList,
    ResearchSource,
)
from src.schemas.review import (
    ReviewAnalysis,
    ReviewInput,
    SentimentBreakdown,
    Theme,
)
from src.schemas.strategy import (
    SWOT,
    MarketGap,
    Opportunity,
    SalesForecast,
    StrategyPanel,
    Trend,
)

__all__ = [
    "SWOT",
    "AdCopy",
    "AdScript",
    "Category",
    "CategoryList",
    "Competitor",
    "ContentRequest",
    "ContentResponse",
    "CustomerReview",
    "ListingContent",
    "MarketGap",
    "Opportunity",
    "Product",
    "ProductCatalog",
    "ProductDescription",
    "ProductDetail",
    "ProductList",
    "ResearchSource",
    "ReviewAnalysis",
    "ReviewInput",
    "SalesForecast",
    "SentimentBreakdown",
    "StoryboardFrame",
    "StrategyPanel",
    "Theme",
    "Trend",
    "VideoConcept",
]
