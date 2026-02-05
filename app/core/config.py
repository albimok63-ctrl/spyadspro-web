"""
Application settings. Single source of truth for env and config.
No business logic, no HTTP.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment (and .env when present)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "health-api"
    debug: bool = False
    version: str = "1.0.0"
    database_url: str = "sqlite:///./app.db"
    # Redis (opzionale, cache-aside)
    redis_host: str = "localhost"
    redis_port: int = 6379
    cache_enabled: bool = False
