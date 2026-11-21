"""Product and competitor schemas."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl


class ResearchSource(BaseModel):
    """A URL citation returned by Gemini's Google Search grounding."""

    title: str
    url: HttpUrl


class BaseProduct(BaseModel):
    """Base product fields shared by Dot & Key and competitor products."""

    id: Annotated[str, Field(description="Unique product identifier")]
    name: Annotated[str, Field(description="Product name")]
    price_inr: Annotated[int | None, Field(description="Current price in Indian Rupees", ge=0)]
    rating: Annotated[float | None, Field(description="Average rating (0-5)", ge=0, le=5)]
    review_count: Annotated[int | None, Field(description="Number of reviews", ge=0)]
    source: Annotated[
        Literal["api", "sample"],
        Field(description="Live API or explicitly labeled sample data source"),
    ] = "api"
    sources: list[ResearchSource] = Field(default_factory=list)


class Competitor(BaseProduct):
    """A competitor product."""

    brand: Annotated[str, Field(description="Brand name")]
    key_ingredients: Annotated[list[str], Field(description="Key active ingredients")] = Field(
        default_factory=list
    )
    usp: Annotated[str | None, Field(description="Unique selling proposition")] = None
    image_url: Annotated[HttpUrl | None, Field(description="Product image URL")] = None


class Product(BaseProduct):
    """A Dot & Key product (summary for listings)."""

    category_id: Annotated[str, Field(description="Category this product belongs to")]
    hero_image: Annotated[HttpUrl | None, Field(description="Hero image URL")] = None
    tagline: Annotated[str | None, Field(description="Marketing tagline")] = None
    key_ingredients: list[str] = Field(default_factory=list)
    is_dot_and_key: Annotated[bool, Field(description="Whether this is a Dot & Key product", default=True)] = True


class ProductList(BaseModel):
    """Response for listing products in a category."""

    category_id: str
    category_name: str
    products: list[Product]  # Dot & Key products only in list
    total: int
    sources: list[ResearchSource] = Field(default_factory=list)
    fetched_at: str
    source: Literal["api", "sample"] = "api"
    cached: bool = False


class ProductCatalog(BaseModel):
    """Live Dot & Key product catalog."""

    products: list[Product]
    total: int
    sources: list[ResearchSource] = Field(default_factory=list)
    fetched_at: str
    source: Literal["api", "sample"] = "api"
    cached: bool = False


class CustomerReview(BaseModel):
    """A public review excerpt cited from a grounded source."""

    text: str
    source: ResearchSource
    published_at: str | None = None


class ProductDetail(BaseModel):
    """Full live product detail with competitors, review excerpts, and citations."""

    product: Product
    competitors: list[Competitor]
    reviews: list[CustomerReview] = Field(default_factory=list)
    sources: list[ResearchSource] = Field(default_factory=list)
    fetched_at: str
    source: Literal["api", "sample"] = "api"
    cached: bool = False