"""Health check endpoint — useful for uptime monitors and n8n/Zapier/Make connectivity tests."""

from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings
from app.schemas.automation import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=__version__,
        environment=settings.APP_ENV,
    )
