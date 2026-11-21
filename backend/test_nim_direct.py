import httpx
import os

api_key = os.getenv("NIM_API_KEY")
if not api_key:
    print("No NIM API key found")
    exit(1)

url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('NIM_API_KEY')}",
    "Content-Type": "application/json"
}
payload = {
    "model": "deepseek-ai/deepseek-v4.1-flash",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}

try:
    response = httpx.post(url, headers=headers, json=payload, timeout=10)
    print("Status:", response.status_code)
    print("Body:", response.text[:500])
except Exception as e:
    print("Error:", e)
