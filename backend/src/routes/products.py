"""Products routes."""

from fastapi import APIRouter, HTTPException, Query
from src.schemas.product import ProductList, ProductDetail, Product, Competitor
from src.data.samples import get_products_by_category, get_product_detail, get_all_dot_and_key_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductList)
async def list_products(category: str = Query(..., description="Category ID to filter by")):
    """List Dot & Key products in a category (excludes competitors)."""
    products = get_products_by_category(category)
    if not products:
        raise HTTPException(status_code=404, detail="Category not found or no products")

    # Filter only Dot & Key products
    dot_and_key_products = [p for p in products if p.get("is_dot_and_key", False)]

    # Get category name
    from src.data.samples import get_categories
    categories = get_categories()
    category_name = next((c["name"] for c in categories if c["id"] == category), category)

    # Validate each product
    validated_products = [Product.model_validate(p) for p in dot_and_key_products]

    return ProductList(
        category_id=category,
        category_name=category_name,
        products=validated_products,
        total=len(validated_products),
    )


@router.get("/dot-and-key")
async def list_dot_and_key_products():
    """List all Dot & Key products across categories."""
    products = get_all_dot_and_key_products()
    validated_products = [Product.model_validate(p) for p in products]
    return {"products": validated_products, "total": len(validated_products)}


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(product_id: str):
    """Get full product detail with competitors and sample reviews."""
    detail = get_product_detail(product_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate nested models
    product = Product.model_validate(detail["product"])
    competitors = [Competitor.model_validate(c) for c in detail["competitors"]]

    return ProductDetail(
        product=product,
        competitors=competitors,
        sample_reviews=detail["sample_reviews"],
    )