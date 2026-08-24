from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = "dev_secret"

    database_url: str = "postgresql://postgres:postgres@localhost:5432/code_reviewer"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    github_client_id: str = ""
    github_client_secret: str = ""
    github_webhook_secret: str = ""
    github_callback_url: str = "http://localhost:8000/api/auth/github/callback"

    anthropic_api_key: str = ""
    groq_api_key: str = ""
    ai_provider: str = "groq"  # "groq" or "anthropic"

    client_url: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    # Cached so Settings() -> reads env vars only once per process.
    return Settings()
