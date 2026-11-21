"""Products routes backed by live Gemini Search research."""

from fastapi import APIRouter, HTTPException, Query

from src.routes.research_errors import research_http_exception
from src.schemas.product import ProductCatalog, ProductDetail, ProductList
from src.schemas.strategy import StrategyPanel
from src.services.comparator import ProductComparator
from src.services.market_research import NimResearchError, market_research
from src.services.strategy import StrategyGenerator

router = APIRouter(prefix="/products", tags=["products"])
comparator = ProductComparator()
strategy_generator = StrategyGenerator()


@router.get("", response_model=ProductList)
async def list_products(category: str = Query(..., description="Category ID to filter by")):
    """List current Dot & Key products researched and cited from Google Search."""
    try:
        products = await market_research.list_products_by_category(category)
    except NimResearchError as exc:
        raise research_http_exception(exc) from exc
    if products is None:
        raise HTTPException(status_code=404, detail="No live product records found for category.")
    return products


@router.get("/dot-and-key", response_model=ProductCatalog)
async def list_dot_and_key_products():
    """List current Dot & Key products with Google Search citations."""
    try:
        return await market_research.list_products()
    except NimResearchError as exc:
        raise research_http_exception(exc) from exc


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(product_id: str):
    """Get live product, competitor, and review data with source citations."""
    try:
        detail = await market_research.get_product_detail(product_id)
    except NimResearchError as exc:
        raise research_http_exception(exc) from exc
    if detail is None:
        raise HTTPException(status_code=404, detail="Product not found in the live catalog.")
    return detail


@router.get("/{product_id}/comparison")
async def compare_product(product_id: str):
    """Compare a product against competitors found in grounded search results."""
    try:
        detail = await market_research.get_product_detail(product_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Product not found in the live catalog.")
        return comparator.compare(product_id, detail.model_dump(mode="json"))
    except NimResearchError as exc:
        raise research_http_exception(exc) from exc


@router.get("/{product_id}/strategy", response_model=StrategyPanel)
async def get_product_strategy(product_id: str):
    """Build a market brief from live product, competitor, and review records."""
    try:
        detail = await market_research.get_product_detail(product_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Product not found in the live catalog.")
        return strategy_generator.generate(product_id, detail.model_dump(mode="json"))
    except NimResearchError as exc:
        raise research_http_exception(exc) from exc
