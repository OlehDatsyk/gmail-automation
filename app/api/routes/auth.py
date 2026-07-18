"""
Google OAuth 2.0 routes.

Flow:
1. User opens `GET /auth/google/login` in a browser -> redirected to Google's consent screen.
2. User approves access -> Google redirects back to `GET /auth/google/callback?code=...`.
3. The app exchanges the code for tokens and stores them locally
   (see GOOGLE_TOKEN_STORE_PATH in .env).
4. `GET /auth/status` can be used at any time to check whether the app is authenticated.

See docs/OAUTH_SETUP.md for the full walkthrough.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.api.deps import get_gmail_service
from app.schemas.automation import AuthStatusResponse, AuthUrlResponse
from app.services.gmail_service import GmailAuthenticationError, GmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/google/login",
    summary="Start the Google OAuth flow",
    description="Redirects the browser to Google's consent screen. Open this URL directly in a browser.",
)
async def google_login(gmail_service: GmailService = Depends(get_gmail_service)) -> RedirectResponse:
    try:
        url = gmail_service.build_authorization_url()
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse(url)


@router.get(
    "/google/authorization-url",
    response_model=AuthUrlResponse,
    summary="Get the Google OAuth consent URL as JSON (instead of redirecting)",
)
async def google_authorization_url(
    gmail_service: GmailService = Depends(get_gmail_service),
) -> AuthUrlResponse:
    try:
        url = gmail_service.build_authorization_url()
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AuthUrlResponse(authorization_url=url)


@router.get(
    "/google/callback",
    summary="OAuth callback (Google redirects here automatically)",
)
async def google_callback(
    code: str = Query(..., description="Authorization code returned by Google"),
    gmail_service: GmailService = Depends(get_gmail_service),
) -> dict:
    try:
        gmail_service.exchange_code_for_token(code)
    except Exception as exc:  # noqa: BLE001
        logger.exception("OAuth callback failed")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {exc}") from exc

    return {
        "message": "Gmail authentication successful! You can close this tab and return to the app.",
        "authenticated": True,
    }


@router.get("/status", response_model=AuthStatusResponse, summary="Check Gmail authentication status")
async def auth_status(gmail_service: GmailService = Depends(get_gmail_service)) -> AuthStatusResponse:
    authenticated = gmail_service.is_authenticated()
    email_address = None
    if authenticated:
        try:
            profile = gmail_service.get_profile()
            email_address = profile.get("emailAddress")
        except Exception:  # noqa: BLE001
            logger.warning("Authenticated but failed to fetch profile info.")

    settings = gmail_service.settings
    return AuthStatusResponse(
        authenticated=authenticated,
        email_address=email_address,
        scopes=settings.google_scopes_list if authenticated else [],
    )
