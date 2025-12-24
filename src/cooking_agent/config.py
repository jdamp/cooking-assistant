"""Configuration management using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Mealie API
    mealie_url: str = "http://localhost:9925"
    mealie_api_token: str

    # Bring Shopping List
    bring_email: str
    bring_password: str

    # OpenAI LLM
    openai_api_key: str
    model_name: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
