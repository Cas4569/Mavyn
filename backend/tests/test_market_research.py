import asyncio
import json

import httpx
import pytest

from src.services.market_research import (
    GeminiMarketResearch,
    GeminiResearchAuthenticationError,
    GeminiResearchOutputError,
    GeminiResearchProviderError,
    GeminiResearchRateLimitError,
)

PRODUCT_URL = "https://www.dotandkey.com/products/vitamin-c-serum"
COMPETITOR_URL = "https://example.in/products/bright-serum"
REVIEW_URL = "https://example.in/reviews/dot-key-vitamin-c"


def _catalog_facts():
    return {
        "products": [
            {
                "name": "Vitamin C Brightening Serum",
                "category_id": "serums",
                "price_inr": 599,
                "rating": 4.4,
                "review_count": 420,
                "tagline": "A brightening serum",
                "key_ingredients": ["Vitamin C"],
                "source_urls": [PRODUCT_URL],
            }
        ]
    }


def _detail_facts():
    return {
        "product": {
            **_catalog_facts()["products"][0],
        },
        "competitors": [
            {
                "name": "Brightening Serum",
                "brand": "Other Brand",
                "price_inr": 650,
                "rating": 4.2,
                "review_count": 210,
                "key_ingredients": ["Niacinamide"],
                "usp": "Daily brightening",
                "source_urls": [COMPETITOR_URL],
            }
        ],
        "reviews": [
            {
                "text": "The texture feels light and absorbs quickly.",
                "source_url": REVIEW_URL,
                "published_at": "2025-11-02",
            }
        ],
    }


def _interaction(payload, citations):
    return {
        "status": "completed",
        "output_text": json.dumps(payload),
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(payload),
                        "annotations": [
                            {
                                "type": "url_citation",
                                "url": url,
                                "title": title,
                            }
                            for url, title in citations
                        ],
                    }
                ],
            }
        ],
    }


def _service(handler):
    return GeminiMarketResearch(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=[],
        transport=httpx.MockTransport(handler),
        cache_ttl_seconds=60,
    )


def test_catalog_uses_google_search_grounding_and_cited_records():
    captured = {}

    def handle(request):
        captured["request"] = request
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json=_interaction(
                _catalog_facts(),
                [(PRODUCT_URL, "Dot & Key product page")],
            ),
        )

    service = _service(handle)
    result = asyncio.run(service.list_products())

    request = captured["request"]
    body = captured["body"]
    assert request.headers["x-goog-api-key"] == "test-key"
    assert request.url.query == b""
    assert body["tools"] == [{"type": "google_search"}]
    assert body["response_format"]["mime_type"] == "application/json"
    assert result.source == "api"
    assert result.products[0].id == "dk-vitamin-c-brightening-serum"
    assert str(result.products[0].sources[0].url) == PRODUCT_URL
    assert result.fetched_at


def test_catalog_cache_returns_copy_without_repeating_paid_search():
    calls = 0

    def handle(_request):
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json=_interaction(
                _catalog_facts(),
                [(PRODUCT_URL, "Dot & Key product page")],
            ),
        )

    service = _service(handle)

    async def run():
        first = await service.list_products()
        first.products.clear()
        second = await service.list_products()
        return second

    result = asyncio.run(run())
    assert calls == 1
    assert len(result.products) == 1


def test_persistent_catalog_snapshot_survives_service_restart_and_rate_limit(tmp_path):
    snapshot_path = tmp_path / "market-research.json"

    def handle_success(_request):
        return httpx.Response(
            200,
            json=_interaction(
                _catalog_facts(),
                [(PRODUCT_URL, "Dot & Key product page")],
            ),
        )

    first_service = GeminiMarketResearch(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=[],
        transport=httpx.MockTransport(handle_success),
        cache_ttl_seconds=60,
        cache_snapshot_path=snapshot_path,
    )
    first = asyncio.run(first_service.list_products())
    assert first.cached is False

    restarted_service = GeminiMarketResearch(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=[],
        transport=httpx.MockTransport(lambda _request: httpx.Response(429)),
        cache_ttl_seconds=60,
        cache_snapshot_path=snapshot_path,
    )
    restarted_service._catalog_cache = (
        0,
        restarted_service._catalog_cache[1],
    )

    result = asyncio.run(restarted_service.list_products())

    assert result.cached is True
    assert result.products[0].name == "Vitamin C Brightening Serum"


