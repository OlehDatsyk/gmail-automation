"""
Domain entities.

These are plain, framework-agnostic representations of the core business
concepts in this application. They do not depend on FastAPI, Gmail, or
OpenAI — that keeps the domain layer testable and portable, per Clean
Architecture principles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EmailCategory(str, Enum):
    """Category labels an email can be classified into."""

    URGENT = "Urgent"
    WORK = "Work"
    PERSONAL = "Personal"
    FINANCE = "Finance"
    PROMOTIONS = "Promotions"
    SOCIAL = "Social"
    SPAM = "Spam"
    SUPPORT = "Support"
    OTHER = "Other"


@dataclass
class EmailMessage:
    """A normalized representation of a Gmail message."""

    message_id: str
    thread_id: str
    sender: str
    to: str
    subject: str
    snippet: str
    body: str
    received_at: datetime | None = None
    labels: list[str] = field(default_factory=list)


@dataclass
class EmailSummary:
    message_id: str
    summary: str
    key_points: list[str] = field(default_factory=list)


@dataclass
class EmailClassification:
    message_id: str
    category: EmailCategory
    confidence: float
    reasoning: str = ""


@dataclass
class ExtractedTask:
    description: str
    due_date: str | None = None
    priority: str = "normal"


@dataclass
class TaskExtractionResult:
    message_id: str
    tasks: list[ExtractedTask] = field(default_factory=list)


@dataclass
class TranslationResult:
    message_id: str
    source_language: str
    target_language: str
    translated_text: str


@dataclass
class AutoReplyDraft:
    message_id: str
    reply_body: str
    tone: str = "professional"
