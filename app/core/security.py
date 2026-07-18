"""
Lightweight security utilities.

This project uses a simple API key check (via the `X-API-Key` header) to
protect its own endpoints when `API_KEY` is configured. Gmail access itself
is protected by Google OAuth 2.0 (see `app/services/gmail_service.py`).
"""

from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """FastAPI dependency that enforces the optional API key.

    If `API_KEY` is not set in the environment, this check is skipped, which
    is convenient for local development. In production, always set `API_KEY`.
    """
    settings = get_settings()
    if not settings.API_KEY:
        return

    if not x_api_key or not hmac.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key. Provide it via the 'X-API-Key' header.",
        )


def verify_webhook_secret(provided_secret: str | None) -> None:
    """Validate a shared secret sent by external automation platforms
    (n8n / Zapier / Make) when calling the /automation/* webhook endpoints.
    """
    settings = get_settings()
    if not settings.AUTOMATION_WEBHOOK_SECRET:
        return

    if not provided_secret or not hmac.compare_digest(
        provided_secret, settings.AUTOMATION_WEBHOOK_SECRET
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid webhook secret.",
        )
