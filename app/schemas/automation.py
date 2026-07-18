"""Pydantic v2 models for automation (n8n / Zapier / Make) and auth endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str


class AuthStatusResponse(BaseModel):
    authenticated: bool
    email_address: str | None = None
    scopes: list[str] = Field(default_factory=list)


class AuthUrlResponse(BaseModel):
    authorization_url: str


class WebhookEmailEvent(BaseModel):
    """Generic payload accepted from n8n / Zapier / Make webhooks.

    External automation tools call this shape when they want the platform to
    process a specific Gmail message (e.g. triggered by a Gmail "new email"
    trigger node upstream).
    """

    message_id: str = Field(..., description="Gmail message ID to process.")
    actions: list[str] = Field(
        default_factory=lambda: ["summarize", "categorize"],
        description="Any of: summarize, categorize, extract_tasks, translate, auto_reply, label",
    )
    target_language: str | None = None
    label_name: str | None = None
    webhook_secret: str | None = Field(
        default=None, description="Shared secret configured in AUTOMATION_WEBHOOK_SECRET."
    )


class WebhookEmailEventResult(BaseModel):
    message_id: str
    summary: str | None = None
    category: str | None = None
    tasks: list[str] = Field(default_factory=list)
    translated_text: str | None = None
    reply_body: str | None = None
    label_applied: str | None = None
