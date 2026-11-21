import asyncio
import sys
sys.path.insert(0, '.')

from src.services.tavily_search import tavily_search
from src.services.market_research import NimMarketResearch

async def main():
    print("Testing Tavily search...")
    results = await tavily_search.search("Dot & Key Vitamin C serum")
    print(f"Found {len(results)} results")
    for i, r in enumerate(results[:3]):
        print(f"{i+1}. {r.title} - {r.url}")
    
    # Test NIM processing
    print("\nTesting NIM processing...")
    try:
        r = NimMarketResearch()
        print('API key configured:', bool(r.api_key))
        print('Model:', r.model)
        print('Fallbacks:', r.fallback_models)
        catalog = await r.list_products()
        print('SUCCESS - Got catalog with', len(catalog.products), 'products')
    except Exception as e:
        print('ERROR:', type(e).__name__, str(e))

asyncio.run(main())