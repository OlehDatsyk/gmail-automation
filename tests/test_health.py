"""Tests for the /health endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_check_returns_ok():
    from app.main import create_app

    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "app_name" in body
    assert "version" in body
