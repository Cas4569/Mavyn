import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.routes import content as content_route
from src.schemas.content import ContentRequest
from src.schemas.product import ProductDetail
from src.services.gemini_content_generator import (
    GeminiAuthenticationError,
    GeminiContentGenerator,
    GeminiOutputError,
)


def _generated_content():
    return {
        "ad_copy": [
            {
                "platform": "instagram",
                "headline": "A cooler daily routine",
                "primary_text": "Explore the sourced product details for this sunscreen.",
                "cta": "Learn more",
                "hashtags": ["DotAndKey"],
            }
        ],
        "product_description": {
            "short_description": "A lightweight sunscreen from the sourced product record.",
            "long_description": "Explore the product using the supplied catalog details.",
            "key_benefits": ["Lightweight feel, as described in the product tagline."],
            "ingredients_highlight": [],
            "usage_instructions": None,
        },
        "listing_content": {
            "title": "Watermelon Cooling Sunscreen SPF 50 PA++++ | Dot & Key",
            "bullet_points": [
                "Use the supplied product tagline.",
                "Listed price in the product record: ₹595.",
                "Verify all product specifications before publishing.",
            ],
            "search_terms": ["sunscreen", "dot key"],
            "enhanced_content": "Explore the supplied product details and public review signals.",
        },
        "ad_scripts": [
            {
                "format": "bumper",
                "duration_seconds": 6,
                "hook": "Meet this daily sunscreen.",
                "script": "[0-6s] Show the product and a clear Learn more end card.",
                "cta": "Learn more",
            }
        ],
        "storyboard": {
            "frames": [
                {
                    "frame_number": 1,
                    "visual_description": "Show approved product packaging.",
                    "audio_cue": "Music begins.",
                    "duration_seconds": 3,
                },
                {
                    "frame_number": 2,
                    "visual_description": "Show the catalog tagline.",
                    "audio_cue": "Read the supplied product description.",
                    "duration_seconds": 4,
                },
                {
                    "frame_number": 3,
                    "visual_description": "Label the review themes as limited public signals.",
                    "audio_cue": "Voiceover explains the source.",
                    "duration_seconds": 5,
                },
            ],
            "total_duration_seconds": 999,
        },
        "video_concepts": [
            {
                "concept_name": "A closer look at daily sunscreen",
                "logline": "An evidence-led introduction to the product.",
                "target_audience": "A hypothesis: shoppers comparing daily sunscreen options.",
                "key_message": "Explore the product and retrieved public review signals.",
                "scripts": [
                    {
                        "format": "reel",
                        "duration_seconds": 20,
                        "hook": "What stands out in this sunscreen?",
                        "script": "[0-5s] Introduce the product. [5-20s] Share review signals.",
                        "cta": "Learn more",
                    }
                ],
                "storyboard": {
                    "frames": [
                        {
                            "frame_number": 1,
                            "visual_description": "Show approved product packaging.",
                            "audio_cue": "Music begins.",
                            "duration_seconds": 3,
                        },
                        {
                            "frame_number": 2,
                            "visual_description": "Show the catalog tagline.",
                            "audio_cue": "Read the supplied product description.",
                            "duration_seconds": 4,
                        },
                        {
                            "frame_number": 3,
                            "visual_description": "Label the review themes as limited public signals.",
                            "audio_cue": "Voiceover explains the source.",
                            "duration_seconds": 5,
                        },
                    ],
                    "total_duration_seconds": 999,
                },
                "production_notes": ["Confirm product claims before publishing."],
            }
        ],
    }


def _research_detail():
    return ProductDetail.model_validate(
        {
            "product": {
                "id": "dk-watermelon-cooling-sunscreen",
                "name": "Watermelon Cooling Sunscreen",
                "category_id": "sunscreens",
                "price_inr": 595,
                "rating": 4.4,
                "review_count": 420,
                "tagline": "Lightweight daily protection",
                "key_ingredients": ["Watermelon Extract"],
                "sources": [
                    {"title": "Product page", "url": "https://example.com/product"}
                ],
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
                    "sources": [
                        {"title": "Competitor", "url": "https://example.com/competitor"}
                    ],
                }
            ],
            "reviews": [
                {
                    "text": "The texture feels light and absorbs quickly.",
                    "source": {
                        "title": "Public review",
                        "url": "https://example.com/review",
                    },
                }
            ],
            "sources": [
                {"title": "Product page", "url": "https://example.com/product"},
                {"title": "Competitor", "url": "https://example.com/competitor"},
                {"title": "Public review", "url": "https://example.com/review"},
            ],
            "fetched_at": "2026-03-05T12:00:00+00:00",
        }
    )


