import httpx
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    print("No Tavily API key found in environment")
    exit(1)

url = "https://api.tavily.com/v1/search"
headers = {"Authorization": f"Bearer {api_key}"}
payload = {
    "query": "Dot & Key Vitamin C serum price",
    "max_results": 5,
    "search_depth": "basic"
}

async def test():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                json=payload, 
                headers={"Authorization": f"Bearer {api_key}"}, 
                timeout=10
            )
            print(f"Status: {response.status_code}")
            print("Response:", print(response.text[:500]))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()