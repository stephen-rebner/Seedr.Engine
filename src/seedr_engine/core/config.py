from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-6"
    max_rows_per_request: int = 100
    log_level: str = "INFO"
    environment: Literal["development", "production"] = "development"


settings = Settings()
