"""Live market records grounded in Tavily web search + NVIDIA NIM reasoning."""

import asyncio
import json
import re
import time
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, Field, SecretStr, ValidationError

from src.config import settings
from src.data.categories import get_categories
from src.schemas.product import (
    Competitor,
    CustomerReview,
    Product,
    ProductCatalog,
    ProductDetail,
    ProductList,
    ResearchSource,
)
from src.services.tavily_search import (
    SearchResult,
    TavilySearchAuthenticationError,
    TavilySearchProviderError,
    TavilySearchRateLimitError,
    tavily_search,
)


_SYSTEM_PROMPT = """You are a market research analyst. Extract verified product facts from the supplied web search results.
Only return facts explicitly stated in the search results. Never invent prices, ratings, ingredients, or URLs.
Use null or an empty list when a field cannot be verified from the supplied results."""


class NimResearchError(Exception):
    """Base error for NVIDIA NIM research."""


class NimResearchConfigurationError(NimResearchError):
    """NIM or Tavily research is not configured."""


class NimResearchAuthenticationError(NimResearchError):
    """NIM rejected the configured API key or model."""


class NimResearchModelUnavailableError(NimResearchError):
    """The configured NIM model is unavailable for grounded search."""


class NimResearchRateLimitError(NimResearchError):
    """NIM search quota or request rate was exceeded."""


class NimResearchTimeoutError(NimResearchError):
    """NIM research did not complete in time."""


class NimResearchProviderError(NimResearchError):
    """NIM could not complete grounded research."""


class NimResearchOutputError(NimResearchError):
    """NIM did not return verifiable structured research."""


