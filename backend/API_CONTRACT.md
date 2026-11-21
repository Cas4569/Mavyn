# MAVYN API Contract

**Version:** 0.1.0  
**Base URL:** `http://localhost:8000`  
**CORS:** Enabled for `http://localhost:5173`  
**Content-Type:** `application/json`

---

## Overview

This contract defines the exact HTTP interfaces between the React frontend (Vite, TypeScript, Tailwind) and the FastAPI backend. All requests/responses use JSON. Field names use `snake_case`.

> **Frontend Team:** Build against these schemas. The backend returns `source: "sample"` on all responses — replace with real data later without changing the contract.

---

## 1. Health Check

### `GET /health`

**Response (200):**
```json
{
  "status": "healthy",
  "app": "MAVYN Backend",
  "version": "0.1.0"
}
```

---

## 2. Categories

### `GET /categories`

**Response (200):**
```json
{
  "categories": [
    {
      "id": "sunscreens",
      "name": "Sunscreens",
      "product_count": 5,
      "description": "Broad-spectrum UV protection for Indian climate"
    },
    {
      "id": "serums",
      "name": "Serums",
      "product_count": 4,
      "description": "Targeted active ingredient treatments"
    },
    {
      "id": "moisturizers",
      "name": "Moisturizers",
      "product_count": 4,
      "description": "Hydration and barrier support"
    },
    {
      "id": "cleansers",
      "name": "Cleansers",
      "product_count": 4,
      "description": "Gentle cleansing for all skin types"
    },
    {
      "id": "toners",
      "name": "Toners & Essences",
      "product_count": 3,
      "description": "Prep and hydration boosters"
    }
  ],
  "total": 5
}
```

### `GET /categories/{category_id}`

**Response (200):** Single category object (same shape as array item above)  
**Response (404):** `{"detail": "Category not found"}`

---

## 3. Products

### `GET /products?category={category_id}`

**Query Params:**
- `category` (required): Category ID from `/categories`

**Response (200):**
```json
{
  "category_id": "sunscreens",
  "category_name": "Sunscreens",
  "products": [
    {
      "id": "dk-sun-001",
      "name": "Watermelon Cooling Sunscreen SPF 50 PA++++",
      "category_id": "sunscreens",
      "price_inr": 595,
      "rating": 4.4,
      "review_count": 1247,
      "hero_image": "https://images.unsplash.com/...",
      "tagline": "Lightweight cooling protection with watermelon extract",
      "is_dot_and_key": true,
      "source": "sample"
    },
    {
      "id": "comp-minimalist-sun",
      "name": "Minimalist SPF 50 PA++++ Sunscreen",
      "brand": "Minimalist",
      "price_inr": 399,
      "rating": 4.3,
      "review_count": 3421,
      "key_ingredients": ["Ethylhexyl Methoxycinnamate", "Bemotrizinol", "Vitamin E"],
      "usp": "No white cast, photostable filters",
      "image_url": "https://images.unsplash.com/...",
      "source": "sample"
    }
    // ... up to 5 products per category (1-2 Dot & Key + competitors)
  ],
  "total": 5
}
```

**Response (404):** `{"detail": "Category not found or no products"}`

---

### `GET /products/dot-and-key`

**Response (200):**
```json
{
  "products": [
    {
      "id": "dk-sun-001",
      "name": "Watermelon Cooling Sunscreen SPF 50 PA++++",
      "category_id": "sunscreens",
      "price_inr": 595,
      "rating": 4.4,
      "review_count": 1247,
      "hero_image": "https://...",
      "tagline": "Lightweight cooling protection...",
      "is_dot_and_key": true,
      "source": "sample"
    }
    // ... all Dot & Key products across categories
  ],
  "total": 7
}
```

---

### `GET /products/{product_id}`

**Response (200):**
```json
{
  "product": {
    "id": "dk-sun-001",
    "name": "Watermelon Cooling Sunscreen SPF 50 PA++++",
    "category_id": "sunscreens",
    "price_inr": 595,
    "rating": 4.4,
    "review_count": 1247,
    "hero_image": "https://...",
    "tagline": "Lightweight cooling protection...",
    "is_dot_and_key": true,
    "source": "sample"
  },
  "competitors": [
    {
      "id": "comp-minimalist-sun",
      "name": "Minimalist SPF 50 PA++++ Sunscreen",
      "brand": "Minimalist",
      "price_inr": 399,
      "rating": 4.3,
      "review_count": 3421,
      "key_ingredients": ["Ethylhexyl Methoxycinnamate", "Bemotrizinol", "Vitamin E"],
      "usp": "No white cast, photostable filters",
      "image_url": "https://...",
      "source": "sample"
    }
    // ... 3-5 competitors
  ],
  "sample_reviews": [
    "Love the lightweight feel! No white cast at all and my oily skin doesn't feel greasy...",
    "Great sunscreen for daily use. Sits well under makeup, doesn't pill...",
    // ... 6-8 sample review strings
  ]
}
```

