"""Content generation service — creates marketing content from strategy insights."""

from datetime import datetime, timezone
from typing import Annotated

from src.schemas.content import (
    ContentRequest,
    ContentResponse,
    AdCopy,
    ProductDescription,
    ListingContent,
    AdScript,
    StoryboardFrame,
    Storyboard,
    VideoConcept,
)
from src.services.strategy import StrategyGenerator
from src.data.samples import get_product_detail


class ContentGenerator:
    """Generates marketing content based on product data and strategy."""

    def __init__(self):
        self.strategy_generator = StrategyGenerator()

    def generate(self, request: ContentRequest) -> ContentResponse:
        """Generate marketing content for a product."""
        # Get product detail
        detail = get_product_detail(request.product_id)
        if not detail:
            raise ValueError(f"Product not found: {request.product_id}")

        product = detail["product"]

        # Get strategy if available (or generate fresh)
        strategy = self.strategy_generator.generate(request.product_id)

        # Determine what to generate
        platforms = request.platforms or ["instagram", "facebook", "google", "youtube"]
        content_types = request.content_types or [
            "ad_copy", "product_description", "listing", "ad_script", "storyboard", "video_concept"
        ]

        # Generate each content type
        ad_copy = []
        if "ad_copy" in content_types:
            ad_copy = self._generate_ad_copy(product, strategy, platforms)

        product_description = None
        if "product_description" in content_types:
            product_description = self._generate_product_description(product, strategy)

        listing_content = None
        if "listing" in content_types:
            listing_content = self._generate_listing_content(product, strategy)

        ad_scripts = []
        if "ad_script" in content_types:
            ad_scripts = self._generate_ad_scripts(product, strategy)

        storyboard = None
        if "storyboard" in content_types:
            storyboard = self._generate_storyboard(product, strategy)

        video_concepts = []
        if "video_concept" in content_types:
            video_concepts = self._generate_video_concepts(product, strategy)

        return ContentResponse(
            product_id=request.product_id,
            ad_copy=ad_copy,
            product_description=product_description,
            listing_content=listing_content,
            ad_scripts=ad_scripts,
            storyboard=storyboard,
            video_concepts=video_concepts,
            generated_at=datetime.now(timezone.utc).isoformat(),
            source="sample",
        )

    def _generate_ad_copy(
        self,
        product: dict,
        strategy,
        platforms: list[str],
    ) -> list[AdCopy]:
        """Generate ad copy for each platform."""
        name = product["name"]
        tagline = product.get("tagline", "")
        price = product["price_inr"]

        # Extract key angles from strategy
        strengths = [s.lower() for s in strategy.swot.strengths]
        opportunities = [o.title for o in strategy.opportunities]

        copies = []

        # Instagram - visual, lifestyle
        if "instagram" in platforms:
            copies.append(AdCopy(
                platform="instagram",
                headline=f"✨ {tagline or 'Your New Skincare Essential'}",
                primary_text=(
                    f"Meet {name} — {tagline.lower()}.\n\n"
                    f"💧 Lightweight, non-greasy formula\n"
                    f"🌿 Dermatologist-tested ingredients\n"
                    f"🇮🇳 Made for Indian skin, Indian climate\n\n"
                    f"Join 1000+ customers who've made the switch. "
                    f"Tap 'Shop Now' to glow up your routine! ✨"
                ),
                cta="Shop Now",
                hashtags=["DotAndKey", "SkincareRoutine", "IndianSkincare", "GlowingSkin", "SkincareIndia"],
                character_count=0,
                source="sample",
            ))

        # Facebook - longer, benefit-focused
        if "facebook" in platforms:
            copies.append(AdCopy(
                platform="facebook",
                headline=f"Discover {name} — {tagline}",
                primary_text=(
                    f"Tired of products that promise but don't deliver? {name} is different.\n\n"
                    f"✅ {tagline}\n"
                    f"✅ {strengths[0] if strengths else 'Proven results from real customers'}\n"
                    f"✅ {strengths[1] if len(strengths) > 1 else 'Trusted by 1000+ users'}\n\n"
                    f"Real reviews from real people:\n"
                    f"💬 \"Love the lightweight feel! No white cast at all...\"\n"
                    f"💬 \"Finally a sunscreen that doesn't sting my sensitive eyes!\"\n\n"
                    f"Priced at just ₹{price}. Try it risk-free with our 30-day satisfaction guarantee."
                ),
                cta="Learn More",
                hashtags=["DotAndKey", "Skincare", "BeautyIndia"],
                character_count=0,
                source="sample",
            ))

        # Google - concise, keyword-rich
        if "google" in platforms:
            copies.append(AdCopy(
                platform="google",
                headline=f"{name} | {tagline} | ₹{price}",
                primary_text=(
                    f"{name} — {tagline}. Lightweight, non-greasy, dermatologist-tested. "
                    f"1000+ 5-star reviews. Free shipping on ₹499+. Shop Dot & Key official."
                ),
                cta="Shop Now",
                hashtags=[],
                character_count=0,
                source="sample",
            ))

        # YouTube - video-focused
        if "youtube" in platforms:
            copies.append(AdCopy(
                platform="youtube",
                headline=f"Watch: Why {name} is Breaking the Internet 🌊",
                primary_text=(
                    f"Is {name} worth the hype? We break down the ingredients, "
                    f"real results, and honest review. Plus: how it compares to "
                    f"Minimalist, Plum & Derma Co at the same price point.\n\n"
                    f"⏱️ 0:00 Intro\n"
                    f"⏱️ 0:30 Ingredient breakdown\n"
                    f"⏱️ 1:15 Real user results\n"
                    f"⏱️ 2:00 Competitor comparison\n"
                    f"⏱️ 3:00 Final verdict\n\n"
                    f"Link in description to shop with exclusive discount! 👇"
                ),
                cta="Watch Full Review",
                hashtags=["DotAndKey", "SkincareReview", "HonestReview"],
                character_count=0,
                source="sample",
            ))

        # LinkedIn - professional, science-backed
        if "linkedin" in platforms:
            copies.append(AdCopy(
                platform="linkedin",
                headline=f"The Science Behind {name}: Why Indian Dermatologists Recommend It",
                primary_text=(
                    f"At Dot & Key, we believe skincare should be backed by science, not just marketing. "
                    f"Our {name} combines {tagline.lower()} with clinically-proven actives at effective concentrations.\n\n"
                    f"🔬 Key differentiators:\n"
                    f"• Stable, bioavailable Vitamin C derivative\n"
                    f"• Barrier-supportive ceramide complex\n"
                    f"• Zero white cast on Fitzpatrick IV-VI skin tones\n"
                    f"• Non-comedogenic, fragrance-free formula\n\n"
                    f"See why 1000+ customers rate us 4.4/5. "
                    f"Partner with us for your clinic or retail shelf."
                ),
                cta="Contact Sales",
                hashtags=["SkincareScience", "Dermatology", "IndianBeauty", "DotAndKey"],
                character_count=0,
                source="sample",
            ))

        return copies

    def _generate_product_description(
        self,
        product: dict,
        strategy,
    ) -> ProductDescription:
        """Generate product description for PDP."""
        name = product["name"]
        tagline = product.get("tagline", "")
        price = product["price_inr"]

        return ProductDescription(
            short_description=f"{tagline}. ₹{price}. 4.4★ from 1000+ reviews.",
            long_description=(
                f"{name} — {tagline}\n\n"
                f"Designed for Indian skin and climate, {name} delivers visible results "
                f"without the irritation. Our formula combines clinically-proven actives "
                f"at effective concentrations in a lightweight, non-greasy texture that "
                f"layers beautifully under makeup and sunscreen.\n\n"
                f"✨ Why it works:\n"
                f"• Stable, bioavailable actives that don't oxidize\n"
                f"• Barrier-supportive ingredients for long-term skin health\n"
                f"• Tested on Indian skin tones (Fitzpatrick III-VI) — zero white cast\n"
                f"• Non-comedogenic, fragrance-free, dermatologist-tested\n\n"
                f"💡 How to use:\n"
                f"1. Cleanse with a gentle face wash\n"
                f"2. Apply 2-3 drops to damp skin\n"
                f"3. Follow with moisturizer and SPF (AM)\n"
                f"4. Use daily for best results\n\n"
                f"📦 What's inside: {name} (30ml), dropper applicator, instruction card"
            ),
            key_benefits=[
                "Visible brightening in 2-4 weeks",
                "Lightweight, fast-absorbing texture",
                "No white cast on deeper skin tones",
                "Non-comedogenic — won't clog pores",
                "Fragrance-free, suitable for sensitive skin",
                "Stable formula — no oxidation worries",
            ],
            ingredients_highlight=[
                "15% Vitamin C (Ethyl Ascorbic Acid)",
                "Vitamin E (Tocopherol)",
                "Ferulic Acid (stabilizer)",
                "Hyaluronic Acid (hydration)",
            ],
            usage_instructions=(
                "Apply 2-3 drops to clean, damp skin morning and evening. "
                "Follow with moisturizer and sunscreen during the day. "
                "Patch test before first use. Store in cool, dark place."
            ),
            source="sample",
        )

    def _generate_listing_content(
        self,
        product: dict,
        strategy,
    ) -> ListingContent:
        """Generate marketplace listing content (Nykaa, Amazon, etc.)."""
        name = product["name"]
        tagline = product.get("tagline", "")

        return ListingContent(
            title=f"{name} - {tagline} | 30ml | Official Dot & Key",
            bullet_points=[
                f"{tagline} — clinically proven actives at effective %",
                "Zero white cast on Indian skin tones (Fitzpatrick III-VI)",
                "Non-comedogenic, fragrance-free, dermatologist-tested",
                "Stable formula — no oxidation, full potency to last drop",
                "Lightweight, fast-absorbing, layers under makeup/SPF",
                "1000+ verified 5-star reviews on Nykaa & Amazon",
                "Made in India 🇮🇳 | Cruelty-free | Vegan",
            ],
            search_terms=[
                "vitamin c serum",
                "brightening serum",
                "dark spots removal",
                "anti aging serum",
                "indian skin care",
                "dot and key",
                "non comedogenic serum",
                "fragrance free skincare",
            ],
            enhanced_content=(
                f"<h2>Why {name}?</h2>"
                f"<p>Most Vitamin C serums oxidize within weeks, turning brown and losing potency. "
                f"Ours uses Ethyl Ascorbic Acid — a stable, oil-soluble derivative that penetrates "
                f"deeper and stays active for 6+ months after opening.</p>"
                f"<h3>Real Results from Real Customers</h3>"
                f"<p>\"Visible brightening in 2 weeks! My post-acne marks have faded significantly.\" — Priya, 28</p>"
                f"<p>\"Finally a Vitamin C that doesn't sting my sensitive skin. The glow is real.\" — Anjali, 34</p>"
                f"<h3>Complete Your Routine</h3>"
                f"<p>Pair with Dot & Key Ceramide Moisturizer for barrier support, "
                f"and Watermelon Sunscreen SPF 50 for daily UV protection.</p>"
            ),
            source="sample",
        )

    def _generate_ad_scripts(
        self,
        product: dict,
        strategy,
    ) -> list[AdScript]:
        """Generate video ad scripts."""
        name = product["name"]
        tagline = product.get("tagline", "")

        scripts = []

        # Reel/Shorts (15-30s)
        scripts.append(AdScript(
            format="reel",
            duration_seconds=25,
            hook="POV: You finally found a Vitamin C that doesn't oxidize 🤯",
            script=(
                "[0-3s] Close-up: Dropper dispensing golden serum into palm\n"
                "[3-8s] Text overlay: '15% Stable Vitamin C • Zero Oxidation • Zero White Cast'\n"
                "[8-15s] Split screen: Before (dull, uneven) → After (bright, even) — 2 weeks\n"
                "[15-20s] User applying under makeup, no pilling\n"
                "[20-25s] Product shot + 'Shop Link in Bio' + Dot & Key logo"
            ),
            cta="Tap the link in bio to shop!",
            source="sample",
        ))

        # In-stream (60s)
        scripts.append(AdScript(
            format="instream",
            duration_seconds=60,
            hook="What if your Vitamin C actually worked... all the way to the last drop?",
            script=(
                "[0-5s] Problem: Brown, oxidized serum bottles in bathroom cabinet\n"
                "[5-15s] Science: 'Most Vitamin C dies in the bottle. Ours doesn't.' — Animation of Ethyl Ascorbic Acid stability\n"
                "[15-30s] Proof: Real customer timeline (Day 1 → Day 14 → Day 30)\n"
                "[30-45s] Comparison: Dot & Key vs 3 competitors on price, stability, white cast\n"
                "[45-55s] Dermatologist quote: 'Finally, a stable C at the right pH for Indian skin'\n"
                "[55-60s] CTA + Offer: 'First order 15% off. Link below.'"
            ),
            cta="Get 15% off your first order — link in description",
            source="sample",
        ))

        # Bumper (6s)
        scripts.append(AdScript(
            format="bumper",
            duration_seconds=6,
            hook="Vitamin C that stays fresh. Really.",
            script=(
                "[0-1s] Serum drop falls in slow motion\n"
                "[1-3s] Text: 'Stable • Effective • No White Cast'\n"
                "[3-5s] Quick before/after flash\n"
                "[5-6s] Logo + 'Dot & Key — Skincare That Works'"
            ),
            cta="Shop DotAndKey.com",
            source="sample",
        ))

        return scripts

    def _generate_storyboard(
        self,
        product: dict,
        strategy,
    ) -> Storyboard:
        """Generate storyboard for video production."""
        name = product["name"]

        frames = [
            StoryboardFrame(
                frame_number=1,
                visual_description="Close-up macro shot: Golden serum droplet forming at dropper tip, catching light",
                audio_cue="Soft *plink* sound, ambient lab hum",
                duration_seconds=2.0,
            ),
            StoryboardFrame(
                frame_number=2,
                visual_description="Animation: Molecular structure of Ethyl Ascorbic Acid vs L-Ascorbic Acid — stability comparison",
                audio_cue="Voiceover: 'Most Vitamin C oxidizes in weeks. Ours stays stable for months.'",
                duration_seconds=4.0,
            ),
            StoryboardFrame(
                frame_number=3,
                visual_description="Split screen: Left — oxidized brown serum in competitor bottle. Right — clear golden Dot & Key serum",
                audio_cue="Voiceover: 'See the difference. Clear = potent.'",
                duration_seconds=3.0,
            ),
            StoryboardFrame(
                frame_number=4,
                visual_description="Diverse Indian skin tones (Fitzpatrick III, IV, V, VI) applying serum — no white cast visible",
                audio_cue="Voiceover: 'Tested on real Indian skin. Zero white cast. Zero gray cast.'",
                duration_seconds=4.0,
            ),
            StoryboardFrame(
                frame_number=5,
                visual_description="Time-lapse: Customer's skin Day 1 → Day 14 → Day 30 (brightening, fade marks)",
                audio_cue="Upbeat music swell. Voiceover: 'Visible results in 2 weeks.'",
                duration_seconds=4.0,
            ),
            StoryboardFrame(
                frame_number=6,
                visual_description="Flat lay: Serum + Ceramide Moisturizer + Watermelon Sunscreen — 'Complete Routine'",
                audio_cue="Voiceover: 'Pair with the routine. Glow daily.'",
                duration_seconds=3.0,
            ),
            StoryboardFrame(
                frame_number=7,
                visual_description="Product hero shot on marble surface, golden hour lighting. Logo animate in. Text: 'Dot & Key — Skincare That Works'",
                audio_cue="Music resolves. Voiceover: 'Shop at DotAndKey.com. 15% off first order.'",
                duration_seconds=3.0,
            ),
        ]

        total_duration = sum(f.duration_seconds for f in frames)

        return Storyboard(
            frames=frames,
            total_duration_seconds=total_duration,
            source="sample",
        )

    def _generate_video_concepts(
        self,
        product: dict,
        strategy,
    ) -> list[VideoConcept]:
        """Generate full video concept packages."""
        name = product["name"]
        tagline = product.get("tagline", "")

        concepts = []

        # Concept 1: Science-First Educational
        concepts.append(VideoConcept(
            concept_name="The Stable C Science",
            logline="Why your Vitamin C stops working — and the one that doesn't.",
            target_audience="Skincare enthusiasts 22-35, ingredient-conscious, research before buying",
            key_message="Stability = efficacy. Dot & Key uses Ethyl Ascorbic Acid for results that last.",
            scripts=[
                AdScript(
                    format="instream",
                    duration_seconds=90,
                    hook="You're wasting money on oxidized Vitamin C. Here's the proof.",
                    script=(
                        "[0-10s] Hook: Show 3 brown oxidized bottles. 'Sound familiar?'\n"
                        "[10-30s] Science segment: Chemist explains oxidation, shows molecular models\n"
                        "[30-50s] Lab test: Accelerated stability testing — Dot & Key vs 3 competitors\n"
                        "[50-70s] Real users: 4 women, different skin tones, 30-day unfiltered results\n"
                        "[70-90s] CTA + offer"
                    ),
                    cta="Try the stable C. 15% off + free shipping.",
                    source="sample",
                ),
            ],
            storyboard=Storyboard(
                frames=[
                    StoryboardFrame(1, "Lab setting: Chemist in coat holding oxidized vs fresh serum", "Lab ambient", 3),
                    StoryboardFrame(2, "Animation: Vitamin C oxidation pathway", "Sci-fi subtle SFX", 4),
                    StoryboardFrame(3, "Split screen stability test results", "Data visualization sounds", 4),
                    StoryboardFrame(4, "Real customers applying, smiling at results", "Upbeat, confident", 5),
                    StoryboardFrame(5, "Product hero + offer", "Brand jingle", 3),
                ],
                total_duration_seconds=19,
                source="sample",
            ),
            production_notes=[
                "Film in clean lab/studio aesthetic — white, glass, stainless steel",
                "Cast 4 women representing Fitzpatrick III-VI",
                "Need chemist/dermatologist for authority figure (can be actor with credentials)",
                "Stability test graphics: motion design team",
                "Music: modern, confident, not clinical",
            ],
            source="sample",
        ))

        # Concept 2: Relatable UGC Style
        concepts.append(VideoConcept(
            concept_name="My 30-Day Vitamin C Journey",
            logline="Real talk: I tried the viral Vitamin C serum for a month. Here's what happened.",
            target_audience="Gen Z / young millennials 18-28, trust creator reviews over ads",
            key_message="Real people, real results, no filter. Dot & Key delivers on the hype.",
            scripts=[
                AdScript(
                    format="reel",
                    duration_seconds=45,
                    hook="Day 1 vs Day 30 — no filter, no edit 😱",
                    script=(
                        "[0-3s] Side-by-side Day 1 / Day 30 selfie\n"
                        "[3-8s] 'I was skeptical...' — show unboxing, first impressions\n"
                        "[8-20s] Weekly check-ins: Day 7 (tingle), Day 14 (glow), Day 21 (marks fading)\n"
                        "[20-35s] Honest cons: 'Smells like oranges', 'Wait 2 mins before moisturizer'\n"
                        "[35-45s] Final verdict + discount code"
                    ),
                    cta="Use code MAVYN15 for 15% off",
                    source="sample",
                ),
            ],
            storyboard=Storyboard(
                frames=[
                    StoryboardFrame(1, "Selfie split: Day 1 (dull) vs Day 30 (glowing)", "Phone camera click", 2),
                    StoryboardFrame(2, "Unboxing: 'Packaging is cute but...'", "Crinkle sounds", 3),
                    StoryboardFrame(3, "Application close-up: 'Tingles a bit!'", "ASMR application sounds", 3),
                    StoryboardFrame(4, "Calendar flip: Week 1, 2, 3, 4 — progressive glow", "Upbeat transition", 4),
                    StoryboardFrame(5, "Honest cons list on screen", "Casual background music", 3),
                    StoryboardFrame(6, "Final smile + product + code", "Brand sound", 2),
                ],
                total_duration_seconds=17,
                source="sample",
            ),
            production_notes=[
                "Shot on iPhone 15 Pro — vertical 9:16, natural lighting",
                "Creator: micro-influencer (10-50k followers), skincare niche",
                "Unscripted talking points, not fully scripted",
                "Include real struggles (tingle, wait time, scent)",
                "Caption with ingredient breakdown in comments",
            ],
            source="sample",
        ))

        return concepts