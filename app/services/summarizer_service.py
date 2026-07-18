"""Email summarization service."""

from __future__ import annotations

import logging

from app.domain.entities import EmailSummary
from app.repositories.email_repository import EmailRepository
from app.services.gmail_service import GmailService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class SummarizerService:
    """Fetches an email from Gmail and produces a concise AI summary."""

    def __init__(
        self,
        gmail_service: GmailService | None = None,
        openai_service: OpenAIService | None = None,
        repository: EmailRepository | None = None,
    ) -> None:
        self.gmail_service = gmail_service or GmailService()
        self.openai_service = openai_service or OpenAIService()
        self.repository = repository or EmailRepository()

    def summarize(self, message_id: str) -> EmailSummary:
        message = self.gmail_service.get_message(message_id)
        if not message:
            raise ValueError(f"Email with id '{message_id}' was not found.")

        result = self.openai_service.summarize_email(message.subject, message.body)
        summary = EmailSummary(
            message_id=message_id,
            summary=result["summary"],
            key_points=result["key_points"],
        )

        self.repository.save_processed_email(
            message_id=message_id,
            subject=message.subject,
            sender=message.sender,
            summary=summary.summary,
        )
        logger.info("Summarized email message_id=%s", message_id)
        return summary
