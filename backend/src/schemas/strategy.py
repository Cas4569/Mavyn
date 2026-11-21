"""Strategy panel schemas (SWOT, gaps, trends, opportunities)."""

from pydantic import BaseModel, Field
from typing import Annotated, Literal


class SWOT(BaseModel):
    """SWOT analysis."""

    strengths: Annotated[list[str], Field(description="Internal strengths", default_factory=list)]
    weaknesses: Annotated[list[str], Field(description="Internal weaknesses", default_factory=list)]
    opportunities: Annotated[list[str], Field(description="External opportunities", default_factory=list)]
    threats: Annotated[list[str], Field(description="External threats", default_factory=list)]
    source: Annotated[Literal["sample", "llm"], Field(description="Analysis source")] = "sample"


class MarketGap(BaseModel):
    """An identified market gap."""

    description: Annotated[str, Field(description="What the gap is")]
    evidence: Annotated[str, Field(description="Supporting evidence from reviews/comparison")]
    severity: Annotated[Literal["high", "medium", "low"], Field(description="Gap severity")]
    source: Annotated[Literal["sample", "llm"], Field(description="Analysis source")] = "sample"


class Trend(BaseModel):
    """A market trend."""

    name: Annotated[str, Field(description="Trend name")]
    description: Annotated[str, Field(description="Trend description")]
    relevance: Annotated[Literal["high", "medium", "low"], Field(description="Relevance to this product")]
    evidence: Annotated[str, Field(description="Supporting evidence")]
    source: Annotated[Literal["sample", "llm"], Field(description="Analysis source")] = "sample"


class Opportunity(BaseModel):
    """A product/marketing opportunity."""

    title: Annotated[str, Field(description="Opportunity title")]
    description: Annotated[str, Field(description="Detailed description")]
    type: Annotated[Literal["new_product", "feature_improvement", "marketing_angle", "channel_expansion"], Field(description="Opportunity type")]
    effort: Annotated[Literal["low", "medium", "high"], Field(description="Implementation effort")]
    impact: Annotated[Literal["low", "medium", "high"], Field(description="Potential impact")]
    source: Annotated[Literal["sample", "llm"], Field(description="Analysis source")] = "sample"


class SalesForecast(BaseModel):
    """Simple sales forecast."""

    period: Annotated[str, Field(description="Forecast period (e.g., 'Q1 2025')")]
    estimated_units: Annotated[int, Field(ge=0, description="Estimated units")]
    estimated_revenue_inr: Annotated[int, Field(ge=0, description="Estimated revenue in INR")]
    confidence: Annotated[Literal["low", "medium", "high"], Field(description="Forecast confidence")]
    assumptions: Annotated[list[str], Field(description="Key assumptions", default_factory=list)]
    source: Annotated[Literal["sample", "llm"], Field(description="Analysis source")] = "sample"


class StrategyPanel(BaseModel):
    """Complete strategy panel for a product."""

    product_id: str
    swot: SWOT
    market_gaps: Annotated[list[MarketGap], Field(default_factory=list)]
    trends: Annotated[list[Trend], Field(default_factory=list)]
    opportunities: Annotated[list[Opportunity], Field(default_factory=list)]
    sales_forecast: Annotated[list[SalesForecast], Field(default_factory=list)]
    generated_at: Annotated[str, Field(description="ISO timestamp")]
    source: Annotated[Literal["sample", "llm"], Field(description="Analysis source")] = "sample"