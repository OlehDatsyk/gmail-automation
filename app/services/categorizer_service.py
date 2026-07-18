"""Email categorization service."""

from __future__ import annotations

import logging

from app.domain.entities import EmailCategory, EmailClassification
from app.repositories.email_repository import EmailRepository
from app.services.gmail_service import GmailService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class CategorizerService:
    """Fetches an email from Gmail and classifies it into a category."""

    def __init__(
        self,
        gmail_service: GmailService | None = None,
        openai_service: OpenAIService | None = None,
        repository: EmailRepository | None = None,
    ) -> None:
        self.gmail_service = gmail_service or GmailService()
        self.openai_service = openai_service or OpenAIService()
        self.repository = repository or EmailRepository()

    def categorize(self, message_id: str) -> EmailClassification:
        message = self.gmail_service.get_message(message_id)
        if not message:
            raise ValueError(f"Email with id '{message_id}' was not found.")

        result = self.openai_service.categorize_email(message.subject, message.body)
        classification = EmailClassification(
            message_id=message_id,
            category=EmailCategory(result["category"]),
            confidence=result["confidence"],
            reasoning=result["reasoning"],
        )

        self.repository.save_processed_email(
            message_id=message_id,
            subject=message.subject,
            sender=message.sender,
            category=classification.category.value,
        )
        logger.info(
            "Categorized email message_id=%s as %s (confidence=%.2f)",
            message_id,
            classification.category.value,
            classification.confidence,
        )
        return classification