def test_gemini_generation_uses_market_evidence_and_returns_validated_content():
    captured_request = {}

    def handle_request(request):
        captured_request["headers"] = request.headers
        captured_request["url"] = request.url
        captured_request["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": json.dumps(_generated_content())}]}}
                ]
            },
        )

    generator = GeminiContentGenerator(
        api_key="test-key",
        model="gemini-3.5-flash-lite",
        transport=httpx.MockTransport(handle_request),
    )
    request = ContentRequest(
        product_id="dk-sun-001",
        platforms=["instagram"],
        content_types=["ad_copy", "video_concept"],
    )

    result = asyncio.run(generator.generate(request, _research_detail().model_dump(mode="json")))

    assert captured_request["headers"]["x-goog-api-key"] == "test-key"
    assert captured_request["url"].query == b""
    sent_body = captured_request["body"]
    assert sent_body["generationConfig"]["responseMimeType"] == "application/json"
    assert sent_body["generationConfig"]["responseSchema"]["required"] == [
        "ad_copy",
        "video_concepts",
    ]
    assert (
        sent_body["generationConfig"]["responseSchema"]["properties"]["ad_copy"]["items"]
        ["properties"]["platform"]["enum"]
        == ["instagram"]
    )
    evidence = json.loads(sent_body["contents"][0]["parts"][0]["text"])
    assert evidence["evidence_source"] == "Gemini Google Search grounding"
    assert evidence["competitors"]
    assert evidence["review_excerpts"]
    assert evidence["research_sources"]
    assert evidence["market_strategy"]["forecast_note"]

    response = result.model_dump(mode="json")
    assert response["source"] == "llm"
    assert response["model"] == "gemini-3.5-flash-lite"
    assert response["research_sources"]
    assert response["research_fetched_at"]
    assert response["ad_copy"][0]["source"] == "llm"
    assert response["ad_copy"][0]["character_count"] == len(
        response["ad_copy"][0]["headline"] + response["ad_copy"][0]["primary_text"]
    )
    concept = response["video_concepts"][0]
    assert concept["source"] == "llm"
    assert concept["scripts"][0]["source"] == "llm"
    assert concept["storyboard"]["source"] == "llm"
    assert concept["storyboard"]["total_duration_seconds"] == 12


def test_gemini_generates_the_complete_content_pack():
    def handle_request(_request):
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": json.dumps(_generated_content())}]}}
                ]
            },
        )

    generator = GeminiContentGenerator(
        api_key="test-key",
        transport=httpx.MockTransport(handle_request),
    )
    request = ContentRequest(product_id="dk-sun-001", platforms=["instagram"])

    result = asyncio.run(generator.generate(request, _research_detail().model_dump(mode="json")))

    assert result.source == "llm"
    assert result.product_description.source == "llm"
    assert result.listing_content.source == "llm"
    assert result.ad_scripts[0].source == "llm"
    assert result.storyboard.source == "llm"
    assert result.storyboard.total_duration_seconds == 12
    assert result.video_concepts[0].source == "llm"


def test_gemini_route_fails_explicitly_when_key_is_missing(monkeypatch):
    generator = GeminiContentGenerator(api_key="placeholder")
    generator.api_key = None
    monkeypatch.setattr(content_route, "gemini_generator", generator)

    class FakeResearch:
        async def get_product_detail(self, _product_id):
            return _research_detail()

    monkeypatch.setattr(content_route, "market_research", FakeResearch())

    response = TestClient(app).post(
        "/content/generate",
        json={"product_id": "dk-sun-001"},
    )

    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_gemini_generation_rejects_malformed_structured_output():
    def handle_request(_request):
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": '{"ad_scripts":[{"format":"reel"}]}'
                                }
                            ]
                        }
                    }
                ]
            },
        )

    generator = GeminiContentGenerator(
        api_key="test-key",
        transport=httpx.MockTransport(handle_request),
    )
    request = ContentRequest(product_id="dk-sun-001", content_types=["ad_script"])

    with pytest.raises(GeminiOutputError, match="required format"):
        asyncio.run(generator.generate(request, _research_detail().model_dump(mode="json")))


def test_gemini_uses_fallback_model_when_primary_is_unavailable():
    requested_models = []

    def handle_request(request):
        requested_models.append(request.url.path.split("/")[-1].split(":")[0])
        if len(requested_models) == 1:
            return httpx.Response(404, json={"error": {"message": "model unavailable"}})
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        {
                                            "ad_copy": [
                                                {
                                                    "platform": "instagram",
                                                    "headline": "A considered routine",
                                                    "primary_text": "Explore the sourced catalog details.",
                                                    "cta": "Learn more",
                                                    "hashtags": [],
                                                }
                                            ]
                                        }
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    generator = GeminiContentGenerator(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=["gemini-fallback"],
        transport=httpx.MockTransport(handle_request),
    )
    request = ContentRequest(
        product_id="dk-sun-001",
        platforms=["instagram"],
        content_types=["ad_copy"],
    )

    result = asyncio.run(generator.generate(request, _research_detail().model_dump(mode="json")))

    assert requested_models == ["gemini-primary", "gemini-fallback"]
    assert result.source == "llm"
    assert result.model == "gemini-fallback"
    assert result.ad_copy[0].source == "llm"


def test_gemini_does_not_retry_invalid_credentials():
    requested_models = []

    def handle_request(request):
        requested_models.append(request.url.path)
        return httpx.Response(403, json={"error": {"message": "permission denied"}})

    generator = GeminiContentGenerator(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=["gemini-fallback"],
        transport=httpx.MockTransport(handle_request),
    )

    with pytest.raises(GeminiAuthenticationError):
        asyncio.run(
            generator.generate(
                ContentRequest(product_id="dk-sun-001", content_types=["ad_script"]),
                _research_detail().model_dump(mode="json"),
            )
        )

    assert len(requested_models) == 1
