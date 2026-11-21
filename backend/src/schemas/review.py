"""Review analysis schemas."""

from pydantic import BaseModel, Field
from typing import Annotated, Literal


class ReviewInput(BaseModel):
    """Input for review analysis."""

    product_id: Annotated[str, Field(description="Product to analyze")]
    reviews: Annotated[list[str] | None, Field(description="Raw review texts")] = None
    competitor_ids: Annotated[list[str] | None, Field(description="Optional competitor IDs for comparison")] = None


class SentimentBreakdown(BaseModel):
    """Sentiment distribution."""

    positive: Annotated[int, Field(ge=0, description="Count of positive reviews")]
    neutral: Annotated[int, Field(ge=0, description="Count of neutral reviews")]
    negative: Annotated[int, Field(ge=0, description="Count of negative reviews")]
    total: Annotated[int, Field(ge=0, description="Total reviews analyzed")]
    positive_pct: Annotated[float, Field(ge=0, le=100, description="Percentage of positive reviews")]
    negative_pct: Annotated[float, Field(ge=0, le=100, description="Percentage of negative reviews")]


class Theme(BaseModel):
    """A recurring theme in reviews."""

    name: Annotated[str, Field(description="Theme name (e.g., 'Texture', 'Scent', 'Effectiveness')")]
    sentiment: Annotated[Literal["positive", "negative", "mixed"], Field(description="Overall sentiment of this theme")]
    mention_count: Annotated[int, Field(ge=0, description="How many reviews mention this")]
    evidence: Annotated[list[str], Field(description="Direct quotes from reviews", min_length=1)]
    source: Annotated[Literal["sample", "llm"], Field(description="How this theme was derived")] = "sample"


class ReviewAnalysis(BaseModel):
    """Complete review analysis for a product."""

    product_id: str
    sentiment: SentimentBreakdown
    top_praise_themes: Annotated[list[Theme], Field(description="Top positive themes")]
    top_complaint_themes: Annotated[list[Theme], Field(description="Top negative themes")]
    key_insights: Annotated[list[str], Field(description="High-level insights", default_factory=list)]
    analyzed_at: Annotated[str, Field(description="ISO timestamp of analysis")]
    source: Annotated[Literal["sample", "llm"], Field(description="Analysis source")] = "sample"