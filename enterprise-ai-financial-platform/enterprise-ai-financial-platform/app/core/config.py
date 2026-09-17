from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Enterprise AI Platform for Financial Operations"

    database_url: str = "postgresql://finops:finops@localhost:5432/finops"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"

    fraud_score_threshold: float = 0.65


@lru_cache
def get_settings() -> Settings:
    return Settings()
