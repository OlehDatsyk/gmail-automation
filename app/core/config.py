"""
Application configuration.

All runtime configuration is loaded from environment variables (optionally via a
`.env` file in the project root). This module defines a single, cached
`Settings` object that the rest of the application depends on.

Never hard-code secrets. Never commit a populated `.env` file.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Central application settings, populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- General ---------------------------------------------------------
    APP_NAME: str = "Gmail Automation Platform"
    APP_ENV: str = Field(default="development")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)
    APP_DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")

    # ---- Security ----------------------------------------------------------
    SECRET_KEY: str = Field(default="change-this-secret-key-in-production")
    API_KEY: str = Field(
        default="",
        description="Optional API key required for calling this service's own endpoints.",
    )
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000")

    # ---- OpenAI --------------------------------------------------------------
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4.1-mini")

    # ---- Google / Gmail --------------------------------------------------------
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/auth/google/callback")
    GOOGLE_SCOPES: str = Field(
        default=(
            "https://www.googleapis.com/auth/gmail.readonly,"
            "https://www.googleapis.com/auth/gmail.send,"
            "https://www.googleapis.com/auth/gmail.modify,"
            "https://www.googleapis.com/auth/gmail.labels"
        )
    )
    GOOGLE_TOKEN_STORE_PATH: str = Field(default=str(BASE_DIR / "data" / "token.json"))

    # ---- Database ---------------------------------------------------------
    DATABASE_PATH: str = Field(default=str(BASE_DIR / "data" / "gmail_automation.db"))

    # ---- Automation (n8n / Zapier / Make) ----------------------------------
    AUTOMATION_WEBHOOK_SECRET: str = Field(default="change-this-webhook-secret")

    # ---- Feature defaults ---------------------------------------------------
    DEFAULT_TRANSLATE_LANGUAGE: str = Field(default="English")
    AUTO_REPLY_ENABLED: bool = Field(default=False)
    MAX_EMAILS_PER_FETCH: int = Field(default=10)

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def _validate_origins(cls, value: str) -> str:
        return value

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def google_scopes_list(self) -> List[str]:
        return [scope.strip() for scope in self.GOOGLE_SCOPES.split(",") if scope.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()
