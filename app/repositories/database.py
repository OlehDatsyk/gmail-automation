"""
SQLite database bootstrap.

Uses the Python standard library `sqlite3` module directly (no ORM) to keep
the dependency footprint minimal, as required for this project. A single
connection factory is provided; each repository call opens a short-lived
connection, which is safe and simple for SQLite's file-based model.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,
    subject TEXT,
    sender TEXT,
    category TEXT,
    summary TEXT,
    label_applied TEXT,
    reply_sent INTEGER DEFAULT 0,
    tasks_found INTEGER DEFAULT 0,
    processed_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS automation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    action TEXT NOT NULL,
    message_id TEXT,
    status TEXT NOT NULL,
    detail TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS extracted_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    description TEXT NOT NULL,
    due_date TEXT,
    priority TEXT DEFAULT 'normal',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_processed_emails_message_id ON processed_emails(message_id);
CREATE INDEX IF NOT EXISTS idx_extracted_tasks_message_id ON extracted_tasks(message_id);
"""


def get_db_path() -> Path:
    settings = get_settings()
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with row factory configured, closing it afterward."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they do not already exist. Call once at startup."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
    logger.info("Database initialized at %s", get_db_path())
