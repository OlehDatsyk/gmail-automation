"""
Automation routes.

These endpoints are the integration surface for external automation tools
(n8n, Zapier, Make). See workflows/ for ready-to-import workflow definitions
and docs/AUTOMATION_ARCHITECTURE.md for the overall design.

Two integration patterns are supported:

1. Pull: automation tools call `GET /emails` and the feature endpoints under
   `/emails/*` directly (simple HTTP nodes / "Custom Request" actions).
2. Push: automation tools call `POST /automation/webhook` with a single
   Gmail message ID and a list of actions to run, receiving one combined
   response. This is the pattern used by the provided n8n/Zapier/Make
   workflow files, since it minimizes the number of HTTP calls a no-code
   workflow needs to make.

`POST /automation/process-inbox` is a convenience endpoint that runs the
full pipeline (categorize -> summarize -> label -> optional auto-reply)
across the most recent unread emails in one call — ideal for a scheduled
n8n/Make workflow or a cron job.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    get_auto_reply_service,
    get_categorizer_service,
    get_gmail_service,
    get_labeling_service,
    get_summarizer_service,
    get_task_extraction_service,
    get_translation_service,
)
from app.core.security import verify_webhook_secret
from app.repositories.database import get_connection
from app.schemas.email import ProcessedEmailResult, ProcessEmailRequest, ProcessEmailResponse
from app.schemas.automation import WebhookEmailEvent, WebhookEmailEventResult
from app.services.auto_reply_service import AutoReplyService
from app.services.categorizer_service import CategorizerService
from app.services.gmail_service import GmailAuthenticationError, GmailService
from app.services.labeling_service import LabelingService
from app.services.summarizer_service import SummarizerService
from app.services.task_extraction_service import TaskExtractionService
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/automation", tags=["Automation (n8n / Zapier / Make)"])


@router.post(
    "/webhook",
    response_model=WebhookEmailEventResult,
    summary="Generic webhook for n8n / Zapier / Make: run one or more actions on a single email",
)
async def automation_webhook(
    payload: WebhookEmailEvent,
    gmail_service: GmailService = Depends(get_gmail_service),
    summarizer: SummarizerService = Depends(get_summarizer_service),
    categorizer: CategorizerService = Depends(get_categorizer_service),
    task_extractor: TaskExtractionService = Depends(get_task_extraction_service),
    translator: TranslationService = Depends(get_translation_service),
    auto_replier: AutoReplyService = Depends(get_auto_reply_service),
    labeler: LabelingService = Depends(get_labeling_service),
) -> WebhookEmailEventResult:
    verify_webhook_secret(payload.webhook_secret)

    result = WebhookEmailEventResult(message_id=payload.message_id)
    actions = {a.lower() for a in payload.actions}

    try:
        if "summarize" in actions:
            s = summarizer.summarize(payload.message_id)
            result.summary = s.summary

        if "categorize" in actions:
            c = categorizer.categorize(payload.message_id)
            result.category = c.category.value

        if "extract_tasks" in actions:
            t = task_extractor.extract(payload.message_id)
            result.tasks = [task.description for task in t.tasks]

        if "translate" in actions:
            tr = translator.translate(payload.message_id, target_language=payload.target_language)
            result.translated_text = tr.translated_text

        if "auto_reply" in actions:
            draft, _sent = auto_replier.draft_and_send(payload.message_id, send=False)
            result.reply_body = draft.reply_body

        if "label" in actions and payload.label_name:
            labeler.label_email(payload.message_id, payload.label_name)
            result.label_applied = payload.label_name

    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Automation webhook processing failed")
        raise HTTPException(status_code=502, detail=f"Processing error: {exc}") from exc

    return result


@router.post(
    "/process-inbox",
    response_model=ProcessEmailResponse,
    summary="Run the full pipeline (categorize, summarize, label, optional auto-reply) over recent unread emails",
)
async def process_inbox(
    payload: ProcessEmailRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
    summarizer: SummarizerService = Depends(get_summarizer_service),
    categorizer: CategorizerService = Depends(get_categorizer_service),
    task_extractor: TaskExtractionService = Depends(get_task_extraction_service),
    labeler: LabelingService = Depends(get_labeling_service),
    auto_replier: AutoReplyService = Depends(get_auto_reply_service),
) -> ProcessEmailResponse:
    try:
        messages = gmail_service.list_messages(max_results=payload.max_results, query="is:unread")
    except GmailAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to list unread emails")
        raise HTTPException(status_code=502, detail=f"Gmail API error: {exc}") from exc

    results: list[ProcessedEmailResult] = []
    for message in messages:
        try:
            classification = categorizer.categorize(message.message_id)
            summary = summarizer.summarize(message.message_id)

            label_applied = None
            if payload.apply_labels:
                labeler.label_email(message.message_id, classification.category.value)
                label_applied = classification.category.value

            tasks_result = task_extractor.extract(message.message_id)

            reply_sent = False
            if payload.auto_reply:
                _draft, reply_sent = auto_replier.draft_and_send(message.message_id, send=True)

            results.append(
                ProcessedEmailResult(
                    message_id=message.message_id,
                    subject=message.subject,
                    category=classification.category.value,
                    summary=summary.summary,
                    label_applied=label_applied,
                    reply_sent=reply_sent,
                    tasks_found=len(tasks_result.tasks),
                )
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to process message_id=%s; skipping.", message.message_id)
            continue

    return ProcessEmailResponse(processed_count=len(results), results=results)


@router.get("/logs/recent", summary="List recent automation events (for debugging n8n/Zapier/Make integrations)")
async def recent_automation_logs(limit: int = 20) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM automation_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return {"results": [dict(row) for row in rows]}
