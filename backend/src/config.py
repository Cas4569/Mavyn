"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
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


settings = Settings()