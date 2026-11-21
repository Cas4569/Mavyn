"""Strategy generation service — SWOT, gaps, trends, opportunities, forecast."""

from datetime import datetime, timezone
from typing import Annotated

from src.schemas.strategy import (
    SWOT,
    MarketGap,
    Trend,
    Opportunity,
    SalesForecast,
    StrategyPanel,
)
from src.services.review_analyzer import ReviewAnalyzer
from src.services.comparator import ProductComparator
from src.data.samples import get_product_detail, get_sample_reviews


class StrategyGenerator:
    """Generates strategy panel from review analysis and competitor comparison."""

    def __init__(self):
        self.review_analyzer = ReviewAnalyzer()
        self.comparator = ProductComparator()

    def generate(self, product_id: str) -> StrategyPanel:
        """Generate full strategy panel for a product."""
        # Get product detail
        detail = get_product_detail(product_id)
        if not detail:
            raise ValueError(f"Product not found: {product_id}")

        product = detail["product"]
        competitors = detail["competitors"]
        sample_reviews = detail["sample_reviews"]

        # Run review analysis
        review_input = type("ReviewInput", (), {
            "product_id": product_id,
            "reviews": sample_reviews,
            "competitor_ids": None
        })()
        review_analysis = self.review_analyzer.analyze(review_input)

        # Run comparison
        comparison = self.comparator.compare(product_id)

        # Generate each section
        swot = self._generate_swot(product, review_analysis, comparison)
        gaps = self._identify_gaps(product, review_analysis, comparison)
        trends = self._identify_trends(product, review_analysis)
        opportunities = self._identify_opportunities(product, review_analysis, comparison, gaps)
        forecast = self._generate_forecast(product, comparison)

        return StrategyPanel(
            product_id=product_id,
            swot=swot,
            market_gaps=gaps,
            trends=trends,
            opportunities=opportunities,
            sales_forecast=forecast,
            generated_at=datetime.now(timezone.utc).isoformat(),
            source="sample",
        )

    def _generate_swot(
        self,
        product: dict,
        review_analysis,
        comparison: dict,
    ) -> SWOT:
        """Generate SWOT analysis."""
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []

        # Strengths from review praise
        for theme in review_analysis.top_praise_themes:
            if theme.sentiment == "positive":
                strengths.append(f"Customers praise {theme.name.lower()} ({theme.mention_count} mentions)")

        # Strengths from comparison
        price_analysis = comparison.get("price_analysis", {})
        rating_analysis = comparison.get("rating_analysis", {})

        if price_analysis.get("position") in ("lowest", "below_average"):
            strengths.append(f"Competitive pricing at ₹{product['price_inr']} ({price_analysis.get('position', '').replace('_', ' ')} vs competitors)")
        if rating_analysis.get("position") in ("highest", "above_average"):
            strengths.append(f"Strong rating of {product['rating']}/5 ({rating_analysis.get('position', '').replace('_', ' ')} vs competitors)")

        # Weaknesses from review complaints
        for theme in review_analysis.top_complaint_themes:
            if theme.sentiment == "negative":
                weaknesses.append(f"Customer complaints about {theme.name.lower()} ({theme.mention_count} mentions)")

        if price_analysis.get("position") in ("highest", "above_average"):
            weaknesses.append(f"Premium pricing at ₹{product['price_inr']} ({price_analysis.get('position', '').replace('_', ' ')} vs competitors)")

        # Opportunities from gaps/trends
        opportunities.append("Expand shade-inclusive marketing to address white cast concerns")
        opportunities.append("Leverage ingredient transparency trend with detailed actives disclosure")
        opportunities.append("Bundle with complementary products (cleanser + serum + moisturizer)")

        # Threats from competitors
        threats.append("Competitors launching similar actives at lower price points")
        threats.append("Market saturation in Vitamin C / Niacinamide categories")
        threats.append("Raw material cost volatility affecting margins")

        return SWOT(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            source="sample",
        )

    def _identify_gaps(
        self,
        product: dict,
        review_analysis,
        comparison: dict,
    ) -> list[MarketGap]:
        """Identify market gaps from reviews and comparison."""
        gaps = []

        # Gap from white cast complaints
        for theme in review_analysis.top_complaint_themes:
            if theme.name == "White Cast" and theme.mention_count >= 2:
                gaps.append(MarketGap(
                    description="No truly invisible sunscreen/serum for deeper skin tones in this price segment",
                    evidence=f"{theme.mention_count} reviews mention white cast on deeper skin tones",
                    severity="high",
                    source="sample",
                ))

        # Gap from breakout complaints
        for theme in review_analysis.top_complaint_themes:
            if theme.name == "Breakouts" and theme.mention_count >= 2:
                gaps.append(MarketGap(
                    description="Non-comedogenic claim not fully delivered for acne-prone users",
                    evidence=f"{theme.mention_count} reviews report breakouts/clogged pores",
                    severity="medium",
                    source="sample",
                ))

        # Gap from packaging complaints
        for theme in review_analysis.top_complaint_themes:
            if theme.name == "Packaging" and theme.mention_count >= 2:
                gaps.append(MarketGap(
                    description="Packaging usability issues (pump failure, waste, pour control)",
                    evidence=f"{theme.mention_count} reviews mention packaging problems",
                    severity="low",
                    source="sample",
                ))

        # Gap from competitor feature comparison
        feature_comp = comparison.get("feature_comparison", {})
        missing = feature_comp.get("competitors_have_not_dk", [])
        if "Ceramides" in missing or "Hyaluronic Acid" in missing:
            gaps.append(MarketGap(
                description="Competitors offer barrier-repair ingredients (ceramides, HA) not in this formula",
                evidence=f"Competitors include: {', '.join(missing[:5])}",
                severity="medium",
                source="sample",
            ))

        return gaps

    def _identify_trends(
        self,
        product: dict,
        review_analysis,
    ) -> list[Trend]:
        """Identify relevant market trends."""
        trends = []

        # Trend: Ingredient transparency
        trends.append(Trend(
            name="Ingredient Transparency & Actives Education",
            description="Consumers increasingly research actives percentages, pH, stability — demand full disclosure",
            relevance="high",
            evidence="Reviews mention specific ingredients (Vitamin C %, niacinamide %, ceramide complex) and stability concerns",
            source="sample",
        ))

        # Trend: Skin barrier focus
        trends.append(Trend(
            name="Skin Barrier Repair & Minimal Routines",
            description="Shift from aggressive actives to barrier-supportive, minimal routines (skin cycling, skin flooding)",
            relevance="high",
            evidence="Praise for ceramide/hyaluronic products; complaints about irritation from strong actives",
            source="sample",
        ))

        # Trend: Inclusive shade/formulation
        trends.append(Trend(
            name="Inclusive Formulation for Indian Skin Tones",
            description="Demand for no-white-cast, no-gray-cast products tested on deeper skin tones (Fitzpatrick IV-VI)",
            relevance="high",
            evidence="Multiple reviews flag white cast on NC40+ skin tones",
            source="sample",
        ))

        # Trend: Multi-functional products
        trends.append(Trend(
            name="Multi-Functional Hybrid Products",
            description="Consumers prefer 2-in-1/3-in-1 (moisturizer+SPF, serum+primer, toner+essence) to simplify routines",
            relevance="medium",
            evidence="Dot & Key's own Vitamin C Day Cream SPF 20 shows this direction; competitors launching hybrids",
            source="sample",
        ))

        return trends

    def _identify_opportunities(
        self,
        product: dict,
        review_analysis,
        comparison: dict,
        gaps: list[MarketGap],
    ) -> list[Opportunity]:
        """Identify product/marketing opportunities."""
        opportunities = []

        # From gaps
        for gap in gaps:
            if gap.severity == "high" and "white cast" in gap.description.lower():
                opportunities.append(Opportunity(
                    title="Reformulate for True Invisibility on All Skin Tones",
                    description="Develop next-gen filter system with zero white cast, validated on Fitzpatrick IV-VI. Market as 'Invisible on Every Indian Skin Tone'.",
                    type="feature_improvement",
                    effort="high",
                    impact="high",
                    source="sample",
                ))
            if gap.severity == "medium" and "non-comedogenic" in gap.description.lower():
                opportunities.append(Opportunity(
                    title="Launch 'Acne-Safe' Certified Variant",
                    description="Create non-comedogenic tested version with salicylic acid + niacinamide for acne-prone skin. Partner with dermatologists for certification.",
                    type="new_product",
                    effort="medium",
                    impact="high",
                    source="sample",
                ))

        # From praise themes
        for theme in review_analysis.top_praise_themes:
            if theme.name == "Value" and theme.sentiment == "positive":
                opportunities.append(Opportunity(
                    title="Value-Focused Bundle Strategy",
                    description="Bundle hero product with complementary items (cleanser + moisturizer) at 15% discount. Position as 'Complete Routine for ₹X'.",
                    type="marketing_angle",
                    effort="low",
                    impact="medium",
                    source="sample",
                ))

        # From trends
        opportunities.append(Opportunity(
            title="Barrier Repair Serum Line Extension",
            description="Launch dedicated barrier repair serum (ceramides + cholesterol + fatty acids + panthenol) to ride barrier trend.",
            type="new_product",
            effort="medium",
            impact="high",
            source="sample",
        ))

        opportunities.append(Opportunity(
            title="Dermatologist Co-Created Content Series",
            description="Partner with 3-5 Indian dermatologists for 'Science of Skincare' content series. Builds trust, drives SEO, supports ingredient transparency trend.",
            type="marketing_angle",
            effort="low",
            impact="medium",
            source="sample",
        ))

        # Channel expansion
        opportunities.append(Opportunity(
            title="Quick Commerce (Blinkit/Zepto/Instamart) Expansion",
            description="List top 5 SKUs on quick commerce platforms for impulse/emergency purchases. 15-20% revenue uplift observed by competitors.",
            type="channel_expansion",
            effort="medium",
            impact="medium",
            source="sample",
        ))

        return opportunities

    def _generate_forecast(
        self,
        product: dict,
        comparison: dict,
    ) -> list[SalesForecast]:
        """Generate simple sales forecast (sample logic)."""
        # Base estimates from review count and rating
        review_count = product.get("review_count", 100)
        rating = product.get("rating", 4.0)
        price = product.get("price_inr", 500)

        # Rough conversion: reviews ≈ 1-2% of buyers
        estimated_buyers = review_count * 75  # Conservative multiplier

        # Quarterly forecast
        base_quarterly = estimated_buyers // 4

        return [
            SalesForecast(
                period="Q1 2025",
                estimated_units=base_quarterly,
                estimated_revenue_inr=base_quarterly * price,
                confidence="medium",
                assumptions=[
                    f"Based on {review_count} reviews (est. 1-2% review rate)",
                    "Assumes steady demand, no major competitor launches",
                    "No marketing spend increase factored in",
                ],
                source="sample",
            ),
            SalesForecast(
                period="Q2 2025",
                estimated_units=int(base_quarterly * 1.15),  # Summer sunscreen boost
                estimated_revenue_inr=int(base_quarterly * 1.15 * price),
                confidence="medium",
                assumptions=[
                    "Seasonal uplift for sunscreen/brightening categories",
                    "Assumes new product launch in Q1 drives halo effect",
                ],
                source="sample",
            ),
            SalesForecast(
                period="Q3 2025",
                estimated_units=int(base_quarterly * 1.05),
                estimated_revenue_inr=int(base_quarterly * 1.05 * price),
                confidence="low",
                assumptions=[
                    "Monsoon season dip for sunscreen, steady for serums",
                    "Festival season prep begins late Q3",
                ],
                source="sample",
            ),
            SalesForecast(
                period="Q4 2025",
                estimated_units=int(base_quarterly * 1.35),  # Festival/wedding season
                estimated_revenue_inr=int(base_quarterly * 1.35 * price),
                confidence="low",
                assumptions=[
                    "Diwali/wedding season peak for skincare gifting",
                    "Assumes gift set launches and promotional campaigns",
                ],
                source="sample",
            ),
        ]