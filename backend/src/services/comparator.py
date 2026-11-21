"""Compare grounded product records and analyze their retrieved review excerpts."""

from typing import Any

from src.schemas.review import ReviewInput
from src.services.review_analyzer import ReviewAnalyzer


class ProductComparator:
    """Compares a researched Dot & Key product against sourced competitors."""

    def __init__(self) -> None:
        self.review_analyzer = ReviewAnalyzer()

    def compare(self, product_id: str, detail: dict[str, Any]) -> dict[str, Any]:
        """Build a comparison using only records supplied by live market research."""
        product = detail["product"]
        competitors = detail["competitors"]
        reviews = detail["reviews"]
        review_analysis = self.review_analyzer.analyze(
            ReviewInput(
                product_id=product_id,
                reviews=[review["text"] for review in reviews],
            ),
            source="api",
            sources=detail["sources"],
        )

        return {
            "product_id": product_id,
            "product_name": product["name"],
            "comparison_table": self._build_comparison_rows(product, competitors),
            "price_analysis": self._analyze_price_positioning(product, competitors),
            "rating_analysis": self._analyze_ratings(product, competitors),
            "feature_comparison": self._compare_features(product, competitors),
            "review_analysis": review_analysis.model_dump(mode="json"),
            "sources": detail["sources"],
            "fetched_at": detail["fetched_at"],
            "source": "api",
        }

    @staticmethod
    def _best_competitor(
        competitors: list[dict[str, Any]],
        field: str,
        direction: str,
    ) -> str | None:
        available = [item for item in competitors if item.get(field) is not None]
        if not available:
            return None
        selector = min if direction == "min" else max
        return selector(available, key=lambda item: item[field])["id"]

    def _build_comparison_rows(
        self,
        product: dict[str, Any],
        competitors: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        all_products = [product, *competitors]
        return [
            {
                "attribute": "Price (₹)",
                "values": {item["id"]: item.get("price_inr") for item in all_products},
                "dot_and_key_value": product.get("price_inr"),
                "best_competitor": self._best_competitor(competitors, "price_inr", "min"),
                "unit": "INR",
            },
            {
                "attribute": "Rating",
                "values": {item["id"]: item.get("rating") for item in all_products},
                "dot_and_key_value": product.get("rating"),
                "best_competitor": self._best_competitor(competitors, "rating", "max"),
                "unit": "/5",
            },
            {
                "attribute": "Review Count",
                "values": {item["id"]: item.get("review_count") for item in all_products},
                "dot_and_key_value": product.get("review_count"),
                "best_competitor": self._best_competitor(competitors, "review_count", "max"),
                "unit": "reviews",
            },
            {
                "attribute": "Key Ingredients",
                "values": {
                    item["id"]: ", ".join(item.get("key_ingredients", [])) or None
                    for item in all_products
                },
                "dot_and_key_value": ", ".join(product.get("key_ingredients", [])) or None,
                "best_competitor": None,
                "unit": "",
            },
            {
                "attribute": "USP",
                "values": {
                    item["id"]: item.get("usp") if item is not product else product.get("tagline")
                    for item in all_products
                },
                "dot_and_key_value": product.get("tagline"),
                "best_competitor": None,
                "unit": "",
            },
        ]

    @staticmethod
    def _analyze_price_positioning(
        product: dict[str, Any],
        competitors: list[dict[str, Any]],
    ) -> dict[str, Any]:
        product_price = product.get("price_inr")
        prices = [item["price_inr"] for item in competitors if item.get("price_inr") is not None]
        if product_price is None or not prices:
            return {
                "position": "unknown",
                "product_price": product_price,
                "details": "Insufficient verified price data for comparison.",
            }

        min_price, max_price = min(prices), max(prices)
        avg_price = sum(prices) / len(prices)
        if product_price <= min_price:
            position = "lowest"
        elif product_price >= max_price:
            position = "highest"
        elif product_price <= avg_price:
            position = "below_average"
        else:
            position = "above_average"

        return {
            "position": position,
            "product_price": product_price,
            "competitor_min": min_price,
            "competitor_max": max_price,
            "competitor_avg": round(avg_price),
            "price_gap_vs_avg": round(product_price - avg_price),
            "details": (
                f"Dot & Key at ₹{product_price} vs competitor average ₹{round(avg_price)} "
                f"({position.replace('_', ' ')})"
            ),
        }

    @staticmethod
    def _analyze_ratings(
        product: dict[str, Any],
        competitors: list[dict[str, Any]],
    ) -> dict[str, Any]:
        product_rating = product.get("rating")
        ratings = [item["rating"] for item in competitors if item.get("rating") is not None]
        if product_rating is None or not ratings:
            return {
                "position": "unknown",
                "product_rating": product_rating,
                "details": "Insufficient verified rating data for comparison.",
            }

        min_rating, max_rating = min(ratings), max(ratings)
        avg_rating = sum(ratings) / len(ratings)
        if product_rating >= max_rating:
            position = "highest"
        elif product_rating <= min_rating:
            position = "lowest"
        elif product_rating >= avg_rating:
            position = "above_average"
        else:
            position = "below_average"

        return {
            "position": position,
            "product_rating": product_rating,
            "competitor_min": min_rating,
            "competitor_max": max_rating,
            "competitor_avg": round(avg_rating, 2),
            "rating_gap_vs_avg": round(product_rating - avg_rating, 2),
            "details": (
                f"Dot & Key at {product_rating}/5 vs competitor average "
                f"{round(avg_rating, 2)}/5 ({position.replace('_', ' ')})"
            ),
        }

    @staticmethod
    def _compare_features(
        product: dict[str, Any],
        competitors: list[dict[str, Any]],
    ) -> dict[str, Any]:
        competitor_ingredients = {
            ingredient
            for competitor in competitors
            for ingredient in competitor.get("key_ingredients", [])
        }
        product_ingredients = set(product.get("key_ingredients", []))
        unique_to_product = product_ingredients - competitor_ingredients
        shared = product_ingredients & competitor_ingredients
        missing = competitor_ingredients - product_ingredients

        return {
            "dot_and_key_ingredients": sorted(product_ingredients),
            "competitor_ingredients": sorted(competitor_ingredients),
            "unique_to_dot_and_key": sorted(unique_to_product),
            "shared_with_competitors": sorted(shared),
            "competitors_have_not_dk": sorted(missing),
            "differentiation_score": (
                len(unique_to_product) / len(product_ingredients) * 100
                if product_ingredients
                else None
            ),
        }
