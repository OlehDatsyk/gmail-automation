"""Shared pytest fixtures.

Ensures tests never touch a developer's real .env, database, or Google
token file by pointing everything at a temporary directory.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Point the app at a throwaway SQLite DB / token store for every test."""
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("GOOGLE_TOKEN_STORE_PATH", str(tmp_path / "token.json"))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-not-real")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("API_KEY", "")
    monkeypatch.setenv("AUTOMATION_WEBHOOK_SECRET", "test-webhook-secret")

    # Settings is cached with lru_cache; clear it so each test sees fresh env vars.
    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
