"""HTTP error mapping for live Gemini market research."""

from fastapi import HTTPException

from src.services.market_research import (
    GeminiResearchAuthenticationError,
    GeminiResearchConfigurationError,
    GeminiResearchError,
    GeminiResearchModelUnavailableError,
    GeminiResearchOutputError,
    GeminiResearchProviderError,
    GeminiResearchRateLimitError,
    GeminiResearchTimeoutError,
)


def research_http_exception(error: GeminiResearchError) -> HTTPException:
    """Translate explicit market-research failures to API status codes."""
    if isinstance(error, GeminiResearchRateLimitError):
        return HTTPException(status_code=429, detail=str(error))
    if isinstance(error, GeminiResearchTimeoutError):
        return HTTPException(status_code=504, detail=str(error))
    if isinstance(error, (GeminiResearchConfigurationError, GeminiResearchAuthenticationError)):
        return HTTPException(status_code=503, detail=str(error))
    if isinstance(error, GeminiResearchModelUnavailableError):
        return HTTPException(status_code=503, detail=str(error))
    if isinstance(error, (GeminiResearchOutputError, GeminiResearchProviderError)):
        return HTTPException(status_code=502, detail=str(error))
    return HTTPException(status_code=502, detail="Live market research failed.")
