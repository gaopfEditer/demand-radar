"""Swappable LLM client. Skips gracefully when no API key is set."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


class LLMClient:
    """Thin OpenAI-compatible client. Replace this class to swap providers."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get(
            "DEMAND_RADAR_API_KEY"
        )
        self.model = model or os.environ.get("DEMAND_RADAR_MODEL", "gpt-4o-mini")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self._client = None
        if self.api_key:
            try:
                from openai import OpenAI

                kwargs: dict[str, Any] = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = OpenAI(**kwargs)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to init OpenAI client: %s", exc)
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None and bool(self.api_key)

    def generate(
        self,
        system_prompt: str,
        user_content: str,
        *,
        temperature: float = 0.3,
    ) -> str:
        if not self.available:
            raise RuntimeError("LLM client unavailable: missing API key")
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        return resp.choices[0].message.content or ""

    def generate_structured(
        self,
        system_prompt: str,
        input_data: Any,
        *,
        schema: Optional[str | dict] = None,
    ) -> Any:
        schema_text = ""
        if isinstance(schema, str):
            path = ROOT / schema if not Path(schema).is_file() else Path(schema)
            if path.exists():
                schema_text = path.read_text(encoding="utf-8")
            else:
                schema_text = schema
        elif isinstance(schema, dict):
            schema_text = json.dumps(schema, ensure_ascii=False, indent=2)

        user_content = (
            "Input data (JSON):\n"
            f"{json.dumps(input_data, ensure_ascii=False, indent=2)}\n\n"
        )
        if schema_text:
            user_content += (
                "Return ONLY valid JSON matching this schema:\n"
                f"{schema_text}\n"
            )
        else:
            user_content += "Return ONLY valid JSON.\n"

        text = self.generate(system_prompt, user_content)
        return _extract_json(text)


def load_prompt(relative_path: str) -> str:
    path = ROOT / relative_path
    return path.read_text(encoding="utf-8")


def split_into_batches(items: list, size: int = 10) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _extract_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise
