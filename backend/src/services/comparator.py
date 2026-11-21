"""Product comparison service — compares Dot & Key products against competitors."""

from typing import Annotated
from decimal import Decimal

from src.schemas.product import Product, Competitor
from src.schemas.review import ReviewAnalysis
from src.data.samples import get_competitors_for_product, get_sample_reviews
from src.services.review_analyzer import ReviewAnalyzer


class ProductComparator:
    """Compares a Dot & Key product against its competitors."""

    def __init__(self):
        self.review_analyzer = ReviewAnalyzer()

    def compare(self, product_id: str) -> dict:
        """Run full comparison for a product."""
        # Get product data
        from src.data.samples import get_product_detail
        detail = get_product_detail(product_id)
        if not detail:
            return {"error": "Product not found"}

        product = detail["product"]
        competitors = detail["competitors"]
        sample_reviews = detail["sample_reviews"]

        # Analyze reviews for the main product
        review_input = type("ReviewInput", (), {"product_id": product_id, "reviews": sample_reviews, "competitor_ids": None})()
        review_analysis = self.review_analyzer.analyze(review_input)

        # Build comparison table
        comparison_rows = self._build_comparison_rows(product, competitors)

        # Price positioning
        price_analysis = self._analyze_price_positioning(product, competitors)

        # Rating analysis
        rating_analysis = self._analyze_ratings(product, competitors)

        # Feature comparison
        feature_comparison = self._compare_features(product, competitors)

        return {
            "product_id": product_id,
            "product_name": product["name"],
            "comparison_table": comparison_rows,
            "price_analysis": price_analysis,
            "rating_analysis": rating_analysis,
            "feature_comparison": feature_comparison,
            "review_analysis": review_analysis.model_dump(),
            "source": "sample",
        }

    def _build_comparison_rows(self, product: dict, competitors: list[dict]) -> list[dict]:
        """Build row-by-row comparison for frontend table."""
        all_products = [product] + competitors

        rows = [
            {
                "attribute": "Price (₹)",
                "values": {p["id"]: p["price_inr"] for p in all_products},
                "dot_and_key_value": product["price_inr"],
                "best_competitor": min(competitors, key=lambda c: c["price_inr"])["id"] if competitors else None,
                "unit": "INR",
            },
            {
                "attribute": "Rating",
                "values": {p["id"]: p["rating"] for p in all_products},
                "dot_and_key_value": product["rating"],
                "best_competitor": max(competitors, key=lambda c: c["rating"])["id"] if competitors else None,
                "unit": "/5",
            },
            {
                "attribute": "Review Count",
                "values": {p["id"]: p["review_count"] for p in all_products},
                "dot_and_key_value": product["review_count"],
                "best_competitor": max(competitors, key=lambda c: c["review_count"])["id"] if competitors else None,
                "unit": "reviews",
            },
            {
                "attribute": "Key Ingredients",
                "values": {
                    p["id"]: ", ".join(p.get("key_ingredients", [])) if not p.get("is_dot_and_key") else "See product details"
                    for p in all_products
                },
                "dot_and_key_value": "See product details",
                "best_competitor": None,
                "unit": "",
            },
            {
                "attribute": "USP",
                "values": {
                    p["id"]: p.get("usp", "") if not p.get("is_dot_and_key") else product.get("tagline", "")
                    for p in all_products
                },
                "dot_and_key_value": product.get("tagline", ""),
                "best_competitor": None,
                "unit": "",
            },
        ]

        return rows

    def _analyze_price_positioning(self, product: dict, competitors: list[dict]) -> dict:
        """Analyze where the product sits in price range."""
        if not competitors:
            return {"position": "unknown", "details": "No competitors"}

        prices = [c["price_inr"] for c in competitors]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        product_price = product["price_inr"]

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
            "competitor_avg": round(avg_price, 0),
            "price_gap_vs_avg": round(product_price - avg_price, 0),
            "details": f"Dot & Key at ₹{product_price} vs competitor avg ₹{round(avg_price)} ({position.replace('_', ' ')})",
        }

    def _analyze_ratings(self, product: dict, competitors: list[dict]) -> dict:
        """Analyze rating position."""
        if not competitors:
            return {"position": "unknown", "details": "No competitors"}

        ratings = [c["rating"] for c in competitors]
        min_rating = min(ratings)
        max_rating = max(ratings)
        avg_rating = sum(ratings) / len(ratings)
        product_rating = product["rating"]

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
            "details": f"Dot & Key at {product_rating}/5 vs competitor avg {round(avg_rating, 2)}/5 ({position.replace('_', ' ')})",
        }

    def _compare_features(self, product: dict, competitors: list[dict]) -> dict:
        """Compare key features/ingredients."""
        # Collect all unique ingredients from competitors
        competitor_ingredients = set()
        for c in competitors:
            competitor_ingredients.update(c.get("key_ingredients", []))

        # Dot & Key ingredients (would come from product detail in real implementation)
        # For now, infer from product name/tagline
        dk_ingredients = self._infer_ingredients(product)

        unique_to_dk = dk_ingredients - competitor_ingredients
        shared = dk_ingredients & competitor_ingredients
        missing = competitor_ingredients - dk_ingredients

        return {
            "dot_and_key_ingredients": list(dk_ingredients),
            "competitor_ingredients": list(competitor_ingredients),
            "unique_to_dot_and_key": list(unique_to_dk),
            "shared_with_competitors": list(shared),
            "competitors_have_not_dk": list(missing),
            "differentiation_score": len(unique_to_dk) / max(len(dk_ingredients), 1) * 100,
        }

    def _infer_ingredients(self, product: dict) -> set[str]:
        """Infer key ingredients from product name/tagline (sample logic)."""
        name = product.get("name", "").lower()
        tagline = product.get("tagline", "").lower()
        text = f"{name} {tagline}"

        ingredient_map = {
            "vitamin c": ["Vitamin C", "Ascorbic Acid"],
            "vitamin e": ["Vitamin E", "Tocopherol"],
            "niacinamide": ["Niacinamide"],
            "ceramide": ["Ceramides"],
            "hyaluronic": ["Hyaluronic Acid"],
            "watermelon": ["Watermelon Extract"],
            "cica": ["Centella Asiatica", "Cica"],
            "green tea": ["Green Tea Extract"],
            "rice water": ["Rice Water", "Sake"],
            "salicylic": ["Salicylic Acid"],
            "pha": ["PHA", "Gluconolactone"],
            "coffee": ["Caffeine"],
            "retinol": ["Retinol"],
            "peptide": ["Peptides"],
        }

        found = set()
        for keyword, ingredients in ingredient_map.items():
            if keyword in text:
                found.update(ingredients)

        return found