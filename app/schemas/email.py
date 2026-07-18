"""Pydantic v2 request/response models for the emails API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmailMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: str
    thread_id: str
    sender: str
    to: str
    subject: str
    snippet: str
    body: str
    received_at: datetime | None = None
    labels: list[str] = Field(default_factory=list)


class ListEmailsResponse(BaseModel):
    count: int
    emails: list[EmailMessageResponse]


class SummarizeRequest(BaseModel):
    message_id: str = Field(..., description="Gmail message ID to summarize.")


class SummarizeResponse(BaseModel):
    message_id: str
    summary: str
    key_points: list[str]


class CategorizeRequest(BaseModel):
    message_id: str


class CategorizeResponse(BaseModel):
    message_id: str
    category: str
    confidence: float
    reasoning: str


class AutoReplyRequest(BaseModel):
    message_id: str
    tone: str = Field(default="professional", description="e.g. professional, friendly, formal, brief")
    send: bool = Field(default=False, description="If true, actually sends the reply via Gmail.")


class AutoReplyResponse(BaseModel):
    message_id: str
    reply_body: str
    tone: str
    sent: bool


class ExtractTasksRequest(BaseModel):
    message_id: str


class ExtractedTaskItem(BaseModel):
    description: str
    due_date: str | None = None
    priority: str = "normal"


class ExtractTasksResponse(BaseModel):
    message_id: str
    tasks: list[ExtractedTaskItem]


class TranslateRequest(BaseModel):
    message_id: str
    target_language: str = Field(default="English")


class TranslateResponse(BaseModel):
    message_id: str
    source_language: str
    target_language: str
    translated_text: str


class LabelEmailRequest(BaseModel):
    message_id: str
    label_name: str = Field(..., description="Label to apply. Created automatically if it does not exist.")


class LabelEmailResponse(BaseModel):
    message_id: str
    label_name: str
    applied: bool


class ProcessEmailRequest(BaseModel):
    """Used by the /automation/process-inbox pipeline endpoint."""

    max_results: int = Field(default=10, ge=1, le=50)
    apply_labels: bool = Field(default=True)
    auto_reply: bool = Field(default=False)
    target_language: str | None = None


class ProcessedEmailResult(BaseModel):
    message_id: str
    subject: str
    category: str
    summary: str
    label_applied: str | None = None
    reply_sent: bool = False
    tasks_found: int = 0


class ProcessEmailResponse(BaseModel):
    processed_count: int
    results: list[ProcessedEmailResult]
