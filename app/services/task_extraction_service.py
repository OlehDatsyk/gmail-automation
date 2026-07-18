"""Task extraction service."""

from __future__ import annotations

import logging

from app.domain.entities import ExtractedTask, TaskExtractionResult
from app.repositories.email_repository import EmailRepository
from app.services.gmail_service import GmailService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class TaskExtractionService:
    """Extracts actionable to-dos / tasks mentioned in an email."""

    def __init__(
        self,
        gmail_service: GmailService | None = None,
        openai_service: OpenAIService | None = None,
        repository: EmailRepository | None = None,
    ) -> None:
        self.gmail_service = gmail_service or GmailService()
        self.openai_service = openai_service or OpenAIService()
        self.repository = repository or EmailRepository()

    def extract(self, message_id: str) -> TaskExtractionResult:
        message = self.gmail_service.get_message(message_id)
        if not message:
            raise ValueError(f"Email with id '{message_id}' was not found.")

        raw_tasks = self.openai_service.extract_tasks(message.subject, message.body)
        tasks = [
            ExtractedTask(
                description=t.get("description", ""),
                due_date=t.get("due_date"),
                priority=t.get("priority", "normal"),
            )
            for t in raw_tasks
            if t.get("description")
        ]

        self.repository.save_extracted_tasks(
            message_id, [t.__dict__ for t in tasks]
        )
        self.repository.save_processed_email(
            message_id=message_id,
            subject=message.subject,
            sender=message.sender,
            tasks_found=len(tasks),
        )
        logger.info("Extracted %d task(s) from message_id=%s", len(tasks), message_id)
        return TaskExtractionResult(message_id=message_id, tasks=tasks)
