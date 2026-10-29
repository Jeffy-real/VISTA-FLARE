"""Application settings."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Vista Flare"
    app_env: str = "development"
    debug: bool = True
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'vista_flare.db'}"
    secret_key: str = "dev-only-change-me"
    session_cookie_name: str = "vista_flare_session"
    csrf_cookie_name: str = "vista_flare_csrf"
    session_max_age: int = 2592000
    secure_cookies: bool = False
    model_version: str = "ANN-v1"
    default_model: str = "ann"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    ingestion_admin_secret: str = ""
    ingestion_stale_after_hours: int = 48
    enable_ingestion_scheduler: bool = False
    ingestion_interval_minutes: int = 360
    job_provider_timeout_seconds: float = 12.0
    job_provider_max_retries: int = 2
    job_provider_page_size: int = 50
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "gb"
    adzuna_query: str = ""
    inference_trace_retention_hours: int = 168

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore", protected_namespaces=())


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Create a singleton settings instance for import
settings = get_settings()
