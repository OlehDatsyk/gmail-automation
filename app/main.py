"""
Gmail Automation Platform — FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Or simply:
    python -m app.main

Interactive API docs are available at /docs (Swagger UI) and /redoc.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import automation, auth, emails, health
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.security import verify_api_key
from app.repositories.database import init_db

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting %s (env=%s)", settings.APP_NAME, settings.APP_ENV)
    init_db()

    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set. AI features will fail until it is configured in .env.")
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        logger.warning(
            "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET are not set. "
            "Gmail features will fail until Google Cloud OAuth is configured. "
            "See docs/GOOGLE_CLOUD_SETUP.md."
        )

    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "A production-ready Gmail automation platform: read, summarize, categorize, "
            "auto-reply, extract tasks from, translate, and label emails using the OpenAI "
            "Responses API — with first-class integration hooks for n8n, Zapier, and Make."
        ),
        version=__version__,
        lifespan=lifespan,
        debug=settings.APP_DEBUG,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health and the OAuth browser flow stay open (no API key required).
    app.include_router(health.router)
    app.include_router(auth.router)

    # Feature endpoints are protected by the optional API key
    # (enforced only if API_KEY is set in .env — see app/core/security.py).
    app.include_router(emails.router, dependencies=[Depends(verify_api_key)])

    # Automation endpoints are called by n8n/Zapier/Make and use their own
    # shared-secret check (AUTOMATION_WEBHOOK_SECRET) instead, so no-code
    # tools only need to manage one credential.
    app.include_router(automation.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
