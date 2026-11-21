# MAVYN API Contract

**Base URL:** `http://localhost:8000`  
**Content-Type:** `application/json`

## Live research behavior

Product, competitor, and public review records are retrieved by Gemini using Google Search
grounding. The backend does not serve a bundled product/review dataset or silently fall back to
one when Gemini is unavailable. Returned records include clickable citations from Gemini's
grounding annotations. Unverified prices, ratings, counts, ingredients, or claims remain `null`
or empty.

Set `GEMINI_API_KEY` in `backend/.env`. `GEMINI_MODEL` selects the primary model and
`GEMINI_FALLBACK_MODELS` is a comma-separated fallback list. Search results are cached on disk and in memory for
`MARKET_DATA_CACHE_TTL_SECONDS` (default: 21,600 seconds / six hours) to reduce repeated
grounded searches. Catalog and detail responses include `cached: true` when a snapshot is served
from cache, including the snapshot fallback during Gemini rate limits. The category taxonomy is static organization metadata; product counts are
not fabricated.

## Health and categories

### `GET /health`

Returns application health and version.

### `GET /categories`

Returns the supported category taxonomy (`sunscreens`, `serums`, `moisturizers`, `cleansers`,
and `toners`). `product_count` is `null`; current catalog counts come from live research.

### `GET /categories/{category_id}`

Returns one category or `404` when the ID is unknown.

## Products and market intelligence

### `GET /products/dot-and-key`

Returns a live catalog:

```json
{
  "products": [
    {
      "id": "dk-vitamin-c-brightening-serum",
      "name": "Vitamin C Brightening Serum",
      "category_id": "serums",
      "price_inr": 599,
      "rating": 4.4,
      "review_count": 420,
      "source": "api",
      "sources": [
        { "title": "Product page", "url": "https://example.com/product" }
      ],
      "tagline": null,
      "key_ingredients": ["Vitamin C"],
      "is_dot_and_key": true,
      "hero_image": null
    }
  ],
  "total": 1,
  "sources": [
    { "title": "Product page", "url": "https://example.com/product" }
  ],
  "fetched_at": "2026-03-05T12:00:00+00:00",
  "source": "api"
}
```

Product IDs are generated from product names and remain stable across refreshes.

### `GET /products?category={category_id}`

Returns live products in a category, plus citations and `fetched_at`. Returns `404` when no
current records are found for that category.

### `GET /products/{product_id}`

Returns:

- `product`: current product fields and source citations.
- `competitors`: sourced records for comparable products in the same category.
- `reviews`: short public review excerpts, each with its citation and optional publication date.
- `sources`: the citations used for the detail, competitor, and review research.
- `fetched_at` and `source: "api"`.

Only records tied to Google Search grounding citations are returned. The review excerpts are
limited public snippets, not a representative sample of all customers.

### `GET /products/{product_id}/comparison`

Returns comparison rows, price/rating positioning, ingredient overlap, review analysis, source
citations, freshness, and `source: "api"`. A metric without verified values is reported as
unknown instead of being estimated.

### `GET /products/{product_id}/strategy`

Returns a SWOT, review signals, evidence-linked market gaps, and testable opportunities from the
live records. `sales_forecast` remains empty because public search results do not provide dated
sales history.

## Review analysis

### `POST /reviews/analyze`

Request:

```json
{ "product_id": "dk-vitamin-c-brightening-serum" }
```

When `reviews` is omitted or empty, MAVYN researches the product and analyzes its retrieved
public review excerpts. Callers may instead provide their own `reviews: string[]`; these are
labeled with `source: "user"` and are not represented as Google Search research. The response
includes sentiment totals, themes, insights, source citations when available, and `analyzed_at`.
Theme extraction uses a lightweight keyword heuristic; it is not a representative customer
survey.

## Gemini content generation

### `POST /content/generate`

Request:

```json
{
  "product_id": "dk-vitamin-c-brightening-serum",
  "provider": "gemini",
  "platforms": ["instagram", "youtube"],
  "content_types": ["ad_copy", "video_concept", "product_description"]
}
```

`platforms` and `content_types` are optional; when omitted, the full content pack is requested.
Supported content types are `ad_copy`, `product_description`, `listing`, `ad_script`,
`storyboard`, and `video_concept`. Gemini uses the product's live citations, competitor records,
review excerpts, and derived strategy as evidence. Verify all draft claims before publication.
The response includes the `research_sources` and `research_fetched_at` used for the draft.

## Errors

Errors use FastAPI's standard JSON shape: `{"detail": "..."}`.

| Status | Meaning |
| --- | --- |
| `404` | Unknown category or product ID |
| `429` | Gemini Search quota/rate limit or content-generation limit |
| `502` | Gemini provider error, invalid structured result, or missing grounding citations |
| `503` | Missing/invalid Gemini configuration or unavailable model |
| `504` | Gemini request timeout |

When live research fails, the backend returns an explicit error and does not substitute static
records.