def test_product_detail_includes_only_records_with_google_search_citations():
    catalog_calls = 0

    def handle(request):
        nonlocal catalog_calls
        body = json.loads(request.content)
        if "Find currently listed" in body["input"]:
            catalog_calls += 1
            return httpx.Response(
                200,
                json=_interaction(
                    _catalog_facts(),
                    [(PRODUCT_URL, "Dot & Key product page")],
                ),
            )
        return httpx.Response(
            200,
            json=_interaction(
                _detail_facts(),
                [
                    (PRODUCT_URL, "Dot & Key product page"),
                    (COMPETITOR_URL, "Competitor product page"),
                    (REVIEW_URL, "Public review page"),
                ],
            ),
        )

    service = _service(handle)
    result = asyncio.run(service.get_product_detail("dk-vitamin-c-brightening-serum"))

    assert catalog_calls == 1
    assert result is not None
    assert result.product.name == "Vitamin C Brightening Serum"
    assert result.competitors[0].brand == "Other Brand"
    assert str(result.reviews[0].source.url) == REVIEW_URL
    assert {str(source.url) for source in result.sources} == {
        PRODUCT_URL,
        COMPETITOR_URL,
        REVIEW_URL,
    }


def test_concurrent_detail_requests_share_one_grounded_search():
    class DelayedTransport(httpx.AsyncBaseTransport):
        def __init__(self):
            self.bodies = []

        async def handle_async_request(self, request):
            body = json.loads(request.content)
            self.bodies.append(body)
            await asyncio.sleep(0.01)
            if "Find currently listed" in body["input"]:
                payload = _catalog_facts()
                citations = [(PRODUCT_URL, "Dot & Key product page")]
            else:
                payload = _detail_facts()
                citations = [
                    (PRODUCT_URL, "Dot & Key product page"),
                    (COMPETITOR_URL, "Competitor product page"),
                    (REVIEW_URL, "Public review page"),
                ]
            return httpx.Response(
                200,
                json=_interaction(payload, citations),
                request=request,
            )

    transport = DelayedTransport()
    service = GeminiMarketResearch(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=[],
        transport=transport,
        cache_ttl_seconds=60,
    )

    async def run():
        return await asyncio.gather(
            *(
                service.get_product_detail("dk-vitamin-c-brightening-serum")
                for _ in range(3)
            )
        )

    results = asyncio.run(run())

    assert len(transport.bodies) == 2
    assert all(result is not None for result in results)


def test_uncited_records_are_not_returned():
    payload = _catalog_facts()
    payload["products"][0]["source_urls"] = ["https://unrelated.invalid/product"]
    service = _service(
        lambda _request: httpx.Response(
            200,
            json=_interaction(payload, [(PRODUCT_URL, "Search result")]),
        )
    )

    with pytest.raises(GeminiResearchOutputError, match="verifiable"):
        asyncio.run(service.list_products())


def test_invalid_grounded_metrics_are_rejected_as_provider_output():
    payload = _catalog_facts()
    payload["products"][0]["rating"] = 6.2
    service = _service(
        lambda _request: httpx.Response(
            200,
            json=_interaction(payload, [(PRODUCT_URL, "Dot & Key product page")]),
        )
    )

    with pytest.raises(GeminiResearchOutputError, match="research schema"):
        asyncio.run(service.list_products())


def test_provider_failure_does_not_fall_back_to_static_records():
    service = _service(lambda _request: httpx.Response(503))

    with pytest.raises(GeminiResearchProviderError):
        asyncio.run(service.list_products())


def test_research_uses_fallback_model_when_primary_is_unavailable():
    requested_models = []

    def handle(request):
        body = json.loads(request.content)
        requested_models.append(body["model"])
        if body["model"] == "gemini-primary":
            return httpx.Response(404)
        return httpx.Response(
            200,
            json=_interaction(
                _catalog_facts(),
                [(PRODUCT_URL, "Dot & Key product page")],
            ),
        )

    service = GeminiMarketResearch(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=["gemini-fallback"],
        transport=httpx.MockTransport(handle),
    )

    result = asyncio.run(service.list_products())

    assert requested_models == ["gemini-primary", "gemini-fallback"]
    assert result.source == "api"


def test_rate_limit_retries_fallback_models():
    requested_models = []

    def handle(request):
        requested_models.append(json.loads(request.content)["model"])
        return httpx.Response(429)

    service = GeminiMarketResearch(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=["gemini-fallback"],
        transport=httpx.MockTransport(handle),
    )

    with pytest.raises(GeminiResearchRateLimitError):
        asyncio.run(service.list_products())

    assert requested_models == ["gemini-primary", "gemini-fallback"]


def test_invalid_credentials_fail_without_trying_fallback_models():
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(403)

    service = GeminiMarketResearch(
        api_key="test-key",
        model="gemini-primary",
        fallback_models=["gemini-fallback"],
        transport=httpx.MockTransport(handle),
    )

    with pytest.raises(GeminiResearchAuthenticationError):
        asyncio.run(service.list_products())

    assert len(requests) == 1
