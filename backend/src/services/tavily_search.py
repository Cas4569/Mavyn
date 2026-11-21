"""Tavily web search adapter for grounded product research."""

from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import SecretStr

from src.config import settings


@dataclass
class SearchResult:
    """A single search result from Tavily."""

    title: str
    url: str
    content: str
    score: float


class TavilySearchError(Exception):
    """Base error for Tavily search."""


class TavilySearchAuthenticationError(TavilySearchError):
    """Tavily rejected the API key."""


class TavilySearchRateLimitError(TavilySearchError):
    """Tavily quota or rate limit exceeded."""


class TavilySearchProviderError(TavilySearchError):
    """Tavily search failed."""


class TavilySearchService:
    """Thin wrapper around Tavily's search API.

    Returns raw results (URL, title, content snippet) so callers can
    feed them into an LLM for grounded extraction without inventing citations.
    """

    def __init__(
        self,
        api_key: str | SecretStr | None = None,
        search_depth: str | None = None,
        max_results: int | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if api_key is None:
            api_key = settings.tavily_api_key
        if isinstance(api_key, SecretStr):
            api_key = api_key.get_secret_value()
        if isinstance(api_key, str):
            api_key = api_key.strip()
        self.api_key = api_key or None
        self.search_depth = search_depth or settings.tavily_search_depth
        self.max_results = max_results or settings.tavily_max_results
        self.transport = transport

    async def search(self, query: str) -> list[SearchResult]:
        """Run a Tavily search and return parsed results."""
        if not self.api_key:
            raise TavilySearchAuthenticationError(
                "Tavily is not configured. Add TAVILY_API_KEY to backend/.env."
            )

        body = {
            "query": query,
            "search_depth": self.search_depth,
            "max_results": self.max_results,
            "include_answer": False,
            "include_images": False,
            "include_raw_content": False,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0, transport=self.transport) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=body,
                )
        except httpx.TimeoutException as exc:
            raise TavilySearchProviderError("Tavily search timed out.") from exc
        except httpx.RequestError as exc:
            raise TavilySearchProviderError("Tavily search is temporarily unavailable.") from exc

        if response.status_code in (401, 403):
            raise TavilySearchAuthenticationError(
                "Tavily rejected the configured API key."
            )
        if response.status_code == 429:
            raise TavilySearchRateLimitError(
                "Tavily Search quota or rate limit reached."
            )
        if response.status_code >= 500:
            raise TavilySearchProviderError("Tavily Search is temporarily unavailable.")
        if response.status_code >= 400:
            raise TavilySearchProviderError(
                f"Tavily Search request failed (status {response.status_code})."
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise TavilySearchProviderError("Tavily Search returned invalid JSON.") from exc

        if not isinstance(data, dict):
            raise TavilySearchProviderError("Tavily Search returned an unexpected payload.")

        results: list[SearchResult] = []
        for item in data.get("results", []) or []:
            url = item.get("url")
            if not url:
                continue
            results.append(
                SearchResult(
                    title=str(item.get("title", "")),
                    url=str(url),
                    content=str(item.get("content", "")),
                    score=float(item.get("score", 0.0)),
                )
            )
        return results


tavily_search = TavilySearchService()
