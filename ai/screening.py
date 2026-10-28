"""Stage-1 opportunity screening via LLM (optional)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ai.client import LLMClient, load_prompt, split_into_batches

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent.parent


def analyze_opportunities(
    opportunities: list[dict],
    llm_client: Optional[LLMClient] = None,
    *,
    write_stub_if_missing: bool = True,
) -> list[dict]:
    """
    opportunities: already clustered & scored with evidence.
    Returns list of screening report dicts (or stub reports).
    """
    client = llm_client or LLMClient()
    prompt = load_prompt("prompts/opportunity_screening.md")
    results: list[dict] = []

    if not client.available:
        msg = (
            "OPENAI_API_KEY (or DEMAND_RADAR_API_KEY) not set. "
            "Skipped live LLM screening; wrote stub report."
        )
        logger.warning(msg)
        if write_stub_if_missing:
            stub = {
                "stub": True,
                "reason": "missing_api_key",
                "message": msg,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "input_count": len(opportunities),
                "opportunities": [
                    {
                        "opportunity_id": str(o.get("cluster_id") or o.get("title")),
                        "opportunity_name": o.get("title"),
                        "total_score": o.get("score"),
                        "confidence_level": o.get("confidence", "pending"),
                        "supporting_keywords": o.get("keywords") or [],
                        "demand_score": o.get("demand_score"),
                        "monetization_score": o.get("monetization_score"),
                        "competition_score": o.get("competition_score"),
                        "development_feasibility_score": o.get("feasibility_score"),
                        "evidence_quality_score": o.get("evidence_score"),
                        "recommended_next_step": "Set API key and re-run screening; also collect SEO competition data.",
                        "unresolved_questions": o.get("pending_dimensions") or [],
                    }
                    for o in opportunities[:10]
                ],
            }
            out_dir = ROOT / "exports" / "reports"
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / "screening_stub.json"
            path.write_text(json.dumps(stub, ensure_ascii=False, indent=2), encoding="utf-8")
            stub["report_path"] = str(path)
            results.append(stub)
        return results

    for batch in split_into_batches(opportunities, size=10):
        payload = [_slim(o) for o in batch]
        try:
            report = client.generate_structured(
                system_prompt=prompt,
                input_data=payload,
                schema="schemas/opportunity_report.json",
            )
            results.append(report if isinstance(report, dict) else {"opportunities": report})
        except Exception as exc:  # noqa: BLE001
            logger.error("screening batch failed: %s", exc)
            results.append({"error": str(exc), "batch_size": len(batch)})
    return results


def _slim(o: dict) -> dict[str, Any]:
    return {
        "title": o.get("title"),
        "category": o.get("category"),
        "cluster_id": o.get("cluster_id"),
        "keywords": o.get("keywords"),
        "score": o.get("score"),
        "demand_score": o.get("demand_score"),
        "monetization_score": o.get("monetization_score"),
        "competition_score": o.get("competition_score"),
        "feasibility_score": o.get("feasibility_score"),
        "evidence_score": o.get("evidence_score"),
        "confidence": o.get("confidence"),
        "pending_dimensions": o.get("pending_dimensions"),
        "rating_notes": o.get("rating_notes"),
    }
