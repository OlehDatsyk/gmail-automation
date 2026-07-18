"""Shared FastAPI dependency providers.

Each provider returns a fresh service instance per request. Services are
lightweight (they lazily open connections/clients), so this keeps request
handling stateless and easy to test.
"""

from __future__ import annotations

from app.repositories.email_repository import EmailRepository
from app.services.auto_reply_service import AutoReplyService
from app.services.categorizer_service import CategorizerService
from app.services.gmail_service import GmailService
from app.services.labeling_service import LabelingService
from app.services.openai_service import OpenAIService
from app.services.summarizer_service import SummarizerService
from app.services.task_extraction_service import TaskExtractionService
from app.services.translation_service import TranslationService


def get_gmail_service() -> GmailService:
    return GmailService()


def get_openai_service() -> OpenAIService:
    return OpenAIService()


def get_email_repository() -> EmailRepository:
    return EmailRepository()


def get_summarizer_service() -> SummarizerService:
    return SummarizerService()


def get_categorizer_service() -> CategorizerService:
    return CategorizerService()


def get_auto_reply_service() -> AutoReplyService:
    return AutoReplyService()


def get_task_extraction_service() -> TaskExtractionService:
    return TaskExtractionService()


def get_translation_service() -> TranslationService:
    return TranslationService()


def get_labeling_service() -> LabelingService:
    return LabelingService()