**Response (404):** `{"detail": "Product not found"}`

---

## 4. Review Analysis

### `POST /reviews/analyze`

**Request:**
```json
{
  "product_id": "dk-sun-001",
  "reviews": [
    "Love the lightweight feel! No white cast at all...",
    "Great sunscreen for daily use. Sits well under makeup...",
    // ... OR omit to use backend sample reviews
  ],
  "competitor_ids": null
}
```

**Notes:**
- `reviews` array optional — if omitted/empty, backend uses built-in sample reviews for that `product_id`
- `competitor_ids` reserved for future comparison feature

**Response (200):**
```json
{
  "product_id": "dk-sun-001",
  "sentiment": {
    "positive": 5,
    "neutral": 1,
    "negative": 2,
    "total": 8,
    "positive_pct": 62.5,
    "negative_pct": 25.0
  },
  "top_praise_themes": [
    {
      "name": "Texture",
      "sentiment": "positive",
      "mention_count": 4,
      "evidence": [
        "Love the lightweight feel! No white cast at all and my oily skin doesn't feel greasy.",
        "Texture is amazing - absorbs in seconds."
      ],
      "source": "sample"
    },
    {
      "name": "Value",
      "sentiment": "positive",
      "mention_count": 2,
      "evidence": ["Good value for money at ₹595..."],
      "source": "sample"
    }
  ],
  "top_complaint_themes": [
    {
      "name": "White Cast",
      "sentiment": "negative",
      "mention_count": 2,
      "evidence": [
        "White cast is minimal but visible on deeper skin tones (I'm NC42)..."
      ],
      "source": "sample"
    },
    {
      "name": "Breakouts",
      "sentiment": "negative",
      "mention_count": 1,
      "evidence": ["Broke me out around the jawline after a week..."],
      "source": "sample"
    }
  ],
  "key_insights": [
    "Strong positive reception (62.5% positive)",
    "Top praise: Texture (4 mentions)",
    "Top complaint: White Cast (2 mentions)",
    "White cast reported — consider reformulation or shade-inclusive marketing"
  ],
  "analyzed_at": "2026-11-21T10:30:00.000000+00:00",
  "source": "sample"
}
```

**Response (404):** `{"detail": "No sample reviews found for product X. Provide reviews in request."}`

---

## 5. Content Generation

### `POST /content/generate`

**Request:**
```json
{
  "product_id": "dk-sun-001",
  "strategy_id": null,
  "platforms": ["instagram", "facebook", "google", "youtube", "linkedin"],
  "content_types": [
    "ad_copy",
    "product_description",
    "listing",
    "ad_script",
    "storyboard",
    "video_concept"
  ]
}
```

**Notes:**
- All fields optional except `product_id`
- Omit `platforms`/`content_types` to generate all

