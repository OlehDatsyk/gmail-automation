"""
Gmail API service.

Wraps Google's OAuth 2.0 flow and the Gmail API (via `google-api-python-client`)
behind a small, testable interface. Credentials are cached to disk at
`GOOGLE_TOKEN_STORE_PATH` after the first successful authorization, and are
refreshed automatically when expired.

See docs/OAUTH_SETUP.md and docs/GOOGLE_CLOUD_SETUP.md for the one-time setup
required in Google Cloud Console before this service can be used.
"""

from __future__ import annotations

import base64
import json
import logging
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import get_settings
from app.domain.entities import EmailMessage

logger = logging.getLogger(__name__)


class GmailAuthenticationError(RuntimeError):
    """Raised when the app has no valid Gmail credentials yet."""


class GmailService:
    """High-level Gmail operations used by the rest of the application."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._credentials: Credentials | None = None

    # ------------------------------------------------------------------
    # OAuth flow
    # ------------------------------------------------------------------
    def _client_config(self) -> dict[str, Any]:
        return {
            "web": {
                "client_id": self.settings.GOOGLE_CLIENT_ID,
                "client_secret": self.settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.settings.GOOGLE_REDIRECT_URI],
            }
        }

    def build_authorization_url(self) -> str:
        """Return the Google consent-screen URL the user must visit."""
        if not self.settings.GOOGLE_CLIENT_ID or not self.settings.GOOGLE_CLIENT_SECRET:
            raise GmailAuthenticationError(
                "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET are not configured. "
                "See docs/GOOGLE_CLOUD_SETUP.md."
            )
        flow = Flow.from_client_config(
            self._client_config(),
            scopes=self.settings.google_scopes_list,
            redirect_uri=self.settings.GOOGLE_REDIRECT_URI,
        )
        auth_url, _state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    def exchange_code_for_token(self, code: str) -> None:
        """Exchange an OAuth authorization code for tokens and persist them."""
        flow = Flow.from_client_config(
            self._client_config(),
            scopes=self.settings.google_scopes_list,
            redirect_uri=self.settings.GOOGLE_REDIRECT_URI,
        )
        flow.fetch_token(code=code)
        self._save_credentials(flow.credentials)
        logger.info("Gmail OAuth token acquired and saved.")

    def _save_credentials(self, credentials: Credentials) -> None:
        token_path = Path(self.settings.GOOGLE_TOKEN_STORE_PATH)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json(), encoding="utf-8")
        self._credentials = credentials

    def _load_credentials(self) -> Credentials | None:
        token_path = Path(self.settings.GOOGLE_TOKEN_STORE_PATH)
        if not token_path.exists():
            return None
        data = json.loads(token_path.read_text(encoding="utf-8"))
        creds = Credentials.from_authorized_user_info(data, self.settings.google_scopes_list)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self._save_credentials(creds)
        return creds

    def is_authenticated(self) -> bool:
        try:
            creds = self._load_credentials()
            return bool(creds and creds.valid)
        except Exception:  # noqa: BLE001
            return False

    def _get_credentials(self) -> Credentials:
        creds = self._credentials or self._load_credentials()
        if not creds or not creds.valid:
            raise GmailAuthenticationError(
                "Not authenticated with Gmail yet. Visit /auth/google/login first."
            )
        self._credentials = creds
        return creds

    def _get_client(self):
        creds = self._get_credentials()
        return build("gmail", "v1", credentials=creds, cacheDiscovery=False)

    def get_profile(self) -> dict[str, Any]:
        service = self._get_client()
        return service.users().getProfile(userId="me").execute()

    # ------------------------------------------------------------------
    # Reading emails
    # ------------------------------------------------------------------
    def list_messages(self, max_results: int = 10, query: str = "") -> list[EmailMessage]:
        service = self._get_client()
        try:
            response = (
                service.users()
                .messages()
                .list(userId="me", maxResults=max_results, q=query)
                .execute()
            )
        except HttpError as exc:
            logger.error("Gmail list_messages failed: %s", exc)
            raise

        messages: list[EmailMessage] = []
        for item in response.get("messages", []):
            full_message = self.get_message(item["id"])
            if full_message:
                messages.append(full_message)
        return messages

    def get_message(self, message_id: str) -> EmailMessage | None:
        service = self._get_client()
        try:
            raw = (
                service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
        except HttpError as exc:
            logger.error("Gmail get_message failed for %s: %s", message_id, exc)
            return None
        return self._parse_message(raw)

    @staticmethod
    def _parse_message(raw: dict[str, Any]) -> EmailMessage:
        headers = {h["name"].lower(): h["value"] for h in raw.get("payload", {}).get("headers", [])}
        body = GmailService._extract_body(raw.get("payload", {}))
        return EmailMessage(
            message_id=raw.get("id", ""),
            thread_id=raw.get("threadId", ""),
            sender=headers.get("from", ""),
            to=headers.get("to", ""),
            subject=headers.get("subject", "(no subject)"),
            snippet=raw.get("snippet", ""),
            body=body,
            labels=raw.get("labelIds", []),
        )

    @staticmethod
    def _extract_body(payload: dict[str, Any]) -> str:
        """Recursively walk MIME parts to find the best plain-text body."""
        if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
            return GmailService._decode_base64(payload["body"]["data"])

        for part in payload.get("parts", []) or []:
            text = GmailService._extract_body(part)
            if text:
                return text

        # Fall back to HTML body if no plain text found
        if payload.get("mimeType") == "text/html" and payload.get("body", {}).get("data"):
            return GmailService._decode_base64(payload["body"]["data"])

        return ""

    @staticmethod
    def _decode_base64(data: str) -> str:
        try:
            return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            return ""

    # ------------------------------------------------------------------
    # Sending emails
    # ------------------------------------------------------------------
    def send_reply(self, message_id: str, body: str) -> dict[str, Any]:
        service = self._get_client()
        original = self.get_message(message_id)
        if not original:
            raise ValueError(f"Message {message_id} not found.")

        mime_message = MIMEText(body)
        mime_message["to"] = original.sender
        mime_message["subject"] = (
            original.subject if original.subject.lower().startswith("re:") else f"Re: {original.subject}"
        )
        raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")

        result = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw, "threadId": original.thread_id})
            .execute()
        )
        logger.info("Reply sent for message_id=%s", message_id)
        return result

    # ------------------------------------------------------------------
    # Labels
    # ------------------------------------------------------------------
    def get_or_create_label(self, label_name: str) -> str:
        service = self._get_client()
        labels = service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"].lower() == label_name.lower():
                return label["id"]

        created = (
            service.users()
            .labels()
            .create(
                userId="me",
                body={
                    "name": label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )
        logger.info("Created new Gmail label: %s", label_name)
        return created["id"]

    def apply_label(self, message_id: str, label_name: str) -> bool:
        service = self._get_client()
        label_id = self.get_or_create_label(label_name)
        service.users().messages().modify(
            userId="me", id=message_id, body={"addLabelIds": [label_id]}
        ).execute()
        logger.info("Applied label '%s' to message_id=%s", label_name, message_id)
        return True