class _ProductFact(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category_id: Literal["sunscreens", "serums", "moisturizers", "cleansers", "toners"]
    price_inr: int | None = Field(ge=0)
    rating: float | None = Field(ge=0, le=5)
    review_count: int | None = Field(ge=0)
    tagline: str | None = Field(max_length=300)
    key_ingredients: list[str]
    source_urls: list[str]


class _CatalogFacts(BaseModel):
    products: list[_ProductFact]


class _CompetitorFact(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    brand: str = Field(min_length=1, max_length=100)
    price_inr: int | None = Field(ge=0)
    rating: float | None = Field(ge=0, le=5)
    review_count: int | None = Field(ge=0)
    key_ingredients: list[str]
    usp: str | None = Field(max_length=300)
    source_urls: list[str]


class _ReviewFact(BaseModel):
    text: str = Field(min_length=1, max_length=3000)
    source_url: str
    published_at: str | None


class _ProductDetailFacts(BaseModel):
    product: _ProductFact
    competitors: list[_CompetitorFact]
    reviews: list[_ReviewFact]


class NimMarketResearch:
    """Retrieve cited product records via Tavily search + NVIDIA NIM structured extraction."""

    def __init__(
        self,
        api_key: str | SecretStr | None = None,
        model: str | None = None,
        fallback_models: str | list[str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        cache_ttl_seconds: int | None = None,
        cache_snapshot_path: str | Path | None = None,
    ) -> None:
        if api_key is None:
            api_key = settings.nim_api_key
        if isinstance(api_key, SecretStr):
            api_key = api_key.get_secret_value()

        self.api_key = api_key.strip() if api_key and api_key.strip() else None
        self.model = (model or settings.nim_model).strip()
        configured_fallbacks = (
            settings.nim_fallback_models if fallback_models is None else fallback_models
        )
        if isinstance(configured_fallbacks, str):
            self.fallback_models = [
                value.strip() for value in configured_fallbacks.split(",") if value.strip()
            ]
        else:
            self.fallback_models = [value.strip() for value in configured_fallbacks if value.strip()]
        self.base_url = settings.nim_base_url.rstrip("/")
        self.transport = transport
        self.cache_ttl_seconds = (
            settings.market_data_cache_ttl_seconds
            if cache_ttl_seconds is None
            else cache_ttl_seconds
        )
        self._catalog_cache: tuple[float, ProductCatalog] | None = None
        self._detail_cache: dict[str, tuple[float, ProductDetail]] = {}
        self._catalog_lock = asyncio.Lock()
        self._detail_locks: dict[str, asyncio.Lock] = {}
        self._request_limit = asyncio.Semaphore(2)
        self._cache_snapshot_path = (
            Path(cache_snapshot_path) if cache_snapshot_path is not None else None
        )
        self._load_persistent_cache()

    def _load_persistent_cache(self) -> None:
        try:
            if self._cache_snapshot_path is None:
                return
            if not self._cache_snapshot_path.exists():
                return
            snapshot = json.loads(self._cache_snapshot_path.read_text(encoding="utf-8"))
            if not isinstance(snapshot, dict):
                return
            catalog = snapshot.get("catalog")
            if isinstance(catalog, dict):
                expires_at_wall = float(catalog["expires_at"])
                remaining_seconds = max(0.0, expires_at_wall - time.time())
                self._catalog_cache = (
                    time.monotonic() + remaining_seconds,
                    ProductCatalog.model_validate(catalog["data"]),
                )
            details = snapshot.get("details")
            if isinstance(details, dict):
                for product_id, detail in details.items():
                    if not isinstance(detail, dict):
                        continue
                    expires_at_wall = float(detail["expires_at"])
                    remaining_seconds = max(0.0, expires_at_wall - time.time())
                    self._detail_cache[product_id] = (
                        time.monotonic() + remaining_seconds,
                        ProductDetail.model_validate(detail["data"]),
                    )
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError, ValueError):
            return

    def _save_persistent_cache(self) -> None:
        try:
            if self._cache_snapshot_path is None:
                return
            snapshot: dict[str, Any] = {
                "catalog": None,
                "details": {},
            }
            if self._catalog_cache is not None:
                expires_at, catalog = self._catalog_cache
                snapshot["catalog"] = {
                    "expires_at": time.time() + max(0.0, expires_at - time.monotonic()),
                    "data": catalog.model_dump(mode="json"),
                }
            for product_id, (expires_at, detail) in self._detail_cache.items():
                snapshot["details"][product_id] = {
                    "expires_at": time.time() + max(0.0, expires_at - time.monotonic()),
                    "data": detail.model_dump(mode="json"),
                }
            self._cache_snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self._cache_snapshot_path.with_suffix(".tmp")
            temporary_path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
            temporary_path.replace(self._cache_snapshot_path)
        except OSError:
            return

    async def list_products(self) -> ProductCatalog:
        now = time.monotonic()
        if self._catalog_cache and self._catalog_cache[0] > now:
            result = self._catalog_cache[1].model_copy(deep=True)
            result.cached = True
            return result

        async with self._catalog_lock:
            now = time.monotonic()
            if self._catalog_cache and self._catalog_cache[0] > now:
                result = self._catalog_cache[1].model_copy(deep=True)
                result.cached = True
                return result

            try:
                payload, citations = await self._generate(
                    self._catalog_prompt(),
                    _schema_for(_CatalogFacts),
                )
            except NimResearchRateLimitError:
                if self._catalog_cache is not None:
                    result = self._catalog_cache[1].model_copy(deep=True)
                    result.cached = True
                    return result
                raise
            facts = _validate_facts(_CatalogFacts, payload)
            products: list[Product] = []
            seen_ids: set[str] = set()
            for fact in facts.products:
                product = _build_product(fact, citations)
                if product is None or product.id in seen_ids:
                    continue
                seen_ids.add(product.id)
                products.append(product)

            if not products:
                raise NimResearchOutputError(
                    "No verifiable Dot & Key product records found."
                )

            source_refs = _unique_sources(
                source for product in products for source in product.sources
            )
            catalog = ProductCatalog(
                products=products,
                total=len(products),
                sources=source_refs,
                fetched_at=datetime.now(UTC).isoformat(),
            )
            self._catalog_cache = (now + self.cache_ttl_seconds, catalog)
            self._save_persistent_cache()
            return catalog.model_copy(deep=True)

    async def list_products_by_category(self, category_id: str) -> ProductList | None:
        catalog = await self.list_products()
        products = [item for item in catalog.products if item.category_id == category_id]
        if not products:
            return None

        category = next((item for item in get_categories() if item["id"] == category_id), None)
        return ProductList(
            category_id=category_id,
            category_name=category["name"] if category else category_id,
            products=products,
            total=len(products),
            sources=_unique_sources(
                source for item in products for source in item.sources
            ),
            fetched_at=catalog.fetched_at,
            cached=catalog.cached,
        )

    async def get_product_detail(self, product_id: str) -> ProductDetail | None:
        catalog = await self.list_products()
        catalog_product = next(
            (item for item in catalog.products if item.id == product_id),
            None,
        )
        if catalog_product is None:
            return None

        now = time.monotonic()
        cached = self._detail_cache.get(product_id)
        if cached and cached[0] > now:
            result = cached[1].model_copy(deep=True)
            result.cached = True
            return result

        lock = self._detail_locks.setdefault(product_id, asyncio.Lock())
        async with lock:
            now = time.monotonic()
            cached = self._detail_cache.get(product_id)
            if cached and cached[0] > now:
                result = cached[1].model_copy(deep=True)
                result.cached = True
                return result

            try:
                payload, citations = await self._generate(
                    self._detail_prompt(catalog_product),
                    _schema_for(_ProductDetailFacts),
                )
            except NimResearchRateLimitError:
                if cached is not None:
                    result = cached[1].model_copy(deep=True)
                    result.cached = True
                    return result
                raise
            facts = _validate_facts(_ProductDetailFacts, payload)
            if _slug(facts.product.name) == _slug(catalog_product.name):
                detail_product = _build_product(
                    facts.product,
                    citations,
                    product_id=product_id,
                )
            else:
                detail_product = None
            if detail_product is None:
                detail_product = catalog_product.model_copy(deep=True)

            competitors = [
                competitor
                for fact in facts.competitors
                if (competitor := _build_competitor(fact, citations)) is not None
            ]
            reviews = [
                review
                for fact in facts.reviews
                if (review := _build_review(fact, citations)) is not None
            ]
            sources = _unique_sources(
                [
                    *detail_product.sources,
                    *(source for item in competitors for source in item.sources),
                    *(review.source for review in reviews),
                ]
            )
            detail = ProductDetail(
                product=detail_product,
                competitors=competitors,
                reviews=reviews,
                sources=sources,
                fetched_at=datetime.now(UTC).isoformat(),
            )
            cache_expires_at = now + self.cache_ttl_seconds
            if self._catalog_cache is not None:
                cache_expires_at = min(cache_expires_at, self._catalog_cache[0])
            self._detail_cache[product_id] = (
                cache_expires_at,
                detail,
            )
            self._save_persistent_cache()
            return detail.model_copy(deep=True)

    async def _generate(
        self,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> tuple[dict[str, Any], list[ResearchSource]]:
        if not self.api_key:
            raise NimResearchConfigurationError(
                "NIM is not configured. Add NIM_API_KEY to backend/.env."
            )
        if not settings.tavily_api_key:
            raise NimResearchConfigurationError(
                "Tavily is not configured. Add TAVILY_API_KEY to backend/.env."
            )

        # Stage 1: search for live evidence
        try:
            search_results = await tavily_search.search(prompt)
        except TavilySearchAuthenticationError as exc:
            raise NimResearchAuthenticationError(
                "Tavily rejected the configured API key."
            ) from exc
        except TavilySearchRateLimitError as exc:
            raise NimResearchRateLimitError(str(exc)) from exc
        except TavilySearchProviderError as exc:
            raise NimResearchProviderError(str(exc)) from exc
        evidence_text = self._format_evidence(search_results)

        # Stage 2: NIM extracts structured facts from the evidence
        full_prompt = (
            f"{prompt}\n\n"
            f"Search results evidence:\n{evidence_text}\n\n"
            "Return ONLY valid JSON matching the requested schema."
        )

        models = list(dict.fromkeys([self.model, *self.fallback_models]))[:3]
        if not models or any(not re.fullmatch(r"[A-Za-z0-9._/-]{1,120}", name) for name in models):
            raise NimResearchConfigurationError(
                "NIM_MODEL and NIM_FALLBACK_MODELS must contain valid model names."
            )

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 6144,
        }

        last_error: NimResearchError | None = None
        for model in models:
            body["model"] = model
            try:
                response = await self._nim_request(body)
                text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not isinstance(text, str) or not text.strip():
                    raise NimResearchOutputError("NIM returned no structured text.")
                # Strip markdown code fences if NIM wrapped JSON in ```json ... ```
                cleaned = text.strip()
                if cleaned.startswith("```"):
                    # Remove opening ```json or ``` fence
                    cleaned = re.sub(r"^```\w*\n?", "", cleaned)
                    # Remove closing ``` fence
                    cleaned = re.sub(r"\n?```$", "", cleaned)
                try:
                    result = json.loads(cleaned)
                except json.JSONDecodeError:
                    # Last-resort salvage: try to extract the first balanced JSON object
                    try:
                        result = _extract_first_json_object(cleaned)
                    except Exception:
                        raise NimResearchOutputError(
                            "NIM returned invalid JSON that could not be repaired."
                        )
                if not isinstance(result, dict):
                    raise NimResearchOutputError("NIM returned an invalid data object.")
                return result, search_results_to_sources(search_results)
            except NimResearchAuthenticationError:
                raise
            except NimResearchRateLimitError:
                last_error = NimResearchRateLimitError(
                    "NIM Search quota or rate limit reached. Trying an available fallback."
                )
            except (
                NimResearchModelUnavailableError,
                NimResearchTimeoutError,
                NimResearchProviderError,
                NimResearchOutputError,
            ) as exc:
                last_error = exc

        if last_error is None:
            raise NimResearchProviderError("NIM Search could not complete the request.")
        raise last_error

    async def _nim_request(self, body: dict[str, Any]) -> dict[str, Any]:
        await self._request_limit.acquire()
        try:
            async with httpx.AsyncClient(timeout=90.0, transport=self.transport) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "authorization": f"Bearer {self.api_key}",
                        "content-type": "application/json",
                    },
                    json=body,
                )
        except httpx.TimeoutException as exc:
            raise NimResearchTimeoutError("NIM Search timed out.") from exc
        except httpx.RequestError as exc:
            raise NimResearchProviderError("NIM Search is temporarily unavailable.") from exc
        finally:
            self._request_limit.release()

        if response.status_code in (401, 403):
            raise NimResearchAuthenticationError(
                "NIM rejected the configured key or model access."
            )
        if response.status_code == 404:
            raise NimResearchModelUnavailableError("The configured NIM model is unavailable.")
        if response.status_code == 429:
            raise NimResearchRateLimitError(
                "NIM Search quota or rate limit reached. Try again shortly."
            )
        if response.status_code >= 500:
            raise NimResearchProviderError("NIM Search is temporarily unavailable.")
        if response.status_code >= 400:
            raise NimResearchProviderError(
                f"NIM rejected the grounded research request (status {response.status_code})."
            )

        try:
            "response_format": {"type": "json_object"},
