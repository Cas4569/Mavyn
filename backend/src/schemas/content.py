"""Content generation schemas."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Literal


class AdCopy(BaseModel):
    """Ad copy for a specific platform."""

    platform: Annotated[Literal["instagram", "facebook", "google", "youtube", "linkedin"], Field(description="Platform")]
    headline: Annotated[str, Field(description="Ad headline")]
    primary_text: Annotated[str, Field(description="Primary ad text")]
    cta: Annotated[str, Field(description="Call to action")]
    hashtags: Annotated[list[str], Field(description="Relevant hashtags", default_factory=list)]
    character_count: Annotated[int, Field(ge=0, description="Total character count")]
    source: Annotated[Literal["sample", "llm"], Field(description="Generation source")] = "sample"


class ProductDescription(BaseModel):
    """Product description for PDP."""

    short_description: Annotated[str, Field(description="Short description (< 160 chars)")]
    long_description: Annotated[str, Field(description="Full product description")]
    key_benefits: Annotated[list[str], Field(description="Bullet-point benefits", default_factory=list)]
    ingredients_highlight: Annotated[list[str], Field(description="Hero ingredients", default_factory=list)]
    usage_instructions: Annotated[str | None, Field(description="How to use")] = None
    source: Annotated[Literal["sample", "llm"], Field(description="Generation source")] = "sample"


class ListingContent(BaseModel):
    """Marketplace listing content (Nykaa, Amazon, etc.)."""

    title: Annotated[str, Field(description="Optimized product title")]
    bullet_points: Annotated[list[str], Field(description="Key feature bullets", min_length=3, max_length=7)]
    search_terms: Annotated[list[str], Field(description="Backend search keywords", default_factory=list)]
    enhanced_content: Annotated[str | None, Field(description="A+ content / enhanced brand content")] = None
    source: Annotated[Literal["sample", "llm"], Field(description="Generation source")] = "sample"


class AdScript(BaseModel):
    """Video ad script."""

    format: Annotated[Literal["reel", "shorts", "instream", "bumper"], Field(description="Video format")]
    duration_seconds: Annotated[int, Field(ge=5, le=120, description="Duration in seconds")]
    hook: Annotated[str, Field(description="First 3 seconds hook")]
    script: Annotated[str, Field(description="Full script with visual cues")]
    cta: Annotated[str, Field(description="End call to action")]
    source: Annotated[Literal["sample", "llm"], Field(description="Generation source")] = "sample"


class StoryboardFrame(BaseModel):
    """Single storyboard frame."""

    frame_number: Annotated[int, Field(ge=1, description="Frame sequence number")]
    visual_description: Annotated[str, Field(description="What happens visually")]
    audio_cue: Annotated[str | None, Field(description="Voiceover / music / SFX")] = None
    duration_seconds: Annotated[float, Field(ge=0.5, description="Frame duration")]


class Storyboard(BaseModel):
    """Complete storyboard."""

    frames: Annotated[list[StoryboardFrame], Field(min_length=3, max_length=12)]
    total_duration_seconds: Annotated[float, Field(ge=0, description="Total duration")]
    source: Annotated[Literal["sample", "llm"], Field(description="Generation source")] = "sample"


class VideoConcept(BaseModel):
    """Video concept package."""

    concept_name: Annotated[str, Field(description="Concept title")]
    logline: Annotated[str, Field(description="One-sentence summary")]
    target_audience: Annotated[str, Field(description="Target audience description")]
    key_message: Annotated[str, Field(description="Core message")]
    scripts: Annotated[list[AdScript], Field(description="Script variations", min_length=1, max_length=3)]
    storyboard: Storyboard
    production_notes: Annotated[list[str], Field(description="Production guidance", default_factory=list)]
    source: Annotated[Literal["sample", "llm"], Field(description="Generation source")] = "sample"


class ContentRequest(BaseModel):
    """Request to generate marketing content."""

    product_id: Annotated[str, Field(description="Product to generate content for")]
    strategy_id: Annotated[str | None, Field(description="Optional strategy panel ID to base content on")] = None
    platforms: Annotated[list[Literal["instagram", "facebook", "google", "youtube", "linkedin"]] | None, Field(description="Platforms for ad copy")] = None
    content_types: Annotated[list[Literal["ad_copy", "product_description", "listing", "ad_script", "storyboard", "video_concept"]] | None, Field(description="Content types to generate")] = None


class ContentResponse(BaseModel):
    """Generated marketing content."""

    product_id: str
    ad_copy: Annotated[list[AdCopy], Field(default_factory=list)]
    product_description: ProductDescription | None = None
    listing_content: ListingContent | None = None
    ad_scripts: Annotated[list[AdScript], Field(default_factory=list)]
    storyboard: Storyboard | None = None
    video_concepts: Annotated[list[VideoConcept], Field(default_factory=list)]
    generated_at: Annotated[str, Field(description="ISO timestamp")]
    source: Annotated[Literal["sample", "llm"], Field(description="Generation source")] = "sample"