**Response (200):**
```json
{
  "product_id": "dk-sun-001",
  "ad_copy": [
    {
      "platform": "instagram",
      "headline": "✨ Lightweight cooling protection with watermelon extract",
      "primary_text": "Meet Watermelon Cooling Sunscreen SPF 50 PA++++ — Lightweight cooling protection with watermelon extract.\n\n💧 Lightweight, non-greasy formula\n🌿 Dermatologist-tested ingredients\n🇮🇳 Made for Indian skin, Indian climate\n\nJoin 1000+ customers who've made the switch. Tap 'Shop Now' to glow up your routine! ✨",
      "cta": "Shop Now",
      "hashtags": ["DotAndKey", "SkincareRoutine", "IndianSkincare", "GlowingSkin", "SkincareIndia"],
      "character_count": 0,
      "source": "sample"
    }
    // ... one per requested platform
  ],
  "product_description": {
    "short_description": "Lightweight cooling protection with watermelon extract. ₹595. 4.4★ from 1000+ reviews.",
    "long_description": "Watermelon Cooling Sunscreen SPF 50 PA++++ — Lightweight cooling protection with watermelon extract\n\nDesigned for Indian skin and climate...",
    "key_benefits": [
      "Visible brightening in 2-4 weeks",
      "Lightweight, fast-absorbing texture",
      "No white cast on deeper skin tones",
      "Non-comedogenic — won't clog pores",
      "Fragrance-free, suitable for sensitive skin",
      "Stable formula — no oxidation worries"
    ],
    "ingredients_highlight": [
      "Watermelon Extract",
      "Vitamin E",
      "Niacinamide",
      "Hyaluronic Acid"
    ],
    "usage_instructions": "Apply generously 15 minutes before sun exposure. Reapply every 2 hours. Use daily as last step in AM routine.",
    "source": "sample"
  },
  "listing_content": {
    "title": "Watermelon Cooling Sunscreen SPF 50 PA++++ - Lightweight cooling protection with watermelon extract | 50g | Official Dot & Key",
    "bullet_points": [
      "Lightweight cooling protection with watermelon extract — clinically proven actives at effective %",
      "Zero white cast on Indian skin tones (Fitzpatrick III-VI)",
      "Non-comedogenic, fragrance-free, dermatologist-tested",
      "Stable formula — no oxidation, full potency to last drop",
      "Lightweight, fast-absorbing, layers under makeup/SPF",
      "1000+ verified 5-star reviews on Nykaa & Amazon",
      "Made in India 🇮🇳 | Cruelty-free | Vegan"
    ],
    "search_terms": [
      "sunscreen spf 50",
      "watermelon sunscreen",
      "no white cast sunscreen",
      "indian skin sunscreen",
      "dot and key sunscreen",
      "non comedogenic sunscreen",
      "fragrance free sunscreen",
      "lightweight sunscreen"
    ],
    "enhanced_content": "<h2>Why Watermelon Cooling Sunscreen?</h2><p>Most sunscreens leave a white cast...</p>",
    "source": "sample"
  },
  "ad_scripts": [
    {
      "format": "reel",
      "duration_seconds": 25,
      "hook": "POV: You finally found a sunscreen with ZERO white cast 🤯",
      "script": "[0-3s] Close-up: Sunscreen dispensing, no white residue visible\n[3-8s] Text overlay: 'SPF 50 • Zero White Cast • Watermelon Cooling'\n[8-15s] Split screen: Before (white cast) → After (invisible) on NC42 skin\n[15-20s] User applying under makeup, no pilling\n[20-25s] Product shot + 'Shop Link in Bio' + Dot & Key logo",
      "cta": "Tap the link in bio to shop!",
      "source": "sample"
    }
    // ... instream (60s), bumper (6s)
  ],
  "storyboard": {
    "frames": [
      {
        "frame_number": 1,
        "visual_description": "Close-up macro shot: Sunscreen dispensing, zero white residue, catching light",
        "audio_cue": "Soft *plink* sound, ambient fresh breeze",
        "duration_seconds": 2.0
      }
      // ... 7 frames total
    ],
    "total_duration_seconds": 23.0,
    "source": "sample"
  },
  "video_concepts": [
    {
      "concept_name": "The Invisible Sunscreen Science",
      "logline": "Why your sunscreen leaves a white cast — and the one that doesn't.",
      "target_audience": "Skincare enthusiasts 22-35, deeper skin tones (Fitzpatrick IV-VI), ingredient-conscious",
      "key_message": "New-gen filters = zero cast. Dot & Key uses Bemotrizinol + DHHB for true invisibility.",
      "scripts": [
        {
          "format": "instream",
          "duration_seconds": 90,
          "hook": "You're wearing a white cast right now. Here's the filter that fixes it.",
          "script": "...",
          "cta": "Try the invisible SPF. 15% off + free shipping.",
          "source": "sample"
        }
      ],
      "storyboard": { "frames": [...], "total_duration_seconds": 19, "source": "sample" },
      "production_notes": [
        "Film in clean lab/studio aesthetic — white, glass, stainless steel",
        "Cast 4 models representing Fitzpatrick III-VI",
        "Need cosmetic chemist for authority figure",
        "Filter comparison graphics: motion design team"
      ],
      "source": "sample"
    }
    // ... 2 concepts
  ],
  "generated_at": "2026-11-21T10:30:00.000000+00:00",
  "source": "sample"
}
```

**Response (404):** `{"detail": "Product not found: X"}`  
**Response (500):** `{"detail": "Content generation failed: ..."}`

---

## TypeScript Types (for Frontend)

