"""
OpenAI service.

Wraps the OpenAI Responses API (`client.responses.create`) for every AI
feature in this platform: summarization, categorization, task extraction,
translation, and auto-reply drafting.

The Responses API is used (not the older Chat Completions API) per project
requirements. Structured data is requested as strict JSON and parsed
defensively, since model output — even when instructed — can occasionally
deviate.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.domain.entities import EmailCategory

logger = logging.getLogger(__name__)


class OpenAIService:
    """High-level AI operations backed by the OpenAI Responses API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not self.settings.OPENAI_API_KEY:
                raise RuntimeError(
                    "OPENAI_API_KEY is not configured. Add it to your .env file."
                )
            self._client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        return self._client

    def _run(self, instructions: str, input_text: str) -> str:
        """Call the Responses API and return the plain text output."""
        response = self.client.responses.create(
            model=self.settings.OPENAI_MODEL,
            instructions=instructions,
            input=input_text,
        )
        return response.output_text.strip()

    def _run_json(self, instructions: str, input_text: str) -> dict[str, Any]:
        """Call the Responses API, requesting a strict JSON object back."""
        response = self.client.responses.create(
            model=self.settings.OPENAI_MODEL,
            instructions=instructions + "\n\nRespond with ONLY valid JSON. No markdown, no commentary.",
            input=input_text,
            text={"format": {"type": "json_object"}},
        )
        raw = response.output_text.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("OpenAI response was not valid JSON, attempting cleanup. Raw: %s", raw[:200])
            cleaned = raw.strip("`").removeprefix("json").strip()
            return json.loads(cleaned)

    # ------------------------------------------------------------------
    # Feature: Summarize
    # ------------------------------------------------------------------
    def summarize_email(self, subject: str, body: str) -> dict[str, Any]:
        instructions = (
            "You are an assistant that summarizes emails concisely and accurately. "
            "Produce a JSON object with keys: 'summary' (2-3 sentence string) and "
            "'key_points' (array of short strings, max 5)."
        )
        input_text = f"Subject: {subject}\n\nBody:\n{body[:6000]}"
        result = self._run_json(instructions, input_text)
        return {
            "summary": result.get("summary", ""),
            "key_points": result.get("key_points", []),
        }

    # ------------------------------------------------------------------
    # Feature: Categorize
    # ------------------------------------------------------------------
    def categorize_email(self, subject: str, body: str) -> dict[str, Any]:
        categories = [c.value for c in EmailCategory]
        instructions = (
            "You are an email triage assistant. Classify the email into exactly one of "
            f"these categories: {', '.join(categories)}. "
            "Produce a JSON object with keys: 'category' (one of the listed values), "
            "'confidence' (float 0.0-1.0), and 'reasoning' (short string)."
        )
        input_text = f"Subject: {subject}\n\nBody:\n{body[:4000]}"
        result = self._run_json(instructions, input_text)
        category = result.get("category", EmailCategory.OTHER.value)
        if category not in categories:
            category = EmailCategory.OTHER.value
        return {
            "category": category,
            "confidence": float(result.get("confidence", 0.5)),
            "reasoning": result.get("reasoning", ""),
        }

    # ------------------------------------------------------------------
    # Feature: Extract tasks
    # ------------------------------------------------------------------
    def extract_tasks(self, subject: str, body: str) -> list[dict[str, Any]]:
        instructions = (
            "Extract any actionable tasks, action items, or to-dos mentioned in this email. "
            "Produce a JSON object with a single key 'tasks', an array of objects each with "
            "'description' (string), 'due_date' (string or null, ISO format if a date is stated), "
            "and 'priority' ('low', 'normal', or 'high'). "
            "If there are no actionable tasks, return an empty array."
        )
        input_text = f"Subject: {subject}\n\nBody:\n{body[:6000]}"
        result = self._run_json(instructions, input_text)
        return result.get("tasks", [])

    # ------------------------------------------------------------------
    # Feature: Translate
    # ------------------------------------------------------------------
    def translate_email(self, body: str, target_language: str) -> dict[str, Any]:
        instructions = (
            "You are a professional translator. Detect the source language of the given text, "
            f"then translate it into {target_language}. "
            "Produce a JSON object with keys: 'source_language' (string), "
            "'target_language' (string), and 'translated_text' (string, preserving paragraph structure)."
        )
        result = self._run_json(instructions, body[:6000])
        return {
            "source_language": result.get("source_language", "unknown"),
            "target_language": result.get("target_language", target_language),
            "translated_text": result.get("translated_text", ""),
        }

    # ------------------------------------------------------------------
    # Feature: Auto-reply
    # ------------------------------------------------------------------
    def generate_reply(self, subject: str, body: str, sender: str, tone: str = "professional") -> str:
        instructions = (
            f"You draft email replies in a {tone} tone on behalf of the user. "
            "Write a complete, ready-to-send reply body (no subject line, no markdown). "
            "Keep it concise, address the sender's points directly, and sign off politely. "
            "Do not fabricate specific facts, dates, or commitments not present in the original email."
        )
        input_text = f"Original email from: {sender}\nSubject: {subject}\n\nBody:\n{body[:5000]}"
        return self._run(instructions, input_text)
