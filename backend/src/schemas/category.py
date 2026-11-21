"""Category schemas."""

from typing import Annotated

from pydantic import BaseModel, Field


class Category(BaseModel):
    """A product category."""

    id: Annotated[str, Field(description="Unique category identifier (slug)")]
    name: Annotated[str, Field(description="Display name")]
    product_count: Annotated[
        int | None,
        Field(description="Number of current researched products in this category", ge=0),
    ] = None
    description: Annotated[str | None, Field(description="Optional category description")] = None


class CategoryList(BaseModel):
    """Response for listing categories."""

    categories: list[Category]
    total: int