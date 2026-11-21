from fastapi.testclient import TestClient

from src.main import app
from src.routes import products as products_route
from src.routes import reviews as reviews_route
from src.schemas.product import ProductCatalog, ProductDetail, ProductList

client = TestClient(app)
PRODUCT_ID = "dk-watermelon-cooling-sunscreen"
SOURCE = {"title": "Product research", "url": "https://example.com/product"}
COMPETITOR_SOURCE = {"title": "Competitor page", "url": "https://example.com/competitor"}
REVIEW_SOURCE = {"title": "Public reviews", "url": "https://example.com/reviews"}


def _detail(product_id=PRODUCT_ID):
    return ProductDetail.model_validate(
        {
            "product": {
                "id": product_id,
                "name": "Watermelon Cooling Sunscreen",
                "category_id": "sunscreens",
                "price_inr": 595,
                "rating": 4.4,
                "review_count": 420,
                "tagline": "Lightweight daily protection",
                "key_ingredients": ["Watermelon Extract"],
                "sources": [SOURCE],
            },
            "competitors": [
                {
                    "id": "comp-example-sunscreen",
                    "name": "Daily Sunscreen",
                    "brand": "Example",
                    "price_inr": 620,
                    "rating": 4.2,
                    "review_count": 250,
                    "key_ingredients": ["Niacinamide"],
                    "usp": "Daily wear",
                    "sources": [COMPETITOR_SOURCE],
                }
            ],
            "reviews": [
                {
                    "text": "The texture feels light and absorbs quickly.",
                    "source": REVIEW_SOURCE,
                    "published_at": "2025-11-02",
                },
                {
                    "text": "I love the glow and it feels gentle.",
                    "source": REVIEW_SOURCE,
                },
                {
                    "text": "The scent is too strong and caused irritation.",
                    "source": REVIEW_SOURCE,
                },
                {
                    "text": "The price feels expensive for the size.",
                    "source": REVIEW_SOURCE,
                },
            ],
            "sources": [SOURCE, COMPETITOR_SOURCE, REVIEW_SOURCE],
            "fetched_at": "2026-03-05T12:00:00+00:00",
        }
    )


class FakeMarketResearch:
    def __init__(self):
        self.detail = _detail()

    async def list_products(self):
        return ProductCatalog(
            products=[self.detail.product],
            total=1,
            sources=[SOURCE],
            fetched_at=self.detail.fetched_at,
        )

    async def list_products_by_category(self, category_id):
        if category_id != "sunscreens":
            return None
        return ProductList(
            category_id=category_id,
            category_name="Sunscreens",
            products=[self.detail.product],
            total=1,
            sources=[SOURCE],
            fetched_at=self.detail.fetched_at,
        )

    async def get_product_detail(self, product_id):
        return self.detail if product_id == PRODUCT_ID else None


def test_catalog_and_detail_expose_grounded_sources(monkeypatch):
    monkeypatch.setattr(products_route, "market_research", FakeMarketResearch())

    catalog = client.get("/products/dot-and-key")
    assert catalog.status_code == 200
    assert catalog.json()["source"] == "api"
    assert catalog.json()["products"][0]["id"] == PRODUCT_ID
    assert catalog.json()["sources"][0]["url"] == SOURCE["url"]

    detail = client.get(f"/products/{PRODUCT_ID}")
    assert detail.status_code == 200
    assert detail.json()["reviews"][0]["text"].startswith("The texture")
    assert len(detail.json()["sources"]) == 3


def test_comparison_uses_live_product_competitors_and_reviews(monkeypatch):
    monkeypatch.setattr(products_route, "market_research", FakeMarketResearch())

    response = client.get(f"/products/{PRODUCT_ID}/comparison")

    assert response.status_code == 200
    result = response.json()
    assert result["product_id"] == PRODUCT_ID
    assert result["source"] == "api"
    assert len(result["comparison_table"]) >= 3
    assert result["price_analysis"]["competitor_avg"] == 620
    assert result["review_analysis"]["sentiment"]["total"] == 4
    assert result["sources"]


def test_strategy_uses_sourced_signals_and_does_not_invent_sales(monkeypatch):
    monkeypatch.setattr(products_route, "market_research", FakeMarketResearch())

    response = client.get(f"/products/{PRODUCT_ID}/strategy")

    assert response.status_code == 200
    result = response.json()
    assert result["source"] == "api"
    assert result["sales_forecast"] == []
    assert "dated sales" in result["forecast_note"].lower()
    assert result["market_gaps"]
    assert all(gap["evidence"] for gap in result["market_gaps"])
    assert result["sources"]
    assert client.get("/products/not-a-product/strategy").status_code == 404


def test_review_analysis_uses_retrieved_excerpt_sources(monkeypatch):
    monkeypatch.setattr(reviews_route, "market_research", FakeMarketResearch())

    response = client.post("/reviews/analyze", json={"product_id": PRODUCT_ID})

    assert response.status_code == 200
    result = response.json()
    assert result["source"] == "api"
    assert result["sentiment"]["total"] == 4
    assert result["sources"][0]["url"] == SOURCE["url"]


def test_comparison_keeps_unknown_numeric_values_unknown(monkeypatch):
    research = FakeMarketResearch()
    research.detail.product.price_inr = None
    research.detail.product.rating = None
    research.detail.competitors[0].price_inr = None
    research.detail.competitors[0].rating = None
    monkeypatch.setattr(products_route, "market_research", research)

    result = client.get(f"/products/{PRODUCT_ID}/comparison").json()

    assert result["price_analysis"]["position"] == "unknown"
    assert result["rating_analysis"]["position"] == "unknown"
    assert result["price_analysis"]["product_price"] is None
