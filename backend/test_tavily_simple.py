import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


async def main():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("No Tavily API key found in environment")
        return

    payload = {
        "query": "Dot & Key Vitamin C serum price",
        "max_results": 3,
        "search_depth": "basic",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
    print("Status:", response.status_code)
    print("Headers:", dict(response.headers))
    print("Body:", print(response.text[:500]))


asyncio.run(main())