"""Application configuration."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "MAVYN Backend"
    app_version: str = "0.1.0"
    debug: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Gemini (legacy)
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.6-flash"
    gemini_fallback_models: str = "gemini-3.5-flash-lite,gemini-3.8-flash"
    market_data_cache_ttl_seconds: int = 21600

    # Tavily (web search + grounded evidence)
    tavily_api_key: SecretStr | None = None
    tavily_search_depth: str = "advanced"
    tavily_max_results: int = 8

    # NVIDIA NIM (reasoning over the search evidence)
    nim_api_key: SecretStr | None = None
    nim_model: str = "deepseek-ai/deepseek-v4.1-flash"
    nim_fallback_models: str = "nvidia/nemotron-3.5-flash"
    nim_base_url: str = "https://integrate.api.nvidia.com/v1"


settings = Settings()