```typescript
// Shared types — copy to frontend/src/types/api.ts

interface Category {
  id: string;
  name: string;
  product_count: number;
  description: string | null;
}

interface CategoryList {
  categories: Category[];
  total: number;
}

interface Product {
  id: string;
  name: string;
  category_id: string;
  price_inr: number;
  rating: number;
  review_count: number;
  hero_image: string | null;
  tagline: string | null;
  is_dot_and_key: boolean;
  source: "sample" | "scraped" | "api";
}

interface Competitor {
  id: string;
  name: string;
  brand: string;
  price_inr: number;
  rating: number;
  review_count: number;
  key_ingredients: string[];
  usp: string;
  image_url: string | null;
  source: "sample" | "scraped" | "api";
}

interface ProductDetail {
  product: Product;
  competitors: Competitor[];
  sample_reviews: string[];
}

interface ProductList {
  category_id: string;
  category_name: string;
  products: Product[];
  total: number;
}

interface SentimentBreakdown {
  positive: number;
  neutral: number;
  negative: number;
  total: number;
  positive_pct: number;
  negative_pct: number;
}

interface Theme {
  name: string;
  sentiment: "positive" | "negative" | "mixed";
  mention_count: number;
  evidence: string[];
  source: "sample" | "llm";
}

interface ReviewAnalysis {
  product_id: string;
  sentiment: SentimentBreakdown;
  top_praise_themes: Theme[];
  top_complaint_themes: Theme[];
  key_insights: string[];
  analyzed_at: string; // ISO timestamp
  source: "sample" | "llm";
}

interface ReviewInput {
  product_id: string;
  reviews?: string[];
  competitor_ids?: string[] | null;
}

// Content types
interface AdCopy {
  platform: "instagram" | "facebook" | "google" | "youtube" | "linkedin";
  headline: string;
  primary_text: string;
  cta: string;
  hashtags: string[];
  character_count: number;
  source: "sample" | "llm";
}

interface ProductDescription {
  short_description: string;
  long_description: string;
  key_benefits: string[];
  ingredients_highlight: string[];
  usage_instructions: string | null;
  source: "sample" | "llm";
}

interface ListingContent {
  title: string;
  bullet_points: string[];
  search_terms: string[];
  enhanced_content: string | null;
  source: "sample" | "llm";
}

interface AdScript {
  format: "reel" | "shorts" | "instream" | "bumper";
  duration_seconds: number;
  hook: string;
  script: string;
  cta: string;
  source: "sample" | "llm";
}

interface StoryboardFrame {
  frame_number: number;
  visual_description: string;
  audio_cue: string | null;
  duration_seconds: number;
}

interface Storyboard {
  frames: StoryboardFrame[];
  total_duration_seconds: number;
  source: "sample" | "llm";
}

interface VideoConcept {
  concept_name: string;
  logline: string;
  target_audience: string;
  key_message: string;
  scripts: AdScript[];
  storyboard: Storyboard;
  production_notes: string[];
  source: "sample" | "llm";
}

interface ContentResponse {
  product_id: string;
  ad_copy: AdCopy[];
  product_description: ProductDescription | null;
  listing_content: ListingContent | null;
  ad_scripts: AdScript[];
  storyboard: Storyboard | null;
  video_concepts: VideoConcept[];
  generated_at: string;
  source: "sample" | "llm";
}

interface ContentRequest {
  product_id: string;
  strategy_id?: string | null;
  platforms?: ("instagram" | "facebook" | "google" | "youtube" | "linkedin")[];
  content_types?: ("ad_copy" | "product_description" | "listing" | "ad_script" | "storyboard" | "video_concept")[];
}
```

---

## Error Format

All errors follow FastAPI standard:
```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:
- `200` — Success
- `400` — Bad request (validation error)
- `404` — Not found
- `422` — Validation error (request body invalid)
- `500` — Server error

---

## Frontend Integration Notes

1. **Base URL:** The Vite app defaults to `/api` and proxies it to `http://127.0.0.1:8000` during development. Set `VITE_API_URL` when connecting to a deployed backend.
2. **CORS:** The local Vite proxy avoids browser CORS restrictions. Direct browser requests to the backend are allowed from `http://localhost:5173`.
3. **Source field:** Every response includes `source: "sample"` — frontend can badge "AI-generated (demo)" or similar
4. **Empty states:** Handle empty arrays (e.g., no competitors, no reviews)
5. **Images:** All `hero_image`/`image_url` are Unsplash placeholders — replace with real assets later
6. **Timestamps:** ISO 8601 strings (`analyzed_at`, `generated_at`) — parse with `new Date()`

---

## Future Extensions (Not Implemented)

| Endpoint | Purpose |
|----------|---------|
| `POST /strategy/generate` | Full SWOT, gaps, trends, opportunities, forecast |
| `GET /products/{id}/strategy` | Cached strategy panel |
| `POST /reviews/analyze` with `competitor_ids` | Comparative sentiment |
| `GET /analytics/dashboard` | Aggregated metrics for admin |

These will follow the same contract pattern when built.