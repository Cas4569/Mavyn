"""Sample Dot & Key skincare products used as offline fallback when live Gemini research is unavailable.

This sample data allows the site to function even when Gemini API is rate-limited or unavailable.
"""

from datetime import UTC, datetime
from typing import Any

from src.schemas.product import (
    Competitor,
    CustomerReview,
    Product,
    ProductCatalog,
    ProductDetail,
    ProductList,
    ResearchSource,
)


_SAMPLE_SOURCES = [
    ResearchSource(title="Dot & Key Official Site", url="https://dotandkey.com"),
    ResearchSource(title="Dot & Key Products", url="https://dotandkey.com/collections/all"),
]

_SAMPLE_PRODUCTS = [
    {
        "id": "dk-vitamin-c-serum",
        "name": "Dot & Key Vitamin C 10% + E Super Glow Face Serum",
        "category_id": "serums",
        "price_inr": 549,
        "rating": 4.4,
        "review_count": 3200,
        "tagline": "Brightens skin and fades dark spots",
        "key_ingredients": ["Vitamin C", "Vitamin E", "Ferulic Acid"],
        "hero_image": "https://cdn.shopify.com/s/files/1/0072/7470/6517/products/vitamin-c-serum.jpg",
    },
    {
        "id": "dk-niacinamide-serum",
        "name": "Dot & Key Niacinamide 5% + Zinc 1% Face Serum",
        "category_id": "serums",
        "price_inr": 499,
        "rating": 4.3,
        "review_count": 2800,
        "tagline": "Controls oil and minimizes pores",
        "key_ingredients": ["Niacinamide", "Zinc", "Hyaluronic Acid"],
        "hero_image": "https://cdn.shopify.com/s/files/1/0072/7470/6517/products/niacinamide-serum.jpg",
    },
    {
        "id": "dk-hyaluronic-acid-moisturizer",
        "name": "Dot & Key Hyaluronic Acid Water Gel Moisturizer",
        "category_id": "moisturizers",
        "price_inr": 699,
        "rating": 4.5,
        "review_count": 4100,
        "tagline": "72-hour hydration for all skin types",
        "key_ingredients": ["Hyaluronic Acid", "Ceramides", "Vitamin B5"],
        "hero_image": "https://cdn.shopify.com/s/files/1/0072/7470/6517/products/hyaluronic-moisturizer.jpg",
    },
    {
        "id": "dk-sunscreen-spf50",
        "name": "Dot & Key SPF 50+ PA++++ Sunscreen",
        "category_id": "sunscreens",
        "price_inr": 599,
        "rating": 4.2,
        "review_count": 3500,
        "tagline": "Lightweight broad spectrum sun protection",
        "key_ingredients": ["Zinc Oxide", "Green Tea", "Vitamin E"],
        "hero_image": "https://cdn.shopify.com/s/files/1/0072/7470/6517/products/sunscreen-spf50.jpg",
    },
    {
        "id": "dk-gentle-cleanser",
        "name": "Dot & Key Gentle PHA Exfoliating Face Cleanser",
        "category_id": "cleansers",
        "price_inr": 449,
        "rating": 4.1,
        "review_count": 1900,
        "tagline": "Gentle daily exfoliation and cleansing",
        "key_ingredients": ["PHA", "Aloe Vera", "Green Tea"],
        "hero_image": "https://cdn.shopify.com/s/files/1/0072/7470/6517/products/cleanser.jpg",
    },
    {
        "id": "dk-toner",
        "name": "Dot & Key Rice Water Toner",
        "category_id": "toners",
        "price_inr": 399,
        "rating": 4.0,
        "review_count": 1200,
        "tagline": "Brightening and hydrating toner",
        "key_ingredients": ["Rice Water", "Niacinamide", "Hyaluronic Acid"],
        "hero_image": "https://cdn.shopify.com/s/files/1/0072/7470/6517/products/rice-toner.jpg",
    },
]

_SAMPLE_COMPETITORS = [
    {
        "id": "comp-plum-vitamin-c",
        "name": "Plum 10% Vitamin C Face Serum",
        "brand": "Plum",
        "price_inr": 499,
        "rating": 4.2,
        "review_count": 2100,
        "key_ingredients": ["Vitamin C", "Ferulic Acid", "Vitamin E"],
        "usp": "100% vegan and cruelty-free",
    },
    {
        "id": "comp-mamaearth-niacinamide",
        "name": "Mamaearth Niacinamide Face Serum",
        "brand": "Mamaearth",
        "price_inr": 399,
        "rating": 4.1,
        "review_count": 1800,
        "key_ingredients": ["Niacinamide", "Vitamin C"],
        "usp": "Toxin-free skincare",
    },
]

_SAMPLE_REVIEWS = [
    {
        "text": "Really helped fade my dark spots within a few weeks. Lightweight and non-greasy.",
        "source_url": "https://dotandkey.com/products/vitamin-c-serum",
    },
    {
        "text": "Good for oily skin, controls sebum production throughout the day.",
        "source_url": "https://dotandkey.com/products/niacinamide-serum",
    },
    {
        "text": "Best moisturizer I've used in Indian summer. Keeps skin hydrated without feeling heavy.",
        "source_url": "https://dotandkey.com/products/hyaluronic-moisturizer",
    },
]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _make_product(data: dict[str, Any], product_id: str | None = None) -> Product:
    return Product(
        id=product_id or data["id"],
        name=data["name"],
        category_id=data["category_id"],
        price_inr=data["price_inr"],
        rating=data["rating"],
        review_count=data["review_count"],
        source="sample",
        sources=list(_SAMPLE_SOURCES),
        tagline=data["tagline"],
        key_ingredients=data["key_ingredients"],
        is_dot_and_key=True,
        hero_image=data.get("hero_image"),
    )


def get_sample_catalog() -> ProductCatalog:
    """Return a sample product catalog as fallback when live research is unavailable."""
    products = [_make_product(d) for d in _SAMPLE_PRODUCTS]
    return ProductCatalog(
        products=products,
        total=len(products),
        sources=list(_SAMPLE_SOURCES),
        fetched_at=_now_iso(),
        source="sample",
        cached=True,
    )


def get_sample_product_list(category_id: str) -> ProductList | None:
    """Return sample products for a category, or None if none match."""
    products = [_make_product(d) for d in _SAMPLE_PRODUCTS if d["category_id"] == category_id]
    if not products:
        return None
    return ProductList(
        category_id=category_id,
        category_name="Sample",
        products=products,
        total=len(products),
        sources=list(_SAMPLE_SOURCES),
        fetched_at=_now_iso(),
        source="sample",
        cached=True,
    )


def get_sample_product_detail(product_id: str) -> ProductDetail | None:
    """Return sample product detail as fallback when live research is unavailable."""
    sample = next((d for d in _SAMPLE_PRODUCTS if d["id"] == product_id), None)
    if sample is None:
        return None

    product = _make_product(sample, product_id=product_id)
    competitors = [Competitor(**c) for c in _SAMPLE_COMPETITORS]
    reviews = [
        CustomerReview(text=r["text"], source=ResearchSource(title="Dot & Key", url=r["source_url"]))
        for r in _SAMPLE_REVIEWS
    ]
    sources = list(_SAMPLE_SOURCES) + [
        ResearchSource(title="Dot & Key Reviews", url=r["source_url"]) for r in _SAMPLE_REVIEWS
    ]

    return ProductDetail(
        product=product,
        competitors=competitors,
        reviews=reviews,
        sources=sources,
        fetched_at=_now_iso(),
        source="sample",
        cached=True,
    )