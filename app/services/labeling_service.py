"""Email labeling service."""

from __future__ import annotations

import logging

from app.repositories.email_repository import EmailRepository
from app.services.gmail_service import GmailService

logger = logging.getLogger(__name__)


class LabelingService:
    """Applies (creating if necessary) a Gmail label to a message."""

    def __init__(
        self,
        gmail_service: GmailService | None = None,
        repository: EmailRepository | None = None,
    ) -> None:
        self.gmail_service = gmail_service or GmailService()
        self.repository = repository or EmailRepository()

    def label_email(self, message_id: str, label_name: str) -> bool:
        message = self.gmail_service.get_message(message_id)
        if not message:
            raise ValueError(f"Email with id '{message_id}' was not found.")

        applied = self.gmail_service.apply_label(message_id, label_name)

        self.repository.save_processed_email(
            message_id=message_id,
            subject=message.subject,
            sender=message.sender,
            label_applied=label_name if applied else None,
        )
        logger.info("Label '%s' applied to message_id=%s: %s", label_name, message_id, applied)
        return applied
