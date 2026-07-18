"""Email translation service."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.domain.entities import TranslationResult
from app.services.gmail_service import GmailService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class TranslationService:
    """Translates an email's body into a target language."""

    def __init__(
        self,
        gmail_service: GmailService | None = None,
        openai_service: OpenAIService | None = None,
    ) -> None:
        self.gmail_service = gmail_service or GmailService()
        self.openai_service = openai_service or OpenAIService()
        self.settings = get_settings()

    def translate(self, message_id: str, target_language: str | None = None) -> TranslationResult:
        message = self.gmail_service.get_message(message_id)
        if not message:
            raise ValueError(f"Email with id '{message_id}' was not found.")

        target = target_language or self.settings.DEFAULT_TRANSLATE_LANGUAGE
        result = self.openai_service.translate_email(message.body, target)

        logger.info("Translated message_id=%s to %s", message_id, target)
        return TranslationResult(
            message_id=message_id,
            source_language=result["source_language"],
            target_language=result["target_language"],
            translated_text=result["translated_text"],
        )
