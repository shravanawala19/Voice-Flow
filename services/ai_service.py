from __future__ import annotations

import logging
import os
from typing import Any

import requests

from services.text_processor import TextProcessor


LOGGER = logging.getLogger(__name__)


class AIService:
    def __init__(self) -> None:
        self.text_processor = TextProcessor()

    def process(self, text: str) -> str:
        endpoint = os.getenv("VOICEFLOW_AI_ENDPOINT")
        api_key = os.getenv("VOICEFLOW_AI_KEY")
        model = os.getenv("VOICEFLOW_AI_MODEL", "gpt-4o-mini")
        if not endpoint or not api_key:
            return self.text_processor.process(text, auto_punctuation=True)
        if not endpoint.lower().startswith("https://"):
            LOGGER.warning("AI endpoint is not HTTPS — skipping cloud AI")
            return self.text_processor.process(text, auto_punctuation=True)

        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=self._payload(model, text),
                timeout=20,
            )
            response.raise_for_status()
            return self._extract(response.json()).strip() or text
        except requests.RequestException:
            LOGGER.exception("AI request failed, falling back to local text cleanup")
            return self.text_processor.process(text, auto_punctuation=True)

    def _payload(self, model: str, text: str) -> dict[str, Any]:
        return {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Rewrite dictated speech into concise, ready-to-type text. "
                        "Preserve code requests as clear coding instructions. Return only the final text."
                    ),
                },
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
        }

    def _extract(self, data: dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            return str(message.get("content") or "")
        return ""
