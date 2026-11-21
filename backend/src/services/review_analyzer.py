"""Review analysis service — analyzes customer reviews for sentiment and themes."""

from datetime import UTC, datetime
from typing import ClassVar, Literal

from src.schemas.product import ResearchSource
from src.schemas.review import (
    ReviewAnalysis,
    ReviewInput,
    SentimentBreakdown,
    Theme,
)


class ReviewAnalyzer:
    """Analyzes review texts for sentiment, themes, and insights."""

    # Lightweight, explainable signal extraction from retrieved review excerpts.

    POSITIVE_KEYWORDS: ClassVar[set[str]] = {
        "love", "great", "amazing", "excellent", "perfect", "best", "awesome",
        "fantastic", "wonderful", "brilliant", "outstanding", "superb", "good",
        "nice", "happy", "satisfied", "pleased", "impressed", "recommend",
        "repurchase", "holy grail", "game changer", "saved", "works", "effective",
        "visible", "noticeable", "difference", "improved", "better", "glow",
        "radiant", "smooth", "hydrated", "soothing", "gentle", "lightweight",
        "non-greasy", "absorbs", "fast", "value", "affordable", "worth",
    }

    NEGATIVE_KEYWORDS: ClassVar[set[str]] = {
        "hate", "terrible", "awful", "worst", "bad", "poor", "disappointed",
        "disappointing", "waste", "money", "regret", "return", "refund",
        "broke out", "breakout", "acne", "pimples", "clogged", "pores",
        "irritation", "irritated", "redness", "burn", "sting", "stinging",
        "sensitive", "reaction", "allergic", "rash", "itchy", "dry", "drying",
        "tight", "stripped", "heavy", "greasy", "oily", "shine", "pilling",
        "pills", "white cast", "oxidized", "smell", "scent", "fragrance",
        "strong", "chemical", "expensive", "pricey", "overpriced", "small",
        "tiny", "packaging", "pump", "broken", "leak", "waste product",
    }

    THEME_KEYWORDS: ClassVar[dict[str, list[str]]] = {
        "Texture": [
            "texture", "consistency", "lightweight", "heavy", "thick", "thin",
            "watery", "gel", "cream", "lotion", "absorb", "absorption", "greasy",
            "oily", "sticky", "tacky", "smooth", "silky", "pilling", "pills",
            "layer", "layering", "spread", "spreadability",
        ],
        "Scent": [
            "scent", "smell", "fragrance", "odor", "perfume", "aroma", "citrus",
            "chemical", "strong", "subtle", "pleasant", "unpleasant", "unscented",
            "fragrance-free", "smells",
        ],
        "Effectiveness": [
            "work", "works", "effective", "result", "results", "improve", "improved",
            "better", "difference", "change", "visible", "noticeable", "fade",
            "faded", "brighten", "brightened", "glow", "radiant", "clear", "cleared",
            "reduce", "reduced", "minimize", "minimized", "control", "controlled",
            "help", "helped", "fix", "fixed", "solve", "solved",
        ],
        "Packaging": [
            "packaging", "bottle", "pump", "dropper", "jar", "tube", "container",
            "dispenser", "leak", "leaking", "broken", "waste", "opening", "pour",
            "size", "travel", "hygienic",
        ],
        "Value": [
            "price", "cost", "expensive", "cheap", "affordable", "value", "worth",
            "money", "budget", "overpriced", "reasonable", "last", "lasts",
            "long", "months", "quantity", "amount", "bang for buck",
        ],
        "Skin Feel": [
            "feel", "feels", "skin", "face", "dry", "hydrated", "moisturized",
            "tight", "stripped", "soft", "smooth", "plump", "supple", "comfortable",
            "soothing", "calm", "cooling", "refreshing", "tingle", "tingling",
            "sting", "stinging", "burn", "burning",
        ],
        "White Cast": [
            "white cast", "whitecast", "cast", "flashback", "flash", "photography",
            "photo", "picture", "tone", "skin tone", "deeper", "darker", "blend",
            "blends", "visible", "noticeable",
        ],
        "Breakouts": [
            "breakout", "breakouts", "acne", "pimple", "pimples", "clogged",
            "clog", "pore", "pores", "comedone", "comedones", "blackhead",
            "blackheads", "whitehead", "whiteheads", "congested", "congestion",
        ],
        "Sensitivity": [
            "sensitive", "reactive", "rosacea", "eczema", "dermatitis", "irritation",
            "irritated", "red", "redness", "rash", "allergy", "allergic", "reaction",
            "patch test", "gentle", "mild", "tolerate", "tolerated",
        ],
    }

    def analyze(
        self,
        input_data: ReviewInput,
        source: Literal["api", "llm", "user"] = "api",
        sources: list[ResearchSource] | None = None,
    ) -> ReviewAnalysis:
        """Analyze reviews and return structured analysis."""
        reviews = input_data.reviews or []

        # Sentiment analysis
        sentiment = self._analyze_sentiment(reviews)

        # Theme extraction
        praise_themes = self._extract_themes(reviews, positive=True, source=source)
        complaint_themes = self._extract_themes(reviews, positive=False, source=source)

        # Key insights
        insights = self._generate_insights(sentiment, praise_themes, complaint_themes)

        return ReviewAnalysis(
            product_id=input_data.product_id,
            sentiment=sentiment,
            top_praise_themes=praise_themes[:5],
            top_complaint_themes=complaint_themes[:5],
            key_insights=insights,
            analyzed_at=datetime.now(UTC).isoformat(),
            source=source,
            sources=sources or [],
        )

    def _analyze_sentiment(self, reviews: list[str]) -> SentimentBreakdown:
        """Simple keyword-based sentiment classification."""
        positive = 0
        negative = 0
        neutral = 0

        for review in reviews:
            review_lower = review.lower()
            pos_score = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in review_lower)
            neg_score = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in review_lower)

            if pos_score > neg_score:
                positive += 1
            elif neg_score > pos_score:
                negative += 1
            else:
                neutral += 1

        total = len(reviews)
        pos_pct = round(positive / total * 100, 1) if total else 0.0
        neg_pct = round(negative / total * 100, 1) if total else 0.0

        return SentimentBreakdown(
            positive=positive,
            neutral=neutral,
            negative=negative,
            total=total,
            positive_pct=pos_pct,
            negative_pct=neg_pct,
        )

    def _extract_themes(
        self,
        reviews: list[str],
        positive: bool,
        source: Literal["api", "llm", "user"],
    ) -> list[Theme]:
        """Extract themes from reviews with sentiment filter."""
        theme_mentions: dict[str, list[str]] = {theme: [] for theme in self.THEME_KEYWORDS}

        for review in reviews:
            review_lower = review.lower()

            # Determine review sentiment
            pos_score = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in review_lower)
            neg_score = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in review_lower)
            review_sentiment = "positive" if pos_score > neg_score else ("negative" if neg_score > pos_score else "mixed")

            # Only include reviews matching requested sentiment
            if positive and review_sentiment not in ("positive", "mixed"):
                continue
            if not positive and review_sentiment not in ("negative", "mixed"):
                continue

            # Check each theme
            for theme, keywords in self.THEME_KEYWORDS.items():
                for kw in keywords:
                    if kw in review_lower:
                        theme_mentions[theme].append(review.strip())
                        break  # Count review once per theme

        # Build Theme objects
        themes = []
        for theme_name, evidence_list in theme_mentions.items():
            if evidence_list:
                # Determine theme sentiment based on majority of evidence reviews
                pos_count = 0
                neg_count = 0
                for ev in evidence_list:
                    ev_lower = ev.lower()
                    p = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in ev_lower)
                    n = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in ev_lower)
                    if p > n:
                        pos_count += 1
                    elif n > p:
                        neg_count += 1

                if pos_count > neg_count:
                    sentiment = "positive"
                elif neg_count > pos_count:
                    sentiment = "negative"
                else:
                    sentiment = "mixed"

                # For praise themes, only include positive/mixed
                # For complaint themes, only include negative/mixed
                if positive and sentiment == "negative":
                    continue
                if not positive and sentiment == "positive":
                    continue

                themes.append(Theme(
                    name=theme_name,
                    sentiment=sentiment,
                    mention_count=len(evidence_list),
                    evidence=evidence_list[:3],  # Top 3 evidence quotes
                    source=source,
                ))

        # Sort by mention count descending
        themes.sort(key=lambda t: t.mention_count, reverse=True)
        return themes

    def _generate_insights(
        self,
        sentiment: SentimentBreakdown,
        praise_themes: list[Theme],
        complaint_themes: list[Theme],
    ) -> list[str]:
        """Generate high-level insights from analysis."""
        insights = []

        # Sentiment insight
        if sentiment.positive_pct > 70:
            insights.append(f"Strong positive reception ({sentiment.positive_pct}% positive)")
        elif sentiment.negative_pct > 40:
            insights.append(f"Significant negative feedback ({sentiment.negative_pct}% negative) — investigate complaints")
        else:
            insights.append(f"Mixed reception — {sentiment.positive_pct}% positive, {sentiment.negative_pct}% negative")

        # Top praise insight
        if praise_themes:
            top_praise = praise_themes[0]
            insights.append(f"Top praise: {top_praise.name} ({top_praise.mention_count} mentions)")

        # Top complaint insight
        if complaint_themes:
            top_complaint = complaint_themes[0]
            insights.append(f"Top complaint: {top_complaint.name} ({top_complaint.mention_count} mentions)")

        # Specific actionable insights
        theme_names_praise = {t.name for t in praise_themes}
        theme_names_complaint = {t.name for t in complaint_themes}

        if "White Cast" in theme_names_complaint:
            insights.append("White cast reported — consider reformulation or shade-inclusive marketing")
        if "Breakouts" in theme_names_complaint:
            insights.append("Breakout reports present — clarify non-comedogenic claims or target skin types")
        if "Packaging" in theme_names_complaint:
            insights.append("Packaging issues mentioned — review dispenser design")
        if "Value" in theme_names_praise:
            insights.append("Strong value perception — leverage in competitive positioning")
        if "Effectiveness" in theme_names_praise:
            insights.append("Effectiveness praised — highlight clinical/visible results in marketing")

        return insights