"""Derive a market brief from live product, competitor, and review research."""

from datetime import UTC, datetime
from typing import Any

from src.schemas.product import ResearchSource
from src.schemas.review import ReviewAnalysis, ReviewInput, Theme
from src.schemas.strategy import SWOT, MarketGap, Opportunity, StrategyPanel, Trend
from src.services.comparator import ProductComparator
from src.services.review_analyzer import ReviewAnalyzer

_GAP_ACTIONS = {
    "Breakouts": "Review the formula's compatibility with acne-prone skin and clarify suitability guidance.",
    "Packaging": "Test dispenser reliability and improve packaging usability.",
    "Scent": "Review fragrance expectations and make scent information easier to find.",
    "Sensitivity": "Clarify patch-testing guidance and suitability for reactive skin.",
    "Texture": "Set clearer texture and layering expectations in product education.",
    "Value": "Test bundle sizes or value messaging against the category price range.",
    "White Cast": "Validate finish claims across skin tones before making inclusivity claims.",
    "Effectiveness": "Set realistic usage timelines and explain outcomes supported by product evidence.",
    "Skin Feel": "Improve guidance for different skin types and climate conditions.",
}


class StrategyGenerator:
    """Derive a cautious product-specific brief from cited live records."""

    def __init__(self) -> None:
        self.review_analyzer = ReviewAnalyzer()
        self.comparator = ProductComparator()

    def generate(self, product_id: str, detail: dict[str, Any]) -> StrategyPanel:
        product = detail["product"]
        reviews = detail["reviews"]
        review_analysis = self.review_analyzer.analyze(
            ReviewInput(
                product_id=product_id,
                reviews=[review["text"] for review in reviews],
            ),
            source="api",
            sources=detail["sources"],
        )
        comparison = self.comparator.compare(product_id, detail)
        gaps = self._identify_gaps(
            review_analysis.top_complaint_themes,
            review_analysis.sentiment.total,
        )
        return StrategyPanel(
            product_id=product_id,
            swot=self._generate_swot(
                product, detail["competitors"], comparison, review_analysis
            ),
            market_gaps=gaps,
            trends=self._identify_review_signals(
                review_analysis.top_praise_themes,
                review_analysis.top_complaint_themes,
                review_analysis.sentiment.total,
            ),
            opportunities=self._identify_opportunities(
                product,
                comparison,
                review_analysis.top_praise_themes,
                review_analysis.top_complaint_themes,
            ),
            sales_forecast=[],
            forecast_note=(
                "Not calculated: public product research does not provide a dated sales or "
                "sell-through time series. Review counts are not a substitute for sales data."
            ),
            generated_at=datetime.now(UTC).isoformat(),
            source="api",
            sources=[ResearchSource.model_validate(source) for source in detail["sources"]],
        )

    def _generate_swot(
        self,
        product: dict[str, Any],
        competitors: list[dict[str, Any]],
        comparison: dict[str, Any],
        review_analysis: ReviewAnalysis,
    ) -> SWOT:
        strengths = [
            f"Retrieved reviews frequently praise {theme.name.lower()} "
            f"({theme.mention_count} mentions)."
            for theme in review_analysis.top_praise_themes[:2]
        ]
        weaknesses = [
            f"Retrieved reviews report concerns about {theme.name.lower()} "
            f"({theme.mention_count} mentions)."
            for theme in review_analysis.top_complaint_themes[:2]
        ]
        if not weaknesses:
            weaknesses.append(
                "No recurring complaint was detected in the retrieved excerpts; this does not "
                "establish that no product issues exist."
            )

        price_position = comparison["price_analysis"]["position"]
        price = product.get("price_inr")
        if price is not None and price_position in ("lowest", "below_average"):
            strengths.append(f"Verified price of ₹{price} is below the available competitor average.")
        elif price is not None and price_position in ("highest", "above_average"):
            weaknesses.append(
                f"Verified price of ₹{price} is above the available competitor average."
            )

        threats = []
        priced_competitors = [
            item for item in competitors if item.get("price_inr") is not None
        ]
        rated_competitors = [
            item for item in competitors if item.get("rating") is not None
        ]
        if price is not None and priced_competitors:
            lowest = min(priced_competitors, key=lambda item: item["price_inr"])
            if lowest["price_inr"] < price:
                threats.append(
                    f"{lowest['brand']} has a lower verified listed price "
                    f"(₹{lowest['price_inr']} vs ₹{price})."
                )
        rating = product.get("rating")
        if rating is not None and rated_competitors:
            highest_rated = max(rated_competitors, key=lambda item: item["rating"])
            if highest_rated["rating"] > rating:
                threats.append(
                    f"{highest_rated['brand']} has a higher listed rating "
                    f"({highest_rated['rating']}/5)."
                )
        if not threats:
            threats.append(
                "The available sourced competitor records do not show a clear price or rating disadvantage."
            )

        return SWOT(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=[
                "Validate recurring public review signals with a larger, representative review set.",
                "Recheck competitor prices and ratings before making time-sensitive campaign claims.",
            ],
            threats=threats,
            source="api",
        )

    def _identify_gaps(self, complaint_themes: list[Theme], total_reviews: int) -> list[MarketGap]:
        gaps = []
        for theme in complaint_themes[:4]:
            ratio = theme.mention_count / total_reviews if total_reviews else 0
            severity = "high" if ratio >= 0.3 else "medium" if theme.mention_count >= 2 else "low"
            evidence = theme.evidence[0] if theme.evidence else "No review excerpt available."
            gaps.append(
                MarketGap(
                    description=_GAP_ACTIONS.get(
                        theme.name,
                        f"Investigate recurring customer feedback about {theme.name.lower()}.",
                    ),
                    evidence=(
                        f"{theme.mention_count} of {total_reviews} retrieved review excerpts mention "
                        f"{theme.name.lower()}. Example: “{evidence}”"
                    ),
                    severity=severity,
                    source="api",
                )
            )
        return gaps

    @staticmethod
    def _identify_review_signals(
        praise_themes: list[Theme],
        complaint_themes: list[Theme],
        total_reviews: int,
    ) -> list[Trend]:
        themes = sorted(
            [*praise_themes, *complaint_themes],
            key=lambda theme: theme.mention_count,
            reverse=True,
        )
        return [
            Trend(
                name=f"Review signal: {theme.name}",
                description=(
                    "A product-specific signal in retrieved public reviews, not evidence of a "
                    "category-wide market trend."
                ),
                relevance="high" if theme.mention_count >= 2 else "medium",
                evidence=(
                    f"{theme.mention_count} of {total_reviews} retrieved excerpts mention "
                    f"{theme.name.lower()}."
                ),
                source="api",
            )
            for theme in themes[:4]
        ]

    @staticmethod
    def _identify_opportunities(
        product: dict[str, Any],
        comparison: dict[str, Any],
        praise_themes: list[Theme],
        complaint_themes: list[Theme],
    ) -> list[Opportunity]:
        opportunities = []
        for theme in complaint_themes[:2]:
            opportunities.append(
                Opportunity(
                    title=f"Address {theme.name.lower()} feedback",
                    description=(
                        f"Test a product or education improvement for {theme.name.lower()}; "
                        "the signal comes from a limited set of retrieved public reviews."
                    ),
                    type="feature_improvement",
                    effort="medium",
                    impact="medium",
                    source="api",
                )
            )

        if praise_themes:
            top_theme = praise_themes[0]
            opportunities.append(
                Opportunity(
                    title=f"Test a {top_theme.name.lower()}-led campaign",
                    description=(
                        f"Build a message variant around {top_theme.name.lower()} and validate "
                        "it with a controlled test."
                    ),
                    type="marketing_angle",
                    effort="low",
                    impact="medium",
                    source="api",
                )
            )

        price = product.get("price_inr")
        if price is not None and comparison["price_analysis"]["position"] in (
            "highest",
            "above_average",
        ):
            opportunities.append(
                Opportunity(
                    title="Test value framing",
                    description=(
                        f"At the verified price of ₹{price}, compare bundle or size options "
                        "with sourced lower-priced competitors; validate margin and conversion."
                    ),
                    type="marketing_angle",
                    effort="medium",
                    impact="medium",
                    source="api",
                )
            )
        return opportunities
