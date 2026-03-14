"""Application configuration loaded from environment / .env file."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object – never hard-code secrets in source code."""

    # .env.local is loaded last and therefore takes highest priority,
    # allowing per-developer overrides without touching the shared .env file.
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    project_name: str = Field(default="Viten API")
    ollama_api_key: str = Field(description="Pseudo API key for Ollama.")
    ollama_base_url: str = Field(
        description="Base URL of the local Ollama OpenAI-compatible endpoint."
    )
    ollama_model: str = Field(description="Ollama model name to use for claim extraction.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance (constructed once per process)."""
    return Settings()


settings: Settings = get_settings()
