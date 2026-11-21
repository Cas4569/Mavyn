"""Content generation route."""

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import APIRouter, HTTPException, Request

from src.routes.research_errors import research_http_exception
from src.schemas.content import ContentRequest, ContentResponse
from src.services.gemini_content_generator import (
    GeminiAuthenticationError,
    GeminiConfigurationError,
    GeminiContentGenerator,
    GeminiOutputError,
    GeminiProviderError,
    GeminiRateLimitError,
    GeminiTimeoutError,
)
from src.services.market_research import GeminiResearchError, market_research

router = APIRouter(prefix="/content", tags=["content"])

gemini_generator = GeminiContentGenerator()
_RATE_LIMIT_WINDOW_SECONDS = 60.0
_RATE_LIMIT_REQUESTS = 8
_request_timestamps: dict[str, deque[float]] = defaultdict(deque)
_rate_limit_lock = Lock()


def _check_generation_rate_limit(client_host: str) -> None:
    now = time.monotonic()
    with _rate_limit_lock:
        for host, timestamps in list(_request_timestamps.items()):
            while timestamps and now - timestamps[0] >= _RATE_LIMIT_WINDOW_SECONDS:
                timestamps.popleft()
            if not timestamps:
                del _request_timestamps[host]

        timestamps = _request_timestamps[client_host]
        if len(timestamps) >= _RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Generation limit reached. Wait a minute before trying again.",
            )
        timestamps.append(now)


@router.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest, http_request: Request):
    """
    Generate marketing content from product, competitor, review, and strategy evidence.

    Gemini generates content from the product's live, cited research records.
    """
    try:
        _check_generation_rate_limit(
            http_request.client.host if http_request.client else "unknown"
        )
        detail = await market_research.get_product_detail(request.product_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Product not found in the live catalog.")
        return await gemini_generator.generate(request, detail.model_dump(mode="json"))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GeminiResearchError as e:
        raise research_http_exception(e) from e
    except GeminiConfigurationError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except GeminiAuthenticationError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except GeminiRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except GeminiTimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e)) from e
    except (GeminiProviderError, GeminiOutputError) as e:
        raise HTTPException(status_code=502, detail=str(e)) from e