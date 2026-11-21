"""HTTP error mapping for live Tavily/NVIDIA NIM market research."""

from fastapi import HTTPException

from src.services.market_research import (
    NimResearchAuthenticationError,
    NimResearchConfigurationError,
    NimResearchError,
    NimResearchModelUnavailableError,
    NimResearchOutputError,
    NimResearchProviderError,
    NimResearchRateLimitError,
    NimResearchTimeoutError,
)


def research_http_exception(error: NimResearchError) -> HTTPException:
    """Translate explicit market-research failures to API status codes."""
    if isinstance(error, NimResearchRateLimitError):
        return HTTPException(status_code=429, detail=str(error))
    if isinstance(error, NimResearchTimeoutError):
        return HTTPException(status_code=504, detail=str(error))
    if isinstance(error, (NimResearchConfigurationError, NimResearchAuthenticationError)):
        return HTTPException(status_code=503, detail=str(error))
    if isinstance(error, NimResearchModelUnavailableError):
        return HTTPException(status_code=503, detail=str(error))
    if isinstance(error, (NimResearchOutputError, NimResearchProviderError)):
        return HTTPException(status_code=502, detail=str(error))
    return HTTPException(status_code=502, detail="Live market research failed.")
