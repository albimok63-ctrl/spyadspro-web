"""
Configurazione centralizzata tramite variabili ambiente (Pydantic BaseSettings).
Single source of truth: tutti i moduli leggono da get_settings() / config.py.
Compatibile con .env.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings caricati da ambiente e .env. Segreti e config in un unico punto."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Segreto principale (JWT, signing). In produzione impostare SECRET_KEY da env.
    secret_key: str = "change-me-in-production-min-32-chars"
    # Scadenza token JWT (minuti).
    access_token_expire_minutes: int = 60
    # Ambiente: development, staging, production.
    environment: str = "development"

    app_name: str = "health-api"
    debug: bool = False
    version: str = "1.0.0"
    database_url: str = "sqlite:///./app.db"
    # Redis (opzionale, cache-aside)
    redis_host: str = "localhost"
    redis_port: int = 6379
    cache_enabled: bool = False
