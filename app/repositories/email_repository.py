"""Repository for persisting processed-email records and automation logs."""

from __future__ import annotations

import logging
from typing import Any

from app.repositories.database import get_connection

logger = logging.getLogger(__name__)


class EmailRepository:
    """Data-access layer for the `processed_emails`, `automation_logs`, and
    `extracted_tasks` tables. Kept free of business logic — callers (services)
    decide what to store and when.
    """

    def save_processed_email(
        self,
        message_id: str,
        subject: str | None = None,
        sender: str | None = None,
        category: str | None = None,
        summary: str | None = None,
        label_applied: str | None = None,
        reply_sent: bool | None = None,
        tasks_found: int | None = None,
    ) -> None:
        """Upsert a processed-email record.

        Fields left as `None` are preserved from any existing row instead of
        being blanked out, so partial updates (e.g. only setting `category`
        after a previous call already set `subject`) accumulate correctly.
        """
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO processed_emails
                    (message_id, subject, sender, category, summary, label_applied, reply_sent, tasks_found)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_id) DO UPDATE SET
                    subject=COALESCE(excluded.subject, processed_emails.subject),
                    sender=COALESCE(excluded.sender, processed_emails.sender),
                    category=COALESCE(excluded.category, processed_emails.category),
                    summary=COALESCE(excluded.summary, processed_emails.summary),
                    label_applied=COALESCE(excluded.label_applied, processed_emails.label_applied),
                    reply_sent=COALESCE(excluded.reply_sent, processed_emails.reply_sent),
                    tasks_found=COALESCE(excluded.tasks_found, processed_emails.tasks_found),
                    processed_at=datetime('now')
                """,
                (
                    message_id,
                    subject,
                    sender,
                    category,
                    summary,
                    label_applied,
                    None if reply_sent is None else int(reply_sent),
                    tasks_found,
                ),
            )
        logger.debug("Saved processed email record for message_id=%s", message_id)

    def save_extracted_tasks(self, message_id: str, tasks: list[dict[str, Any]]) -> None:
        if not tasks:
            return
        with get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO extracted_tasks (message_id, description, due_date, priority)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        message_id,
                        task.get("description", ""),
                        task.get("due_date"),
                        task.get("priority", "normal"),
                    )
                    for task in tasks
                ],
            )

    def log_automation_event(
        self,
        source: str,
        action: str,
        status: str,
        message_id: str | None = None,
        detail: str | None = None,
    ) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO automation_logs (source, action, message_id, status, detail)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source, action, message_id, status, detail),
            )
        logger.info("Automation event logged: source=%s action=%s status=%s", source, action, status)

    def get_processed_email(self, message_id: str) -> dict[str, Any] | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM processed_emails WHERE message_id = ?", (message_id,)
            ).fetchone()
            return dict(row) if row else None

    def list_recent_processed_emails(self, limit: int = 20) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM processed_emails ORDER BY processed_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
