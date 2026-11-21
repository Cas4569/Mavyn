"""Category schemas."""

from pydantic import BaseModel, Field
from typing import Annotated


class Category(BaseModel):
    """A product category."""

    id: Annotated[str, Field(description="Unique category identifier (slug)")]
    name: Annotated[str, Field(description="Display name")]
    product_count: Annotated[int, Field(description="Number of products in this category", ge=0)]
    description: Annotated[str | None, Field(description="Optional category description")] = None


class CategoryList(BaseModel):
    """Response for listing categories."""

    categories: list[Category]
    total: int