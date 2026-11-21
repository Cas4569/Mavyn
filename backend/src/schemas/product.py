"""Product and competitor schemas."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Literal, Union
from decimal import Decimal


class BaseProduct(BaseModel):
    """Base product fields shared by Dot & Key and competitor products."""

    id: Annotated[str, Field(description="Unique product identifier")]
    name: Annotated[str, Field(description="Product name")]
    price_inr: Annotated[int, Field(description="Price in Indian Rupees", ge=0)]
    rating: Annotated[float, Field(description="Average rating (0-5)", ge=0, le=5)]
    review_count: Annotated[int, Field(description="Number of reviews", ge=0)]
    source: Annotated[Literal["sample", "scraped", "api"], Field(description="Data source")] = "sample"


class Competitor(BaseProduct):
    """A competitor product."""

    brand: Annotated[str, Field(description="Brand name")]
    key_ingredients: Annotated[list[str], Field(description="Key active ingredients")]
    usp: Annotated[str, Field(description="Unique selling proposition")]
    image_url: Annotated[HttpUrl | None, Field(description="Product image URL")] = None


class Product(BaseProduct):
    """A Dot & Key product (summary for listings)."""

    category_id: Annotated[str, Field(description="Category this product belongs to")]
    hero_image: Annotated[HttpUrl | None, Field(description="Hero image URL")] = None
    tagline: Annotated[str | None, Field(description="Marketing tagline")] = None
    is_dot_and_key: Annotated[bool, Field(description="Whether this is a Dot & Key product", default=True)] = True


class ProductList(BaseModel):
    """Response for listing products in a category."""

    category_id: str
    category_name: str
    products: list[Product]  # Dot & Key products only in list
    total: int


class ProductDetail(BaseModel):
    """Full product detail with competitors and sample reviews."""

    product: Product
    competitors: list[Competitor]
    sample_reviews: Annotated[
        list[str], Field(description="Sample customer reviews for analysis", default_factory=list)
    ]