"""Stage-2 deep project plan generation (optional LLM)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ai.client import LLMClient, load_prompt

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent.parent


def generate_project_plan(
    opportunity: dict,
    *,
    evidence: Optional[list[dict]] = None,
    llm_client: Optional[LLMClient] = None,
) -> dict[str, Any]:
    client = llm_client or LLMClient()
    prompt = load_prompt("prompts/project_plan.md")
    package = {
        "opportunity": opportunity,
        "evidence": evidence or [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    out_dir = ROOT / "exports" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in str(opportunity.get("title") or "opportunity")
    )[:60]

    if not client.available:
        stub = {
            "stub": True,
            "reason": "missing_api_key",
            "message": (
                "OPENAI_API_KEY not set. Stub project plan written. "
                "Rule-based scores are available; AI narrative skipped."
            ),
            "opportunity": opportunity,
            "evidence": evidence or [],
            "sections": {
                "opportunity_assessment": "Pending LLM — set OPENAI_API_KEY and re-run.",
                "product_design": None,
                "seo_strategy": None,
                "technical_implementation": None,
                "monetization": None,
                "validation_plan": (
                    "Cheapest test: landing page + waitlist for the primary keyword cluster."
                ),
                "execution_roadmap": None,
            },
        }
        path = out_dir / f"plan_stub_{safe_name}.json"
        path.write_text(json.dumps(stub, ensure_ascii=False, indent=2), encoding="utf-8")
        stub["report_path"] = str(path)
        return stub

    try:
        text = client.generate(
            prompt,
            "Evidence package (JSON):\n"
            + json.dumps(package, ensure_ascii=False, indent=2)
            + "\n\nWrite a full Markdown implementation plan.",
        )
        path = out_dir / f"plan_{safe_name}.md"
        path.write_text(text, encoding="utf-8")
        return {"report_path": str(path), "content": text, "stub": False}
    except Exception as exc:  # noqa: BLE001
        logger.error("deep research failed: %s", exc)
        return {"error": str(exc), "stub": True}