"            temperature": 0.2,
        except ValueError as exc:
            raise NimResearchOutputError("NIM Search returned an invalid response.") from exc

    def _format_evidence(self, results: list[SearchResult]) -> str:
        if not results:
            return "No search results returned."
        lines: list[str] = []
        for i, result in enumerate(results, start=1):
            lines.append(
                f"[{i}] {result.title}\nURL: {result.url}\nContent: {result.content}\n"
            )
        return "\n".join(lines)

    @staticmethod
    def _catalog_prompt() -> str:
        categories = ", ".join(
            f'{item["id"]} ({item["name"]})' for item in get_categories()
        )
        return (
            f"{_SYSTEM_PROMPT}\n\n"
            "Find currently listed Dot & Key skincare products from the public web. "
            "Search official Dot & Key pages first, then reputable Indian retailers for "
            "current INR price, rating, review count, and ingredients. Return up to 25 "
            "distinct products across these exact category IDs: "
            f"{categories}. Each product must include source_urls copied exactly from "
            "the web search citations that support its fields. Use null for any "
            "unverified price, rating, review count, or tagline; use an empty ingredient "
            "list if ingredients are not shown. Do not invent products or fill gaps from memory."
        )

    @staticmethod
    def _detail_prompt(product: Product) -> str:
        return (
            f"{_SYSTEM_PROMPT}\n\n"
            f"Research the current Dot & Key product {product.name!r} in category "
            f"{product.category_id!r}. Search official product information and reputable "
            "Indian retail/review pages. Return the product's current verified facts, up to "
            "five clearly comparable products from other brands in the same category, and "
            "up to eight short publicly visible customer review excerpts specifically about "
            "this product. Competitors must have cited records; reviews must be direct excerpts "
            "and each must include the exact web search citation URL. Return null or empty "
            "values rather than guessing. The product name must match the requested product. "
            "Use source_urls for each product and competitor."
        )


