"""Auto-reply drafting and sending service."""

from __future__ import annotations

import logging

from app.domain.entities import AutoReplyDraft
from app.repositories.email_repository import EmailRepository
from app.services.gmail_service import GmailService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class AutoReplyService:
    """Drafts (and optionally sends) an AI-generated reply to an email."""

    def __init__(
        self,
        gmail_service: GmailService | None = None,
        openai_service: OpenAIService | None = None,
        repository: EmailRepository | None = None,
    ) -> None:
        self.gmail_service = gmail_service or GmailService()
        self.openai_service = openai_service or OpenAIService()
        self.repository = repository or EmailRepository()

    def draft_reply(self, message_id: str, tone: str = "professional") -> AutoReplyDraft:
        message = self.gmail_service.get_message(message_id)
        if not message:
            raise ValueError(f"Email with id '{message_id}' was not found.")

        reply_body = self.openai_service.generate_reply(
            subject=message.subject, body=message.body, sender=message.sender, tone=tone
        )
        return AutoReplyDraft(message_id=message_id, reply_body=reply_body, tone=tone)

    def draft_and_send(self, message_id: str, tone: str = "professional", send: bool = False) -> tuple[AutoReplyDraft, bool]:
        draft = self.draft_reply(message_id, tone=tone)
        sent = False
        if send:
            self.gmail_service.send_reply(message_id, draft.reply_body)
            sent = True

        self.repository.save_processed_email(
            message_id=message_id,
            subject=message.subject,
            sender=message.sender,
            reply_sent=sent,
        )
        logger.info("Auto-reply drafted for message_id=%s (sent=%s)", message_id, sent)
        return draft, sent
