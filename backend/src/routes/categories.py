"""Categories routes."""

from fastapi import APIRouter, HTTPException
from src.schemas.category import CategoryList
from src.data.samples import get_categories

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoryList)
async def list_categories():
    """List all product categories."""
    categories = get_categories()
    return CategoryList(categories=categories, total=len(categories))


@router.get("/{category_id}")
async def get_category(category_id: str):
    """Get a single category by ID."""
    categories = get_categories()
    for cat in categories:
        if cat["id"] == category_id:
            return cat
    raise HTTPException(status_code=404, detail="Category not found")