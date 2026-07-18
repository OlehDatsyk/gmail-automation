"""
Email feature routes.

Implements the seven core features: read, summarize, categorize, auto-reply,
extract tasks, translate, and label. Each endpoint is intentionally narrow
and single-purpose, in keeping with the modular-services architecture — the
routes themselves only translate HTTP <-> service calls.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import (
    get_auto_reply_service,
    get_categorizer_service,
    get_email_repository,
    get_gmail_service,
    get_labeling_service,
    get_summarizer_service,
    get_task_extraction_service,
    get_translation_service,
)
from app.core.config import get_settings
from app.repositories.email_repository import EmailRepository
from app.schemas.email import (
    AutoReplyRequest,
    AutoReplyResponse,
    CategorizeRequest,
    CategorizeResponse,
    EmailMessageResponse,
    ExtractedTaskItem,
    ExtractTasksRequest,
    ExtractTasksResponse,
    LabelEmailRequest,
    LabelEmailResponse,
    ListEmailsResponse,
    SummarizeRequest,
    SummarizeResponse,
    TranslateRequest,
    TranslateResponse,
)
from app.services.auto_reply_service import AutoReplyService
from app.services.categorizer_service import CategorizerService
from app.services.gmail_service import GmailAuthenticationError, GmailService
from app.services.labeling_service import LabelingService
from app.services.summarizer_service import SummarizerService
from app.services.task_extraction_service import TaskExtractionService
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["Emails"])


def _handle_auth_error(exc: Exception) -> None:
    if isinstance(exc, GmailAuthenticationError):
        raise HTTPException(status_code=401, detail=str(exc)) from exc


# ------------------------------------------------------------------------
# 1. Read Emails
# ------------------------------------------------------------------------
@router.get("", response_model=ListEmailsResponse, summary="List / read recent emails")
async def list_emails(
    max_results: int = Query(default=10, ge=1, le=50),
    query: str = Query(default="", description="Gmail search query, e.g. 'is:unread'"),
    gmail_service: GmailService = Depends(get_gmail_service),
) -> ListEmailsResponse:
    try:
        settings = get_settings()
        limit = min(max_results, settings.MAX_EMAILS_PER_FETCH) if settings.MAX_EMAILS_PER_FETCH else max_results
        messages = gmail_service.list_messages(max_results=limit, query=query)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to list emails")
        raise HTTPException(status_code=502, detail=f"Gmail API error: {exc}") from exc

    return ListEmailsResponse(
        count=len(messages),
        emails=[EmailMessageResponse.model_validate(m.__dict__) for m in messages],
    )


@router.get("/{message_id}", response_model=EmailMessageResponse, summary="Get a single email by ID")
async def get_email(
    message_id: str, gmail_service: GmailService = Depends(get_gmail_service)
) -> EmailMessageResponse:
    try:
        message = gmail_service.get_message(message_id)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    if not message:
        raise HTTPException(status_code=404, detail=f"Email '{message_id}' not found.")
    return EmailMessageResponse.model_validate(message.__dict__)


# ------------------------------------------------------------------------
# 2. Summarize Emails
# ------------------------------------------------------------------------
@router.post("/summarize", response_model=SummarizeResponse, summary="Summarize an email")
async def summarize_email(
    payload: SummarizeRequest, service: SummarizerService = Depends(get_summarizer_service)
) -> SummarizeResponse:
    try:
        result = service.summarize(payload.message_id)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Summarization failed")
        raise HTTPException(status_code=502, detail=f"AI processing error: {exc}") from exc

    return SummarizeResponse(
        message_id=result.message_id, summary=result.summary, key_points=result.key_points
    )


# ------------------------------------------------------------------------
# 3. Categorize Emails
# ------------------------------------------------------------------------
@router.post("/categorize", response_model=CategorizeResponse, summary="Categorize an email")
async def categorize_email(
    payload: CategorizeRequest, service: CategorizerService = Depends(get_categorizer_service)
) -> CategorizeResponse:
    try:
        result = service.categorize(payload.message_id)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Categorization failed")
        raise HTTPException(status_code=502, detail=f"AI processing error: {exc}") from exc

    return CategorizeResponse(
        message_id=result.message_id,
        category=result.category.value,
        confidence=result.confidence,
        reasoning=result.reasoning,
    )


# ------------------------------------------------------------------------
# 4. Auto Reply
# ------------------------------------------------------------------------
@router.post("/auto-reply", response_model=AutoReplyResponse, summary="Draft (and optionally send) an AI reply")
async def auto_reply(
    payload: AutoReplyRequest, service: AutoReplyService = Depends(get_auto_reply_service)
) -> AutoReplyResponse:
    try:
        draft, sent = service.draft_and_send(payload.message_id, tone=payload.tone, send=payload.send)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Auto-reply failed")
        raise HTTPException(status_code=502, detail=f"Processing error: {exc}") from exc

    return AutoReplyResponse(
        message_id=draft.message_id, reply_body=draft.reply_body, tone=draft.tone, sent=sent
    )


# ------------------------------------------------------------------------
# 5. Extract Tasks
# ------------------------------------------------------------------------
@router.post("/extract-tasks", response_model=ExtractTasksResponse, summary="Extract action items from an email")
async def extract_tasks(
    payload: ExtractTasksRequest, service: TaskExtractionService = Depends(get_task_extraction_service)
) -> ExtractTasksResponse:
    try:
        result = service.extract(payload.message_id)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Task extraction failed")
        raise HTTPException(status_code=502, detail=f"AI processing error: {exc}") from exc

    return ExtractTasksResponse(
        message_id=result.message_id,
        tasks=[
            ExtractedTaskItem(description=t.description, due_date=t.due_date, priority=t.priority)
            for t in result.tasks
        ],
    )


# ------------------------------------------------------------------------
# 6. Translate Emails
# ------------------------------------------------------------------------
@router.post("/translate", response_model=TranslateResponse, summary="Translate an email")
async def translate_email(
    payload: TranslateRequest, service: TranslationService = Depends(get_translation_service)
) -> TranslateResponse:
    try:
        result = service.translate(payload.message_id, target_language=payload.target_language)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Translation failed")
        raise HTTPException(status_code=502, detail=f"AI processing error: {exc}") from exc

    return TranslateResponse(
        message_id=result.message_id,
        source_language=result.source_language,
        target_language=result.target_language,
        translated_text=result.translated_text,
    )


# ------------------------------------------------------------------------
# 7. Label Emails
# ------------------------------------------------------------------------
@router.post("/label", response_model=LabelEmailResponse, summary="Apply a Gmail label to an email")
async def label_email(
    payload: LabelEmailRequest, service: LabelingService = Depends(get_labeling_service)
) -> LabelEmailResponse:
    try:
        applied = service.label_email(payload.message_id, payload.label_name)
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Labeling failed")
        raise HTTPException(status_code=502, detail=f"Gmail API error: {exc}") from exc

    return LabelEmailResponse(message_id=payload.message_id, label_name=payload.label_name, applied=applied)


# ------------------------------------------------------------------------
# History (SQLite-backed) — useful for dashboards / automation debugging
# ------------------------------------------------------------------------
@router.get("/history/recent", summary="List recently processed emails from the local database")
async def recent_history(
    limit: int = Query(default=20, ge=1, le=100),
    repository: EmailRepository = Depends(get_email_repository),
) -> dict:
    return {"results": repository.list_recent_processed_emails(limit=limit)}
