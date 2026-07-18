"""Unit tests for CategorizerService using mocked Gmail/OpenAI dependencies.

No real network calls are made — Gmail and OpenAI are replaced with simple
stand-ins, keeping these tests fast and free.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.domain.entities import EmailCategory, EmailMessage
from app.services.categorizer_service import CategorizerService


@pytest.fixture
def sample_message() -> EmailMessage:
    return EmailMessage(
        message_id="msg-123",
        thread_id="thread-123",
        sender="boss@example.com",
        to="me@example.com",
        subject="Quarterly report due Friday",
        snippet="Please send the Q3 report...",
        body="Hi, please send the Q3 report by Friday EOD. Thanks!",
    )


def test_categorize_returns_expected_classification(sample_message: EmailMessage):
    gmail_service = MagicMock()
    gmail_service.get_message.return_value = sample_message

    openai_service = MagicMock()
    openai_service.categorize_email.return_value = {
        "category": EmailCategory.WORK.value,
        "confidence": 0.92,
        "reasoning": "Mentions a work deliverable and deadline.",
    }

    repository = MagicMock()

    service = CategorizerService(
        gmail_service=gmail_service, openai_service=openai_service, repository=repository
    )

    result = service.categorize("msg-123")

    assert result.category == EmailCategory.WORK
    assert result.confidence == pytest.approx(0.92)
    gmail_service.get_message.assert_called_once_with("msg-123")
    repository.save_processed_email.assert_called_once()


def test_categorize_raises_for_missing_email():
    gmail_service = MagicMock()
    gmail_service.get_message.return_value = None

    service = CategorizerService(
        gmail_service=gmail_service, openai_service=MagicMock(), repository=MagicMock()
    )

    with pytest.raises(ValueError):
        service.categorize("does-not-exist")
