from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clinical Voice AI Agent"
    environment: str = "local"
    redis_url: str | None = None
    latency_budget_ms: int = 450
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="VOICE_AGENT_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
