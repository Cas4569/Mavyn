import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")
print("API key:", api_key[:20] + "..." if api_key else "NOT SET")