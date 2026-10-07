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
    model_version: str = "ANN-v1"
    default_model: str = "ann"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore", protected_namespaces=())


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Create a singleton settings instance for import
settings = get_settings()
