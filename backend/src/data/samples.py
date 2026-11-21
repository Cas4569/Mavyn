"""
Sample data for MAVYN backend — CLEARLY LABELED AS SAMPLE.

All data here is hardcoded sample data for hackathon demo purposes.
No live scraping, no fabricated reviews presented as real.
Every object has `source: "sample"` for traceability.

Structure:
- 5 categories
- 2 Dot & Key products per category + 3-5 competitors each
- Sample reviews for each Dot & Key product
"""

from datetime import datetime, timezone

# ============================================================
# CATEGORIES (5)
# ============================================================
SAMPLE_CATEGORIES = [
    {
        "id": "sunscreens",
        "name": "Sunscreens",
        "product_count": 5,
        "description": "Broad-spectrum UV protection for Indian climate",
    },
    {
        "id": "serums",
        "name": "Serums",
        "product_count": 4,
        "description": "Targeted active ingredient treatments",
    },
    {
        "id": "moisturizers",
        "name": "Moisturizers",
        "product_count": 4,
        "description": "Hydration and barrier support",
    },
    {
        "id": "cleansers",
        "name": "Cleansers",
        "product_count": 4,
        "description": "Gentle cleansing for all skin types",
    },
    {
        "id": "toners",
        "name": "Toners & Essences",
        "product_count": 3,
        "description": "Prep and hydration boosters",
    },
]