def search_results_to_sources(results: list[SearchResult]) -> list[ResearchSource]:
    """Convert Tavily search results to ResearchSource citations."""
    sources: list[ResearchSource] = []
    for result in results:
        try:
            sources.append(ResearchSource(title=result.title or result.url, url=result.url))
        except ValidationError:
            continue
    return _unique_sources(sources)


def _extract_first_json_object(text: str) -> dict[str, Any]:
    """Attempt to extract the first balanced JSON object from garbled text."""
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found")
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if c == "\\" and in_string:
            escape = True
            continue
        if c == '"' and not escape:
            in_string = not in_string
            continue
        if not in_string:
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    snippet = text[start:i+1]
                    return json.loads(snippet)
    raise ValueError("Unterminated JSON object")


def _build_product(
    fact: _ProductFact,
    citations: list[ResearchSource],
    product_id: str | None = None,
) -> Product | None:
    sources = _match_sources(fact.source_urls, citations)
    if not sources:
        return None
    return Product(
        id=product_id or _product_id(fact.name),
        name=fact.name.strip(),
        category_id=fact.category_id,
        price_inr=fact.price_inr,
        rating=fact.rating,
        review_count=fact.review_count,
        source="api",
        sources=sources,
        tagline=fact.tagline,
        key_ingredients=fact.key_ingredients,
        is_dot_and_key=True,
    )


