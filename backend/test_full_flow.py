import asyncio
import sys
sys.path.insert(0, '.')

from src.services.tavily_search import tavily_search
from src.services.market_research import NimMarketResearch

async def main():
    print("Testing Tavily search...")
    results = await tavily_search.search("Dot & Key")
    print(f"Found {len(results)} results")

    print("\nTesting NIM processing...")
    try:
        r = NimMarketResearch()
        print('API key configured:', bool(r.api_key))
        catalog = await r.list_products()
        print('SUCCESS - Got catalog with', len(catalog.products), 'products')
    except Exception as e:
        print('ERROR:', type(e).__name__, str(e))

if __name__ == "__main__":
    # Fix unicode issues by forcing utf-8 for stdout
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())