import httpx
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("NIM_API_KEY")
url = "https://integrate.api.nvidia.com/v1/chat/completions"

models_to_try = [
    "mistralai/mistral-large-4-1t-a52b",
    "moonshotai/kimi-k3.1-pro",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "google/gemma-4-31b-it",
    "minimaxai/minimax-m3.1-flash",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
]

for model in models_to_try:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say hi"}],
        "max_tokens": 10,
    }
    try:
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )
        print(f"{model}: {response.status_code}")
        if response.status_code == 200:
            print("  WORKS ->", response.json()["choices"][0]["message"]["content"][:50])
        else:
            print("  ->", response.text[:120])
    except Exception as e:
        print(f"{model}: Error {e}")