# ============================================================
# PRODUCTS BY CATEGORY
# Each category has 1-2 Dot & Key products + competitors
# ============================================================
SAMPLE_PRODUCTS = {
    "sunscreens": [
        # Dot & Key product
        {
            "id": "dk-sun-001",
            "name": "Watermelon Cooling Sunscreen SPF 50 PA++++",
            "category_id": "sunscreens",
            "price_inr": 595,
            "rating": 4.4,
            "review_count": 1247,
            "hero_image": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop",
            "tagline": "Lightweight cooling protection with watermelon extract",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Competitors
        {
            "id": "comp-minimalist-sun",
            "name": "Minimalist SPF 50 PA++++ Sunscreen",
            "brand": "Minimalist",
            "price_inr": 399,
            "rating": 4.3,
            "review_count": 3421,
            "key_ingredients": ["Ethylhexyl Methoxycinnamate", "Bemotrizinol", "Vitamin E"],
            "usp": "No white cast, photostable filters",
            "image_url": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
        {
            "id": "comp-plum-sun",
            "name": "Plum Green Tea Day-Light Sunscreen SPF 35",
            "brand": "Plum",
            "price_inr": 475,
            "rating": 4.2,
            "review_count": 2156,
            "key_ingredients": ["Green Tea", "Calendula", "Niacinamide"],
            "usp": "Antioxidant-rich, matte finish",
            "image_url": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
        {
            "id": "comp-dermaco-sun",
            "name": "Derma Co 1% Hyaluronic Sunscreen SPF 50",
            "brand": "Derma Co",
            "price_inr": 499,
            "rating": 4.1,
            "review_count": 1873,
            "key_ingredients": ["Hyaluronic Acid", "Ceramides", "Vitamin E"],
            "usp": "Hydrating + sun protection in one",
            "image_url": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
        {
            "id": "comp-mcaffeine-sun",
            "name": "mCaffeine Coffee Sunscreen SPF 50 PA++++",
            "brand": "mCaffeine",
            "price_inr": 449,
            "rating": 4.0,
            "review_count": 987,
            "key_ingredients": ["Caffeine", "Vitamin E", "Pro-Vitamin B5"],
            "usp": "Caffeine-powered UV defense",
            "image_url": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
    ],
    "serums": [
        # Dot & Key product
        {
            "id": "dk-ser-001",
            "name": "Vitamin C + E Super Bright Serum",
            "category_id": "serums",
            "price_inr": 695,
            "rating": 4.5,
            "review_count": 892,
            "hero_image": "https://images.unsplash.com/photo-1620916566398-79f665a0e665?w=400&h=400&fit=crop",
            "tagline": "15% Vitamin C for radiant, even-toned skin",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Dot & Key product 2
        {
            "id": "dk-ser-002",
            "name": "10% Niacinamide + Zinc Pore Control Serum",
            "category_id": "serums",
            "price_inr": 595,
            "rating": 4.3,
            "review_count": 654,
            "hero_image": "https://images.unsplash.com/photo-1620916566398-79f665a0e665?w=400&h=400&fit=crop",
            "tagline": "Minimizes pores, controls oil, reduces marks",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Competitors
        {
            "id": "comp-minimalist-vitc",
            "name": "Minimalist 10% Vitamin C + 1% Ferulic Acid",
            "brand": "Minimalist",
            "price_inr": 599,
            "rating": 4.4,
            "review_count": 4123,
            "key_ingredients": ["L-Ascorbic Acid", "Ferulic Acid", "Vitamin E"],
            "usp": "Stable Vitamin C at effective pH",
            "image_url": "https://images.unsplash.com/photo-1620916566398-79f665a0e665?w=400&h=400&fit=crop",
            "source": "sample",
        },
        {
            "id": "comp-plum-vitc",
            "name": "Plum 15% Vitamin C Face Serum",
            "brand": "Plum",
            "price_inr": 675,
            "rating": 4.2,
            "review_count": 2876,
            "key_ingredients": ["Ethyl Ascorbic Acid", "Kakadu Plum", "Hyaluronic Acid"],
            "usp": "Gentle stable derivative, beginner-friendly",
            "image_url": "https://images.unsplash.com/photo-1620916566398-79f665a0e665?w=400&h=400&fit=crop",
            "source": "sample",
        },
    ],
    "moisturizers": [
        # Dot & Key product
        {
            "id": "dk-moist-001",
            "name": "Ceramide + Hyaluronic Acid Barrier Repair Moisturizer",
            "category_id": "moisturizers",
            "price_inr": 495,
            "rating": 4.4,
            "review_count": 723,
            "hero_image": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "tagline": "24hr hydration, strengthens skin barrier",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Dot & Key product 2
        {
            "id": "dk-moist-002",
            "name": "Vitamin C + E Brightening Day Cream SPF 20",
            "category_id": "moisturizers",
            "price_inr": 545,
            "rating": 4.2,
            "review_count": 412,
            "hero_image": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "tagline": "Brighten + protect + hydrate in one step",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Competitors
        {
            "id": "comp-minimalist-moist",
            "name": "Minimalist 3% Sepicalm + 5% Ceramide Moisturizer",
            "brand": "Minimalist",
            "price_inr": 399,
            "rating": 4.3,
            "review_count": 2654,
            "key_ingredients": ["Ceramides", "Sepicalm", "Hyaluronic Acid"],
            "usp": "Soothes irritation, repairs barrier",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
        {
            "id": "comp-plum-moist",
            "name": "Plum Green Tea Oil-Free Moisturizer",
            "brand": "Plum",
            "price_inr": 425,
            "rating": 4.1,
            "review_count": 1987,
            "key_ingredients": ["Green Tea", "Glycolic Acid", "Niacinamide"],
            "usp": "Lightweight gel-cream for oily skin",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
    ],
    "cleansers": [
        # Dot & Key product
        {
            "id": "dk-clean-001",
            "name": "Cica + Green Tea Gentle Cleanser",
            "category_id": "cleansers",
            "price_inr": 345,
            "rating": 4.3,
            "review_count": 567,
            "hero_image": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "tagline": "Soothes while it cleans, no tightness",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Dot & Key product 2
        {
            "id": "dk-clean-002",
            "name": "Vitamin C Brightening Face Wash",
            "category_id": "cleansers",
            "price_inr": 295,
            "rating": 4.1,
            "review_count": 423,
            "hero_image": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "tagline": "Glow-boosting cleanse with stable Vitamin C",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Competitors
        {
            "id": "comp-minimalist-clean",
            "name": "Minimalist 2% Salicylic Acid Face Wash",
            "brand": "Minimalist",
            "price_inr": 299,
            "rating": 4.2,
            "review_count": 3156,
            "key_ingredients": ["Salicylic Acid", "Zinc PCA", "Allantoin"],
            "usp": "Unclogs pores, prevents breakouts",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
        {
            "id": "comp-plum-clean",
            "name": "Plum Green Tea Pore Cleansing Face Wash",
            "brand": "Plum",
            "price_inr": 325,
            "rating": 4.1,
            "review_count": 2234,
            "key_ingredients": ["Green Tea", "Glycolic Acid", "Cellulose Beads"],
            "usp": "Gentle exfoliation + deep cleanse",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
    ],
    "toners": [
        # Dot & Key product
        {
            "id": "dk-toner-001",
            "name": "Rice Water + Niacinamide Brightening Toner",
            "category_id": "toners",
            "price_inr": 395,
            "rating": 4.4,
            "review_count": 389,
            "hero_image": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "tagline": "K-beauty inspired glow in a bottle",
            "is_dot_and_key": True,
            "source": "sample",
        },
        # Competitors
        {
            "id": "comp-minimalist-toner",
            "name": "Minimalist 3% PHA Toner",
            "brand": "Minimalist",
            "price_inr": 349,
            "rating": 4.2,
            "review_count": 1876,
            "key_ingredients": ["Gluconolactone", "Lactobionic Acid", "Hyaluronic Acid"],
            "usp": "Gentle daily exfoliation, barrier-safe",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
        {
            "id": "comp-plum-toner",
            "name": "Plum Green Tea Alcohol-Free Toner",
            "brand": "Plum",
            "price_inr": 375,
            "rating": 4.1,
            "review_count": 1432,
            "key_ingredients": ["Green Tea", "Glycolic Acid", "Witch Hazel"],
            "usp": "Balances pH, minimizes pores",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b9a0d0f6?w=400&h=400&fit=crop",
            "source": "sample",
        },
    ],
}

# ============================================================
# SAMPLE REVIEWS (for Dot & Key products only)
# Each review is labeled with source="sample"
# ============================================================
SAMPLE_REVIEWS = {
    "dk-sun-001": [
        "Love the lightweight feel! No white cast at all and my oily skin doesn't feel greasy. The watermelon scent is subtle and refreshing. Been using for 3 weeks and no breakouts.",
        "Great sunscreen for daily use. Sits well under makeup, doesn't pill. The cooling sensation is real - perfect for Mumbai summers. Only wish the bottle was larger.",
        "Finally a sunscreen that doesn't sting my sensitive eyes! I have rosacea and this is one of the few I can use daily. The PA++++ rating gives me confidence.",
        "Texture is amazing - absorbs in seconds. But I do find it slightly drying around my nose area by evening. Need to layer a moisturizer underneath.",
        "Good value for money at ₹595. Lasts me about 2 months with daily use. The pump dispenser is hygienic and convenient.",
        "Broke me out around the jawline after a week. My skin is acne-prone and this clogged my pores. Returning it.",
        "The cooling effect is nice but wears off quickly. Protection seems decent - no tan lines after outdoor events. Would repurchase.",
        "White cast is minimal but visible on deeper skin tones (I'm NC42). Blends out after a few minutes but still noticeable in flash photography.",
    ],
    "dk-ser-001": [
        "Visible brightening in 2 weeks! My post-acne marks have faded significantly. The dropper packaging is hygienic and dispenses the right amount.",
        "Tingles slightly on application but goes away fast. Skin feels smoother and more radiant. Using it every morning under sunscreen.",
        "Expensive at ₹695 but a little goes a long way. Bottle lasted me 3 months. The Vitamin C hasn't oxidized - still clear after 2 months.",
        "Caused redness and irritation on my sensitive skin. Had to stop using after 3 days. Patch test first if you have reactive skin!",
        "Great for dullness. My skin looks more awake even on tired days. Layering with hyaluronic acid serum works perfectly.",
        "The smell is strong - very citrusy/chemical. Not unpleasant but noticeable. Results are there though - pores look smaller.",
    ],
    "dk-ser-002": [
        "My holy grail for oil control! Pores visibly smaller after 1 month. No more midday shine on my T-zone.",
        "Gentle enough for daily use. Doesn't dry out my cheeks while controlling oil on forehead/nose. The zinc really helps with active breakouts.",
        "Takes time to show results - saw real difference at week 6. Patience is key with niacinamide.",
        "Pilling under my moisturizer if I don't wait long enough. Need to let it absorb fully (2-3 mins) before next step.",
        "Good budget option compared to The Ordinary. Similar results at lower price point.",
    ],
    "dk-moist-001": [
        "Saved my damaged moisture barrier! After over-exfoliating, this was the only thing that didn't sting. 2 weeks and my skin is back to normal.",
        "Rich but not heavy. Perfect for my combo skin - hydrates dry patches without making oily areas greasy. The ceramide complex works.",
        "Pump stopped working halfway through the bottle. Had to decant into another container. Product itself is great though.",
        "Fragrance-free which I appreciate. My eczema-prone skin tolerates this beautifully. Wish it came in a larger size.",
        "Good for winter but too heavy for humid summers. Switching to gel moisturizer for now.",
    ],
    "dk-moist-002": [
        "Love the 3-in-1 concept! Saves time in morning routine. SPF 20 is enough for indoor days, I layer SPF 50 for outdoors.",
        "Brightening effect is subtle but noticeable after a month. Skin tone looks more even. Non-greasy finish.",
        "Pills terribly under makeup. Tried different application methods - same result. Can't use on days I wear foundation.",
        "The Vitamin C percentage isn't disclosed which is annoying. Feels more like a moisturizer with marketing claims.",
        "Decent for the price. Would be 5 stars if it didn't pill.",
    ],
    "dk-clean-001": [
        "So gentle! My skin feels clean but not stripped. The cica really soothes my redness. Using twice daily for a month now.",
        "Removes sunscreen well without double cleansing. Lathers nicely with a little water. No tightness after rinse.",
        "Wish it foamed more - feels like I need to use a lot of product. But a bottle lasts 3+ months so value is okay.",
        "Didn't remove my waterproof mascara. Need a separate eye makeup remover. Fine as a second cleanse though.",
        "Perfect for sensitive skin. No fragrance, no irritation. My dermatologist recommended this ingredient combo.",
    ],
    "dk-clean-002": [
        "Brightening face wash that actually works! Skin looks fresher after each wash. The Vitamin C is stable - no oxidation smell.",
        "Gentle daily cleanser. Doesn't dry out my skin. Good for morning cleanse, use oil cleanser at night for sunscreen removal.",
        "Very mild - might not be enough for oily/acne skin. My friend with oily skin found it didn't control shine.",
        "Nice gel texture, lathers well. Subtle citrus scent. Good value at ₹295.",
    ],
    "dk-toner-001": [
        "Game changer for my dull skin! The rice water + niacinamide combo gives that glass skin glow. Using for 6 weeks.",
        "Absorbs instantly, no sticky residue. Layer it 2-3 times for extra hydration (Korean 7-skin method works great).",
        "Helped fade my sun spots faster than expected. Also calms my reactive skin. No alcohol burn.",
        "The bottle opening pours too fast - easy to waste product. Wish it had a dropper or smaller opening.",
        "Great toner but similar to much cheaper options. Paying for the brand/ packaging.",
    ],
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_categories() -> list[dict]:
    """Return all categories."""
    return SAMPLE_CATEGORIES


def get_products_by_category(category_id: str) -> list[dict]:
    """Return products for a category."""
    return SAMPLE_PRODUCTS.get(category_id, [])


def get_product_detail(product_id: str) -> dict | None:
    """Return full product detail with competitors and sample reviews."""
    # Search across all categories
    for category_products in SAMPLE_PRODUCTS.values():
        for product in category_products:
            if product["id"] == product_id:
                # Build detail response
                competitors = [p for p in category_products if p["id"] != product_id and not p.get("is_dot_and_key", False)]
                dot_and_key_products = [p for p in category_products if p.get("is_dot_and_key", False)]
                # Return the main product + competitors + reviews
                return {
                    "product": product,
                    "competitors": competitors,
                    "sample_reviews": SAMPLE_REVIEWS.get(product_id, []),
                }
    return None


def get_all_dot_and_key_products() -> list[dict]:
    """Return all Dot & Key products across categories."""
    result = []
    for category_products in SAMPLE_PRODUCTS.values():
        for product in category_products:
            if product.get("is_dot_and_key", False):
                result.append(product)
    return result


def get_competitors_for_product(product_id: str) -> list[dict]:
    """Return competitors for a given Dot & Key product."""
    detail = get_product_detail(product_id)
    if detail:
        return detail["competitors"]
    return []


def get_sample_reviews(product_id: str) -> list[str]:
    """Return sample reviews for a product."""
    return SAMPLE_REVIEWS.get(product_id, [])


# Current timestamp for sample data
SAMPLE_TIMESTAMP = datetime.now(timezone.utc).isoformat()