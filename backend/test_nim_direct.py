import httpx
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NIM_API_KEY")
url = "https://integrate.api.nvidia.com/v1/chat/completions"
payload = {
    "model": "mistralai/mistral-large-4-1t-a52b",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}

try:
    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60
    )
    print("Status:", response.status_code)
    print("Body:", response.text)
except Exception as e:
    print("Error:", e)