def _build_competitor(
    fact: _CompetitorFact,
    citations: list[ResearchSource],
) -> Competitor | None:
    sources = _match_sources(fact.source_urls, citations)
    if not sources:
        return None
    return Competitor(
        id=f"comp-{_slug(fact.brand)}-{_slug(fact.name)}",
        name=fact.name.strip(),
        brand=fact.brand.strip(),
        price_inr=fact.price_inr,
        rating=fact.rating,
        review_count=fact.review_count,
        source="api",
        sources=sources,
        key_ingredients=fact.key_ingredients,
        usp=fact.usp,
    )


def _build_review(
    fact: _ReviewFact,
    citations: list[ResearchSource],
) -> CustomerReview | None:
    sources = _match_sources([fact.source_url], citations)
    text = fact.text.strip()
    if not sources or not text:
        return None
    return CustomerReview(text=text[:600], source=sources[0], published_at=fact.published_at)


def _product_id(name: str) -> str:
    return f"dk-{_slug(name)}"[:64].rstrip("-")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "product"


def _normalize_url(value: str) -> str | None:
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"


def _match_sources(urls: list[str], citations: list[ResearchSource]) -> list[ResearchSource]:
    by_url = {_normalize_url(str(source.url)): source for source in citations}
    matched: list[ResearchSource] = []
    seen: set[str] = set()
    for url in urls:
        normalized = _normalize_url(url)
        if normalized and normalized in by_url and normalized not in seen:
            matched.append(by_url[normalized])
            seen.add(normalized)
    return matched


def _unique_sources(sources: Iterable[ResearchSource]) -> list[ResearchSource]:
    unique: dict[str, ResearchSource] = {}
    for source in sources:
        unique.setdefault(str(source.url), source)
    return list(unique.values())


def _validate_facts[FactModel: BaseModel](
    model: type[FactModel],
    payload: dict[str, Any],
) -> FactModel:
    try:
        return model.model_validate(payload)
    except (ValidationError, TypeError, ValueError) as exc:
        raise NimResearchOutputError(
            "Tavily/NIM Search returned records that did not match the research schema."
        ) from exc


def _schema_for(model: type[BaseModel]) -> dict[str, Any]:
    raw = model.model_json_schema()
    definitions = raw.get("$defs", {})

    def normalize(node: dict[str, Any]) -> dict[str, Any]:
        if "$ref" in node:
            key = node["$ref"].rsplit("/", 1)[-1]
            return normalize(definitions[key])
        if "anyOf" in node:
            options = [option for option in node["anyOf"] if option.get("type") != "null"]
            if not options:
                return {"type": "string", "nullable": True}
            result = normalize(options[0])
            if len(options) != len(node["anyOf"]):
                result["nullable"] = True
            return result

        result: dict[str, Any] = {}
        for key in ("type", "description", "enum", "minimum", "maximum", "minItems", "maxItems"):
            if key in node:
                result[key] = node[key]
        if "items" in node:
            result["items"] = normalize(node["items"])
        if "properties" in node:
            result["properties"] = {
                name: normalize(value) for name, value in node["properties"].items()
            }
        if "required" in node:
            result["required"] = node["required"]
        if "additionalProperties" in node:
            result["additionalProperties"] = node["additionalProperties"]
        return result

    return normalize(raw)


market_research = NimMarketResearch(
    cache_snapshot_path=Path(__file__).resolve().parents[2] / ".cache" / "market-research.json"
)

# Compatibility aliases for callers and tests from the former Gemini implementation.
GeminiResearchError = NimResearchError
GeminiResearchConfigurationError = NimResearchConfigurationError
GeminiResearchAuthenticationError = NimResearchAuthenticationError
GeminiResearchModelUnavailableError = NimResearchModelUnavailableError
GeminiResearchRateLimitError = NimResearchRateLimitError
GeminiResearchTimeoutError = NimResearchTimeoutError
GeminiResearchProviderError = NimResearchProviderError
GeminiResearchOutputError = NimResearchOutputError
GeminiMarketResearch = NimMarketResearch
